from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dijon.routers import (
    changes,
    formats,
    login,
    meetings,
    naws_codes,
    root_servers,
    service_bodies,
    snapshots,
    users,
)


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(changes.router)
app.include_router(formats.router)
app.include_router(login.router)
app.include_router(meetings.router)
app.include_router(naws_codes.router)
app.include_router(root_servers.router)
app.include_router(service_bodies.router)
app.include_router(snapshots.router)
app.include_router(users.router)
