from __future__ import annotations


class RetrievalPolicyService:
    def __init__(self):
        self.small_talk_patterns = [
            "tôi có đẹp trai không",
            "tôi có xinh không",
            "bạn khỏe không",
            "xin chào",
            "hello",
            "chào nhé",
            "bạn là ai",
            "cảm ơn",
            "thank you",
            "bye",
            "tạm biệt",
            "good morning",
            "good night",
            "chúc ngủ ngon",
        ]

        self.follow_up_markers = [
            "còn",
            "thế còn",
            "vậy thì",
            "cái đó",
            "phần đó",
            "chi tiết hơn",
            "nói rõ hơn",
            "giải thích thêm",
        ]

    def should_retrieve(
        self,
        user_message: str,
        memory_messages: list[dict] | None = None,
    ) -> bool:
        text = (user_message or "").lower().strip()
        memory_messages = memory_messages or []

        if not text:
            return False

        if any(pattern in text for pattern in self.small_talk_patterns):
            return False

        if any(marker in text for marker in self.follow_up_markers):
            return len(memory_messages) > 0

        # Với chatbot tri thức, mặc định nên retrieve
        return True