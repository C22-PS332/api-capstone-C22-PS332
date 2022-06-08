from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from schemas import *
from models import *
from database import get_db
from sqlalchemy.orm import Session
from hash import get_password_hash, verify_password
from auth import JWT_ALGORITHM, JWT_SECRET, signJWT
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

auth_scheme = OAuth2PasswordBearer(tokenUrl='api/login')

async def check_user(data: UserSchema, db : Session = Depends(get_db)):
    loginData = db.query(User).filter(User.username == data.username).first()
    return (loginData.username == data.username and verify_password(loginData.password) == data.password)
    
@app.get("/api/user")
def get_user(db : Session = Depends(get_db)) :
    try :
        return db.query(User).all()
    except Exception as e :
        return e


@app.post("/api/user")
def add_user(newUser : UserSchema, db:Session = Depends(get_db)) :
    try :
        user = User(
            username = newUser.username,
            password = get_password_hash(newUser.password)
        )
        db.add(user)
        db.commit()

        return {
            'status' : 'user created'
        }
    except Exception as e :
        print(e)
        return e

@app.post('/api/login', tags=['Authorization'])
async def user_login(user: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):

    loginData = db.query(User).filter(User.username == user.username).first()
    if not loginData :
        print('not login data')
        print(loginData)
        raise HTTPException(status_code=401, detail='Invalid Credential')
    if (loginData.username == user.username and verify_password(user.password, loginData.password)) :
        return signJWT(loginData)
    else :
        print('else')
        print(user.username, user.password)
        print(loginData.username, loginData.password)
        raise HTTPException(status_code=401, detail='Invalid Credential')

async def get_current_user(db: Session = Depends(get_db), token:str = Depends(auth_scheme)) :
    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        user = db.query(User).get(payload['username'])
    except Exception as e:
        raise HTTPException(status_code=401, detail="invalid credentials")

    return UserSchema.from_orm(user)


@app.get('/api/me', dependencies=[Depends(auth_scheme)], tags=['Me'])
async def user_login(user:UserSchema = Depends(get_current_user)):
    return {"username" : user.username}

@app.post('/api/test')
async def test(user:UserSchema) :
    return user