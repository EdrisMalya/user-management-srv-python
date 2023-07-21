import logging
import os
from datetime import date, datetime
from typing import List

from sqlalchemy import exc

from app import models
from app.db.session import SessionLocal

# Set Time Zone
os.environ["TZ"] = "Asia/Kabul"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    db = SessionLocal()
    # Get all the users
    users: List[models.User] = db.query(models.User).all()

    for user in users:
        if user.expiryDate != None and user.expiryDate != "":
            expiry_date = datetime.strptime(user.expiryDate, "%m/%d/%Y")
            if expiry_date.date() > date.today():
                logger.info("Not Expired")
            else:
                logger.info("Expired")
                user.is_active = False
                user.needsToChangePassword = True
                user.expiryDate = ""
                try:
                    db.commit()
                    logger.info(
                        f"Expired user {user.first_name} {user.last_name} has been de-activated successfully"
                    )
                except exc.SQLAlchemyError:
                    db.rollback()
                    logger.error("Internal Server Error")
        else:
            logger.info(f"User {user.first_name} {user.last_name} is not expired")


def main() -> None:
    logger.info("Checking user Expiry started")
    init()
    logger.info("Action Completed")


if __name__ == "__main__":
    main()
