from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app import crud
from app.core.exceptions import ErrorEnum, ErrorModel
from app.models.schemas.user import UserOut, UserUpdate
from app.models.tables import User
from app.core.db import AsyncSessionDep
from app.models.response import RespModel
from jose import jwt, JWTError
from app.core.config import settings

# OAuth2PasswordBearer 用于从请求头获取 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/login_by_phone")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSessionDep,
) -> User:
    """
    从 token 中获取当前用户
    
    Args:
        token: JWT token
        session: 数据库会话
    
    Returns:
        User: 用户对象
        
    Raises:
        HTTPException: token无效或过期时抛出
    """
    credentials_exception = Exception(ErrorModel(
        message="请登录后使用",
        error_type=ErrorEnum.login
    ))
    
    try:
        # 解码 token
        print(f'解码 token: {token}')
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户
    user = await crud.get_user_by_id(user_id, session)
    if user is None:
        raise credentials_exception
        
    return user
# 创建一个依赖项，用于在需要认证的路由中获取当前用户
CurrentUser = Annotated[User, Depends(get_current_user)]


###===========================================
### 用户 router
###===========================================
router = APIRouter()

@router.get("/me")
async def get_current_user_info(
    current_user: CurrentUser
) -> RespModel[User]:
    """获取当前登录用户信息"""
    data = UserOut.model_validate(current_user)
    data.fuck = "fuck me"
    return RespModel(
        code=200,
        message="获取成功",
        data=data
    )

@router.get("/all")
async def get_all_user_info(session: AsyncSessionDep) -> RespModel[list[User]]:
    data = await crud.get_first_100_users(session)
    
    return RespModel(
        code=200,
        message="获取用户信息成功",
        data=data,
    )
 

@router.post("/update")
async def update_user_info(
    user_update: UserUpdate,
    current_user: CurrentUser,
    session: AsyncSessionDep
) -> RespModel[User]:
    is_updated = False
    
    # 更新用户名 - 只有当新值不为空且与当前值不同时才更新
    if not user_update.username  and user_update.username != current_user.username:
        user_by_username = await crud.get_user_by_username(user_update.username, session)
        if user_by_username and user_by_username.id != current_user.id:
            raise Exception(ErrorModel(
                message="用户名已存在",
            ))
        current_user.username = user_update.username
        is_updated = True
    
    # 更新手机号 - 只有当新值不为空且与当前值不同时才更新
    if not user_update.phone and user_update.phone != current_user.phone:
        current_user.phone = user_update.phone
        is_updated = True
    
    # 只有在有更新时才更新时间戳和保存
    if is_updated:
        current_user.updated_at = datetime.now()
        user = await crud.update_user(current_user, session)
    else:
        user = current_user

    return RespModel( 
        code=200,
        message="更新用户信息成功",
        data= user,
        attach={
            "user_update": user_update,
            "isNoneOrEmpty": not ""
        }
    )
