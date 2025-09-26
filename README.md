# 📦 Analytics Cursor

## 📌 Описание
Analytics Cursor — это аналитическая система для анализа CSV-логов использования Cursor (IDE/редактор кода).
Проект позволяет быстро разворачивать интерактивную дашборд-систему с графиками и таблицами, используя Python, FastAPI и Streamlit.

### Архитектура
Архитектура строго типизирована и разделена на несколько слоёв:
- **DTO** (Pydantic) для каждой строки CSV;
- **CSVRepository** для работы с файлами и преобразования данных;
- **Service Layer** для агрегаций и бизнес-логики;
- **API** (FastAPI) для доступа к агрегированным данным;
- **UI** (Streamlit + Plotly) для визуализации отчётов.

## ⚡️ Функциональность
- Загрузка CSV с полями:
  - `Date`, `User`, `Kind`, `Model`, `Max Mode`,
  - `Input (w/ Cache Write)`, `Input (w/o Cache Write)`,
  - `Cache Read`, `Output Tokens`, `Total Tokens`, `Requests`;
- Автоматическое преобразование строк в DTO;
- Три готовых отчёта:
  1. 📈 *Events per day* (линейный график + таблица);
  2. 👤 *Tokens per user* (bar chart + таблица);
  3. 🤖 *Tokens by model* (pie chart + таблица);
- Гибкая архитектура для добавления новых графиков и метрик;
- Возможность расширить систему саммари/чат-ботом в будущем.

## 🗂 Структура репозитория
```
analytics-cursor/
├── backend/           # FastAPI + сервисный слой, тесты
├── frontend/          # Streamlit-приложение с визуализациями
└── docker-compose.yml # Запуск стека через Docker Compose
```

## 🚀 Запуск через Docker Compose
1. Склонировать репозиторий:
   ```bash
   git clone https://github.com/mishka-k/analytics-cursor.git
   cd analytics-cursor
   ```
2. Положить CSV-файлы в папку `data/`.
3. Собрать и запустить контейнеры:
   ```bash
   docker-compose up --build
   ```
4. Доступ к сервисам:
   - Backend API: http://localhost:8000/docs
   - Frontend (дашборд): http://localhost:8501

## 🧪 Тесты
Тесты расположены в `backend/app/tests` и используют `pytest`.

### Запуск тестов
```bash
cd backend
pytest --maxfail=1 --disable-warnings -q
```

### Покрытие кода
```bash
pytest --cov=app --cov-report=term-missing
```

## 🛠 Технологии
- Python 3.11
- FastAPI
- Pydantic
- pandas
- Streamlit
- Plotly
- Docker, Docker Compose
- pytest
