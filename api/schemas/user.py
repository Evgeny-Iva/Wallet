from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Схема запроса регистрации пользователя"""
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Схема запроса авторизации пользователя"""
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    """Схема ответа регистрации пользователя"""
    message: str
    user_id: int


class LoginResponse(BaseModel):
    """Схема ответа авторизации пользователя"""
    access_token: str
    token_type: str


class LogoutResponse(BaseModel):
    """Схема ответа сброса сессии"""
    message: str