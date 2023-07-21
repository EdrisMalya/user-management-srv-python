from typing import Any, List

from app import crud, models, schemas
from app.api import deps
from app.schemas.role_group import RoleGroupOutput
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()

# GET Multiple role_group
@router.get("/", response_model=List[RoleGroupOutput])
def read_role_group(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    "Retrieve role group"
    loggedInUser = current_user.__dict__
    if "roles.view" in permissions or loggedInUser["is_superuser"] == True:
        role_groups = crud.role_group.get_multi(db=db)
        return role_groups
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": False, "message": "Note enough permission"},
        )


# GET Single role_group
@router.get(
    "/{role_group_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.RoleGroupSchema,
    response_model_exclude_none=True,
)
def read_role_group(
    *,
    db: Session = Depends(deps.get_db),
    role_group_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    "GET role group by ID"
    loggedInUser = current_user.__dict__
    if "roles.view" in permissions or loggedInUser["is_superuser"] == True:
        role_group = crud.role_group.get(db=db, id=role_group_id)
        if not role_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": False, "message": "RoleGroup not found"},
            )
        if not crud.user.is_superuser(current_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"status": False, "message": "Note enough permission"},
            )
        return role_group
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": False, "message": "Note enough permission"},
        )


# Insert the role_group
@router.post(
    "/",
    response_model=schemas.RoleGroup,
)
def create_role_group(
    *,
    db: Session = Depends(deps.get_db),
    role_group_in: schemas.RoleGroupCreate = Body(embed=False),
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
) -> models.RoleGroup:
    "Create new RoleGroup"
    loggedInUser = current_user.__dict__
    if "roles.add" in permissions or loggedInUser["is_superuser"] == True:
        role_group = crud.role_group.create(
            db=db, obj_in=role_group_in, user_id=current_user.id
        )
        if role_group:
            raise HTTPException(
                status_code=status.HTTP_201_CREATED,
                detail={"status": True, "message": "Role Group created successfully"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": False, "message": "You do not have enough privileges"},
        )


@router.put("/{role_group_id}", response_model=schemas.RoleGroup)
def update_role_group(
    *,
    db: Session = Depends(deps.get_db),
    role_group_id: int,
    role_group_in: schemas.RoleGroupUpdate = Body(embed=False),
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    "Update Role Group"
    loggedInUser = current_user.__dict__
    if "roles.edit" in permissions or loggedInUser["is_superuser"] == True:
        role_group = crud.role_group.get(db=db, id=role_group_id)
        if not role_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": False, "message": "RoleGroup not found"},
            )
        role_group = crud.role_group.update(
            db=db, db_obj=role_group, obj_in=role_group_in
        )
        if role_group:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={"status": True, "message": "Role Group updated successfully"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": False, "message": "You do not have enough privileges"},
        )


@router.delete("/{role_group_id}")
def delete_item(
    *,
    db: Session = Depends(deps.get_db),
    role_group_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
) -> None:
    "Delete role group"
    loggedInUser = current_user.__dict__
    if "roles.delete" in permissions or loggedInUser["is_superuser"] == True:
        role_group = crud.role_group.get(db=db, id=role_group_id)
        if not role_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": False, "message": "Role Group not found"},
            )
        # Check if role group has any role's assigned to it
        if crud.role_group.check_role_group_has_any_roles(
            db=db, role_group_id=role_group_id
        ):
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={
                    "status": False,
                    "message": "Role Group has roles assigned to it, cannot be deleted",
                },
            )
        role_group = crud.role_group.delete(db=db, id=role_group_id)
        if role_group == None or role_group == True:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={"status": True, "message": "Role Group deleted successfully"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": False, "message": "You do not have enough privileges"},
        )
