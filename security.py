from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
from database import Student, Admin

# Security
SECRET_KEY = "6d17953ac67c9106beb0bec7931e4ca78ba2d0241c4a8b688528e85a88087927"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")





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
