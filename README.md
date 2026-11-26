# AI Assistant 🤖

**Modern modular AI assistant** built with Python.

Chat with OpenAI, OpenRouter, or any OpenAI-compatible API.  
Streaming responses · Persistent history · Clean architecture · Secure `.env` config.

**Author:** [Amirhossein Bakhshi](https://github.com/Amirhosseinbakhshi2011)

---

## Features

- 💬 Interactive terminal chat
- ⚡ Streaming responses
- 🧠 Persistent conversation history (JSON)
- 🔌 Multi-provider (OpenAI, OpenRouter, any compatible endpoint)
- 🔒 Secrets only in `.env`
- 🧩 Modular structure ready for tools / agents / GUI later

---

## Requirements

- Python **3.11+**
- An API key (OpenAI, OpenRouter, etc.)

---

## Quick start

```bash
git clone https://github.com/Amirhosseinbakhshi2011/ai-assistant.git
cd ai-assistant

python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and put your API key

python main.py
```

---

## Configuration

Copy `.env.example` → `.env`:

```env
API_KEY=your_key_here
BASE_URL=https://api.openai.com/v1
MODEL=gpt-4o-mini
SYSTEM_PROMPT=You are a helpful AI assistant.
```

Examples:

| Provider   | BASE_URL                          | Example model      |
|------------|-----------------------------------|--------------------|
| OpenAI     | `https://api.openai.com/v1`       | `gpt-4o-mini`      |
| OpenRouter | `https://openrouter.ai/api/v1`    | `openai/gpt-4o-mini` |
| Groq       | `https://api.groq.com/openai/v1`  | `llama-3.1-8b-instant` |

---

## Project structure

```text
ai-assistant/
├── main.py              # Entry point
├── config/
│   └── settings.py      # Load .env + defaults
├── core/
│   ├── client.py        # OpenAI-compatible client + streaming
│   ├── assistant.py     # Conversation logic
│   └── history.py       # Save / load chats
├── data/chats/          # Chat history (gitignored)
├── .env.example
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Commands inside the chat

| Command     | Action                    |
|-------------|---------------------------|
| `/clear`    | Clear current conversation |
| `/save`     | Force save history        |
| `/history`  | Show recent messages      |
| `/quit` or `/exit` | Exit                 |

---

## License

MIT © Amirhossein Bakhshi

---

Built with curiosity.  
**Amirhossein Bakhshi** · 16 · Iran → USA
