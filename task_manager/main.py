from fastapi import FastAPI, Depends, HTTPException, status, Form,APIRouter
from sqlalchemy.orm import Session
from task_manager.db import database, schemas
from task_manager.utilitis import models, auth
from task_manager.utilitis.auth import get_current_user

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()


@app.post("/auth/register")
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = auth.hash_password(password)
    new_user = models.User(username=username, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}


@app.post("/auth/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

router = APIRouter(prefix="/users", tags=["Users"])
@app.get("/me")
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username
    }

@app.delete("/me")
def delete_current_user(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted successfully. Please log out."}

@app.post("/tasks")
def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db), current_user=Depends(auth.get_current_user)):
    new_task = models.Task(title=task.title, description=task.description, owner=current_user.username)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/tasks")
def get_tasks(db: Session = Depends(database.get_db), current_user=Depends(auth.get_current_user)):
    return db.query(models.Task).filter(models.Task.owner == current_user.username).all()

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, updated_task: schemas.TaskUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = updated_task.title
    task.description = updated_task.description
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}