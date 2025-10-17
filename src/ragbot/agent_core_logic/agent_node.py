from langchain_groq import ChatGroq
from .agent_tools import tools


from pydantic import BaseModel, Field, validator, model_validator
from typing import Literal, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ddgs import DDGS

from langchain_core.messages import BaseMessage, ToolMessage, AIMessage, SystemMessage
from .state import LegalAgentState, AgentOutput
from .agent_tools import retrieve_legal_documents, duckduckgo_search_tool
import logging
from langchain_openai import ChatOpenAI
from .prompts import  route_system_message


async def agent(state: LegalAgentState):
    messages = [SystemMessage(content=route_system_message)] + state['messages']
    # model = ChatGroq(model="llama3-70b-8192").with_structured_output(AgentOutput)
    model = ChatOpenAI(model="gpt-4.1-mini").with_structured_output(AgentOutput)
    
    try:
        response = await model.ainvoke(messages)
        logging.debug("Agent output: %s", response)
        return {
            "messages": state["messages"],
            "agent_output": response  # ✅ Correctly set
        }
        

    except Exception as e:
        logging.error("fail in generating the answer: %s", e)
        return {
            "messages": state["messages"],
            "agent_output": None  # Still needed for graceful fallback
        }


def add_ai_message(state: LegalAgentState) -> LegalAgentState:
    output: AgentOutput = state.get("agent_output")
    if output:
        state["messages"].append(AIMessage(content=output.answer))
    return state



class RelevanceCheck(BaseModel):
    relevance: Literal["relevant", "not relevant"] = Field(...)

llm = ChatGroq(model="llama3-70b-8192")

async def retrieve_node(state: LegalAgentState) -> dict:
    # print("---Retrivernode---")

    logging.debug("Running retrieve_node")
    documents = []
   
    query = ""
    result = {'messages': state['messages'],  "attempt_count": state["attempt_count"],"reformed_question": query}
    if not state.get("reformed_question"):
        logging.debug("Using AI-generated tool_call query")
        documents = await retrieve_legal_documents.ainvoke(state["messages"][-1].content)
        result["documents"] = documents
    # CASE 2: We have a reformed question — use it directly for vector retrieval
    else:
        logging.debug("Using reformed question")
        query = state.get("reformed_question")
        documents = await retrieve_legal_documents.ainvoke(query)
        result["documents"] = documents
  
    return result
  



structured_model = llm.with_structured_output(RelevanceCheck)
async def document_checker(query, document):
    input_text = f"""
    Given the following user query and document, decide whether the document is relevant to the query.

    Only return "relevant" or "not relevant" under the 'relevance' key.

    User Query:
    {query}

    Document:
    {document}
    """
    result = await structured_model.ainvoke(input_text)
    return result.relevance  # will be exactly "relevant" or "not relevant"

async def relevency_check(state:LegalAgentState):
    # print("---RELEVENCY CHECK---")

    logging.debug("relevency check called")

    docs = state.get("documents", [])
    
    query = state.get("reformed_question") or state["messages"][-1].content
    state["reformed_question"] = query
    if state['attempt_count'] >= 1:
            return {
            "__route__": "web_search",
            "attempt_count": state["attempt_count"],
            "messages": state["messages"],
            "reformed_question": query
        }
    state["attempt_count"] = state.get("attempt_count", 0) + 1
    # print( state["attempt_count"])
    for doc in docs:
        check = await document_checker(query, doc.page_content)
        if check == "relevant":
            state['relevant_document'] = doc.page_content
            print("this is a relevent document:-  ", state['relevant_document'])
            return {
                "__route__": "relevant",
                "messages": state["messages"],
                "attempt_count": state.get("attempt_count", 0),  # include current count
                 "reformed_question": query,
                "relevant_document": doc.page_content,

            }

    


    
    
    
    return {
        "__route__": "not relevant",
        "attempt_count": state["attempt_count"],
        "messages": state["messages"],
        "reformed_question": query
    }


# Prompt
system = """You a question re-writer that converts an input question to a better version in english language that is optimized \n 
     for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
re_write_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        (
            "human",
            "Here is the initial question: \n\n {question} \n Formulate an improved question.",
        ),
    ]
)

question_rewriter = re_write_prompt | llm | StrOutputParser()


async def transform_query(state:LegalAgentState):
 
    logging.debug("trasform_query called")
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    # print("---TRANSFORM QUERY---")

    attempt_count = state.get("attempt_count", 0)

    if state.get("attempt_count", 0) > 1:
        logging.warning("Already attempted reform, skipping further transforms.")
        return {
            "__route__": "web_search",
            "attempt_count": state["attempt_count"],
            "messages": state["messages"],
            "reformed_question": state["reformed_question"]
        }

    question = state['messages'][-1].content

    # Re-write question
    better_question = await question_rewriter.ainvoke({"question": question})
    # print("this is transform query :-   ", better_question)
    state['reformed_question'] = better_question
    return {
        "reformed_question": better_question,
        "attempt_count": state["attempt_count"],
        "messages": state["messages"]
    }


async def websearch_relevency_check(state: LegalAgentState):
    # print("---websearch relevency check---")
    logging.debug("web search relevency check called")

    docs = state.get('web_documents', '')
  
    query = state['messages'][-1].content if hasattr(state['messages'][-1], "content") else str(state['messages'][-1])

    if not docs:
        return {
             "__route__": "not relevant",
            'messages': state['messages'],
            'web_documents': '',
            'attempt_count': state.get("attempt_count", 0),
        }
   
    check = await document_checker(query, docs if isinstance(docs, str) else docs.page_content)

    result = {
        'messages': state['messages'],
        'web_documents': docs,
        'attempt_count': state.get("attempt_count", 0),
    }
    if check == "relevant":
        # print("relevant_web_document :-   ", docs)
        result["__route__"]= ["relevant"]
        result['relevant_web_document'] = docs
    else: result["__route__"]= ["not relevant"]

    return result 


async def web_search(state:LegalAgentState):
 
    logging.debug("web search ")
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    # print("---WEB SEARCH---")
   
    query =  state.get("reformed_question") or state['messages'][-1].content
   
    with DDGS() as ddgs:
        results = ddgs.text(query, region='wt-wt', safesearch='Off', max_results=3)
        if not results:
            return {'messages': state['messages'],'web_documents': "",  "attempt_count": state["attempt_count"] }
        
        # You can also return the full list if needed
        response = ""
        for r in results:
            response += f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n\n"
        
        state['web_documents'] = response
        # print("this is web document: -   ", response)


    return {'messages': state['messages'],'web_documents': response,  "attempt_count": state["attempt_count"] }





def final_answer_generator(documents):
    
    system_message  = f"""**Role**: AI Legal Assistant for Indian Law  
    **Response Language**: Match user's language   

    use this document to answer the last question of the user ->

    {documents}

    **Critical Rules**:  
    1. Strictly legal queries only:  
    - Non-legal: "I cannot give legal advice" / "I only handle legal topics"  

    2. Always add: "Consult an advocate for personal cases"  """

    return system_message

async def agent1(state:LegalAgentState):
    # print("----retiever relevand documents founded")
    documents=  state['relevant_document']
    system_message = final_answer_generator(documents)
    chat =   [SystemMessage(system_message)] + state['messages']

    result = await llm.ainvoke(chat)
    ans = AIMessage(content = result.content)
    updated_message = state['messages'] = state['messages'].append(ans)

    return {"message":updated_message}





async def agent2(state:LegalAgentState):
    print("---web_documents was founded---")
    documents=  state.get('relevant_web_document', "")
    system_message = final_answer_generator(documents)
    chat =   [SystemMessage(content = system_message)] + state['messages']
    result = await llm.ainvoke(chat)
    ans = AIMessage(content = result.content)
    updated_message = state['messages'] = state['messages'].append(ans)

    return {"message":updated_message}




def final_answer_generator_without_document():
    
    system_message  = f"""**Role**: AI Legal Assistant for Indian Law  
    **Response Language**: Match user's language   

    **Critical Rules**:  
    1. Strictly legal queries only:  
    - Non-legal: "I cannot give legal advice" / "I only handle legal topics"  

    2. Always add: "Consult an advocate for personal cases"  """

    return system_message

async def agent3(state:LegalAgentState):
    print("---no documents was founded----")
    sys = final_answer_generator_without_document()
    chat = [SystemMessage(content= sys)] + state['messages']
    result = await llm.ainvoke(chat)
  
    ans = AIMessage(content=result.content)
    updated_message = state['messages'] = state['messages'].append(ans)

    return {"message":updated_message}