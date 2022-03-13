import sys
sys.path.append("..") # This will allow to properly be able to import everything that is in the parent directory of auth.

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, Request # Depends = Dependencies
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from pydantic import BaseModel, Field
from .auth import get_current_user, get_user_exception

# Front end library
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

#app = FastAPI()
router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={401: {"description":"Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

class Todo(BaseModel): # POST request : We need to create all the variables within the class todo that we want to receive as a post requests
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6)
    complete: bool

@router.get("/test")
async def test(request: Request):
    return templates.TemplateResponse("register.html", {"request": request}) # Context, must return the request to the file which been rendered

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def http_success(status_code:int):
    return {
        'status_code':status_code,
        'transaction': 'Successful'
    }

def http_exception():
    return HTTPException(status_code=404, detail="To do not found")

@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()

@router.get("/user")
async def read_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()

@router.get("/{todo_id}")
async def read_todo(todo_id: int, user:dict = Depends(get_current_user),db: Session = Depends(get_db)):
    
    if user is None:
        raise get_user_exception()
    
    todo_model = db.query(models.Todos)\
                    .filter(models.Todos.id == todo_id)\
                    .filter(models.Todos.owner_id == user.get("id"))\
                    .first() # Todo id of the path parameter need to match the record

    if todo_model is not None:
        return todo_model
    return http_exception()

@router.post("/")
async def create_todo(todo: Todo, 
                        user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    
    if user is None:
        raise get_user_exception()
    
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("id")
    # add, The state will be persisted for the next operation. 
    db.add(todo_model)
    # Commit the changes
    db.commit()
    
    return http_success(200)

@router.put("/{todo_id}")
async def update_todo(todo_id:int, todo:Todo, user: dict= Depends(get_current_user), db: Session = Depends(get_db)):
    
    if user is None:
        raise get_user_exception()
    
    todo_model = db.query(models.Todos)\
                    .filter(models.Todos.id == todo_id)\
                    .filter(models.Todos.owner_id == user.get("id"))\
                    .first()

    if todo_model is None:
        raise http_exception()
    
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return http_success(200)

@router.delete("/{todo_id}")
async def delete_todo(todo_id:int, 
                        user:dict= Depends(get_current_user), 
                        db:Session= Depends(get_db)):
    
    if user is None:
        raise get_user_exception()
    
    
    todo_model = db.query(models.Todos)\
                    .filter(models.Todos.id == todo_id)\
                    .filter(models.Todos.owner_id == user.get("id"))\
                    .first()

    if todo_model is None:
        return http_exception()
    
    db.query(models.Todos)\
        .filter(models.Todos.id == todo_id)\
        .filter(models.Todos.owner_id == user.get("id"))\
        .delete()
    db.commit()

    return http_success(201)
