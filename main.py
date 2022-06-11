from logging import raiseExceptions
from fastapi import FastAPI, HTTPException, UploadFile, File
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
import asyncio
import requests
from predict import predictImage

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

auth_scheme = OAuth2PasswordBearer(tokenUrl='api/login')

# async def check_user(data: UserSchema, db : Session = Depends(get_db)):
#     loginData = db.query(User).filter(User.email == data.email).first()
#     return (loginData.email == data.email and verify_password(loginData.password) == data.password)
    
@app.get("/api/user", tags=["test"])
def get_user(db : Session = Depends(get_db)) :
    try :
        return db.query(User).all()
    except Exception as e :
        return e


@app.post("/api/user", tags=["Authorization"])
def add_user(newUser : UserSchema, db:Session = Depends(get_db)) :
    try :
        user = User(
            email = newUser.email,
            name = newUser.name,
            password = get_password_hash(newUser.password)
        )
        userSearch = db.query(User).filter(User.email == user.email).first()
        if userSearch :
            raise HTTPException(status_code=400, detail='Email already exist')
        db.add(user)
        db.commit()

        return {
            'status' : 'user created'
        }
    except Exception as e :
        print(e)
        raise HTTPException(status_code=500, detail=e)

@app.post('/api/login', tags=['Authorization'])
# async def user_login(user: LoginSchema, db:Session = Depends(get_db)):
async def user_login(user: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    try:
        loginData = db.query(User).filter(User.email == user.username).first()
        if not loginData :
            print('not login data')
            print(loginData)
            raise HTTPException(status_code=401, detail='Invalid Credential')
        if (loginData.email == user.username and verify_password(user.password, loginData.password)) :
            return signJWT(loginData)
        else :
            raise HTTPException(status_code=401, detail='Invalid Credential')
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Invalid Credential")

async def get_current_user(db: Session = Depends(get_db), token:str = Depends(auth_scheme)) :
    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        user = db.query(User).get(payload['email'])
    except Exception as e:
        raise HTTPException(status_code=401, detail="invalid credentials")

    return UserSchema.from_orm(user)


@app.get('/api/me', dependencies=[Depends(auth_scheme)], tags=['Me'])
async def user_login(user:UserSchema = Depends(get_current_user)):
    return {"email" : user.email, "name" :user.name}

@app.post('/api/test', tags=['test'])
async def test(user:UserSchema) :
    return user

@app.put('/api/user/change-password', tags=["Authorization"])
async def change_password(updatedUser:ChangePassword, db:Session=Depends(get_db)) :
    try :
        user = User(
            email = updatedUser.email,
            password = updatedUser.password,
        )
        userValidaiton = db.query(User).filter(User.email == user.email).first()
        if not userValidaiton :
            print(userValidaiton)
            raise HTTPException(status_code=401, detail='Invalid Credential')
        if (userValidaiton.email == user.email and verify_password(user.password, userValidaiton.password)) :
            # return signJWT(loginData)
            userValidaiton.password = get_password_hash(updatedUser.newPassword)
            db.flush()
            db.add(userValidaiton)
            db.commit()
            db.refresh(userValidaiton)
            return {"message" : "password changed"}            
        raise HTTPException(status_code=401, detail='Invalid Credential')
        
    except Exception as e :
        raise HTTPException(status_code=400, detail='Invalid email and current password')

@app.post("/api/predict", tags=["Machine Learning"])
async def create_upload_file(file: UploadFile = File(...)):

    contents = await file.read()  # <-- Important!
    prediction = predictImage(contents)

    # example of how you can save the file
    # with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        # f.write(contents)
    prediction = predictImage(contents)
    url = 'https://api.spoonacular.com/recipes/findByIngredients?ingredients='+str(prediction)+'&number=10&limitLicense=true&instructionsRequired=true&fillIngredients=false&ranking=1&ignorePantry=false&apiKey=3ff72eac98e545da878857652b999020'
    response = requests.get(url)
    return response.json()