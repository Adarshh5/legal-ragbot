
from typing import List, Optional, Sequence, Annotated, Literal
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from pydantic import model_validator, BaseModel




class AgentOutput(BaseModel):
    route: Literal["retrieve", "web_search", "direct_answer"]
    answer: Optional[str] = None

    @model_validator(mode="after")
    def validate_answer(cls, values):
        route = values.route
        answer = values.answer
        if route == "direct_answer" and not answer:
            raise ValueError("Answer must be provided when route is 'direct_answer'")
        return values
    
    
class LegalAgentState(TypedDict, total=False):
    documents: Optional[List[Document]]
    web_documents: Optional[str]
    attempt_count: int=  0
    reformed_question: Optional[str]
    messages: Annotated[Sequence[BaseMessage], add_messages]
    agent_output:Optional[AgentOutput]
    relevant_document: str
    relevant_web_document:str
