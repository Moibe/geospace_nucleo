"""
CLI interactivo para hacer preguntas en lenguaje natural sobre los datos.

Usa Vanna.ai con SQLite (local) o MariaDB (producción).

Uso:
    python ask.py                        → Inicia chat interactivo
    python ask.py --refresh              → Reconstruye caché SQLite antes de iniciar
    python ask.py --question "¿Cuántos usuarios hay de MX?"  → Pregunta única
"""
import argparse
import asyncio

from config.settings import ENVIRONMENT, SQLITE_DB_PATH
from data.vanna_engine import create_agent


def ensure_local_cache(force: bool = False):
    """En modo local, asegura que el SQLite exista."""
    if ENVIRONMENT != "production":
        from data.sqlite_cache import build_sqlite_cache
        build_sqlite_cache(force=force)


async def ask_question(agent, question: str) -> str:
    """Envía una pregunta al agente y recopila la respuesta limpia."""
    from vanna.core.user import RequestContext

    request_context = RequestContext(headers={}, cookies={}, query_params={})

    sql_generated = None
    table_data = None
    text_parts = []

    async for component in agent.send_message(request_context, question):
        # Extraer simple_component si existe (más limpio que rich_component)
        simple = getattr(component, 'simple_component', None)
        rich = getattr(component, 'rich_component', None)

        # Capturar el SQL generado desde los metadatos del StatusCard
        if rich and hasattr(rich, 'metadata') and isinstance(rich.metadata, dict):
            if 'sql' in rich.metadata:
                sql_generated = rich.metadata['sql']

        # Capturar datos tabulares del DataFrame component
        if rich and hasattr(rich, 'rows') and rich.rows:
            table_data = rich.rows

        # Capturar texto final (RichTextComponent)
        if rich and hasattr(rich, 'content') and hasattr(rich, 'markdown'):
            text_parts.append(rich.content)

    # Construir salida limpia
    output = []
    if sql_generated:
        output.append(f"  SQL: {sql_generated}")
    if table_data:
        import pandas as pd
        df = pd.DataFrame(table_data)
        output.append(f"\n{df.to_string(index=False)}")
    if text_parts:
        output.append(f"\n  {text_parts[-1]}")

    return "\n".join(output) if output else "(sin respuesta)"


def interactive_loop(agent):
    """Loop interactivo de preguntas y respuestas."""
    print("\n=== Geospace Ask — Pregunta en lenguaje natural ===")
    print(f"Ambiente: {ENVIRONMENT}")
    print("Escribe 'salir' para terminar.\n")

    while True:
        try:
            question = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break

        if not question:
            continue
        if question.lower() in ("salir", "exit", "quit", "q"):
            print("Hasta luego.")
            break

        try:
            response = asyncio.run(ask_question(agent, question))
            print(f"\nRespuesta: {response}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


def main():
    parser = argparse.ArgumentParser(description="Pregunta sobre tus datos con lenguaje natural")
    parser.add_argument("--refresh", action="store_true", help="Reconstruir caché SQLite")
    parser.add_argument("--question", "-q", type=str, help="Pregunta única (sin modo interactivo)")
    args = parser.parse_args()

    # Asegurar datos locales
    ensure_local_cache(force=args.refresh)

    # Crear agente Vanna
    print("Iniciando agente Vanna...")
    agent = create_agent()

    if args.question:
        response = asyncio.run(ask_question(agent, args.question))
        print(response)
    else:
        interactive_loop(agent)


if __name__ == "__main__":
    main()
