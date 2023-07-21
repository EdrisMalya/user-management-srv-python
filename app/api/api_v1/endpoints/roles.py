from typing import Any, List

from app import crud, models, schemas
from app.api import deps
from app.schemas.role import RoleOutput, Role
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[RoleOutput])
async def read_roles(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        permissions: list = Depends(deps.get_current_active_user_permissions),
        skip: int = 1,
        limit: int = 10,
) -> Any:
    """
    Retrieve roles.
    """
    loggedInUser = current_user.__dict__
    if "roles.view" in permissions or loggedInUser["is_superuser"] == True:
        return crud.role.get_multi(db=db, skip=skip, limit=limit)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": False, "message": "Note enough permission"},
        )


@router.get("/role_short", response_model=schemas.ShortRole | Any)
def short_role_details(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
        permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    loggedInUser = current_user.__dict__
    if "roles.view" in permissions or loggedInUser["is_superuser"] == True:
        roles = crud.role.get_short(db)
        print(roles[0].id)
        return roles
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": False, "message": "Note enough permission"},
        )


@router.get("/{role_id}", response_model=schemas.Role)
def read_role(
        *,
        db: Session = Depends(deps.get_db),
        role_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
        permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    """
    GET role by ID.
    """
    loggedInUser = current_user.__dict__
    if "roles.view" in permissions or loggedInUser["is_superuser"] == True:
        role = crud.role.get(db=db, id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"status": False, "message": "Role not found"},
            )
        return role
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": False, "message": "Not enough permission"},
        )


@router.post("/", response_model=schemas.Role)
def create_role(
        *,
        db: Session = Depends(deps.get_db),
        role_in: schemas.RoleCreate = Body(embed=False),
        current_user: models.User = Depends(deps.get_current_active_user),
        permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    """
    Create new role
    """
    loggedInUser = current_user.__dict__
    if "role.add" in permissions or loggedInUser["is_superuser"] == True:
        role_name = crud.role.get_by_role_name(db=db, name=role_in.name)
        if role_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"field_name": "name", "message": "Role name already exists"},
            )
        role = crud.role.create(db=db, obj_in=role_in, user_id=current_user.id)
        if role:
            raise HTTPException(
                status_code=status.HTTP_201_CREATED,
                detail={"status": True, "message": "Role created successfully"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": False, "message": "Not enough permission"},
        )


@router.put("/{role_id}", response_model=schemas.Role)
def update_role(
        *,
        db: Session = Depends(deps.get_db),
        role_id: int,
        role_in: schemas.RoleUpdate,
        current_user: models.User = Depends(deps.get_current_active_user),
        permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    """
    Update a role
    """
    loggedInUser = current_user.__dict__
    if "roles.edit" in permissions or loggedInUser["is_superuser"] == True:
        role = crud.role.get(db=db, id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={"status": False, "message": "Role not found"},
            )
        role = crud.role.update(db=db, db_obj=role, obj_in=role_in)
        if role:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={"status": True, "message": "Role updated successfully"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Note enough permission"
        )


@router.delete("/{role_id}", response_model=schemas.Msg)
def delete_item(
        *,
        db: Session = Depends(deps.get_db),
        role_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
        permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    """
    Delete a role
    """
    loggedInUser = current_user.__dict__
    if "roles.delete" in permissions or loggedInUser["is_superuser"] == True:
        if crud.role.check_if_role_has_permissions(db=db, id=role_id):
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={
                    "status": False,
                    "message": "Role has permissions assigned to it",
                },
            )

        if crud.role.delete(db=db, id=role_id):
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={"status": True, "message": "Role deleted successfully"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": False, "message": "Note enough permission"},
        )
