from fastapi.security import HTTPBearer

from fastapi import Request, status, Depends

from fastapi.security.http import HTTPAuthorizationCredentials

from .utils import decode_token

import redis
from fastapi.exceptions import HTTPException

from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserService
from typing import List, Any
from src.auth.models import User
from src.db.redis import  token_in_blocklist

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials
        token_data = decode_token(token)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                "message": "Token is invalid Or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },

            )
        
        try:
            if await token_in_blocklist(token_data['jti']):
                raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            }, 

            )
            
        except redis.exceptions.ConnectionError:
            # Optional: log this
            print("⚠️ Redis is not available. Skipping token blocklist check.")


        

        self.verifiy_token_data(token_data)
        return token_data
    
   
           
    def verifiy_token_data(self, token_data:dict) -> bool:
        raise NotImplementedError("Please Override this method is child classes")
    

class AccessTokenBearer(TokenBearer):

    def verifiy_token_data(self, token_data:dict) -> None:
        if token_data and token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            }, 

            )


class RefreshTokenBearer(TokenBearer):
     def verifiy_token_data(self, token_data:dict) -> None:
        if token_data and not token_data['refresh']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                "error_code": "refresh_token_required",
            },
            )
        

async def get_current_user(token_details: dict = Depends(AccessTokenBearer()),
                     session:AsyncSession =  Depends(get_session)
                     ):
    user_email = token_details['user']['email']

    user = await user_service.get_user_by_email(user_email, session)

    return user



class RoleChecker:
    def __init__(self, allowed_roles:List[str]) -> None:

        self.allowed_roles = allowed_roles


    def __call__(self, current_user: User =  Depends(get_current_user)) -> Any:

        if not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                  "message":"Account not verifield",
                  "error_code":"account_not_verified",
                  "resolution":"please check your email for verification details"
              }
                

            )

        if current_user.role in self.allowed_roles:
            return True
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },

        )