import tkinter as tk
from tkinter import scrolledtext, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.chatbot import parse_input as parse_input_nlu, handle_intent as handle_intent_router
from db import initialize_database
from utils.logger import log_command


class FootballChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Football League Chatbot")
        self.root.geometry("900x650")
        self.root.configure(bg="#1e1e1e")

        initialize_database()

        self._setup_ui()
        self._add_welcome_message()

    def _setup_ui(self):
        title_frame = tk.Frame(self.root, bg="#2d2d2d", height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="⚽ Football League Chatbot",
            font=("Arial", 16, "bold"),
            bg="#2d2d2d",
            fg="#ffffff"
        )
        title_label.pack(pady=12)

        self.chat_display = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            bg="#252526",
            fg="#d4d4d4",
            font=("Consolas", 11),
            state=tk.DISABLED,
            borderwidth=0
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        self.input_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.input_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        self.input_entry = tk.Entry(
            self.input_frame,
            bg="#3c3c3c",
            fg="#ffffff",
            font=("Consolas", 11),
            borderwidth=0,
            insertbackground="#ffffff"
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.input_entry.bind("<Return>", self._on_send)

        self.send_button = tk.Button(
            self.input_frame,
            text="Send",
            command=self._on_send,
            bg="#0e639c",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            borderwidth=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.send_button.pack(side=tk.LEFT, padx=(10, 0))

        quick_frame = tk.Frame(self.root, bg="#1e1e1e", height=40)
        quick_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        quick_frame.pack_propagate(False)

        quick_actions = [
            ("помощ", "help"),
            ("клубове", "list_clubs"),
            ("играчи", "list_all_players"),
            ("класиране", "get_standings"),
        ]

        for label, cmd in quick_actions:
            btn = tk.Button(
                quick_frame,
                text=label,
                command=lambda c=cmd: self._execute_quick_command(c),
                bg="#3c3c3c",
                fg="#ffffff",
                font=("Arial", 9),
                borderwidth=0,
                padx=10,
                pady=5,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=2)

    def _add_welcome_message(self):
        welcome = "Добре дошли във Football League Chatbot!\nНапишете 'помощ' за списък с команди."
        self._add_message("Bot", welcome)

    def _on_send(self, event=None):
        user_input = self.input_entry.get().strip()
        if not user_input:
            return

        self._add_message("You", user_input)
        self.input_entry.delete(0, tk.END)

        self._process_input(user_input)

    def _execute_quick_command(self, cmd):
        if cmd == "help":
            input_text = "помощ"
        elif cmd == "list_clubs":
            input_text = "покажи клубове"
        elif cmd == "list_all_players":
            input_text = "покажи всички играчи"
        elif cmd == "get_standings":
            input_text = "покажи класиране Първа лига"
        else:
            input_text = cmd

        self._add_message("You", input_text)
        self._process_input(input_text)

    def _process_input(self, user_input):
        try:
            intent, params = parse_input_nlu(user_input)
            response = handle_intent_router(intent, params)

            if response == "exit":
                self.root.quit()
                return

            self._add_message("Bot", response)
            log_command(user_input, response)
        except Exception as e:
            self._add_message("Bot", f"Грешка: {str(e)}")

    def _add_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)

        if sender == "You":
            self.chat_display.insert(tk.END, "You: ", "user_tag")
            self.chat_display.insert(tk.END, f"{message}\n")
        else:
            self.chat_display.insert(tk.END, "Bot: ", "bot_tag")

            if message.startswith("ID  Име"):
                self.chat_display.insert(tk.END, "\n" + message + "\n", "table_tag")
            else:
                self.chat_display.insert(tk.END, f"{message}\n")

        self.chat_display.tag_config("user_tag", foreground="#4fc3f7", font=("Consolas", 11, "bold"))
        self.chat_display.tag_config("bot_tag", foreground="#81c784", font=("Consolas", 11, "bold"))
        self.chat_display.tag_config("table_tag", foreground="#d4d4d4", font=("Consolas", 10))

        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = FootballChatbotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
