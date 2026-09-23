
from typing import TypedDict, Optional
import os
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()
logger = logging.getLogger(__name__)

# 1. Define the State Structure
class AgentState(TypedDict):
    user_query: str
    route_decision: Optional[str]  # Will hold 'SQL' or 'VECTOR'
    retrieved_context: Optional[str] # Will hold the database output or PDF text
    context_grade: Optional[str] # NEW: Will hold 'PASS', 'FAIL_TEXT', or 'FAIL_SQL'
    final_answer: Optional[str]

# Initialize the ultra-fast Llama 3 model via Groq
llm = ChatGroq(
    temperature=0, # Temperature 0 means we want factual, deterministic routing, not creativity
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="openai/gpt-oss-20b"
)

# Define the strict instructions for the Router
router_prompt = PromptTemplate.from_template(
    """You are an advanced enterprise data routing supervisor. Analyze the user's query and decide whether it requires fetching unstructured text policy or structured database data.

    Available Routes:
    1. 'SQL': Use this for any question that needs data from employee or sales tables.
       This includes named employee lookups (department, joining date, remote status),
       employee lists/counts, sales/revenue/amounts, invoices, customers, products,
       regions, dates, and metrics. Examples: "Which department does Asha Sharma
       work in?", "list Engineering employees", "total sales in March", and
       "which salesperson has the highest revenue?".
    2. 'VECTOR': Use this only for unstructured corporate rules, policy allowances,
       guidelines, configurations, or instructions. Examples: "what is the remote
       work policy?", "how many days am I allowed to work remotely?", and
       "how do I change my password?".

    Crucial Edge Case: A policy/rule question remains VECTOR even if it mentions
    employees. A factual question about a named employee or sales record is always SQL.

    Do not output any other text, reasoning, or markdown. Output exactly either 'SQL' or 'VECTOR'.

    User Query: {query}
    Decision:"""
)

def router_node(state: AgentState) -> AgentState:
    """
    Analyzes the user query and updates the state with the routing decision.
    """
    logger.info("Routing query: %s", state["user_query"])
    
    # Create the chain and execute it
    chain = router_prompt | llm
    decision = chain.invoke({"query": state["user_query"]}).content.strip().upper()
    if decision not in {"SQL", "VECTOR"}:
        logger.warning("Unexpected routing decision %r; falling back to VECTOR", decision)
        decision = "VECTOR"
    
    logger.info("Decision: route to %s", decision)
    
    # We return the updated state dictionary
    return {"route_decision": decision}


if __name__ == "__main__":
    # Test 1: A Text/Policy Question
    test_state_1 = {"user_query": "What is the company policy on remote work?"}
    updated_state_1 = router_node(test_state_1)
    
    # Test 2: A Metrics/Database Question
    test_state_2 = {"user_query": "How many employees took vacation time last month?"}
    updated_state_2 = router_node(test_state_2)
