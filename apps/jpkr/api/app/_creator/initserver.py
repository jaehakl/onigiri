from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import Base, engine
from dotenv import load_dotenv

from _creator.settings import settings
from user_auth.routes import router as auth_router


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
        "http://localhost:5173",
        settings.app_base_url
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    async def start():
        print("admin user id: ", settings.ADMIN_USER_ID)
        print("stable diffusion ckpt: ", settings.STABLE_DIFFUSION_CKPT)
        app.state.progress = 0
        Base.metadata.create_all(bind=engine)        
        app.include_router(auth_router)

        print("service is started.")

    def shutdown():
        print("service is stopped.")

    return app