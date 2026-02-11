import asyncio

from app.core.config import settings
from app.db.mongodb import get_client


SAMPLE_DISHES = [
    {
        "title": "Margherita Pizza",
        "description": "Classic pizza with tomato sauce, mozzarella and basil.",
        "price": 8.99,
        "image_url": "https://example.com/images/margherita.jpg",
        "category": "pizza",
        "rating": 4.7,
        "rating_count": 124,
        "restaurant_name": "Italiano Pizza",
    },
    {
        "title": "Pepperoni Pizza",
        "description": "Tomato sauce, mozzarella and spicy pepperoni.",
        "price": 9.99,
        "image_url": "https://example.com/images/pepperoni.jpg",
        "category": "pizza",
        "rating": 4.8,
        "rating_count": 210,
        "restaurant_name": "Italiano Pizza",
    },
    {
        "title": "Cheeseburger",
        "description": "Grilled beef patty with cheddar, lettuce and tomato.",
        "price": 7.49,
        "image_url": "https://example.com/images/cheeseburger.jpg",
        "category": "burgers",
        "rating": 4.5,
        "rating_count": 98,
        "restaurant_name": "Burger House",
    },
    # ... здесь по аналогии можно добавить ещё 30–60 блюд разных категорий
]


async def main() -> None:
    client = get_client()
    db = client[settings.db_name]
    col = db["dishes"]
    await col.delete_many({})
    await col.insert_many(SAMPLE_DISHES)
    print(f"Inserted {len(SAMPLE_DISHES)} dishes")


if __name__ == "__main__":
    asyncio.run(main())




