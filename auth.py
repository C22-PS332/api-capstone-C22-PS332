import jwt

from models import User
from schemas import UserSchema

JWT_SECRET = b'7d02b0a882dac395c44e1fc000bc5340a2d055b30be580cd'
JWT_ALGORITHM = 'HS256'

def token_response(token: str):
    return {
        "access_token" : token
    }

def signJWT(user: User) :
    user_obj = UserSchema.from_orm(user)

    token = jwt.encode(user_obj.dict(), JWT_SECRET, JWT_ALGORITHM)

    # return dict(acces_token=token, token_type = 'bearer')
    return token_response(token)

def decodeJWT(token: str) :
    try :
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except :
        return {'message' : 'Failed to decode token'}


