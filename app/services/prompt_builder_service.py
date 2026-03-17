from __future__ import annotations

from typing import List, Dict


class PromptBuilderService:
    def build_chat_prompt(
        self,
        user_message: str,
        memory_messages: List[Dict] | None = None,
        retrieved_contexts: List[str] | None = None,
    ) -> str:
        memory_messages = memory_messages or []
        retrieved_contexts = retrieved_contexts or []

        memory_text = self._format_memory(memory_messages)
        context_text = self._format_contexts(retrieved_contexts)

        prompt = f"""
Bạn là trợ lý AI cho hệ thống FlowAssist.

## Vai trò
- Trả lời rõ ràng, chính xác, ngắn gọn nhưng đủ ý.
- Ưu tiên tiếng Việt.
- Nếu không đủ dữ liệu từ ngữ cảnh hoặc lịch sử hội thoại, hãy nói rõ bạn chưa có đủ thông tin.
- Không bịa thông tin.

## Lịch sử hội thoại gần đây
{memory_text}

## Ngữ cảnh truy xuất từ knowledge base
{context_text}

## Câu hỏi người dùng
{user_message}

## Yêu cầu trả lời
- Bám sát câu hỏi.
- Nếu có ngữ cảnh liên quan, ưu tiên dùng ngữ cảnh đó.
- Nếu ngữ cảnh không đủ để kết luận, nói rõ phần nào chưa chắc chắn.
- Trả lời theo văn phong hỗ trợ người dùng cuối.
""".strip()

        return prompt

    def _format_memory(self, memory_messages: List[Dict]) -> str:
        if not memory_messages:
            return "(không có lịch sử hội thoại gần đây)"

        lines = []
        for item in memory_messages:
            role = item.get("role", "unknown")
            content = item.get("content", "").strip()
            if not content:
                continue
            lines.append(f"{role}: {content}")

        return "\n".join(lines) if lines else "(không có lịch sử hội thoại gần đây)"

    def _format_contexts(self, retrieved_contexts: List[str]) -> str:
        if not retrieved_contexts:
            return "(không có ngữ cảnh truy xuất)"

        blocks = []
        for idx, ctx in enumerate(retrieved_contexts, start=1):
            text = (ctx or "").strip()
            if not text:
                continue
            blocks.append(f"[Tài liệu {idx}]\n{text}")

        return "\n\n".join(blocks) if blocks else "(không có ngữ cảnh truy xuất)"