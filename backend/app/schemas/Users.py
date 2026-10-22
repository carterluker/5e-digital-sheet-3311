from pydantic import BaseModel, Field

class NewUser(BaseModel):
    """Model/schema for the Create User endpoint POST body."""
    username: str = Field(default="", min_length=3, max_length=30)  # max matches the User.username column
    password: str = Field(default="", min_length=8, max_length=128)
    login_after: bool = False

class UserLogin(BaseModel):
    """Model/schema for the Login endpoint POST body."""
    username: str = ""
    password: str = ""
