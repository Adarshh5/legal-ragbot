from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Union, Dict

def to_langchain_messages(history: List[Dict]) -> List[Union[HumanMessage, AIMessage]]:
    lc_messages = []
    for item in history:
        if item["type"] == "human":
            lc_messages.append(HumanMessage(content=item["message"]))
        elif item["type"] == "ai":
            lc_messages.append(AIMessage(content=item["message"]))
    return lc_messages