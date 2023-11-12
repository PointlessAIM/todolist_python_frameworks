from fastapi import FastAPI, Depends, Request, Form, status, HTTPException

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine


#this code is to create the database
models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

#Depends
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()
    return templates.TemplateResponse("base.html", {"request": request, "todo_list": todos} )

@app.get("/items/{item_id}")
async def read_item(item_id:int, db: Session = Depends(get_db)):# -> dict[str, Any]:
    return {"item_id":item_id, "item": db.query(models.Todo).filter(models.Todo.id==item_id).first()}

@app.post("/add")
async def add(request: Request, title:str = Form(...), db:Session=Depends(get_db)):
    #checking if todo exists
    existing_todo = db.query(models.Todo).filter(models.Todo.title == title).first()
    if existing_todo:
        return {"message": "Item with the same title already exists."}
    
    new_todo=models.Todo(title=title)
    try:
        db.add(new_todo)
        db.commit()
        db.close()
    except:
        raise HTTPException(status_code=500,detail={"Error": "An error ocurred"})

    url= app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/update/{todo_id}", status_code=status.HTTP_302_FOUND)
def update(request: Request, todo_id:int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.complete = not todo.complete # type: ignore
    db.commit()
    db.close()

    url= app.url_path_for("home")
    return RedirectResponse(url=url)

@app.get("/delete/{todo_id}", status_code=status.HTTP_302_FOUND)
async def delete(request: Request, todo_id:int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    try:
        db.delete(todo)
        db.commit()
        db.close()
    except:
        raise HTTPException(status_code=500,detail={"Error": "An error ocurred"})
    
    url= app.url_path_for("home")
    return RedirectResponse(url=url)

@app.get("/delete-all", status_code=status.HTTP_302_FOUND)
async def deleteAll(request: Request, db: Session = Depends(get_db)):
    try:
        db.query(models.Todo).delete()
        db.commit()
        db.close()
    except:
        raise HTTPException(status_code=500,detail={"Error": "An error ocurred"})
    
    url= app.url_path_for("home")
    return RedirectResponse(url=url)