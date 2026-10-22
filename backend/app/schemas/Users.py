from pydantic import BaseModel

class NewUser(BaseModel):
    """Model/schema for the Create User endpoint POST body."""
    username: str = ""
    password: str = ""
    login: bool = False

class UserLogin(BaseModel):
    """Model/schema for the Login endpoint POST body."""
    username: str = ""
    password: str = ""