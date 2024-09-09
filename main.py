from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import  OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import List

from database import Admin, Course, CourseBase, CourseCreate, CourseEnroll, Student, StudentResponse, Token, UserCreate, get_db
from security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context, oauth2_scheme



app = FastAPI()

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    student = db.query(Student).filter(Student.username == username).first()
    if student and verify_password(password, student.hashed_password):
        return student, "student"
    admin = db.query(Admin).filter(Admin.username == username).first()
    if admin and verify_password(password, admin.hashed_password):
        return admin, "admin"
    return None, None

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_type: str = payload.get("type")
        if username is None or user_type is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    if user_type == "student":
        user = db.query(Student).filter(Student.username == username).first()
    elif user_type == "admin":
        user = db.query(Admin).filter(Admin.username == username).first()
    else:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    return user, user_type

async def get_current_admin(current_user: tuple = Depends(get_current_user)):
    user, user_type = current_user
    if user_type != "admin":
        raise HTTPException(status_code=400, detail="Not an admin user")
    return user

# API endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user, user_type = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "type": user_type}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/add_student")
async def add_student(user: UserCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    db_user = Student(username=user.username, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Student added successfully"}

@app.post("/add_admin")
async def add_admin(user: UserCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    db_user = Admin(username=user.username, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Admin added successfully"}

@app.get("/get_courses", response_model=List[CourseBase])
async def get_courses(db: Session = Depends(get_db), current_user: tuple = Depends(get_current_user)):
    courses = db.query(Course).all()
    return courses

@app.get("/get_students", response_model=List[StudentResponse])
async def get_students(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    students = db.query(Student).all()
    return students

@app.post("/add_course")
async def add_course(course: CourseCreate, db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    db_course = Course(name=course.name)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return {"message": "Course added successfully"}

@app.post("/enroll_course")
async def enroll_course(enrollment: CourseEnroll, db: Session = Depends(get_db), current_user: tuple = Depends(get_current_user)):
    user, user_type = current_user
    if user_type != "student":
        raise HTTPException(status_code=400, detail="Only students can enroll in courses")
    
    course = db.query(Course).filter(Course.id == enrollment.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    user.courses.append(course)
    db.commit()
    return {"message": "Enrolled in course successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)