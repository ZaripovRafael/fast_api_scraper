import uvicorn
from db import connect
from envparse import Env
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from sites_parser import gov_parser
from starlette.requests import Request

router = APIRouter()
env = Env()

MONGO_DB_URL = env.str("MONDO_DB_URL", default="mongodb://localhost:27017/parse_db")

DATA_PARSER = gov_parser.HtmlParser()

async def index() -> dict:
    return {"status": "ok"}

async def write_data(request: Request) -> dict:
    data = DATA_PARSER.create_data()
    mongo_client = request.app.state.mongo_client["parse_db"]
    await mongo_client.record.insert_one(data)
    return {"Sucess": True}

async def search(request: Request, search_data) -> dict:
    mongo_client = request.app.state.mongo_client["parse_db"]
    cursor = mongo_client.records.find({search_data})
    res: list = []
    for document in await cursor.to_list(length=100):
        document["_id"] = str(document["_id"])
        res.append(document)
    return res


routes = [
    APIRoute(path='/', endpoint=index, methods=["GET"]),
    APIRoute(path='/write_data', endpoint=write_data, methods=["POST"]),
    APIRoute(path='/search', endpoint=search, methods=["GET"]),
]

db_client = connect.create_client(MONGO_DB_URL)
app: FastAPI = FastAPI()
app.state.mongo_client = db_client
app.include_router(APIRouter(routes=routes))


if __name__ == "__main__":
    uvicorn.run(app=app, host="localhost", port=8000)
