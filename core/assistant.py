"""
لایه اصلی دستیار هوش مصنوعی.
این کلاس هسته منطق برنامه است و UI فقط با آن صحبت می‌کند.
در آینده می‌توان قابلیت‌هایی مثل حافظه، ابزارها و Agent را به راحتی به آن اضافه کرد.
"""

from typing import List, Dict, Optional, Generator

from core.ai_client import AIClient
from core.chat_history import ChatHistory
from utils.logger import get_logger

logger = get_logger(__name__)


class Assistant:
    """دستیار هوش مصنوعی اصلی."""
    SYSTEM_PROMPT_FA = (
        "تو یک دستیار هوش مصنوعی به نام «امیرحسین بخشی» هستی. "
        "تو توسط امیرحسین بخشی ساخته شده‌ای. "
        "به زبان فارسی پاسخ بده مگر اینکه کاربر به زبان دیگری صحبت کند. "
        "پاسخ‌هایت را مفید، دقیق، مودب و ساخت‌یافته نگه دار. "
        "اگر کسی از اسم تو پرسید، بگو نام تو امیرحسین بخشی است."
    )

    SYSTEM_PROMPT_EN = (
        "You are an AI assistant named «Amirhossein Bakhshi». "
        "You were created by Amirhossein Bakhshi. "
        "Respond in the same language the user is using. "
        "Keep your answers helpful, accurate, polite and well-structured. "
        "If someone asks your name, say that your name is Amirhossein Bakhshi."
    )
    def __init__(self, language: str = "fa") -> None:
        self.ai_client = AIClient()
        self.history = ChatHistory()
        self.language = language.lower()
        self.system_prompt = (
            self.SYSTEM_PROMPT_FA if self.language == "fa" else self.SYSTEM_PROMPT_EN
        )

        # شروع با یک گفتگوی جدید
        self.history.new_chat()
        self.history.add_message("system", self.system_prompt)

    def send_message(self, user_message: str, stream: bool = False) -> str | Generator[str, None, None]:
        """
        ارسال پیام کاربر و دریافت پاسخ مدل.

        Args:
            user_message: متن پیام کاربر
            stream: اگر True باشد پاسخ جریانی برگردانده می‌شود

        Returns:
            پاسخ کامل یا ژنراتور توکن‌ها
        """
        if not user_message.strip():
            raise ValueError("پیام نمی‌تواند خالی باشد.")

        # افزودن پیام کاربر به تاریخچه
        self.history.add_message("user", user_message.strip())

        messages = self.history.get_messages()

        try:
            if stream:
                # برای استریم، پاسخ را جمع می‌کنیم تا در تاریخچه ذخیره شود
                full_response = ""
                def generator():
                    nonlocal full_response
                    for token in self.ai_client.chat(messages, stream=True):
                        full_response += token
                        yield token
                    # پس از اتمام استریم، پاسخ را ذخیره می‌کنیم
                    self.history.add_message("assistant", full_response.strip())
                return generator()
            else:
                response = self.ai_client.chat(messages, stream=False)
                self.history.add_message("assistant", response)
                return response

        except Exception as e:
            # در صورت خطا، پیام کاربر را از تاریخچه حذف می‌کنیم تا وضعیت تمیز بماند
            if self.history.messages and self.history.messages[-1]["role"] == "user":
                self.history.messages.pop()
                self.history._save()
            raise e

    def new_chat(self) -> None:
        """شروع یک گفتگوی کاملاً جدید."""
        self.history.new_chat()
        self.history.add_message("system", self.system_prompt)
        logger.info("گفتگوی جدید شروع شد")

    def load_chat(self, chat_id: str) -> bool:
        """بارگذاری یک گفتگوی قبلی."""
        success = self.history.load_chat(chat_id)
        if success and not any(m["role"] == "system" for m in self.history.messages):
            # اگر system prompt نبود، اضافه می‌کنیم
            self.history.messages.insert(0, {"role": "system", "content": self.system_prompt})
            self.history._save()
        return success

    def list_chats(self) -> List[Dict[str, str]]:
        """لیست گفتگوهای ذخیره شده."""
        return self.history.list_chats()

    def delete_chat(self, chat_id: str) -> bool:
        """حذف یک گفتگو."""
        return self.history.delete_chat(chat_id)

    def get_current_messages(self) -> List[Dict[str, str]]:
        """پیام‌های گفتگوی فعلی (بدون system برای نمایش)."""
        return [m for m in self.history.get_messages() if m["role"] != "system"]