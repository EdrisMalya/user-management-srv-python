from typing import Any

from app import crud, models, schemas
from app.api import deps
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()

# GET Multiple permission_group
@router.get("/", response_model=Any)
def read_permission_group(
    db: Session = Depends(deps.get_db),
    skip: int = 1,
    limit: int = 10,
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
    
) -> Any:
    "Retrive permission group"
    loggedInUser = current_user.__dict__
    if "permission.view" in permissions or loggedInUser["is_superuser"] == True:
        permission_groups = crud.permission_group.get_multi(db=db, skip=skip, limit=limit)
        return permission_groups
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": False, "message": "You do not have enough privileges"},
        )
        

# GET Single permission_group
@router.get(
    "/{permission_group_id}",
    response_model=Any,
)
def read_single_permission_group(
    *,
    db: Session = Depends(deps.get_db),
    permission_group_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
    
) -> Any:
    "GET permission_group by ID"
    loggedInUser = current_user.__dict__
    if "permission.view" in permissions or loggedInUser["is_superuser"] == True:
        permission_group = crud.permission_group.get(db=db, id=permission_group_id)
        if not permission_group:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={"status": False, "message": "Permission Group not found"},
            )
        return permission_group    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": False, "message": "You do not have enough privileges"},
        )


# Insert the permission_group
@router.post(
    "/",
    response_model=schemas.PermissionGroup,
)
def create_permission_group(
    *,
    db: Session = Depends(deps.get_db),
    name: str = Body(...),
    permission_group_id: int = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),
    
) -> models.PermissionGroup:
    "Create new PermissionGroup"
    loggedInUser = current_user.__dict__
    if "permission.add" in permissions or loggedInUser["is_superuser"] == True:
        permission_group_in = schemas.PermissionGroupCreate(
            name=name, permission_group_id=permission_group_id
        )
        if not permission_group_in.name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Permission Group name is required",
            )
        if crud.permission_group.create(
            db=db, obj_in=permission_group_in, user_id=current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_201_CREATED,
                detail={"status": True, "message": "Permission Group Created Successfully"},
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


@router.put("/{permission_group_id}", response_model=schemas.PermissionGroup)
def update_permission_group(
    *,
    db: Session = Depends(deps.get_db),
    permission_group_in: schemas.PermissionGroupUpdate = Body(embed=False),
    permission_group_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),

) -> Any:
    "update Permission Group"
    loggedInUser = current_user.__dict__
    if "permission.edit" in permissions or loggedInUser["is_superuser"] == True:
        permission_group = crud.permission_group.get_single_record(
            db=db, id=permission_group_id
        )
        if not permission_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": False, "message": "PermissionGroup not found"},
            )
        if crud.permission_group.update(
            db=db, db_obj=permission_group, obj_in=permission_group_in
        ):
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={"status": True, "message": "Permission Group Updated Successfully"},
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


@router.delete("/{permission_group_id}", response_model=schemas.PermissionGroup)
def delete_item(
    *,
    db: Session = Depends(deps.get_db),
    permission_group_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    permissions: list = Depends(deps.get_current_active_user_permissions),

) -> Any:
    "Delete Permission Group"
    loggedInUser = current_user.__dict__
    if "permission.delete" in permissions or loggedInUser["is_superuser"] == True:
        # First check if permission_group has no other permission_group inside it
        if crud.permission_group.check_permission_group_has_groups(
            db=db, id=permission_group_id
        ):
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={
                    "status": False,
                    "message": "Cannot delete, because this group contains groups",
                },
            )

        # Check if the group has any permissions assigned to it
        if crud.permission_group.check_if_group_has_permissions(
            db=db, id=permission_group_id
        ):
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={
                    "status": False,
                    "message": "Cannot delete, because this group contains permissions",
                },
            )

        # IF there are no groups attached to this group then you can delete it
        if crud.permission_group.delete(db=db, id=permission_group_id):
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={"status": True, "message": "Permission Group Deleted Successfully"},
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
