# SwiftEats Backend (FastAPI + MongoDB Atlas)

Backend для iOS‑приложения SwiftEats (SwiftUI). Реализованы:

- регистрация / логин (JWT)
- каталог блюд (поиск / категории / сортировка)
- избранное
- корзина (полный CRUD на сервере)
- оформление заказа (checkout → order)
- история заказов
- трекинг заказа (симуляция статусов по времени)

## Требования

- Python 3.11+
- MongoDB Atlas (или любой совместимый MongoDB URI)

## Установка

```bash
cd /home/yerulan/Files/nativeka
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка `.env`

Создай файл `.env` в корне проекта со значениями (пример):

```env
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=swifteats

JWT_SECRET=super-secret-key-change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

CORS_ORIGINS=*

DELIVERY_FEE=5.0
FREE_DELIVERY_THRESHOLD=25.0
TRACKING_ETA_SECONDS=60
```

## Запуск сервера

Из корня проекта:

```bash
uvicorn app.main:app --reload
```

Документация FastAPI:

- Swagger UI: `http://127.0.0.1:8000/api/docs`
- OpenAPI: `http://127.0.0.1:8000/api/v1/openapi.json`

## Seed тестовых данных (dishes)

После настройки `.env` можно засеять тестовые блюда:

```bash
python -m scripts.seed
```

После этого `GET /api/v1/dishes` будет возвращать список блюд.

## Основные роуты

Все роуты под префиксом `/api/v1`.

### Auth

- **POST** `/api/v1/auth/register`
  - Body: `{"name","email","password"}`
  - Ответ: `{"id","name","email"}`

- **POST** `/api/v1/auth/login`
  - Body: `{"email","password"}`
  - Ответ: `{"access_token","token_type":"bearer"}`

- **GET** `/api/v1/auth/me`
  - Header: `Authorization: Bearer <token>`
  - Ответ: `{"id","name","email"}`

### Categories

- **GET** `/api/v1/categories`
  - Ответ: `{"items":[...category_strings...]}` — берётся из `dishes.category (distinct)`

### Dishes

- **GET** `/api/v1/dishes`
  - Query:
    - `q` — поиск по title (case-insensitive)
    - `category`
    - `sort` = `popular|rating|price_asc|price_desc`
    - `page` (default 1)
    - `limit` (default 20)
  - Ответ:
    - `{"items":[Dish], "page", "limit", "total", "pages"}`

- **GET** `/api/v1/dishes/{id}`
  - Ответ: `Dish`

### Favorites (требует JWT)

Header: `Authorization: Bearer <token>`

- **GET** `/api/v1/favorites`
  - Ответ: `{"dish_ids":[string]}`

- **POST** `/api/v1/favorites/{dish_id}`
  - Toggle: если блюдо уже в избранном — удаляет, иначе добавляет.
  - Ответ: `{"dish_ids":[string]}`

- **DELETE** `/api/v1/favorites/{dish_id}`
  - Удаляет блюдо из избранного.
  - Ответ: `{"dish_ids":[string]}`

### Cart (FULL CRUD, требует JWT)

- **GET** `/api/v1/cart`
  - Ответ:
    ```json
    {
      "items": [...],
      "subtotal": 0,
      "delivery_fee": 0,
      "total": 0
    }
    ```

- **POST** `/api/v1/cart/items`
  - Body: `{"dish_id","qty":1}`
  - Логика:
    - если блюдо уже в cart → увеличивает qty
    - иначе добавляет новый item с snapshot полями
  - Ответ: полный cart

- **PUT** `/api/v1/cart/items/{dish_id}`
  - Body: `{"qty"} (>=1)`
  - Ответ: полный cart

- **DELETE** `/api/v1/cart/items/{dish_id}`
  - Удаляет позицию.
  - Ответ: полный cart

- **DELETE** `/api/v1/cart`
  - Очищает корзину.
  - Ответ: пустой cart (но с подсчитанными totals).

Тоталы считаются по правилам из ТЗ:

- `subtotal = sum(price_snapshot * qty)`
- `delivery_fee = 0`, если `subtotal >= FREE_DELIVERY_THRESHOLD`, иначе `DELIVERY_FEE`, либо 0 при пустой корзине.
- `total = subtotal + delivery_fee`

### Orders + Checkout (JWT)

- **POST** `/api/v1/orders`
  - Body (CheckoutRequest):
    ```json
    {
      "address": "string",
      "delivery_time": "ASAP",
      "leave_at_door": true,
      "courier_note": "optional",
      "payment_method": "card",
      "promo_code": "optional"
    }
    ```
  - Логика:
    1. Берётся cart пользователя.
    2. Если корзина пустая → 400.
    3. Создаётся order со snapshot items и totals.
    4. `status = "ordered"`.
    5. `tracking_started_at = now`, `eta_seconds = TRACKING_ETA_SECONDS`.
    6. Cart очищается.
  - Ответ:
    ```json
    {
      "id": "...",
      "status": "ordered",
      "created_at": "...",
      "total": 12.34,
      "eta_seconds": 60
    }
    ```

- **GET** `/api/v1/orders`
  - Ответ:
    ```json
    {
      "items": [
        {
          "id": "...",
          "status": "ordered",
          "created_at": "...",
          "total": 12.34,
          "items_count": 3,
          "restaurant_name_preview": "из первого item"
        }
      ]
    }
    ```

- **GET** `/api/v1/orders/{id}`
  - Ответ: полный order (items + totals + address + status и т.д.)

- **PATCH** `/api/v1/orders/{id}/cancel`
  - Если уже `delivered` → `409`.
  - Иначе `status = "canceled"`.
  - Ответ: `{id,status,created_at,total,eta_seconds}` (в формате `OrderCreatedResponse`).

### Tracking (JWT)

- **GET** `/api/v1/orders/{id}/tracking`
  - Ответ:
    ```json
    {
      "order_id": "...",
      "status": "preparing|on_way|arriving|delivered|canceled",
      "progress": 0.0,
      "eta_remaining_seconds": 42,
      "steps": [
        {"name": "ordered", "completed": true},
        {"name": "preparing", "completed": true},
        ...
      ]
    }
    ```
  - Логика по времени:
    - `canceled` → всегда canceled.
    - `elapsed < 15s` → `preparing`.
    - `15–50` → `on_way`.
    - `50–60` → `arriving`.
    - `>=60` → `delivered`, `progress = 1`.

## Формат ошибок

Все ошибки приходят в формате:

```json
{
  "detail": {
    "code": "some_code",
    "message": "Human readable message",
    "details": {...optional...}
  }
}
```

## Пример тестового аккаунта

Через Swagger (`/api/docs`) или Postman:

1. Вызвать `POST /api/v1/auth/register`:
   ```json
   {
     "name": "Test User",
     "email": "test@test.com",
     "password": "test123456"
   }
   ```
2. Потом войти через `POST /api/v1/auth/login` и использовать `access_token` в `Authorization: Bearer <token>` для всех защищённых роутов.

