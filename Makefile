SHELL := /bin/bash

.PHONY: venv install dev up down logs rebuild test fmt

venv:
	python3 -m venv .venv

install:
	. .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

dev:
	# Запуск Core API (порт 8001) + Телеграм бота локально
	@echo ">>> Run Core API"
	@(. .venv/bin/activate && uvicorn api.app:app --host 0.0.0.0 --port 8001 &) \
	 && sleep 2 \
	 && echo ">>> Run Telegram Bot" \
	 && (. .venv/bin/activate && python transports/telegram_bot.py)

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

rebuild:
	docker compose build --no-cache

test:
	. .venv/bin/activate && pytest -q

