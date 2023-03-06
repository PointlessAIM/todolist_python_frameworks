from fastapi import FastAPI, Depends, Request, Form, status

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine

templates = Jinja2Templates(directory="templates")

app = FastAPI()

#this code is to create the database
models.Base.metadata.create_all(bind=engine)
#Depends
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()
    return templates.TemplateResponse("base.html", {"request": request, "todo_list": todos} )

@app.get("/items/{item_id}")
async def read_item(item_id:int):
    return {"item_id":item_id}

@app.post("/add", status_code=status.HTTP_303_SEE_OTHER)
async def add(request: Request, title:str = Form(...), db:Session=Depends(get_db)):
    new_todo=models.Todo(title=title)
    db.add(new_todo)
    db.commit()

    url= app.url_path_for("home")
    return RedirectResponse(url=url)

@app.get("/update/{todo_id}", status_code=status.HTTP_302_FOUND)
def update(request: Request, todo_id:int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.complete = not todo.complete
    db.commit()

    url= app.url_path_for("home")
    return RedirectResponse(url=url)

@app.get("/delete/{todo_id}", status_code=status.HTTP_302_FOUND)
async def delete(request: Request, todo_id:int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()

    url= app.url_path_for("home")
    return RedirectResponse(url=url)

