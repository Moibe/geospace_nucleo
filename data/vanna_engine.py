"""
Motor de Vanna.ai: configura el agente según el ambiente (local/producción).

Local:      SQLite  (datos descargados de la API)
Producción: MariaDB (conexión directa)
"""
import os
from datetime import datetime
from typing import List, Optional

from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.core.system_prompt.base import SystemPromptBuilder
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool,
    SaveTextMemoryTool,
)
from vanna.integrations.local.agent_memory import DemoAgentMemory

from config.settings import ENVIRONMENT, SQLITE_DB_PATH, OPENAI_API_KEY

# Leer el DDL del schema
_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schema.sql")
with open(_SCHEMA_PATH, encoding="utf-8") as f:
    _DDL = f.read()


class GeospaceSystemPrompt(SystemPromptBuilder):
    """System prompt que incluye el schema de la base de datos."""

    async def build_system_prompt(self, user: User, tools: List) -> Optional[str]:
        today = datetime.now().strftime("%Y-%m-%d")
        return (
            "Eres un asistente de análisis de datos para Geospace, un sitio que registra "
            "interacciones geoespaciales. Respondes en español.\n\n"
            f"La fecha de hoy es: {today}\n\n"
            "La base de datos tiene una sola tabla. Aquí está su esquema:\n\n"
            f"```sql\n{_DDL}\n```\n\n"
            "Notas importantes:\n"
            "- La tabla se llama 'map_interactions'\n"
            "- 'type' puede ser: organic_visit, ad_visit, map_interaction, map_wait, phone_search, purchase, buy_click, sell_pop\n"
            "- 'ga_client_id' identifica un mismo navegador/usuario\n"
            "- Hay campos UTM (utm_source, utm_medium, utm_campaign, utm_term, utm_content) que pueden ser NULL\n"
            "- 'gclid' indica tráfico de Google Ads, 'fbclid' de Facebook Ads\n"
            "- Los timestamps están en formato 'YYYY-MM-DD HH:MM:SS' (UTC, CDMX y zona del usuario)\n"
            "- Cuando el usuario diga 'marzo' sin especificar año, usa el año actual\n"
            "- Usa SQL compatible con SQLite en ambiente local y MariaDB en producción\n"
        )


class SimpleUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        return User(id="admin", email="admin@geospace.local", group_memberships=["admin"])


def _build_db_tool() -> RunSqlTool:
    """Crea el RunSqlTool según el ambiente."""

    if ENVIRONMENT == "production":
        from vanna.integrations.mysql import MysqlRunner
        from config.settings import MARIADB_HOST, MARIADB_PORT, MARIADB_USER, MARIADB_PASSWORD, MARIADB_DATABASE

        sql_runner = MysqlRunner(
            host=MARIADB_HOST,
            port=int(MARIADB_PORT),
            user=MARIADB_USER,
            password=MARIADB_PASSWORD,
            database=MARIADB_DATABASE,
        )
    else:
        from vanna.integrations.sqlite import SqliteRunner

        sql_runner = SqliteRunner(database_path=SQLITE_DB_PATH)

    return RunSqlTool(sql_runner=sql_runner)


def create_agent() -> Agent:
    """Crea y devuelve el agente Vanna configurado."""
    from vanna.integrations.openai import OpenAILlmService

    llm = OpenAILlmService(
        model="gpt-4o-mini",
        api_key=OPENAI_API_KEY,
    )

    db_tool = _build_db_tool()
    agent_memory = DemoAgentMemory(max_items=1000)

    tools = ToolRegistry()
    tools.register_local_tool(db_tool, access_groups=["admin", "user"])
    tools.register_local_tool(VisualizeDataTool(), access_groups=["admin", "user"])
    tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=["admin"])
    tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=["admin", "user"])
    tools.register_local_tool(SaveTextMemoryTool(), access_groups=["admin", "user"])

    agent = Agent(
        llm_service=llm,
        tool_registry=tools,
        user_resolver=SimpleUserResolver(),
        agent_memory=agent_memory,
        system_prompt_builder=GeospaceSystemPrompt(),
    )

    return agent
