from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from db import Base, engine
from fastapi.staticfiles import StaticFiles
import os

def server():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # When service starts.
        await start()
    
        yield
        
        # When service is stopped.
        shutdown()

    app = FastAPI(lifespan=lifespan)

    origins = [
        "http://localhost",
        "http://localhost:5173"
    ]


    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    async def start():
        app.state.progress = 0
        #async with engine.begin() as conn:
        #    await conn.run_sync(Base.metadata.create_all)

        print("service is started.")

    def shutdown():
        print("service is stopped.")

    return app
