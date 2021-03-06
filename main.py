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
from secret import SPOON_API_KEY
import re

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
    
# @app.get("/api/user", tags=["test"])
# def get_user(db : Session = Depends(get_db)) :
#     try :
#         return db.query(User).all()
#     except Exception as e :
#         return e


def validateEmail(email):
    emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    return re.fullmatch(emailRegex, email)
        

@app.post("/api/user", tags=["Authorization"])
def add_user(newUser : UserSchema, db:Session = Depends(get_db)) :

    if (not validateEmail(newUser.email)) :
        raise HTTPException(status_code=400, detail='Invalid email format')

    if (len(newUser.password) < 8) :
        raise HTTPException(status_code=400, detail='Password length must 8 character')
    
    user = User(
        email = newUser.email,
        name = newUser.name,
        password = get_password_hash(newUser.password)
    )

    try:
        userSearch = db.query(User).filter(User.email == user.email).first()
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

    if userSearch :
        raise HTTPException(status_code=400, detail='Email already exist')

    try :
        db.add(user)
        db.commit()
    except Exception as e :
        # print(e)
        raise HTTPException(status_code=500, detail=e)

    return {
        'status' : 'user created'
    }
    

@app.post('/api/login', tags=['Authorization'])
# async def user_login(user: LoginSchema, db:Session = Depends(get_db)):
async def user_login(user: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):

    try:
        loginData = db.query(User).filter(User.email == user.username).first()
    except Exception as e :
        raise HTTPException(status_code=500, detail=e)

    if not loginData :
        # print('not login data')
        # print(loginData)
        raise HTTPException(status_code=404, detail='User not found')

    if (loginData.email == user.username and verify_password(user.password, loginData.password)) :
        return signJWT(loginData)

    else :
        raise HTTPException(status_code=401, detail='Invalid Credential')


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



@app.put('/api/user/change-password', tags=["Authorization"])
async def change_password(updatedUser:ChangePassword, db:Session=Depends(get_db)) :

    if (not validateEmail(updatedUser.email)):
        raise HTTPException(status_code=400, detail='Invalid email format')

    if (len(updatedUser.password) < 8) :
        raise HTTPException(status_code=400, detail='Password length must 8 character')

    user = User(
        email = updatedUser.email,
        password = updatedUser.password,
    )

    userValidation = db.query(User).filter(User.email == user.email).first()

    if not userValidation :
        # print(userValidation)
        raise HTTPException(status_code=404, detail='User not found')

    if (userValidation.email == user.email and verify_password(user.password, userValidation.password)) :
        # return signJWT(loginData)
        try :
            userValidation.password = get_password_hash(updatedUser.newPassword)
            db.flush()
            db.add(userValidation)
            db.commit()
            db.refresh(userValidation)
            return {"message" : "password changed"}   

        except Exception as e :
            raise HTTPException(status_code=500, detail=e)
                 
    raise HTTPException(status_code=401, detail='Invalid Credential')


@app.post("/api/predict", tags=["Machine Learning"])
async def create_upload_file(file: UploadFile = File(...), token:str = Depends(auth_scheme), db:Session=Depends(get_db)):

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        user = db.query(User).get(payload['email'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

    if not user :
        raise HTTPException(status_code=401, detail='Unauthorized! please register/login first!')

    try:
        contents = await file.read()
        prediction = predictImage(contents)
        url = 'https://api.spoonacular.com/recipes/findByIngredients?ingredients='+str(prediction)+'&number=10&limitLicense=true&ranking=1&ignorePantry=false&apiKey='+str(SPOON_API_KEY)
        response = requests.get(url)
        response = requests.get(url)
        arrayResult = response.json()
        for i in range(len(arrayResult)):
            arrayResult[i].pop('usedIngredientCount')
            arrayResult[i].pop('missedIngredientCount')
            arrayResult[i].pop('missedIngredients')
            arrayResult[i].pop('usedIngredients')
            arrayResult[i].pop('unusedIngredients')
            arrayResult[i].pop('likes')
            arrayResult[i].update({'summary' : str('Recipe for ' + str(arrayResult[i]['title']))})
        return arrayResult

    except Exception as e:
        raise HTTPException(status_code=500, detail=e)