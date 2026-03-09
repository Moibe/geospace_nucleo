"""
Endpoint /api/ask — recibe una pregunta en lenguaje natural y devuelve
SQL, datos y resumen generado por Vanna.ai.
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter()


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000, description="Pregunta en lenguaje natural")


class AskResponse(BaseModel):
    question: str
    sql: str | None = None
    data: list[dict] | None = None
    summary: str | None = None


@router.post("/ask", response_model=AskResponse)
async def ask_question(body: AskRequest, request: Request):
    """Pregunta en lenguaje natural sobre los datos de Geospace."""
    from vanna.core.user import RequestContext

    agent = request.app.state.vanna_agent

    request_context = RequestContext(headers={}, cookies={}, query_params={})

    sql_generated = None
    table_data = None
    text_parts = []

    try:
        async for component in agent.send_message(request_context, body.question):
            rich = getattr(component, 'rich_component', None)

            # Capturar SQL desde los metadatos del StatusCard
            if rich and hasattr(rich, 'metadata') and isinstance(rich.metadata, dict):
                if 'sql' in rich.metadata:
                    sql_generated = rich.metadata['sql']

            # Capturar datos tabulares del DataFrame component
            if rich and hasattr(rich, 'rows') and rich.rows:
                table_data = rich.rows

            # Capturar texto final (RichTextComponent)
            if rich and hasattr(rich, 'content') and hasattr(rich, 'markdown'):
                text_parts.append(rich.content)
    except Exception as exc:
        return AskResponse(
            question=body.question,
            summary=f"Error procesando la pregunta: {exc}",
        )

    return AskResponse(
        question=body.question,
        sql=sql_generated,
        data=table_data,
        summary=text_parts[-1] if text_parts else None,
    )
