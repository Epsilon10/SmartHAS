from app import app
import asyncpg

async def open_db_pool(dsn):
	return await asyncpg.create_pool(dsn=dsn, user='moommen', command_timeout=60, loop=app.loop)

async def fetch_row(query, *args):
	args = list(args)
	con = await app.db_pool.acquire()
	async with con.transaction():
		row = await con.fetchrow(query, *args)
	await app.db_pool.release(con)
	return row

async def fetch_val(query, *args):
	args = list(args)
	con = await app.db_pool.acquire()
	async with con.transaction():
		value = await con.fetchval(query, *args)
	await app.db_pool.release(con)
	return value

async def fetch_many(query, *args):
	args = list(args)
	con = await app.db_pool.acquire()
	async with con.transaction():
		result = await con.fetch(query, *args)
	await app.db_pool.release(con)
	return result

async def execute_job(query, *args):
	args = list(args)
	con = await app.db_pool.acquire()
	async with con.transaction():
		await con.execute(query, *args)
	await app.db_pool.release(con)

