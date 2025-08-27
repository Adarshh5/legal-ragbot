

import os

from dotenv import load_dotenv
from typing import  Literal

from langchain_core.messages import  AIMessage


from langgraph.graph import END, StateGraph, START

import logging
from .agent_tools import tools
from .agent_node import agent, relevency_check, transform_query, web_search, websearch_relevency_check, retrieve_node, agent1, agent2, agent3, add_ai_message

from .state import LegalAgentState, AgentOutput
load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")



def route_condition(state: LegalAgentState) -> Literal["tools", END]:
    
    output: AgentOutput = state.get("agent_output")

    if not output:
        raise ValueError("Missing agent_output in state")

    if output.route == "direct_answer":
        state["messages"].append(AIMessage(content=output.answer))
       
        return END
    elif output.route == "retrieve":

        return "retrieve"
    elif output.route == "web_search":
        return "web_search"
    else:
        logging.warning(f"Unknown route: {output.route}")
        return END

  



workflow = StateGraph(LegalAgentState)

workflow.add_node("agent", agent)
workflow.add_node("add_ai_message", add_ai_message)
workflow.add_node("agent1", agent1, )
workflow.add_node("agent2", agent2)
workflow.add_node("agent3", agent3)
workflow.add_node("retrieve",  retrieve_node)
workflow.add_node('relevency_check', relevency_check)
workflow.add_node('transform_query', transform_query)
workflow.add_node('web_search', web_search)
workflow.add_node('websearch_relevency_check', websearch_relevency_check)


workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    route_condition,
    {
        # Translate the condition outputs to nodes in our graph
        "retrieve": "retrieve",
        "web_search":"web_search",
        END: "add_ai_message",
    },
)

workflow.add_edge(
    "retrieve","relevency_check"
    
)
workflow.add_edge(
    "web_search","websearch_relevency_check"
    
)


workflow.add_conditional_edges(
    "relevency_check",
    lambda state: state.get("__route__"),
    {
        "relevant": "agent1",
        "not relevant": "transform_query",
        "web_search": "web_search"
    }
)
workflow.add_edge('transform_query', 'retrieve')
workflow.add_conditional_edges('websearch_relevency_check',
        lambda state: state.get("__route__"),
    {
        "relevant": "agent2",
        "not relevant": "agent3",
    } )

workflow.add_edge("agent1", END)
workflow.add_edge("agent2", END)
workflow.add_edge("agent3", END)
workflow.add_edge("add_ai_message", END)
# Final compilation
legal_agent = workflow.compile()