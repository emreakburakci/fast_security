from contextlib import asynccontextmanager
from fastapi import Body, FastAPI, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.security import  OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Annotated, List
from fastapi.middleware.cors import CORSMiddleware


from database import Admin, Course, CourseBase, CourseCreate, CourseEnroll, Enrollment, Student, StudentResponse, Token, UserCreate, get_db
from security import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context, oauth2_scheme
from security import authenticate_user, get_password_hash, create_access_token
from nlp import *
from filetype import FileType

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_nltk()
    yield

app = FastAPI(lifespan=lifespan)

# CORS settings
origins = [
    "http://localhost:3000",
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user_type
    }


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



@app.post("/student/courses", response_model=List[str], )
async def get_student_courses(username: str = Body(...), db: Session = Depends(get_db),current_user: tuple = Depends(get_current_user)):
    student = current_user[0]
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student.id).all()
    courses = [db.query(Course).filter(Course.id == enrollment.course_id).first().name for enrollment in enrollments]
    
    return courses








@app.post("/add_admin_dev")
async def add_admin(user: UserCreate, db: Session = Depends(get_db)):
    db_user = Admin(username=user.username, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Admin added successfully"}





@app.delete("/delete_admin_dev")
async def add_admin(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(Admin).filter(Admin.username == user.username).first()
    db.delete(db_user)
    db.commit()
    return {"message": "Admin deleted successfully"}



@app.post("/files/")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }



@app.post("/test/")
async def create_file(
    
    test:str = Body(...),
):
    return {
        "content": test,
    }




@app.post("/analyze_file/")
async def create_file(
    file: Annotated[UploadFile, File()],
    file_type: Annotated[FileType, Form()], current_user: tuple = Depends(get_current_user)
):
    content = await file.read()
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    text = extract_text_from_file(file_path, file_type)
    return {"text": text}

@app.post("/word_frequency/")
async def get_word_frequency(
    file: Annotated[UploadFile, File()],
    file_type: Annotated[FileType, Form()], current_user: tuple = Depends(get_current_user)
):
    content = await file.read()
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    text = extract_text_from_file(file_path, file_type)
    return word_frequency(text)

@app.post("/pos_tags/")
async def get_pos_tags(
    file: Annotated[UploadFile, File()],
    file_type: Annotated[FileType, Form()], current_user: tuple = Depends(get_current_user)
):
    content = await file.read()
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    text = extract_text_from_file(file_path, file_type)
    return pos_tags(text)

@app.post("/named_entities/")
async def get_named_entities(
    file: Annotated[UploadFile, File()],
    file_type: Annotated[FileType, Form()], current_user: tuple = Depends(get_current_user)
):
    content = await file.read()
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    text = extract_text_from_file(file_path, file_type)
    return named_entities(text)

@app.post("/sentiment_analysis/")
async def get_sentiment_analysis(
    file: Annotated[UploadFile, File()],
    file_type: Annotated[FileType, Form()], current_user: tuple = Depends(get_current_user)
):
    content = await file.read()
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    text = extract_text_from_file(file_path, file_type)
    return sentiment_analysis(text)

@app.post("/ngrams/")
async def get_ngrams(
    file: Annotated[UploadFile, File()],
    file_type: Annotated[FileType, Form()],
    n: Annotated[int, Form()] = 2, current_user: tuple = Depends(get_current_user)
):
    content = await file.read()
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    text = extract_text_from_file(file_path, file_type)
    return ngrams(text, n)

@app.post("/concordance/")
async def get_concordance(
    file: Annotated[UploadFile, File()],
    file_type: Annotated[FileType, Form()],
    word: Annotated[str, Form()], current_user: tuple = Depends(get_current_user)
):
    content = await file.read()
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(content)
    
    text = extract_text_from_file(file_path, file_type)
    return concordance(text, word)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)