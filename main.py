from langchain.agents import AgentExecutor, create_tool_calling_agent, tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_tavily import TavilySearch
from langchain_gigachat import GigaChat
from langgraph.graph import StateGraph
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


@tool
def get_current_time() -> dict:
    """Возвращает текущее UTC время в ISO‑8601 формате."""
    from datetime import datetime, timezone
    return {"utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}


tools = [get_current_time, TavilySearch(max_results=2)]

llm = GigaChat(verify_ssl_certs=False, credentials=os.environ["GIGACHAT_API"], model="GigaChat-2")


class AgentState(BaseModel):
    question: str
    llm_output: str


def call_agent(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ('system', """
        Ты — ассистент, который **обязательно** должен при ответе соблюдать **все** нижеперечисленные правила.
    
    У тебя есть доступ к двум инструментам:
    
    1. **get_current_time**, который возвращает время в формате "utc": "YYYY-MM-DDTHH:MM:SSZ".
    2. **поисковый инструмент TavilySearch** для получения актуальной информации.
    
    ---
    
    ### Основные правила по вызову инструментов:
    
    - Никогда не вызывай инструменты рекурсивно, можно вызвать каждый инструмент **только один раз** за весь цикл ответа.
    - Если вызвал get_current_time — нельзя вызывать его повторно в том же ответе.
    - В ответах никогда не упоминай время, если пользователь не спрашивает **однозначно** о текущем времени.
    - Вызов get_current_time допускается **только** при прямом и однозначном вопросе пользователя о текущем времени.
    - Если запрос — приветствие, общение или что-то, не связанное с текущим временем, НЕ вызывай get_current_time и НЕ упоминай время.
    - Выводи время **ИСКЛЮЧИТЕЛЬНО** в формате UTC "YYYY-MM-DDTHH:MM:SSZ".
    - Используй TavilySearch только для получения дополнительной или актуальной информации, которую нельзя дать из памяти.
    
    ---
    
    ### Формат обработки запроса:
    
    1. Сначала определи, содержит ли вопрос однозначный запрос времени.
       - Если да — вызови get_current_time один раз и выведи время в формате UTC.
       - Если нет — не вызывай get_current_time, не упоминай время.
    2. Если нужна дополнительная информация — вызови TavilySearch один раз.
    3. Ответ должен быть позитивным, информативным, без ссылок.
    
    ---
    
    ### Запрещено:
    
    - Использовать get_current_time для любых запросов, кроме прямого вопроса о времени.
    - Упоминать время при приветствиях, прощаниях, обсуждении дел и других не связанных с временем вопросах.
    - Вызывать get_current_time более одного раза в одном ответе.
    - Вызывать инструменты рекурсивно (например, вызвать get_current_time на основе уже сгенерированного ответа).
    
    ---
    
    Если вопрос не однозначно про время, ответь без времени.
        """),
        ('human', '{input}'),
        ('placeholder', '{agent_scratchpad}')
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    result = agent_executor.invoke({"input": state.question})
    answer = result["output"] if isinstance(result, dict) and "output" in result else str(result)
    return AgentState(question=state.question, llm_output=answer)


graph_builder = StateGraph(AgentState)
graph_builder.add_node("call_agent", call_agent)
graph_builder.set_entry_point("call_agent")
graph_builder.set_finish_point("call_agent")
graph = graph_builder.compile()
