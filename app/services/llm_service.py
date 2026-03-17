from langchain_groq import ChatGroq

from app.core.config import settings
from app.services.prompt_builder_service import PromptBuilderService


class LLMService:
    def __init__(self, prompt_builder: PromptBuilderService | None = None):
        self.model_name = settings.LLM_MODEL_NAME
        self.prompt_builder = prompt_builder or PromptBuilderService()

        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.LLM_MODEL_NAME,
            temperature=settings.LLM_TEMPERATURE,
        )

    async def generate_answer(
        self,
        user_message: str,
        memory_messages: list[dict] | None = None,
        retrieved_contexts: list[str] | None = None,
    ) -> str:
        prompt = self.prompt_builder.build_chat_prompt(
            user_message=user_message,
            memory_messages=memory_messages,
            retrieved_contexts=retrieved_contexts,
        )

        response = await self.llm.ainvoke(prompt)
        return response.content if hasattr(response, "content") else str(response)