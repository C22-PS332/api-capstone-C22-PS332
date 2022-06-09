from pydantic import BaseModel

class UserSchema(BaseModel) :
    email: str
    password: str
    name: str

    class Config:
        orm_mode = True

class ChangePassword(BaseModel) :
    email: str
    password: str
    newPassword: str

    class Config:
        orm_mode = True
class LoginSchema(BaseModel):
    email: str
    password: str
    class Config:
        orm_mode = True