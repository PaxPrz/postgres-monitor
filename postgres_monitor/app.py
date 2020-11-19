from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.config import Config
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
import json
import asyncpg
import asyncio
import re

config = Config('postgres_monitor/.env')
DATABASE_URL = config('DATABASE_URL')
DATABASE = config('DATABASE')
conn = None
SLEEP_TIME = 2

templates = Jinja2Templates(directory='postgres_monitor/templates')

datname_query = 'SELECT datname FROM pg_database WHERE oid = {oid}'

stat_query = '''SELECT 'session_stats' AS chart_name, row_to_json(t) AS chart_data  
  FROM (SELECT 
    (SELECT count(*) FROM pg_stat_activity WHERE datname = '{datname}') AS "Total",
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND datname = '{datname}')  AS "Active", 
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle' AND datname = '{datname}')  AS "Idle"
  ) t
  UNION ALL
  SELECT 'tps_stats' AS chart_name, row_to_json(t) AS chart_data 
  FROM (SELECT 
    (SELECT sum(xact_commit) + sum(xact_rollback) FROM pg_stat_database WHERE datname = '{datname}') AS "Transactions",
    (SELECT sum(xact_commit) FROM pg_stat_database WHERE datname = '{datname}') AS "Commits",
    (SELECT sum(xact_rollback) FROM pg_stat_database WHERE datname = '{datname}') AS "Rollbacks"
 ) t;
 '''

def sanitize_input(data):
    return re.sub(r"[^a-zA-Z0-9 ]", "", data)

async def get_db_gen(database_name=DATABASE):
    json_data = {}
    while True:
        data = await conn.fetch(stat_query.format(datname=database_name))
        for row in data:
            json_data.update({row.get('chart_name'):row.get('chart_data')})
        yield json.dumps(json_data)
        await asyncio.sleep(SLEEP_TIME)

async def get_db_name(request):
    row = await conn.fetchrow(datname_query.format(oid=16384))
    return JSONResponse(dict(row.items()))

async def get_db_stats(request):
    return EventSourceResponse(get_db_gen())

async def homepage(request):
    return templates.TemplateResponse('index.html', {'request':request})

ROUTES = [
    Route('/', homepage),
    Route('/stats', get_db_stats),
    Route('/name', get_db_name),
    Mount('/static', StaticFiles(directory="postgres_monitor/templates/static"), name="static"),
]

app = Starlette(debug=True, routes=ROUTES)

@app.on_event("startup")
async def setup_database():
    global conn 
    conn = await asyncpg.connect(DATABASE_URL)
    print("Connection Setup successful")

@app.on_event("shutdown")
async def close_database():
    await conn.close()
    print("Connection closed")