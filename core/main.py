from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from auth.jwt_auth import get_authenticated_user
from users.models import UserModel
from tasks.routes import router as tasks_routes
from users.routes import router as users_routes
from fastapi.middleware.cors import CORSMiddleware

tags_metadata = [
    {
        "name": "tasks",
        "description": "Operations related to task management",
        "externalDocs": {
            "description": "More about tasks",
            "url": "https://example.com/docs/tasks",
        },
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    yield
    print("Application shutdown")


app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)


app.include_router(tasks_routes)
app.include_router(users_routes)


@app.get("/public")
def public_route():
    return {"message": "This is a public route."}


@app.get("/private")
def private_route(current_user: UserModel = Depends(get_authenticated_user)):
    return {"message": "This is a private route."}


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # یا استفاده از متغیر origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    error_response = {
        "error": True,
        "status_code": exc.status_code,
        "detail": str(exc.detail),
    }
    return JSONResponse(status_code=exc.status_code, content=error_response)
