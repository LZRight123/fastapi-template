from datetime import UTC, datetime, timedelta
from jose import jwt
from app.core.config import settings
from app.models.schemas.token import Token

def create_access_token(user_id: str) -> Token:
    """
    创建 JWT access token
    
    Args:
        user_id: 需要编码到token中的数据
    
    Returns:
        str: JWT token字符串
    """
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return Token(
        access_token=encoded_jwt,
        expires=expire
    )
