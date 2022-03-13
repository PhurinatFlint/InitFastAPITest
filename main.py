from fastapi import FastAPI, Depends
import models
from database import engine
from router import auth, todos
from starlette.staticfiles import StaticFiles
from starlette import status
from starlette.responses import RedirectResponse

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Mounting technique to mount static to application, Adding a completely indepentdent application to a specific path tha then takes care of handling everythin under the path
app.mount("/static", StaticFiles(directory="static"), name="static")

# Get
@app.get("/")
async def root():
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(todos.router)



