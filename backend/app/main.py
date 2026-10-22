from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.db import SessionLocal, create_tables, get_db

from .models.User import User
from .models.UserSession import UserSession

from .schemas.Users import UserLogin, NewUser

from .schemas.CharacterModels import (
    BackgroundSchema, CharacterClassSchema, FeatSchema, SpeciesSchema, SpellSchema, SubclassSchema,
)

from .services.character_models import (
    get_backgrounds, get_character_classes, get_feats, get_species, get_spells, get_subclasses,
)
from .services.characters import get_user_characters
from .services.users import (
    login, logout, create_user, setup_default_user, delete_expired_sessions,
    get_current_session, get_current_user,
)

from sqlalchemy.orm import Session

app = FastAPI(title="5e Digital Character Sheet")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- App Startup ---

@app.on_event("startup")
def on_startup():
    create_tables()
    with SessionLocal() as db:
        setup_default_user(db)
        delete_expired_sessions(db)

# --- Users and Login ---

@app.post("/api/user/create/", tags=["Users"])
def create_user_endpoint(new_user: NewUser, db: Session = Depends(get_db)):
    """Creates a new user using the provided credentials. Optionally logs the new user in by returning a session token."""

    user = create_user(new_user.username, new_user.password, db)
    response = {"username": user.username}
    if new_user.login_after:
        response["session_token"] = login(new_user.username, new_user.password, db)
    return response


@app.post("/api/user/login/", tags=["Users"])
def login_endpoint(user_login: UserLogin, db: Session = Depends(get_db)):
    """Given a username and password, validate the users credentials and return a session token."""
    
    return {"session_token": login(user_login.username, user_login.password, db)}


@app.get("/api/user/me/", tags=["Users"])
def me_endpoint(user: User = Depends(get_current_user)):
    """Returns the user that owns the session token given in the Authorization header."""

    return {"username": user.username}


@app.post("/api/user/logout/", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def logout_endpoint(user_session: UserSession = Depends(get_current_session), db: Session = Depends(get_db)):
    """Ends the session given in the Authorization header."""

    logout(user_session, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)



# --- Characters ---

@app.get("/api/characters/", tags=["Characters"])
def list_characters_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns a summary (id and name) of every character owned by the logged in user."""

    return [{"id": character.id, "name": character.name} for character in get_user_characters(user, db)]

# --- Models ---

# --- Character Component Models ---
# Read-only lists of the rules content a character is built from. Login required, like the rest of the API.

@app.get("/api/model/class/", response_model=list[CharacterClassSchema], tags=["Model"])
def list_character_classes_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns every character class."""

    return get_character_classes(db)


@app.get("/api/model/subclass/", response_model=list[SubclassSchema], tags=["Model"])
def list_subclasses_endpoint(class_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns every subclass of the character class with the given class_id."""

    return get_subclasses(class_id, db)


@app.get("/api/model/species/", response_model=list[SpeciesSchema], tags=["Model"])
def list_species_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns every species."""

    return get_species(db)


@app.get("/api/model/background/", response_model=list[BackgroundSchema], tags=["Model"])
def list_backgrounds_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns every background."""

    return get_backgrounds(db)


@app.get("/api/model/feat/", response_model=list[FeatSchema], tags=["Model"])
def list_feats_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns every feat."""

    return get_feats(db)


@app.get("/api/model/spell/", response_model=list[SpellSchema], tags=["Model"])
def list_spells_endpoint(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns every spell, ordered by level then name."""

    return get_spells(db)
