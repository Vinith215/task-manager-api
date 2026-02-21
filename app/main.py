from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .database import get_db, engine
from .models import Base, Task
from .cache import get_cached_task, set_cached_task, delete_cached_task

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API")

# ---------- Pydantic Schemas ----------
class TaskCreate(BaseModel):
    title: str
    status: Optional[str] = "pending"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Routes ----------
@app.get("/")
def root():
    return {"message": "Task Manager API is running"}

@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(title=task.title, status=task.status)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks", response_model=list[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    # Check cache first
    cached = get_cached_task(task_id)
    if cached:
        print(f"Cache HIT for task {task_id}")
        return cached

    # Fall back to database
    print(f"Cache MISS for task {task_id} — querying DB")
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Store in cache for next time
    task_data = {"id": task.id, "title": task.title,
                 "status": task.status, "created_at": task.created_at.isoformat()}
    set_cached_task(task_id, task_data)
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_update.title:
        task.title = task_update.title
    if task_update.status:
        task.status = task_update.status

    db.commit()
    db.refresh(task)
    delete_cached_task(task_id)  # Invalidate stale cache
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    delete_cached_task(task_id)
    return {"message": f"Task {task_id} deleted"}