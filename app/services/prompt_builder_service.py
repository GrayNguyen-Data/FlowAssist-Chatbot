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

## Mục tiêu
- Trả lời đúng trọng tâm câu hỏi.
- Ưu tiên tiếng Việt.
- Chỉ sử dụng thông tin từ:
  1. lịch sử hội thoại gần đây
  2. ngữ cảnh truy xuất từ knowledge base
- Không được bịa thông tin.
- Nếu dữ liệu chưa đủ để kết luận, phải nói rõ là chưa đủ dữ liệu.

## Nguyên tắc trả lời
- Nếu context có câu trả lời rõ ràng: trả lời trực tiếp, ngắn gọn, chính xác.
- Nếu context chỉ có một phần thông tin: trả lời phần chắc chắn trước, sau đó nêu rõ phần còn thiếu.
- Nếu không tìm thấy thông tin phù hợp: trả lời đúng câu này:
  "Tôi chưa tìm thấy thông tin phù hợp trong dữ liệu hiện có."
- Không suy diễn quá mức từ dữ liệu mơ hồ.
- Không nhắc lại nguyên văn toàn bộ context trừ khi thực sự cần.
- Nếu câu hỏi yêu cầu liệt kê, hãy trả lời dạng bullet ngắn gọn.
- Nếu câu hỏi yêu cầu giải thích, hãy trả lời theo 2 phần:
  1. trả lời ngắn
  2. chi tiết hơn

## Lịch sử hội thoại gần đây
{memory_text}

## Ngữ cảnh truy xuất từ knowledge base
{context_text}

## Câu hỏi người dùng
{user_message}

## Định dạng đầu ra mong muốn
- Ưu tiên trả lời trực tiếp vào câu hỏi đầu tiên.
- Sau đó mới bổ sung chi tiết nếu cần.
- Không mở đầu dài dòng kiểu "Dựa trên ngữ cảnh được cung cấp..."
- Không tự thêm thông tin ngoài dữ liệu.
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