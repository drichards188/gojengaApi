import logging

from fastapi import FastAPI, HTTPException, status, Request
from opentelemetry.instrumentation.asgi import collect_request_attributes
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.propagate import extract

from models.User import User
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "gojenga"})
    )
)
tracer = trace.get_tracer(__name__)

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

from storage.dynamo import get_item
from user.handler import handle_get_user, handle_create_user, handle_update_user

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/user/{username}")
async def get_user(request: Request, username: str):
    with tracer.start_as_current_span(
            "server_request",
            context=extract(request.headers),
            kind=trace.SpanKind.SERVER
    ):
        try:
            user = handle_get_user(username)
            return {"response": user}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/user")
async def post_user(request: Request, data: User):
    with tracer.start_as_current_span(
            "server_request",
            context=extract(request.headers),
            kind=trace.SpanKind.SERVER
    ):
        try:
            resp = handle_create_user(data.name, data.password)
            return {"response": resp}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.put("/user/{username}")
async def put_user(request: Request, username: str, data: User):
    with tracer.start_as_current_span(
            "server_request",
            context=extract(request.headers),
            kind=trace.SpanKind.SERVER
    ):
        try:
            resp = handle_update_user(username, data.password)
            return {"response": resp}
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# todo test endpoints

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"response": f"Hello {name}"}


FastAPIInstrumentor.instrument_app(app)
