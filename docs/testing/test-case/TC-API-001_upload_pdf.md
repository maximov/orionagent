# TC API 001 upload pdf
Предусловия: Авторизация валидна, стенд доступен.

Шаги:

1) POST /upload с файлом test.pdf

Ожидание: 201 + JSON {"status": "success"}

Связи: test-plan №2; api-checklist №1