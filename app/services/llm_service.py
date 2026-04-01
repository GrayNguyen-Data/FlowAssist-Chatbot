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

    # ===== CLEAN TEXT =====
    def _normalize_text(self, text: str) -> str:
        return " ".join((text or "").strip().split())

    # ===== PREPARE CONTEXT =====
    def _prepare_contexts(self, retrieved_contexts: list[str] | None = None) -> list[str]:
        retrieved_contexts = retrieved_contexts or []

        cleaned: list[str] = []
        seen: set[str] = set()

        for ctx in retrieved_contexts:
            text = self._normalize_text(ctx)
            if not text:
                continue

            # cắt context quá dài
            if len(text) > 1200:
                text = text[:1200].rstrip() + "..."

            key = text.lower()
            if key in seen:
                continue

            seen.add(key)
            cleaned.append(text)

        return cleaned[:5]

    # ===== DETECT REALTIME QUESTION =====
    def _is_realtime_question(self, text: str) -> bool:
        text = (text or "").lower()
        keywords = [
            "hôm nay",
            "bây giờ",
            "hiện tại",
            "thời tiết",
            "nhiệt độ",
            "giá vàng",
            "tỷ giá",
            "giá xăng",
        ]
        return any(k in text for k in keywords)

    # ===== MAIN GENERATE =====
    async def generate_answer(
        self,
        user_message: str,
        memory_messages: list[dict] | None = None,
        retrieved_contexts: list[str] | None = None,
    ) -> str:
        prepared_contexts = self._prepare_contexts(retrieved_contexts)

        if not prepared_contexts:
            if self._is_realtime_question(user_message):
                prompt = f"""
Bạn là trợ lý AI.

Câu hỏi: {user_message}

Yêu cầu:
- Đây là câu hỏi cần dữ liệu thời gian thực.
- Bạn không có dữ liệu realtime.
- Hãy trả lời tự nhiên, hữu ích.
- Gợi ý người dùng kiểm tra nguồn khác (Google, app, v.v.).
"""
            else:
                prompt = f"""
Bạn là trợ lý AI.

Câu hỏi: {user_message}

Yêu cầu:
- Trả lời dựa trên kiến thức chung của bạn.
- Trả lời rõ ràng, dễ hiểu.
- Không cần nói về "context" hay "dữ liệu hệ thống".
"""
        else:
            prompt = self.prompt_builder.build_chat_prompt(
                user_message=user_message,
                memory_messages=memory_messages,
                retrieved_contexts=prepared_contexts,
            )

        response = await self.llm.ainvoke(prompt)
        return response.content if hasattr(response, "content") else str(response)