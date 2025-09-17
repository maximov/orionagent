# AI Agent: Core API + Telegram UI

Монолит из двух процессов:
- **Core API (FastAPI)** - единая точка `/v1/chat` для всех UI (Telegram, веб-страница и т.д.)
- **Telegram Bot** - тонкий адаптер, шлёт запросы в Core API

## Быстрый старт (Docker)

```bash
cp .env.example .env   # заполните ключи
docker compose up -d
# Core API: http://localhost:8001
# Пробный запрос:
curl -X POST http://localhost:8001/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"channel":"web","user_id":"u1","text":"Привет!"}'
```

## Локальный запуск без Docker

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Core API
uvicorn api.app:app --reload --port 8001

# В другом терминале: Telegram Bot
python transports/telegram_bot.py
```

## Создание иерархии проекта

```bash
set -e

proj="ai-agent-full"

# Папки
mkdir -p "$proj"/{api/static,core,domain,services,llm,vectorstores,embedder,transports/web_landing,docker,scripts,tests}

# Файлы в корне
touch "$proj"/{.env,.env.example,.gitignore,README.md,requirements.txt,docker-compose.yml,Makefile,main.py}

# API
touch "$proj"/api/__init__.py
touch "$proj"/api/app.py
touch "$proj"/api/static/{index.html,app.js,styles.css}

# CORE
touch "$proj"/core/__init__.py
touch "$proj"/core/{config.py,history.py,utils.py,logging.py}

# DOMAIN
touch "$proj"/domain/__init__.py
touch "$proj"/domain/{message.py,rag.py}

# SERVICES
touch "$proj"/services/__init__.py
touch "$proj"/services/{orchestrator.py,retriever.py,prompts.py}

# LLM
touch "$proj"/llm/__init__.py
touch "$proj"/llm/{base.py,openai_compat.py,decorators.py,factory.py}

# VECTORSTORES
touch "$proj"/vectorstores/__init__.py
touch "$proj"/vectorstores/{base.py,chroma_store.py,qdrant_store.py,factory.py}

# EMBEDDER
touch "$proj"/embedder/__init__.py
touch "$proj"/embedder/{base.py,hf_embedder.py,factory.py}

# TRANSPORTS (UI)
touch "$proj"/transports/__init__.py
touch "$proj"/transports/telegram_bot.py
touch "$proj"/transports/web_landing/{index.html,app.js,styles.css}

# Docker
touch "$proj"/docker/Dockerfile.core
touch "$proj"/docker/Dockerfile.tg

# Скрипты и тесты
touch "$proj"/scripts/{run_dev.sh,seed_chroma.py,seed_qdrant.py}
chmod +x "$proj"/scripts/run_dev.sh
touch "$proj"/tests/__init__.py
touch "$proj"/tests/{test_llm.py,test_api.py,test_retriever.py"
```