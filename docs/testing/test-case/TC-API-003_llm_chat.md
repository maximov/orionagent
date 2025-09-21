1. Отправка валидного запроса POST /v1/chat/ с телом:
{
  "channel": "web",
  "user_id": "u-123",
  "text": "Привет"
}
2. проверить ответ

Код-статуса ответа: 200

{
  "parts": ["echo: Привет"],
  "provider": "openrouter"
}
