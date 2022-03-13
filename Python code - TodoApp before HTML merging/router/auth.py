import sys
sys.path.append("..") # This will allow to properly be able to import everything that is in the parent directory of auth.

from fastapi import Depends, HTTPException, status, APIRouter
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
import models
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm # when users totry signin, they gonna sign in thru Oauth2 sign in form
from fastapi.security import OAuth2PasswordBearer # Type of token and authorization platform
from datetime import datetime, timedelta
from jose import jwt, JWTError

# Add secret key
SECRET_KEY = "KlgH6AzYDeZZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

#app = FastAPI()
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token") # Extract the data from the authorization header

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_password_hashed(password): # Return an encryption in a hash using bcrypt
    return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str, db: Session=Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta]=None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str

async def get_current_user(token: str= Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise get_user_exception()
        return {"username":username, "id":user_id}
    except JWTError:
        raise get_user_exception()

@router.post("/create/user")
async def create_new_user(create_user: CreateUser, db: Session= Depends(get_db)):
    create_user_model = models.Users()
    create_user_model.email = create_user.email
    create_user_model.username = create_user.username
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name
    ##### Password hashed #######
    hash_password = get_password_hashed(create_user.password)
    #create_user_model.hashed_password = create_user.password # Need to encrypted the password
    create_user_model.hashed_password = hash_password
    create_user_model.is_active = True

    db.add(create_user_model)
    db.commit()


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise token_exception()
    #return "User Validated"
    token_expires = timedelta(minutes=120)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)
    
    return {"token": token}

# Exceptions
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception

def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token_exception_response