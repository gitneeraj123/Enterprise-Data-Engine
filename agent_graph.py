
from typing import TypedDict, Optional
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()

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
    model_name="llama-3.1-8b-instant" 
)

# Define the strict instructions for the Router
router_prompt = PromptTemplate.from_template(
    """You are an advanced enterprise data routing supervisor. Analyze the user's query and decide whether it requires fetching unstructured text policy or structured database data.

    Available Routes:
    1. 'SQL': Use this ONLY if the user is asking for live transactional records, counting actual employees/sales, or calculating historical metrics from database tables (e.g., "how many people did X", "total sales for yesterday", "list of users").
    2. 'VECTOR': Use this if the user is asking about corporate rules, policy allowances, guidelines, configurations, or instructions (e.g., "how many days am I ALLOWED to do X", "what is the policy on X", "how do I change my password").

    Crucial Edge Case: If a question asks "how many days/hours am I allowed" or "what is the limit for", that is a POLICY question (VECTOR), not a database query.

    Do not output any other text, reasoning, or markdown. Output exactly either 'SQL' or 'VECTOR'.

    User Query: {query}
    Decision:"""
)

def router_node(state: AgentState) -> AgentState:
    """
    Analyzes the user query and updates the state with the routing decision.
    """
    print(f"--- Routing Query: '{state['user_query']}' ---")
    
    # Create the chain and execute it
    chain = router_prompt | llm
    decision = chain.invoke({"query": state["user_query"]}).content.strip().upper()
    
    print(f"--- Decision: Route to {decision} ---")
    
    # We return the updated state dictionary
    return {"route_decision": decision}


if __name__ == "__main__":
    # Test 1: A Text/Policy Question
    test_state_1 = {"user_query": "What is the company policy on remote work?"}
    updated_state_1 = router_node(test_state_1)
    
    # Test 2: A Metrics/Database Question
    test_state_2 = {"user_query": "How many employees took vacation time last month?"}
    updated_state_2 = router_node(test_state_2)