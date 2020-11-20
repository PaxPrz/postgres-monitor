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
from postgres_monitor.core.query import (datname_query, stat_query, db_list_query, all_stat_query)

config = Config('postgres_monitor/.env')
DATABASE_URL = config('DATABASE_URL')

conn = None
SLEEP_TIME = 2

templates = Jinja2Templates(directory='postgres_monitor/templates')

def sanitize_input(data):
    return re.sub(r"[^a-zA-Z0-9-_ ]", "", data)

async def get_db_gen(database_name='ALL'):
    json_data = {}
    while True:
        if database_name in ('ALL',''):
            data = await conn.fetch(all_stat_query)
        else:
            data = await conn.fetch(stat_query.format(datname=database_name))
        for row in data:
            json_data.update({row.get('chart_name'):row.get('chart_data')})
        yield json.dumps(json_data)
        await asyncio.sleep(SLEEP_TIME)

async def get_specific_db(request):
    db_name = sanitize_input(request.path_params['database'])
    if db_name in ('ALL', ''):
        return EventSourceResponse(get_db_gen())
    else:
        return EventSourceResponse(get_db_gen(database_name=db_name))

async def get_db_name(request):
    row = await conn.fetchrow(datname_query.format(oid=16384))
    return JSONResponse(dict(row.items()))

async def get_db_list(request):
    rows = await conn.fetch(db_list_query)
    dbs = ['ALL']
    for row in rows:
        db = row.get('datname')
        if db:
            dbs.append(db)
    return JSONResponse(dbs)

async def get_db_stats(request):
    return EventSourceResponse(get_db_gen())

async def homepage(request):
    return templates.TemplateResponse('index.html', {'request':request})

ROUTES = [
    Route('/', homepage),
    Route('/db/{database:str}', get_specific_db),
    Route('/stats', get_db_stats),
    Route('/name', get_db_name),
    Route('/dblist', get_db_list),
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