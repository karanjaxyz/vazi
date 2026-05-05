from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    user_uid: str
    email: str

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    """Used internally when creating a user from a Firebase token.
    Not exposed as an API input — Firebase handles registration."""

    user_uid: str
    email: str
