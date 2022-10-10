from motor.motor_asyncio import AsyncIOMotorClient


def create_client(db_url: str) -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(db_url)
    return client


