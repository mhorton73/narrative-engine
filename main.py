
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router
from loader import load_story

app = FastAPI()
app.include_router(router)

app.state.story = load_story()
app.state.sessions = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

