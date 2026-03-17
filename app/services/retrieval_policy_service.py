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
        ]

        self.knowledge_patterns = [
            "flowassist",
            "hệ thống",
            "chatbot",
            "rag",
            "redis",
            "tidb",
            "minio",
            "api",
            "backend",
            "ticket",
            "history",
            "mcp",
            "tài liệu",
            "quy trình",
            "hướng dẫn",
            "cấu trúc",
            "kiến trúc",
            "solf world", 
        ]

        self.question_markers = [
            "là gì",
            "như thế nào",
            "ở đâu",
            "bao nhiêu",
            "khi nào",
            "tại sao",
            "vì sao",
            "làm sao",
            "thế nào",
            "giải thích",
            "hãy cho tôi biết",
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

        if any(pattern in text for pattern in self.knowledge_patterns):
            return True

        if any(marker in text for marker in self.question_markers):
            return True

        if "?" in text:
            return True

        follow_up_markers = [
            "còn",
            "thế còn",
            "vậy thì",
            "cái đó",
            "phần đó",
            "chi tiết hơn",
            "nói rõ hơn",
            "giải thích thêm",
        ]
        if any(marker in text for marker in follow_up_markers):
            return len(memory_messages) > 0

        return False