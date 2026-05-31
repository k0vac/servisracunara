from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from routers import auth, cases, inventory

app = FastAPI(title="Servis Racunara API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(inventory.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
