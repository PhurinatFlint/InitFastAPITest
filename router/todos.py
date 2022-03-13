from pyexpat import model
import sys
sys.path.append("..") # This will allow to properly be able to import everything that is in the parent directory of auth.

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, Request, Form # Depends = Dependencies

from starlette.responses import RedirectResponse
from starlette import status


from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from pydantic import BaseModel, Field
from .auth import get_current_user

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

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session=Depends(get_db)):

    user = await get_current_user(request=request) 
    if user is None: # If the user is none. Redirect to auth page
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    # Query database
    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()

    return templates.TemplateResponse("home.html", {"request": request, "todos":todos, "user":user}) # Pass in all of the todo by using context.

@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request=request) 
    if user is None: # If the user is none. Redirect to auth page
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("add-todo.html", {"request": request, "user":user})

@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request: Request, title: str=Form(...), description: str=Form(...), priority: int=Form(...), db: Session=Depends(get_db)):
    
    user = await get_current_user(request=request) 
    if user is None: # If the user is none. Redirect to auth page
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND) # when submit complete, it will redirect to the page that submit.

@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session=Depends(get_db)):

    user = await get_current_user(request=request) 
    if user is None: # If the user is none. Redirect to auth page
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user":user})

@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def update_todo(request: Request, 
                        todo_id: int, 
                        title:str=Form(...),
                        description:str=Form(...),
                        priority:int=Form(...),
                        db: Session=Depends(get_db)):
    
    user = await get_current_user(request=request) 
    if user is None: # If the user is none. Redirect to auth page
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority

    db.add(todo_model)
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/delete/{todo_id}", response_class=HTMLResponse) # DELETE USE GET ON HTML 
async def delete_todo(request: Request, todo_id:int, db: Session=Depends(get_db)):
    
    user = await get_current_user(request=request) 
    if user is None: # If the user is none. Redirect to auth page
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)    
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id)\
                            .filter(models.Todos.owner_id == user.get("id"))\
                            .first()

    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id:int, db: Session=Depends(get_db)):

    user = await get_current_user(request=request) 
    if user is None: # If the user is none. Redirect to auth page
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    todo.complete = not todo.complete # Complete is an boolean, Switch the false to true or tru to false

    db.add(todo)
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)