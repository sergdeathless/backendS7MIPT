# План поставок запчастей

**Прогноз сроков поставки запчастей** по сетке «страна × запчасть»: в интерфейсе тепловая карта, в ячейках — **через сколько календарных дней** после даты заказа ожидается поставка.

---

## Архитектура

```
browser → dash (8050) → api (8000) → postgres (5432)
```

| Компонент | Назначение |
|-----------|------------|
| `dash/` | SPA: авторизация, календарь даты заказа, тепловая карта. Обновление матрицы при входе и при смене даты. Стили календаря: [`dash/dashboard/assets/custom.css`](dash/dashboard/assets/custom.css). |
| `backend/` | FastAPI: JWT, эндпоинты матрицы и вспомогательного ряда по одной паре part/region. |
| `docker-compose.yml` | Сервисы `db` (PostgreSQL 16), `api`, `dash`. |

---

## Каталоги

**Регионы (строки матрицы), в порядке отображения:** China, USA, India, Turkey, Russia.

**Запчасти (столбцы):** `brake_pad`, `oil_filter`, `spark_plug`, `timing_belt`, `battery`, `radiator_hose`, `wiper_blade`, `air_filter`, `cabin_filter`, `alternator`, `starter`, `fuel_filter`, `shock_absorber`, `wheel_bearing`, `cv_joint`, `clutch_disc`, `thermostat`, `water_pump`, `ignition_coil`, `lambda_sensor` (всего 20 позиций).

---

## API (v1)

| Метод | Описание |
|-------|----------|
| `GET /api/v1/health` | Healthcheck. |
| `POST /auth/register` | Регистрация. |
| `POST /auth/token` | OAuth2 password flow → JWT. |
| `GET /auth/me` | Профиль текущего пользователя (Bearer). |
| `GET /api/v1/timeseries/sources` | Список **запчастей** (публично). |
| `GET /api/v1/timeseries/regions` | Список **регионов** (публично). |
| `GET /api/v1/timeseries?part=&region=&days=` | Синтетический ряд «обещанный lead time» по дням для одной пары (Bearer). |
| `POST /api/v1/timeseries/forecast` | Тело JSON: опционально `anchor_date` (если нет — используется сегодня). Ответ: `anchor_date`, `matrix` с полями `parts`, `regions`, `lead_days` — матрица целых **дней до поставки** от даты заказа (Bearer). |
| `GET /api/v1/timeseries/admin/recent` | Последние обращения к API (только роль `admin`). Для запроса матрицы: `source = parts_delivery`, поле `days` хранит внутренний числовой индекс даты заказа (служебная кодировка для логов). |

Подробная схема запросов/ответов: http://localhost:8000/docs после запуска API.

---

## Запуск через docker-compose

```bash
docker compose up --build
```

- API: http://localhost:8000/docs  
- Dash: http://localhost:8050  

Переменные окружения задаются в [`docker-compose.yml`](docker-compose.yml) (`DATABASE_URL`, `JWT_SECRET`, `API_BASE_URL` для dash).

---

## Локальный запуск без Docker

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="sqlite:///./app.db"
export JWT_SECRET="dev"
uvicorn app.main:app --reload
```

### Dash

```bash
cd dash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export API_BASE_URL=http://localhost:8000
python app.py
```

---

## Тесты

```bash
cd backend
source .venv/bin/activate
pytest
```

Используются `pytest` и `pytest-cov` (см. [`backend/pytest.ini`](backend/pytest.ini)).

---

## Демо-сценарий (UI)

1. Открыть http://localhost:8050.
2. В блоке **Authentication** ввести логин/пароль, при необходимости **Register**, затем **Login**.
3. Выбрать **день заказа** в календаре (крестик сбрасывает дату — тогда для расчёта берётся сегодня). После входа матрица подгружается сама; при смене даты запрос к API выполняется снова.
4. На тепловой карте: по оси Y — страны из каталога, по оси X — запчасти; в ячейках и в цветовой шкале — **дни до поставки**.

---

## Структура репозитория (фрагмент)

```
backend/
├── app/
│   ├── api/v1/{health,auth,timeseries}.py
│   ├── auth/{security,dependencies}.py
│   ├── core/config.py
│   ├── db/{base,session}.py
│   ├── models/{user,timeseries_request}.py
│   ├── schemas/{auth,timeseries}.py
│   ├── services/timeseries.py    # каталоги + заглушка матрицы и ряда
│   └── main.py
├── alembic/
├── tests/
├── Dockerfile
└── requirements.txt

dash/
├── app.py
├── dashboard/
│   ├── index.py
│   ├── content.py
│   ├── api_client.py
│   ├── assets/custom.css         # вёрстка DatePickerSingle
│   └── layouts/
│       ├── pages/main_page.py
│       └── callbacks/graph_update.py
├── Dockerfile
└── requirements.txt
```

---
