import logging.config
from typing import Optional

from opentelemetry.metrics import get_meter
from fastapi import Request, Header
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.propagate import extract
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from starlette.middleware.cors import CORSMiddleware

from common.Auth import MyAuth, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_active_user, \
    authenticate_user, Token
from common.Lib import Lib
from handlers.account_handler import AccountHandler
from models.Account import Account
from models.Transaction import Transaction
from models.User import User
from handlers.user_handler import UserHandler

from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "gojenga"})
    )
)
tracer = trace.get_tracer(__name__)

meter = get_meter(__name__)

# create a JaegerExporter
jaeger_exporter = JaegerExporter(
    # configure agent
    agent_host_name='localhost',
    agent_port=6831,
    # optional: configure also collector
    # collector_endpoint='http://localhost:14268/api/traces?format=jaeger.thrift',
    # username=xxxx, # optional
    # password=xxxx, # optional
    # max_tag_value_length=None # optional
)
# Create a BatchSpanProcessor and add the exporter to it
span_processor = BatchSpanProcessor(jaeger_exporter)

# add to the tracer
trace.get_tracer_provider().add_span_processor(span_processor)

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

my_auth: MyAuth = MyAuth()


@app.get("/hello", tags=["Debug"])
async def hello():
    return {"message": 'hiya'}


@app.post("/login", response_model=Token, tags=["Login"])
async def login_for_access_token(request: Request, is_test: Optional[bool] | None = Header(default=False),
                                 form_data: OAuth2PasswordRequestForm = Depends()):
    with tracer.start_as_current_span(
            "login",
            context=extract(request.headers),
            attributes={'form_data': form_data, 'is_test': is_test},
            kind=trace.SpanKind.SERVER
    ):
        table_name: str = 'users'
        if is_test:
            table_name = 'usersTest'
        user = authenticate_user(table_name, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["name"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user/{username}", tags=["User"])
async def get_user(request: Request, username: str, is_test: Optional[bool] | None = Header(default=False),
                   current_user: User = Depends(get_current_active_user)):
    with tracer.start_as_current_span(
            "get_user",
            context=extract(request.headers),
            attributes={'attr.username': username, 'attr.is_test': is_test},
            kind=trace.SpanKind.SERVER
    ):
        if Lib.detect_special_characters(username):
            raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail='please send legal username')
        try:
            print(f'--> the oauth user {current_user}')
            user = UserHandler.handle_get_user(username, is_test)
            return {"response": user}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/user", tags=["User"])
async def post_user(request: Request, data: User, is_test: Optional[bool] | None = Header(default=False)):
    with tracer.start_as_current_span(
            "post_user",
            context=extract(request.headers),
            attributes={'attr.username': data.name, 'attr.is_test': is_test},
            kind=trace.SpanKind.SERVER
    ):
        try:
            if Lib.detect_special_characters(data.name):
                raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail='please send legal username')

            resp = UserHandler.handle_create_user(data.name, data.password, is_test)
            return {"response": resp}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.put("/user/{username}", tags=["User"])
async def put_user(request: Request, username: str, data: User, is_test: Optional[bool] | None = Header(default=False)):
    with tracer.start_as_current_span(
            "put_user",
            context=extract(request.headers),
            attributes={'username': username, 'attr.is_test': is_test},
            kind=trace.SpanKind.SERVER
    ):
        if Lib.detect_special_characters(username):
            raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail='please send legal username')
        try:
            resp = UserHandler.handle_update_user(username, data.password, is_test)
            return {"response": resp}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.delete("/user/{username}", tags=["User"])
async def delete_user(request: Request, username: str, is_test: Optional[bool] | None = Header(default=False)):
    with tracer.start_as_current_span(
            "delete_user",
            context=extract(request.headers),
            attributes={'username': username, 'is_test': is_test},
            kind=trace.SpanKind.SERVER
    ):
        if Lib.detect_special_characters(username):
            raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail='please send legal username')
        try:
            resp = UserHandler.handle_delete_user(username, is_test)
            return {"response": resp}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/account/{username}", tags=["Account"])
async def get_user(request: Request, username: str, is_test: Optional[bool] | None = Header(default=False)):
    with tracer.start_as_current_span(
            "get_account",
            context=extract(request.headers),
            attributes={'attr.username': username, 'attr.is_test': is_test},
            kind=trace.SpanKind.SERVER
    ):
        if Lib.detect_special_characters(username):
            raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail='please send legal username')
        try:
            account = AccountHandler.handle_get_account(username, is_test)
            return {"response": account}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/account", tags=["Account"])
async def post_account(request: Request, data: Account, is_test: Optional[bool] | None = Header(default=False)):
    with tracer.start_as_current_span(
            "post_account",
            context=extract(request.headers),
            attributes={'attr.username': data.name, 'attr.is_test': is_test},
            kind=trace.SpanKind.SERVER
    ):
        try:
            if Lib.detect_special_characters(data.name):
                raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail='please send legal username')

            resp = AccountHandler.handle_create_account(data.name, data.balance, is_test)
            return {"response": resp}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.put("/account/{username}", tags=["Account"])
async def put_user(request: Request, username: str, data: Account,
                   is_test: Optional[bool] | None = Header(default=False)):
    with tracer.start_as_current_span(
            "put_user",
            context=extract(request.headers),
            attributes={'username': username, 'attr.is_test': is_test},
            kind=trace.SpanKind.SERVER
    ):
        if Lib.detect_special_characters(username):
            raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail='please send legal username')
        try:
            resp = AccountHandler.handle_update_account(username, data.balance, is_test)
            return {"response": resp}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.delete("/account/{username}", tags=["Account"])
async def delete_user(request: Request, username: str, is_test: Optional[bool] | None = Header(default=False)):
    with tracer.start_as_current_span(
            "delete_account",
            context=extract(request.headers),
            attributes={'username': username, 'is_test': is_test},
            kind=trace.SpanKind.SERVER
    ):
        if Lib.detect_special_characters(username):
            raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail='please send legal username')
        try:
            resp = AccountHandler.handle_delete_account(username, is_test)
            return {"response": resp}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/deposit", tags=["Deposit"])
async def post_deposit(request: Request, data: Account, is_test: Optional[bool] | None = Header(default=False)):
    with tracer.start_as_current_span(
            "post_deposit",
            context=extract(request.headers),
            attributes={'attr.username': data.name, 'attr.is_test': is_test},
            kind=trace.SpanKind.SERVER
    ):
        try:
            if Lib.detect_special_characters(data.name):
                raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail='please send legal username')

            resp = AccountHandler.handle_modify_account(data.name, data.balance, is_test)
            return {"response": resp}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/transaction", tags=["Transaction"])
async def post_account(request: Request, data: Transaction, is_test: Optional[bool] | None = Header(default=False)):
    with tracer.start_as_current_span(
            "post_transaction",
            context=extract(request.headers),
            attributes={'attr.data': data, 'attr.is_test': is_test},
            kind=trace.SpanKind.SERVER
    ):
        try:
            if Lib.detect_special_characters(data.sender) or Lib.detect_special_characters(data.receiver):
                raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT,
                                    detail='please send legal sender and receiver')

            resp = AccountHandler.handle_transaction(data.sender, data.receiver, data.amount, is_test)
            return {"response": resp}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


FastAPIInstrumentor.instrument_app(app)
