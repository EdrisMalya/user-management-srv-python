import os
import socket
import urllib

from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if os.getenv('FASTAPI_ENV') == 'production':
    driver = os.getenv("MSSQL_DRIVER")
    user = os.getenv("MSSQL_LIVE_USER")
    password = os.getenv("MSSQL_LIVE_PASS")
    db = os.getenv("MSSQL_LIVE_DATABASE")
    server = os.getenv("MSSQL_LIVE_SERVER")
    params = urllib.parse.quote_plus(
        f"DRIVER={driver};SERVER={server};DATABASE={db};UID={user};PWD={password};ENCRYPT=no;CONNECTION_TIMEOUT=30"
    )
elif os.getenv('FASTAPI_ENV') == 'development':
    driver = os.getenv("MSSQL_DRIVER_PRODUCTION")
    user = os.getenv("MSSQL_TEST_USER")
    password = os.getenv("MSSQL_TEST_PASS")
    db = os.getenv("MSSQL_TEST_DATABASE")
    params = urllib.parse.quote_plus(
        f"DSN={driver};DATABASE={db};UID={user};PWD={password};ENCRYPT=no;CONNECTION_TIMEOUT=30"
    )
else:
    server = settings.MSSQL_TEST_SERVER if socket.gethostname().upper() != 'NAIM-FAIZY-PC' else 'NAIM-FAIZY-PC'
    password = settings.MSSQL_TEST_PASS if socket.gethostname().upper() != 'NAIM-FAIZY-PC' else 'Kabul@123'
    params = urllib.parse.quote_plus(
        f"DRIVER={settings.MSSQL_DRIVER};SERVER={server};DATABASE={settings.MSSQL_TEST_DATABASE};UID={settings.MSSQL_TEST_USER};PWD={password};ENCRYPT=no;CONNECTION_TIMEOUT=30"
    )

engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
