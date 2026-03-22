# 🛡️ PII Masking Proxy Service

> Интеллектуальный сервис-прокси для автоматического обнаружения, маскирования и восстановления персональных данных перед отправкой в языковые модели.

---

## 🔍 Как это работает

```
Пользователь → [Промпт с PII] → Маскирование → LLM → Размаскирование → [Ответ]
```

Сервис перехватывает запрос пользователя, автоматически находит и заменяет персональные данные на безопасные токены, отправляет анонимизированный текст в LLM, а затем восстанавливает оригинальные данные в ответе.

---

## 🤖 Модель

- **Архитектура:** DistilBERT-base
- **Датасет:** `ai4privacy/open-pii-masking-500k-ai4privacy`
- **Поддерживаемые языки:** English, Français, Deutsch, Español, Italiano, Nederlands
- **Экспорт:** поддерживается конвертация в ONNX формат

### 📊 Метрики качества

| Метрика   | Значение |
|-----------|----------|
| Accuracy  | **0.98** |
| F1 Score  | **0.92** |
| Precision | **0.92** |
| Recall    | **0.93** |

> 📓 Процесс обучения и конвертация в ONNX подробно описаны в [Google Colab](./src/model/README.md)

---

## 🚀 Быстрый старт

### 1. Настройка окружения

```bash
cp .env.example .env
```

При необходимости задайте пароль администратора Grafana:

```env
GF_SECURITY_ADMIN_PASSWORD=your_password
```

### 2. Запуск сервиса

**CPU:**
```bash
docker-compose up -d
```

**GPU:**
```bash
docker-compose -f docker-compose.gpu.yml up -d
```

---

## 📡 Использование API

Сервис совместим с форматом [GigaChat API](https://developers.sber.ru/studio/workspaces).

### Получение токена доступа

1. Перейдите на [developers.sber.ru](https://developers.sber.ru/studio/workspaces) и получите **Access Key**
2. Запустите скрипт для получения токена:

```bash
python gigachat_token.py
```

3. Введите ваш Access Key — на выходе получите **Access Token**, который необходимо передавать в заголовках запросов.

---

## 📊 Мониторинг

### Grafana

1. Откройте Grafana в браузере
2. Добавьте источник данных: `http://prometheus:9090`
3. Импортируйте дашборд из репозитория

### Логи

```bash
tail -f prod.log
```

---

## 📁 Структура проекта

```
.
├── docker-compose.yml            # Запуск на CPU
├── docker-compose.gpu.yml        # Запуск на GPU
├── gigachat_token.py             # Получение Access Token
├── prod.log                      # Логи сервиса
├── prometheus/
│   └── prometheus.yml            # Конфигурация Prometheus
├── dash-graphana-triton.json     # Дашборд Grafana
├── src/
│   ├── config.py                 # Конфигурация сервиса
│   ├── logger_config.py          # Настройка логирования
│   ├── api/
│   │   ├── Dockerfile            # Образ API-сервиса
│   │   ├── main.py               # Точка входа FastAPI
│   │   ├── routers.py            # Маршруты API
│   │   └── deps.py               # Зависимости
│   ├── model/
│   │   ├── README.md             # Google Colab & обучение модели
│   │   └── triton_infer.py       # Инференс через Triton
│   └── utils/
│       ├── masking.py            # Логика маскирования PII
│       └── streaming.py          # Стриминг ответов
└── triton/
    └── models/
        └── ner_onnx/
            ├── 1/
            │   ├── model.onnx        # ONNX модель
            │   └── model.onnx.data   # Веса модели
            └── config.pbtxt          # Конфигурация Triton
```

---

## 🔒 Безопасность

Сервис гарантирует, что персональные данные пользователей **никогда не покидают периметр** — в LLM передаётся только анонимизированный текст.