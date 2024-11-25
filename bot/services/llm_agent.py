from bot.utils.load_promt_model import load_promt_model
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from bot.utils.tools import get_tools
from typing import Dict, List

from pydantic import BaseModel, Field
from langgraph.graph import MessagesState

# Определение структуры ответа
class SkincareResponse(BaseModel):
    """Ответ пользователю с советами по уходу за кожей или информацией о продуктах."""

    ingredients: List[str] = Field(
        default_factory=list,
        description="Список ингредиентов, считанных или предоставленных вручную."
    )
    ingredient_descriptions: dict = Field(
        default_factory=dict,
        description="Описание каждого ингредиента."
    )
    recommendation: str = Field(
        default="",
        description="Рекомендация по продукту для ухода за кожей в зависимости от типа кожи."
    )
    skin_type: str = Field(
        default="",
        description="Определенный тип кожи пользователя."
    )


class AgentState(MessagesState):
    final_response: SkincareResponse


# Определение функции генерации ответа
def generate_response(input_text: str) -> str:
    llm_pipeline = load_promt_model()
    response = llm_pipeline(input_text, max_new_tokens=150, return_full_text=False)
    return response[0]['generated_text']


class SkincareAgent:
    def __init__(self, tools, response_model, state_model):
        self.tools = tools
        self.response_model = response_model
        self.state_model = state_model

    def bind_tools(self, tools):
        self.tools = tools
        return self

    def with_structured_output(self, response_type):
        self.response_model = response_type
        return self

    def invoke(self, messages):
        user_message = messages[-1].content
        response_text = generate_response(user_message)
        return response_text


distilgpt2_agent = SkincareAgent(tools=get_tools(), response_model=SkincareResponse, state_model=AgentState)
model_with_tools = distilgpt2_agent.bind_tools(get_tools())
model_with_structured_output = distilgpt2_agent.with_structured_output(SkincareResponse)


# Определяем функцию для вызова модели с инструментами
def call_model(state: AgentState) -> Dict:
    """
    Функция для вызова модели с инструментами.
    В данном случае модель использует инструменты, связанные с изображениями и текстом.
    """
    # Вызов модели с инструментами для обработки сообщений, добавляя запрос на краткий ответ в сообщении
    last_user_message = state["messages"][-1].content + " (Дайте короткий и содержательный ответ.)"
    response = model_with_tools.invoke([HumanMessage(content=last_user_message)])
    return {"messages": [response]}

def respond(state: AgentState) -> Dict:
    """
    Создание окончательного ответа для пользователя с использованием модели и структурного вывода.
    """
    # Добавляем запрос на краткий ответ в сообщение пользователя
    last_user_message = state["messages"][-2].content + " (Дайте короткий и содержательный ответ.)"
    response = model_with_structured_output.invoke([HumanMessage(content=last_user_message)])
    return {"final_response": response}

# Логика проверки, нужно ли продолжать работу или отправить ответ
def should_continue(state: AgentState) -> str:
    """
    Определяет, следует ли продолжать выполнение агента или отправить ответ пользователю.
    Проверяет, есть ли вызовы инструментов в последнем сообщении.
    """
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    else:
        return "respond"

# Создаем граф состояний
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("respond", respond)
workflow.add_node("tools", ToolNode(get_tools()))

# Устанавливаем начальный узел
workflow.set_entry_point("agent")

# Добавляем условные переходы
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "respond": "respond",
    },
)
workflow.add_edge("tools", "agent")
workflow.add_edge("respond", END)

# Компилируем граф для запуска
graph = workflow.compile()

# пример запроса
user_input = input("Введите ваш запрос: ")
response = graph.invoke({"messages": [HumanMessage(content=user_input)]})["final_response"]
print(response)