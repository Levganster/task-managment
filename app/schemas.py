from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    owner: UserBase
    completed: bool

    class Config:
        orm_mode = True

class TokenData(BaseModel):
    username: Optional[str] = None