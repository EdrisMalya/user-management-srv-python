import json

import pandas as pd
from app import crud, schemas
from app.core.config import settings
from app.db import base  # noqa: F401
from sqlalchemy.orm import Session

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28

def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    user = crud.user.get_by_email(db=db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PW,
            is_superuser=True,
            is_active=True,
            lastChangedPasswordDate=settings.USER_CHANGED_PASSWORD_DATE,
            needsToChangePassword=False,
            roles=[],
        )
        user_in = crud.user.create(db=db, obj_in=user_in)
        print("User Details:")
        print(user)
    else:
        print("User already exists")

    # Import CSV
    data = pd.read_csv(r'./app/db/dbo.permission_group.csv')
    permission_groups = pd.DataFrame(data)
    for row in permission_groups.itertuples():
        permission_group = crud.permission_group.get_by_permission_group_name(
            db=db, name=row.name
        )
        if not permission_group:    
            permission_group_id = str(row.permission_group_id)
            if permission_group_id == 'nan':
                permission_group_in = schemas.PermissionGroupCreate(name=row.name)
            else:
                permission_group_in = schemas.PermissionGroupCreate(name=row.name, permission_group_id=row.permission_group_id)
            crud.permission_group.create(db=db, obj_in=permission_group_in, user_id=1)
            print(f"Permission group {row.name} created successfully")
        else:
            print(f"Permission group {row.name} already exists")
    print("")

    # Import CSV
    data = pd.read_csv(r'./app/db/dbo.permission.csv')
    permissions = pd.DataFrame(data)
    # Insert DataFrame to Table
    for row in permissions.itertuples():
        permission_name = crud.permission.get_by_permission_name(db=db, name=row.name)
        if permission_name == None:
            permission_in = schemas.PermissionCreate(name=row.name, description=row.description, group_id=row.group_id)
            crud.permission.create(db=db, obj_in=permission_in, user_id=1)
            print(f"Permission {row.name} has been created successfully")
        elif row.name != permission_name.name:
            permission_in = schemas.PermissionCreate(name=row.name, description=row.description, group_id=row.group_id)
            crud.permission.create(db=db, obj_in=permission_in, user_id=1)
            print(f"Permission {row.name} has been created successfully")
        else:
            print(f"Permission {row.name} already exists")
    print("")


    role = crud.role.get_by_role_name(db=db, name="Admin")
    if not role:
        role_in = schemas.RoleCreate(
            name="Admin",
            description="Administrator Role",
            permissions=[],
            role_group_id=1,
        )
        role = crud.role.create(db=db, obj_in=role_in, user_id=1)
        print("Admin role created successfully")
        print("")
        permissions=[]
        crud.permission.assign_permissions_to_role(db=db, role_id=1, permission=permissions)
        print("Permissions assigned to Admin role successfully")
        print("")
        user_obj = schemas.UserUpdate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PW,
            role_id=[{"label": "Administrator", "value": 1}],
        )
        if user == None:
            user = crud.user.get_by_email(db=db, email=settings.FIRST_SUPERUSER)
            crud.user.update(db=db, db_obj=user, obj_in=user_obj)
        else:
            crud.user.update(db=db, db_obj=user, obj_in=user_obj)            
        print("Admin role assigned to user")
        print("")
    else:
        print("Role already exists")
        print("")

    role_group = crud.role_group.get_by_role_group_name(db=db, name="Super Admin")
    if not role_group:
        role_group_in = schemas.RoleGroupCreate(name="Super Admin", roles=[1])
        role_group = crud.role_group.create(
            db=db, obj_in=role_group_in, user_id=1
        )
        print("Role Group created successfully")
        print("")
    else:
        print("Role Group already exists")
        print("")
    
    print("Initial Data insertion completed successfully")
