from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dijon.routers import login, root_servers, users


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(login.router)
app.include_router(root_servers.router)
app.include_router(users.router)
