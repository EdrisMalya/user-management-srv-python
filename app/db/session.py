import os
import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from app.core.config import settings

odbc_driver = settings.MSSQL_DRIVER.strip("'")
host = settings.MSSQL_SERVER.strip("'")
database = settings.MSSQL_DATABASE
user = settings.MSSQL_USER
password = settings.MSSQL_PASS

params = urllib.parse.quote_plus(
    f"DRIVER={odbc_driver};SERVER={host};DATABASE={database};UID={user};PWD={password};ENCRYPT=no;CONNECTION_TIMEOUT=30;TrustServerCertificate=yes"
)
engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print(f"DRIVER={os.getenv('ODBC_DRIVER')}")

