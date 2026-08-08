from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


def _route_from_state(final_state: dict) -> str | None:
    """Return the route even when LangGraph omits a consumed routing channel."""
    route = final_state.get("route_decision")
    if route:
        return route

    context = final_state.get("retrieved_context", "")
    if context.startswith("SQL Query Executed:"):
        return "SQL"
    if context.startswith("Web Search Fallback Results:"):
        return "WEB_SEARCH"
    if context.startswith("Retrieved Context:") or context.startswith("Vector Retrieval Error:"):
        return "VECTOR"
    return None


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, _: dict = Depends(get_current_user)) -> ChatResponse:
    try:
        # Keep the existing LangGraph invocation contract intact.
        from src.main_loop import app as langgraph_app

        final_state = langgraph_app.invoke({"user_query": request.query})
        return ChatResponse(
            answer=final_state.get("final_answer", "No response generated."),
            route=_route_from_state(final_state),
            grade=final_state.get("context_grade"),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to process chat request") from exc
