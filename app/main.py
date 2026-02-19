import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from langchain_community.chat_message_histories import RedisChatMessageHistory

APP_NAME = "langchain-redis-ecs-canary"

REDIS_URL = os.getenv("REDIS_URL")  # ex: redis://host:6379/0 (ou rediss:// se TLS)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
ENV = os.getenv("ENVIRONMENT", "blue")  # só pra você enxergar qual taskset respondeu

if not REDIS_URL:
    raise RuntimeError("REDIS_URL is required")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is required")

app = FastAPI(title=APP_NAME)

class ChatIn(BaseModel):
    session_id: str
    message: str

@tool
def get_env() -> str:
    """Returns which environment/version is serving the request (blue/green)."""
    return ENV

def build_agent(session_id: str) -> AgentExecutor:
    history = RedisChatMessageHistory(session_id=session_id, url=REDIS_URL)

    llm = ChatOpenAI(model=MODEL, temperature=0.2)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are a helpful assistant. Use tools when helpful. Keep answers concise."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    tools = [get_env]

    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

    return executor, history

@app.get("/health")
def health():
    return {"status": "ok", "env": ENV}

@app.post("/chat")
def chat(payload: ChatIn):
    try:
        executor, history = build_agent(payload.session_id)

        # Repassa histórico ao agente
        result = executor.invoke(
            {"input": payload.message, "chat_history": history.messages}
        )

        # Salva turno no Redis
        history.add_user_message(payload.message)
        history.add_ai_message(result["output"])

        return {"answer": result["output"], "env": ENV}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
