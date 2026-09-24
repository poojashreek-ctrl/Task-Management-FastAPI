from sqlalchemy import create_engine,text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
from ..routers.todos import get_db,get_current_user
from fastapi.testclient import TestClient
from fastapi import status
import pytest
from ..models import Task
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine=create_engine(
    SQLALCHEMY_DATABASE_URL,
)

TestingSessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db=TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username':'poojashree','id':1,'user_role':'admin'}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client=TestClient(app)

@pytest.fixture
def test_todo():
    db = TestingSessionLocal()
    db.query(Task).filter(Task.owner_id == 1).delete()
    db.commit()
    todo = Task(
        title="Learn to code!",
        description="everyday",
        status="todo",
        priority="medium",
        due_date=datetime(2026, 9, 30, 10, 0),
        owner_id=1
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    yield todo
    db.delete(todo)
    db.commit()
    db.close()

def test_read_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    task = data[0]
    assert task["title"] == "Learn to code!"
    assert task["description"] == "everyday"
    assert task["status"] == "todo"
    assert task["priority"] == "medium"
    assert task["owner_id"] == 1

def test_read_one_authenticated(test_todo):
    response = client.get(f"/task/{test_todo.id}")
    assert response.status_code == status.HTTP_200_OK
    task = response.json()
    assert task["title"] == "Learn to code!"
    assert task["description"] == "everyday"
    assert task["status"] == "todo"
    assert task["priority"] == "medium"
    assert task["owner_id"] == 1

def test_create_todo(test_todo):
    request_data={
        'title':'New Todo!',
        'description':'New todos',
        'status':'todo',
        'priority':'medium',
    }
    response=client.post('/task/',json=request_data)
    assert response.status_code == 201
    db = TestingSessionLocal()
    model=db.query(Task).filter(Task.id==response.json()["id"]).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.status == request_data.get('status')
    assert model.priority == request_data.get('priority')

def test_update_todo(test_todo):
    request_data={
        'title':'change the title',
        'description':'New todos',
        'status':'todo',
        'priority':'medium',
    }
    response=client.put(f'/task/{test_todo.id}',json=request_data)
    assert response.status_code==204
    db=TestingSessionLocal()
    model=db.query(Task).filter(Task.id == test_todo.id).first()
    assert model.title == 'change the title'

def test_delete_todo(test_todo):
    response=client.delete(f'/task/{test_todo.id}')
    assert response.status_code==204
    db=TestingSessionLocal()
    model=db.query(Task).filter(Task.id==test_todo.id).first()
    assert model is None


@pytest.fixture
def another_user_todo():
    db = TestingSessionLocal()
    todo = Task(
        title="Another user's task",
        description="This belongs to user 2",
        status="todo",
        priority="medium",
        due_date=datetime(2026, 9, 30, 10, 0),
        owner_id=2
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    yield todo
    db.delete(todo)
    db.commit()
    db.close()

def test_user_cannot_access_another_users_task(another_user_todo):
    response = client.get(
        f"/task/{another_user_todo.id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


    
