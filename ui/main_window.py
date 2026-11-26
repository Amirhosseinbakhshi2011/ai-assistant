"""
رابط کاربری مدرن دسکتاپ با customtkinter.
پشتیبانی کامل از فارسی و انگلیسی، تم تاریک/روشن و مدیریت خطا.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Optional

from core.assistant import Assistant
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# تنظیم ظاهر کلی
ctk.set_appearance_mode("System")  # System, Dark, Light
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    """پنجره اصلی برنامه."""

    def __init__(self) -> None:
        super().__init__()

        self.title("امیرحسین بخشی | دستیار هوش مصنوعی")
        self.geometry("1000x700")
        self.minsize(800, 550)

        # نمونه دستیار
        self.assistant = Assistant(language=settings.default_language)

        # متغیرهای وضعیت
        self.is_processing = False
        self.stream_mode = True  # پاسخ جریانی (زیباتر)

        self._build_ui()
        self._load_chat_list()

        # بستن تمیز
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _build_ui(self) -> None:
        """ساخت تمام اجزای رابط کاربری."""

        # ----- سایدبار چپ (تاریخچه) -----
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar, text="گفتگوها", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10), padx=10)

        self.new_chat_btn = ctk.CTkButton(
            self.sidebar, text="+ گفتگوی جدید", command=self._on_new_chat, height=36
        )
        self.new_chat_btn.pack(pady=(0, 10), padx=12, fill="x")

        # لیست گفتگوها
        self.chat_list_frame = ctk.CTkScrollableFrame(self.sidebar, label_text="")
        self.chat_list_frame.pack(fill="both", expand=True, padx=8, pady=5)

        # دکمه تنظیمات ظاهر
        self.theme_btn = ctk.CTkButton(
            self.sidebar,
            text="تغییر تم (تاریک/روشن)",
            command=self._toggle_theme,
            height=32,
            fg_color="transparent",
            border_width=1,
        )
        self.theme_btn.pack(pady=12, padx=12, fill="x", side="bottom")

        # ----- ناحیه اصلی چت -----
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True)

        # هدر
        self.header = ctk.CTkFrame(self.main_frame, height=50, corner_radius=0)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.title_label = ctk.CTkLabel(
            self.header,
            text="دستیار هوش مصنوعی",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.title_label.pack(side="left", padx=20, pady=10)

        # ناحیه نمایش پیام‌ها
        self.chat_display = ctk.CTkTextbox(
            self.main_frame,
            wrap="word",
            font=ctk.CTkFont(size=14),
            state="disabled",
            activate_scrollbars=True,
        )
        self.chat_display.pack(fill="both", expand=True, padx=15, pady=(10, 5))

        # تگ‌های رنگ برای نقش‌ها
        self.chat_display.tag_config("user", foreground="#3B82F6")
        self.chat_display.tag_config("assistant", foreground="#10B981")
        self.chat_display.tag_config("error", foreground="#EF4444")
        self.chat_display.tag_config("system", foreground="#9CA3AF")

        # نوار ورودی
        self.input_frame = ctk.CTkFrame(self.main_frame, height=70, corner_radius=0)
        self.input_frame.pack(fill="x", padx=10, pady=10)
        self.input_frame.pack_propagate(False)

        self.message_entry = ctk.CTkTextbox(
            self.input_frame, height=50, font=ctk.CTkFont(size=14), wrap="word"
        )
        self.message_entry.pack(side="left", fill="both", expand=True, padx=(5, 8), pady=8)
        self.message_entry.bind("<Return>", self._on_enter_pressed)
        self.message_entry.bind("<Shift-Return>", lambda e: None)  # اجازه خط جدید

        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="ارسال",
            width=90,
            height=42,
            command=self._on_send,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.send_btn.pack(side="right", padx=(0, 8), pady=8)

        # فوکوس روی ورودی
        self.message_entry.focus_set()

    def _toggle_theme(self) -> None:
        current = ctk.get_appearance_mode()
        new_mode = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)

    def _on_enter_pressed(self, event) -> str:
        """ارسال با Enter (بدون Shift)."""
        if not event.state & 0x1:  # Shift نگه داشته نشده
            self._on_send()
            return "break"
        return None

    def _on_new_chat(self) -> None:
        if self.is_processing:
            return
        self.assistant.new_chat()
        self._clear_chat_display()
        self._load_chat_list()
        self._append_system_message("گفتگوی جدید شروع شد. پیام خود را بنویسید.")

    def _load_chat_list(self) -> None:
        """بارگذاری لیست گفتگوها در سایدبار."""
        for widget in self.chat_list_frame.winfo_children():
            widget.destroy()

        chats = self.assistant.list_chats()
        for chat in chats:
            btn = ctk.CTkButton(
                self.chat_list_frame,
                text=chat["title"][:35] + ("..." if len(chat["title"]) > 35 else ""),
                anchor="w",
                height=36,
                fg_color="transparent",
                command=lambda cid=chat["id"]: self._load_selected_chat(cid),
            )
            btn.pack(fill="x", pady=2)

    def _load_selected_chat(self, chat_id: str) -> None:
        if self.is_processing:
            return
        if self.assistant.load_chat(chat_id):
            self._clear_chat_display()
            for msg in self.assistant.get_current_messages():
                role = msg["role"]
                content = msg["content"]
                self._append_message(role, content)
            self._load_chat_list()

    def _clear_chat_display(self) -> None:
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")

    def _append_message(self, role: str, content: str) -> None:
        self.chat_display.configure(state="normal")
        prefix = "شما: " if role == "user" else "دستیار: "
        tag = role if role in ("user", "assistant", "error") else "system"
        self.chat_display.insert("end", prefix, tag)
        self.chat_display.insert("end", content + "\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _append_system_message(self, text: str) -> None:
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", text + "\n\n", "system")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def _on_send(self) -> None:
        if self.is_processing:
            return

        message = self.message_entry.get("1.0", "end").strip()
        if not message:
            return

        self.message_entry.delete("1.0", "end")
        self._append_message("user", message)
        self.is_processing = True
        self.send_btn.configure(state="disabled", text="...")

        # اجرا در thread جدا تا UI قفل نشود
        thread = threading.Thread(target=self._process_message, args=(message,), daemon=True)
        thread.start()

    def _process_message(self, message: str) -> None:
        try:
            if self.stream_mode:
                self.chat_display.configure(state="normal")
                self.chat_display.insert("end", "دستیار: ", "assistant")
                self.chat_display.configure(state="disabled")

                full = ""
                for token in self.assistant.send_message(message, stream=True):
                    full += token
                    self.chat_display.configure(state="normal")
                    self.chat_display.insert("end", token, "assistant")
                    self.chat_display.configure(state="disabled")
                    self.chat_display.see("end")
                    self.update_idletasks()

                self.chat_display.configure(state="normal")
                self.chat_display.insert("end", "\n\n")
                self.chat_display.configure(state="disabled")
            else:
                response = self.assistant.send_message(message, stream=False)
                self._append_message("assistant", response)

            # به‌روزرسانی لیست گفتگوها بعد از اولین پیام
            self.after(0, self._load_chat_list)

        except ValueError as e:
            error_msg = str(e)
            self.after(0, lambda msg=error_msg: self._show_error(msg))
        except (TimeoutError, ConnectionError) as e:
            error_msg = str(e)
            self.after(0, lambda msg=error_msg: self._show_error(msg))
        except Exception as e:
            logger.exception("خطا در پردازش پیام")
            error_msg = f"خطای غیرمنتظره: {str(e)}"
            self.after(0, lambda msg=error_msg: self._show_error(msg))
        finally:
            self.after(0, self._finish_processing)

    def _show_error(self, text: str) -> None:
        self._append_message("error", text)
        messagebox.showerror("خطا", text)

    def _finish_processing(self) -> None:
        self.is_processing = False
        self.send_btn.configure(state="normal", text="ارسال")
        self.message_entry.focus_set()

    def _on_closing(self) -> None:
        self.destroy()