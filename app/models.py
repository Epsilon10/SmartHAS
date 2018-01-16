from app import app
from motor.motor_asyncio import AsyncIOMotorClient

async def open_db(host, port):
	motor_client = AsyncIOMotorClient(host=host, port=port)
	app.db = motor_client.smart_has
	print(f'MongoDB connected on {host}:{port}')

async def unique_db(collection,data):
	return await collection.distinct(data) != []

