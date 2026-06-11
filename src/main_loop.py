from langgraph.graph import StateGraph, END
from agent_graph import AgentState, router_node, llm
from langchain_core.prompts import PromptTemplate
from sql_tool import execute_sql
from vector_tool import retrieve_documents
from langchain_tavily import TavilySearch
sql_generation_prompt = PromptTemplate.from_template(
    """You are an expert SQL engineer. Convert the user's question into a valid PostgreSQL query.
    Database Schema:
    - Table: employees (id, name, department, is_remote: BOOLEAN, join_date)
    Rules: Only return raw SQL. No markdown. No explanations.
    User Question: {question}
    SQL Query:"""
)

def sql_action_node(state: AgentState) -> AgentState:
    print("\n[Executing Live Text-to-SQL Agent]")
    chain = sql_generation_prompt | llm
    generated_sql = chain.invoke({"question": state["user_query"]}).content.strip()
    print(f"-> Generated SQL: {generated_sql}")
    
    # Execute the query
    result = execute_sql(generated_sql)
    
    # THE FIX: Combine the SQL query and the result so the Responder understands the data
    rich_context = f"SQL Query Executed: {generated_sql}\nDatabase Result:\n{result}"
    
    return {"retrieved_context": rich_context}

def vector_action_node(state: AgentState) -> AgentState:
    print("\n[Executing Vector Agent]")
    result = retrieve_documents(state["user_query"])
    return {"retrieved_context": result}

# 2. NEW: Prompt and Node for drafting the natural language answer
response_generation_prompt = PromptTemplate.from_template(
    """You are a helpful enterprise assistant. Answer the user's question accurately using ONLY the provided retrieved context. 

    Retrieved Context:
    {context}

    User Question: {question}
    Answer:"""
)

def responder_node(state: AgentState) -> AgentState:
    print("\n[Executing Final Responder Agent]")
    chain = response_generation_prompt | llm
    final_answer = chain.invoke({
        "question": state["user_query"],
        "context": state["retrieved_context"]
    }).content.strip()
    return {"final_answer": final_answer}



# 1. The Evaluator Prompt
evaluator_prompt = PromptTemplate.from_template(
    """You are a strict grading evaluator. Check if the provided Context contains relevant information to answer the User Question.
    If the context is relevant and helpful, output exactly 'PASS'.
    If the context is irrelevant, unhelpful, or empty, output exactly 'FAIL'.
    Do not output anything else.

    User Question: {question}
    Context: {context}
    Grade:"""
)

# 2. The Evaluator Node
def evaluator_node(state: AgentState) -> AgentState:
    print("\n[Executing Evaluator Guardrail]")
    context = state.get("retrieved_context", "")
    
    # Check A: Did the SQL Agent fail?
    if state["route_decision"] == "SQL":
        if "SQL Execution Error" in context:
            print("-> SQL Syntax Error Detected. Forcing loop back to SQL Agent.")
            return {"context_grade": "FAIL_SQL"}
        else:
            print("-> SQL Data Valid.")
            return {"context_grade": "PASS"}
            
    # Check B: Did the Vector Agent pull bad text?
    chain = evaluator_prompt | llm
    grade = chain.invoke({
        "question": state["user_query"],
        "context": context
    }).content.strip().upper()
    
    print(f"-> Vector Context Grade: {grade}")
    return {"context_grade": "FAIL_TEXT" if "FAIL" in grade else "PASS"}

# 3. The Web Search Fallback Node
def web_search_node(state: AgentState) -> AgentState:
    print("\n[Executing Web Search Fallback]")
    try:
        # Initialize TavilySearch
        search = TavilySearch(max_results=2)
        results = search.invoke(state["user_query"])
        print(f"Web search results: {results}")  # Debugging the structure of results

        # Access the 'results' key in the dictionary
        search_results = results.get('results', [])
        
        # Format the web results into a single string
        formatted_results = "\n".join([f"- {r['content']}" for r in search_results])
        return {"retrieved_context": f"Web Search Fallback Results:\n{formatted_results}"}
    except Exception as e:
        print(f"Error during web search: {e}")
        return {"retrieved_context": "Web search failed."}


# 4. The Evaluation Routing Logic
def evaluation_routing(state: AgentState) -> str:
    """Reads the grade and tells LangGraph where to go next."""
    grade = state.get("context_grade")
    if grade == "FAIL_SQL":
        return "sql_agent"     # Loop back and try writing SQL again
    elif grade == "FAIL_TEXT":
        return "web_search"    # Route to the internet
    else:
        return "responder"     # Context is good, write the final answer



# 3. Define the Conditional Edge Logic
def route_decision(state: AgentState) -> str:
    if state["route_decision"] == "SQL":
        return "sql_path"
    else:
        return "vector_path"

# 4. Build the Compiled Flowchart Graph
print("Compiling Agent Graph...")
workflow = StateGraph(AgentState)

# Add ALL nodes to the graph
workflow.add_node("router", router_node)
workflow.add_node("sql_agent", sql_action_node)
workflow.add_node("vector_agent", vector_action_node)
workflow.add_node("evaluator", evaluator_node)  # NEW
workflow.add_node("web_search", web_search_node) # NEW
workflow.add_node("responder", responder_node)

workflow.set_entry_point("router")

# 1. Initial Routing (SQL vs Vector)
workflow.add_conditional_edges(
    "router",
    route_decision,
    {"sql_path": "sql_agent", "vector_path": "vector_agent"}
)

# 2. Force both tools to go to the Evaluator instead of the Responder
workflow.add_edge("sql_agent", "evaluator")
workflow.add_edge("vector_agent", "evaluator")

# 3. The CRAG Loop: Conditional routing based on the Evaluator's grade
workflow.add_conditional_edges(
    "evaluator",
    evaluation_routing,
    {
        "sql_agent": "sql_agent",   # The Loop Back
        "web_search": "web_search", # The Web Fallback
        "responder": "responder"    # The Success Path
    }
)

# 4. Web search goes to the Responder
workflow.add_edge("web_search", "responder")
workflow.add_edge("responder", END)

app = workflow.compile()

if __name__ == "__main__":
    print("\n=== SYSTEM TEST: CRAG Web Fallback ===")
    # This policy doesn't exist in our DB!
    test_crag = {"user_query": "Why Can’t You Add Data with a Non-Matching Foreign Key?"}
    final_state = app.invoke(test_crag)
    print(f"👉 FINAL AI RESPONSE: {final_state['final_answer']}")
