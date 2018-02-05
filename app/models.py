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

async def fetch_user(email):
	result = await fetch_row('SELECT * FROM details WHERE email = $1', email)
	if result is None:
		return None
	result = dict(result)
	return User(id=result['id'], email=result['email'])
	

class User():
	def __init__(self, id, email):
		self.id = id
		self.email = email
	
	@classmethod
	async def new_user(cls,email,password):
		await execute_job('INSERT INTO details (email,password) VALUES ($1,$2)', email, password)
		id = dict(await fetch_row('SELECT * FROM details WHERE email=$1 AND password = $2', email, password))['id']
		return cls(id, email)
		

		
	


		
