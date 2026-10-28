from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from tasks.routes import router as tasks_routes
from users.routes import router as users_routes

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


app = FastAPI(
    lifespan=lifespan,
    openapi_tags=tags_metadata
)


app.include_router(tasks_routes)
app.include_router(users_routes)

# header_schema = APIKeyHeader(name="x-key")
security = HTTPBearer(scheme_name="token")

@app.get("/public")
def public_route():
    return {"message": "This is a public route."}


@app.get("/private")
def private_route(credentials:HTTPAuthorizationCredentials = Depends(security)):
    print(credentials)
    return {"message": "This is a private route."}
