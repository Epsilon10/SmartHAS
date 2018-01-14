from app import app
from motor.motor_asyncio import AsyncIOMotorClient

async def open_db(host, port):
	app.db = AsyncIOMotorClient(host=host, port=port)
	print(f'MongoDB connected on {host}:{port}')

async def unique_db(collection, data):
	return await collection.find({data:{'$exists': True}})

