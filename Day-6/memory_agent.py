import json
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

HISTORY_FILE = "chat_history.json"
MODEL_NAME = "gemini-2.5-flash"


class GeminiChatAgent:
    def __init__(self, history_file: str = HISTORY_FILE):
        self.history_file = history_file
        self.client = genai.Client()
        self.history = self.load_history()
        self.chat = self._create_chat_with_history()

    # ---------- JSON persistence ----------

    def load_history(self):
        if not os.path.exists(self.history_file):
            return []

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    # basic sanity check on keys
                    for msg in data:
                        if "role" not in msg or "content" not in msg:
                            raise ValueError("Invalid history format")
                    return data
                else:
                    print("History file is not a list, starting empty.")
                    return []
        except (json.JSONDecodeError, OSError, ValueError) as e:
            print(f"Could not load history ({e}). Starting with empty history.")
            return []

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"Error saving history: {e}")

    def _append_message(self, role: str, content: str):
        self.history.append(
            {
                "role": role,  # "user" or "model"
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self.save_history()

    # ---------- GenAI chat setup ----------

    def _history_to_genai(self):
        """
        Convert our JSON messages into google.genai.types.Content[]
        """
        contents = []
        for msg in self.history:
            # Only keep simple text parts here
            contents.append(
                types.Content(
                    role=msg["role"],
                    parts=[types.Part.from_text(text=msg["content"])],
                )
            )
        return contents

    def _create_chat_with_history(self):
        """
        Create a chat session seeded with previous messages.
        If no history, we just create an empty chat.
        """
        if self.history:
            genai_history = self._history_to_genai()
            chat = self.client.chats.create(
                model=MODEL_NAME,
                history=genai_history,
            )
        else:
            chat = self.client.chats.create(model=MODEL_NAME)
        return chat

    # ---------- Chat loop ----------

    def run_cli(self):
        if self.history:
            print("Loaded previous conversation:")
            for msg in self.history:
                print(f"[{msg['role']}] {msg['content']}")
            print("-" * 40)
        else:
            print("No previous history. Starting fresh.")
            print("-" * 40)

        print("Type 'exit' or 'quit' to stop.\n")

        try:
            while True:
                user_input = input("You: ").strip()
                if user_input.lower() in ("exit", "quit"):
                    print("Goodbye!")
                    break

                # 1) Save user message locally
                self._append_message("user", user_input)

                # 2) Send to Gemini chat
                response = self.chat.send_message(user_input)
                reply_text = response.text  # SDK convenience property :contentReference[oaicite:1]{index=1}

                # 3) Save model reply
                self._append_message("model", reply_text)

                print(f"Gemini: {reply_text}")

        except KeyboardInterrupt:
            print("\nInterrupted. History saved.")
        finally:
            # Optional: sync GenAI chat history back into file if you want to trust SDK history instead
            pass


if __name__ == "__main__":
    agent = GeminiChatAgent()
    agent.run_cli()
