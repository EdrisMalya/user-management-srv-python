import json
from datetime import datetime, timedelta
from typing import Any

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.producer import publisher
from app.core.security import get_password_hash, verify_password
from app.models.user_password_history import UserPasswordHistory
from app.utils import check_password_policy, generate_password_reset_token, verify_password_reset_token
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import exc
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    print(
        'test'
    )
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
        # return user
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    # Check if the user is active or not
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    # First check if there are any roles assigned to the user
    roles = crud.user.get_user_roles(db=db, user_id=user.id)
    if roles:
        role_arr = []
        for r in roles:
            role_arr.append(r.role_id)
        role_arr = json.dumps(role_arr)

        # Second retrive all the permissions for the user in the assigned roles
        get_permissions_by_role_id = []
        get_permissions_by_permission_id = []
        for r in roles:
            get_permissions_by_role_id.append(
                crud.user.get_user_permissions_based_on_roles(db=db, role_id=r.role_id)
            )
        # Loop through the permissions retrived respected to role_id from role_permission table
        # Store the result in a variable
        for permission in get_permissions_by_role_id:
            for p in permission:
                get_permissions_by_permission_id.append(
                    crud.permission.get(db=db, id=p.permission_id)
                )
        # This iteration is for getting the permissions name from permission table respected to the permission ID
        permissions = []
        for x in get_permissions_by_permission_id:
            permissions.append(x.name)
        permissions = json.dumps(permissions)
    else:
        print("No Roles")
        role_arr = []
        permissions = []
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # publisher.publish(queue_name="logging", exchange_name="logging", method="login_successfull", message={"message":f"User {user.email} loggedin successfully", "severityId": 1, "categoryId": 2}, routing_key="logging")
    return {
        "access_token": security.create_access_token(
            user.id,
            expires_delta=access_token_expires,
            roles=role_arr,
            permissions=permissions,
        ),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=schemas.UserLoginSchema | Any)
def test_token(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Test access token
    """
    # First check if there are any roles assigned to the user
    roles = crud.user.get_user_roles(db=db, user_id=current_user.id)
    if roles:
        role_arr = []
        for r in roles:
            role_arr.append(r.role_id)

        # Second retrive all the permissions for the user in the assigned roles
        get_permissions_by_role_id = []
        get_permissions_by_permission_id = []
        for r in roles:
            get_permissions_by_role_id.append(
                crud.user.get_user_permissions_based_on_roles(db=db, role_id=r.role_id)
            )
        # Loop through the permissions retrived respected to role_id from role_permission table
        # Store the result in a variable
        for permission in get_permissions_by_role_id:
            for p in permission:
                get_permissions_by_permission_id.append(
                    crud.permission.get(db=db, id=p.permission_id)
                )
        # This iteration is for getting the permissions name from permission table respected to the permission ID
        permissions = []
        for x in get_permissions_by_permission_id:
            permissions.append(x.name)

        current_user = current_user.__dict__
        current_user["roles"] = role_arr
        current_user["permissions"] = permissions
        return current_user
    else:
        current_user = current_user.__dict__
        current_user["roles"] = []
        current_user["permissions"] = []
        return current_user


# Change password endpoint
@router.post("/change_password", response_model=Any)
def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    # 1. Check the user's old password is correct
    user = crud.user.get_by_email(db, email=current_user.email)
    if not verify_password(old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "field_name": "old_password",
                "message": "Old password does not match",
            },
        )

    # store old password hashed for later use
    old_password_hashed = user.password

    # Check if the password policy matches
    if not check_password_policy(new_password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "field_name": "new_password",
                "message": "Password does not meet the menimum password policy requirement",
            },
        )

    # 2. Verify the new_password and confirm_password matches
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "field_name": "confirm_password",
                "message": "Confirm Password do not match",
            },
        )

    # 3. Check in the user_password_history table for the password that this user has used it before or not
    passwords = crud.user.get_previous_passwords_of_current_user(
        db=db, user_id=current_user.id
    )
    for p in passwords:
        print(p)
        if verify_password(new_password, p.password):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "field_name": "new_password",
                    "message": "This password is already used!",
                },
            )

    # 4. Update the user with new_password and change the NeedsToChangePassword field status to false
    crud.user.update(
        db=db,
        db_obj=user,
        obj_in={
            "password": get_password_hash(new_password),
            "needsToChangePassword": False,
            "lastUpdatedBy": user.id,
            "lastUpdatedDate": datetime.now(),
        },
    )

    # 5. Insert the old password hashed value to the reset_password table with the user id
    passwordHistory = UserPasswordHistory(user_id=user.id, password=old_password_hashed)
    db.add(passwordHistory)
    db.commit()

    # 6. Send an email to the user that the password has been changed successfully
    publisher.publish(
        queue_name="emails",
        exchange_name="emails",
        method="user_password_changed",
        message={"email": current_user.email},
        routing_key="emails",
    )

    # 7. Returnt the status_code with message
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"status": True, "message": "Your password changed successfully"},
    )


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(
    email: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Password Recovery
    """
    user = crud.user.get_by_email(db, email=email)
    password_reset_token = generate_password_reset_token(email=email)
    publisher.publish(
        queue_name="emails",
        exchange_name="emails",
        method="user_reset_password",
        message={"email_to": user.email, "email": email, "token": password_reset_token},
        routing_key="emails",
    )
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"status": True, "message": "Password recovery email sent successfully"},
    )


@router.post("/reset-password/", response_model=schemas.Msg)
def reset_password(
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    # 1. Check that token is valid
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(
            status_code=404, detail={"status": False, "message": "Invalid token"}
        )

    # 2. Check the email is valid
    user = crud.user.get_by_email(db=db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "message": "The user with this username does not exist in the system.",
            },
        )

    # 3. Check if the user is active
    if not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"field_name": "new_password", "message": "Inactive user"},
        )

    # 4. Check if the new password meets the password policy
    if not check_password_policy(new_password):
        # Check if the password policy matches
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "field_name": "new_password",
                "message": "Password does not meet the minimum password policy requirement",
            },
        )

    # 5. Verify the new_password and confirm_password matches
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "field_name": "confirm_password",
                "message": "Confirm Password do not match",
            },
        )

    # 6. Check in the user_password_history table for the password that this user has used it before or not
    passwords = crud.user.get_previous_passwords_of_current_user(db=db, user_id=user.id)
    for p in passwords:
        if verify_password(new_password, p.password):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "field_name": "new_password",
                    "message": "This password is already used!",
                },
            )

    # 7. Insert the old password hashed value to the reset_password table with the user id
    passwordHistory = UserPasswordHistory(user_id=user.id, password=user.password)
    db.add(passwordHistory)

    # 8. Hash the new password and store it in the password filed of user
    hashed_password = get_password_hash(new_password)
    user.password = hashed_password
    db.add(user)

    try:
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail={"status": True, "message": "Password updated successfully"},
        )
    except exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": False, "message": "Internal Server Error"},
        )
