# Test Plan - OrionAgent
Версия 1.0 | Отвественный: QA Lead | Дата: 18.09.2025

## 1. Цели / область
[ссылки] ./checklists/api_checklist.md, ./checklists/ui_checklist.md

POST /v1/chat/ (валидные и не валидные запросы)
GET /healthz
GET /


## 2. Стратегия
Smoke перед каждым билдом; ручные сценарии для promt-injection
ФТ API


## 3. Критерии входа/выхода
Вход: стенд поднят, токены LLM/Tg есть

Выход: 0 Критических ошибок, >=95% тестов пройдено успешно

## 4. Риски
Promt Injection, таймаут LLM, утечки в логах



## 5. Матрица покрытия
| Объект | Чек-лист | Тест-кейс |
|--------|----------|-----------|
| API загрузка| api_checklist №1-3 | TC-API-001_upload_pdf,<br> TC-API-002_upload_csv_unauth |

