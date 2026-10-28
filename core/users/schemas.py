from datetime import datetime

from pydantic import BaseModel , Field, field_validator

class UserLoginSchema(BaseModel):
    username:str = Field(..., max_length=150 , min_length=5 , description="Username of the user" )
    password:str = Field(... , description="password of the user" )

class UserRegisterSchema(BaseModel):
    username:str = Field(..., max_length=150 , min_length=5 , description="Username of the user" )
    password:str = Field(... , description="password of the user" )
    password_confirm:str = Field(... , description="confirm password of the user" )


    @field_validator("password")
    def check_password_match(cls , password_confirm , validation):
        if not (password_confirm == validation.data.get("password")):
            raise ValueError("passwords does not match")
        return password_confirm