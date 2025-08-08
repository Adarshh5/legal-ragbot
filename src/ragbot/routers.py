from fastapi import APIRouter, Depends, status
from .schemas import UserMessage, ChatHistory, DeleteRequest
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException

from fastapi.responses import JSONResponse
from datetime import datetime,timedelta
from src.config import Config
from src.auth.dependencies import AccessTokenBearer, get_current_user, RoleChecker
from .agent_core_logic.core_logic import legal_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from .services import ChatService
import logging
from src.db.redis import delete_chat_history

chat_service = ChatService()
chat_router = APIRouter()
role_checker = Depends(RoleChecker(['admin', 'user']))

access_token_brearer = AccessTokenBearer()


@chat_router.post("/chat", status_code=status.HTTP_202_ACCEPTED, response_model=ChatHistory, dependencies=[role_checker])
async def chat_message(user_message: UserMessage, session: AsyncSession = Depends(get_session),
                       token_details: dict = Depends(access_token_brearer)):
   
    try:
        user_id = token_details.get('user')['user_uid']
        message = user_message.human
        updated_history = await chat_service.call_llm(message, user_id, session)

        if updated_history:
            return {"history": updated_history}
        return {"history": [], "error": "No update found"}

    except Exception as e:
        logging.exception("Chat route error")
        raise HTTPException(status_code=500, detail=str(e))






@chat_router.delete("/chat", status_code=status.HTTP_200_OK, dependencies=[role_checker])
async def delete_chat_endpoint(session: AsyncSession = Depends(get_session),
                       token_details: dict = Depends(access_token_brearer)):
    user_id = token_details.get('user')['user_uid']
    success = await delete_chat_history(user_id)
    if success:
        return {"message": f"Chat history for user {user_id} deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="No chat history found for this user.")