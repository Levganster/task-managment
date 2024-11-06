from pydantic import BaseModel
from typing import Optional
from fastapi import Form

class UserBase(BaseModel):
    username: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str

    @classmethod
    def as_form(cls, username: str = Form(...), password: str = Form(...)):
        return cls(username=username, password=password)

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