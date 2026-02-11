from motor.motor_asyncio import AsyncIOMotorDatabase


async def init_indexes(db: AsyncIOMotorDatabase) -> None:
    # users: email unique
    await db["users"].create_index("email", unique=True)

    # carts: one cart per user
    await db["carts"].create_index("user_id", unique=True)

    # favorites: one favorites doc per user
    await db["favorites"].create_index("user_id", unique=True)

    # dishes: category, title
    await db["dishes"].create_index("category")
    await db["dishes"].create_index("title")

    # orders: user_id + created_at
    await db["orders"].create_index([("user_id", 1), ("created_at", -1)])




