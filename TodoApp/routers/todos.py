from sqlalchemy.orm import Session
from fastapi import APIRouter,Depends,Path,HTTPException,Query
from ..database import SessionLocal
from pydantic import BaseModel,Field
from starlette import status
from .auth import get_current_user
from ..models import Task
from datetime import datetime
from typing import Literal,Optional,Annotated
from pydantic import BaseModel, Field


router = APIRouter()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

class TaskRequest(BaseModel):
    title: str = Field(min_length=3)
    description: Optional[str] = Field(default=None, max_length=100)
    status: Literal["todo", "in_progress", "done"] = "todo"
    priority: Literal["low", "medium", "high"] = "medium"
    due_date: Optional[datetime] = None

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3)
    description: Optional[str] = Field(default=None, max_length=100)
    status: Optional[Literal["todo", "in_progress", "done"]] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    due_date: Optional[datetime] = None

@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency,db: db_dependency,task_status: Optional[Literal["todo", "in_progress", "done"]] = Query(default=None),
    priority: Optional[Literal["low", "medium", "high"]] = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort_by: Literal["due_date", "created_at"] = Query(default="created_at"),
):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication Failed"
        )
    query = db.query(Task).filter(Task.owner_id == user.get("id"))
    if task_status:
        query = query.filter(Task.status == task_status)
    if priority:
        query = query.filter(Task.priority == priority)
    if sort_by == "due_date":
        query = query.order_by(Task.due_date)
    else:
        query = query.order_by(Task.created_at)
    tasks = query.offset(offset).limit(limit).all()
    return tasks

@router.get("/task/{task_id}", status_code=status.HTTP_200_OK)
async def read_task(user:user_dependency,db:db_dependency,task_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    task_model=db.query(Task).filter(Task.id == task_id).filter(Task.owner_id==user.get('id')).first()
    if task_model is not None:
        return task_model
    raise HTTPException(status_code=404,detail='Task not found')

@router.post("/task",status_code=status.HTTP_201_CREATED)
async def create_task(user:user_dependency,db:db_dependency,task_request:TaskRequest):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    task_model = Task(**task_request.dict(),owner_id=user.get('id'))
    db.add(task_model)
    db.commit()
    db.refresh(task_model)
    return task_model

@router.put("/task/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_task(user:user_dependency,db:db_dependency,task_request:TaskRequest,task_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    task_model=db.query(Task).filter(Task.id==task_id).first()
    if task_model is None:
        raise HTTPException(status_code=404,detail='task not found')
    task_model.title = task_request.title
    task_model.status = task_request.status
    task_model.priority = task_request.priority
    task_model.due_date = task_request.due_date
    db.add(task_model)
    db.commit()

@router.delete("/task/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(user:user_dependency,db:db_dependency,task_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail='Authentication Failed')
    task_model=db.query(Task).filter(Task.id==task_id).filter(Task.owner_id==user.get('id')).first()
    if task_model is None:
        raise HTTPException(status_code=404,detail='task not found')
    db.query(Task).filter(Task.id==task_id).filter(Task.owner_id == user.get('id')).delete()
    db.commit()

@router.patch("/task/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_task_partial(user: user_dependency,db: db_dependency,task_request: TaskUpdateRequest,task_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication Failed")
    task_model = db.query(Task).filter(Task.id == task_id,Task.owner_id == user.get("id")).first()
    if task_model is None:
        raise HTTPException(status_code=404,detail="Task not found")
    update_data = task_request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task_model, field, value)
    db.commit()


