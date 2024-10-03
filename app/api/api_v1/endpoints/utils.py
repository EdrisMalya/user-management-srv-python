from typing import Any

from app import schemas
from app.core.producer import publisher
from app.utils import generate_random_password
from fastapi import APIRouter
import re
from pydantic.networks import EmailStr

router = APIRouter()


@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
def test_email(
    email_to: EmailStr,
    # current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    # celery_app.send_task("user_added", args=[email_to])
    random_password = generate_random_password()
    publisher.publish(
        queue_name="emails",
        exchange_name="emails",
        method="user_created",
        message={"email": email_to, "random_password": random_password},
        routing_key="emails",
    )
    return {"msg": "Test email sent"}


def slug(text):
    # Convert the text to lowercase
    text = text.lower()

    # Replace all non-alphanumeric characters with a hyphen
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text)

    # Remove any leading or trailing hyphens
    text = text.strip('-')

    # Return the resulting slug
    return text
