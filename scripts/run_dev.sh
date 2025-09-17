#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# конфиг
: "${API_HOST:=0.0.0.0}"
: "${API_PORT:=8001}"
: "${API_RELOAD:=true}"
: "${PYTHON:=python3}"
: "${VENV_DIR:=.venv}"

API_CMD="uvicorn api.app:app --host ${API_HOST} --port ${API_PORT} $( [ "${API_RELOAD}" = "true" ] && echo --reload )"
BOT_CMD="${PYTHON} transports/telegram_bot.py"

# подготовка окружения
if [ ! -d "${VENV_DIR}" ]; then
  echo "- Создаю venv → ${VENV_DIR}"
  ${PYTHON} -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

if ! command -v uvicorn >/dev/null 2>&1; then
  echo "- Устанавливаю зависимости"
  pip install -U pip && pip install -r requirements.txt
fi

export PYTHONPATH="${ROOT_DIR}"
[ -f .env ] && export $(grep -v '^#' .env | xargs -d '\n' -I {} bash -c 'k="${0%%=*}"; v="${0#*=}"; printf "%s=%q\n" "$k" "$v"' {}) >/dev/null 2>&1 || true

# ---- запуск ----
echo "- Запускаю Core API: ${API_CMD}"
bash -c "${API_CMD}" &
API_PID=$!

sleep 1

echo "- Запускаю Telegram Bot: ${BOT_CMD}"
bash -c "${BOT_CMD}" &
BOT_PID=$!

cleanup() {
  echo "- Останавливаю процессы (${API_PID}, ${BOT_PID})"
  kill "${BOT_PID}" 2>/dev/null || true
  kill "${API_PID}" 2>/dev/null || true
  wait "${BOT_PID}" 2>/dev/null || true
  wait "${API_PID}" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

echo "- Готово: API http://localhost:${API_PORT} ; бота в Telegram"
# ждём, пока один из процессов завершится
wait -n
