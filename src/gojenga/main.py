import logging

from fastapi import FastAPI, HTTPException, status

from storage.dynamo import get_item
from user.handler import get_user, create_user

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def get_user():
    try:
        user = get_user('david')
        return {"message": user}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

@app.post("/")
async def post_user():
    try:
        resp = create_user('david', 200)
        return {"message": resp}
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
