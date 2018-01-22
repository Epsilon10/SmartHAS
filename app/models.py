from app import app
from motor.motor_asyncio import AsyncIOMotorClient

async def open_db(host, port):
	motor_client = AsyncIOMotorClient(host=host, port=port)
	app.db = motor_client.smarthas
	print(f'MongoDB connected on {host}:{port}')

async def unique_db(collection, data):
	return len(await collection.distinct(data)) != 0

async def update_db(collection, ref, data):
	await collection.update_one(ref, {'$set': data}, upsert=True)

