from fastapi import FastAPI

# import routers
from api.routes import health, rag, chat

app = FastAPI(title="FlowAssist Chatbot API")

# include sub-routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(rag.router, prefix="/rag", tags=["rag"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])


@app.on_event("startup")
def startup_event():
    print("Starting FlowAssist backend...")

@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down FlowAssist backend...")
