from typing import Any, List

from app import crud, models, schemas
from app.api import deps
from fastapi import APIRouter, Body, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.api.api_v1.endpoints.utils import slug

router = APIRouter()

# Get Multiple permissions
@router.get("/", response_model=List[schemas.Permission])
def read_permissions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
    
) -> Any:
    "Retrive Permission"
    loggedInUser = current_user.__dict__
    if "permission.view" in permissions or loggedInUser["is_superuser"] == True:
        permissions = crud.permission.get_multi(db, skip=skip, limit=limit)
        return permissions


# Get Signle permission respected to the permission_id
@router.get("/{permission_id}", response_model=schemas.Permission)
def read_role(
    *,
    db: Session = Depends(deps.get_db),
    permission_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    "GET Single Permission"
    loggedInUser = current_user.__dict__
    if "permission.view" in permissions or loggedInUser["is_superuser"] == True:
        permission = crud.permission.get(db=db, id=permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
            )
        if not crud.user.is_superuser(current_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Note enough permission"
            )
        return permission
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": False, "message": "You do not have enough privileges"},
        )


@router.post("/", response_model=schemas.Permission)
def create_permission(
        *,
        db: Session = Depends(deps.get_db),
        description: str = Body(...),
        group_id: int = Body(...),
        current_user: models.User = Depends(deps.get_current_active_user),
        permissions: list = Depends(deps.get_current_active_user_permissions),

) -> Any:
    "Create new Permission"
    loggedInUser = current_user.__dict__
    if "permission.add" in permissions or loggedInUser["is_superuser"] == True:
        # 1. First check if the permission with this name is already in the permissions list
        permission_group = crud.permission_group.get_group_by_id(db=db, group_id=group_id)
        name = slug(permission_group.name + ' ' + description)
        result = crud.permission.get_by_permission_name(db=db, name=name)
        if result is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"field_name": "description", "message": "Permission is duplicate, please choose another name"}
            )
        permission_in = schemas.PermissionCreate(
            name=name, description=description, group_id=group_id
        )
        if crud.permission.create(db=db, obj_in=permission_in, user_id=current_user.id):
            raise HTTPException(
                status_code=status.HTTP_201_CREATED,
                detail={"status": True, "message": "Permission Inserted successfully"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"status": False, "message": "Internal Server Error"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": False, "message": "You do not have enough privileges"},
        )


@router.post("/assinged/{role_id}", response_model=schemas.Msg)
def assign_permissions_to_role(
    *,
    db: Session = Depends(deps.get_db),
    role_id: int,
    name: str = Body(...),
    permission: list[int] = Body(...),
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    "Assign Permissions to Role"
    loggedInUser = current_user.__dict__
    if "roles-access" in permissions or loggedInUser["is_superuser"] == True:
        # First delete all the permissions for the selected role
        crud.permission.delete_permissions_base_on_role_id(db=db, role_id=role_id)
        # Then store the permissions based on the role id
        if crud.permission.assign_permissions_to_role(
            db=db, role_id=role_id, permission=permission
        ):
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={"status": True, "message": "Permissions assigned successfully"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"status": False, "message": "Internal Server Error"},
            )
        # Send the status
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": False, "message": "You do not have enough privileges"},
        )


@router.get("/assign_roles/{role_id}", response_model=Any)
def retrive_assigned_permissions_to_role(
    *,
    db: Session = Depends(deps.get_db),
    role_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    "Retrieve Assigned Permissions for specific Role"
    loggedInUser = current_user.__dict__
    if "roles-access" in permissions or loggedInUser["is_superuser"] == True:
        permissions = crud.permission.get_assigned_permissions(db=db, role_id=role_id)
        role = db.query(models.Role).filter(models.Role.id == role_id).first()
        role = role.__dict__
        return {"roles": permissions, "name": role["name"]}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": False, "message": "You do not have enough privileges"},
        )


@router.put("/{permission_id}", response_model=schemas.Permission)
def update_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission_id: int,
    name: str = Form(...),
    description: str = Form(None),
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    "Update Permission"
    loggedInUser = current_user.__dict__
    if "permission.edit" in permissions or loggedInUser["is_superuser"] == True:
        permission_in = schemas.PermissionUpdate(name=name, description=description)
        permission = crud.permission.get(db=db, id=permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": False, "message": "Permission not found"},
            )
        if not crud.user.is_superuser(current_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Note enough permission"
            )
        permission_result = crud.permission.update(
            db=db, db_obj=permission, obj_in=permission_in
        )
        return permission_result
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": False, "message": "You do not have enough privileges"},
        )


@router.delete("/{permission_id}", response_model=schemas.Permission)
def delete_permission(
    *,
    db: Session = Depends(deps.get_db),
    permission_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
    
) -> Any:
    "Delete Permission"
    loggedInUser = current_user.__dict__
    if "permission.delete" in permissions or loggedInUser["is_superuser"] == True:
        if crud.permission.remove(db=db, id=permission_id) == None:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={"status": True, "message": "Permission Deleted Successfully"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"status": False, "message": "Internal Server Error"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": False, "message": "You do not have enough privileges"},
        )
