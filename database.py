from typing import List
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./student_enrollment.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models
class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    courses = relationship("Course", secondary="enrollments", back_populates="students")

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    students = relationship("Student", secondary="enrollments", back_populates="courses")

Base.metadata.create_all(bind=engine)

# Pydantic models
class CourseBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str

class CourseCreate(BaseModel):
    name: str

class CourseEnroll(BaseModel):
    course_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class StudentResponse(BaseModel):
    id: int
    username: str
    courses: List[CourseBase]

    class Config:
        orm_mode = True
