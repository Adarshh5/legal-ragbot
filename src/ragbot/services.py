from src.ragbot.lang_utils  import to_langchain_messages

from .agent_core_logic.core_logic import legal_agent

from .schemas import ChatHistory, UserMessage
from src.db.redis import append_chat_message, get_full_chat_history, get_recent_chat_messages

from datetime import datetime, date

from sqlmodel.ext.asyncio.session import AsyncSession
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.ragbot.models import UserTotalTime, UserDailyMessageUsage
from sqlalchemy import select, and_
from fastapi import HTTPException
from datetime import datetime, timezone

now = datetime.now(timezone.utc)


class ChatService:

    async def call_llm(self,message:UserMessage,  user_id:str, session:AsyncSession):

          
            user_time = await session.get(UserTotalTime, user_id)

            if not user_time:
                  raise HTTPException(status_code=404, detail="user time info not found")
   
            now = datetime.now(timezone.utc)
            days_used = (now - user_time.start_date).days

            if days_used > 10:
                  raise HTTPException(status_code=403, detail="❌ Free trial expired after 10 days.")
            
            
           
            today = date.today()
            usage = await session.scalar(
            select(UserDailyMessageUsage).where(
                and_(
                    UserDailyMessageUsage.user_id == user_id,
                    UserDailyMessageUsage.usage_date == today
                )
            )
        )

       
          
            if not usage:
                  usage = UserDailyMessageUsage(user_id=user_id, usage_date=today,message_count=0)
                  session.add(usage)
                  await session.commit()
                  await session.refresh(usage)
            

            
            if usage.message_count >= 20:
                   raise HTTPException(status_code=403, detail="🚫 Daily message limit (20) reached.")

                  


            previous_messages = await get_recent_chat_messages(user_id,limit=2)
            langchain_history = to_langchain_messages(previous_messages)
           
            initial_messages = [
                *langchain_history,
                HumanMessage(content=message)
            ]
       

            response = await legal_agent.ainvoke({
                        "messages": initial_messages,
                        "attempt_count": 0,
                    }, config={"recursion_limit": 15})

            print("🧠 Final graph response:", response['messages'])
     


            ai_reply = response['messages'][-1] or "I don't have an answer at the moment."
          
            

            await append_chat_message(user_id, {"type": "human", "message": message})
            await append_chat_message(user_id, {"type": "ai", "message": ai_reply.content})
            

            usage.message_count += 1
            session.add(usage)
            await session.commit()

            update_history = await get_full_chat_history(user_id)
            
            return update_history
    


   