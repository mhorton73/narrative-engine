
from fastapi import APIRouter, Request
from uuid import uuid4
import os, json, re

from models import Character, Stats
from engine import apply_effect, resolve_next

# Save file validation

BASE_DIR = os.path.abspath("saves")

def sanitize_save_name(save_name: str) -> str:
    save_name = save_name.strip().lower()

    # allow only safe characters
    if not re.match(r"^[a-z0-9_-]+$", save_name):
        raise ValueError("Invalid save name")

    if len(save_name) > 32:
        raise ValueError("Save name too long")

    return save_name

def save_path(save_name: str):
    path = os.path.abspath(os.path.join(BASE_DIR, f"{save_name}.json"))

    if not os.path.commonpath([path, BASE_DIR]) == BASE_DIR:
        raise ValueError("Invalid path")
    return path

# API endpoints

router = APIRouter()

@router.post("/start")
def start_game(request: Request):
    session_id = str(uuid4())

    story = request.app.state.story

    state = Character(
        name="Player",
        rpgClass="Adventurer",
        stats=Stats(strength=3, dexterity=3, intelligence=3, faith=3),
        current_node="start"
    )

    request.app.state.sessions[session_id] = state

    node = story[state.current_node]

    return {
        "session_id": session_id,
        "node": node.model_dump(),
        "state": state.model_dump()
    }

@router.post("/load/{save_name}")
def load_game(save_name: str, session_id: str, request: Request):
    save_name = sanitize_save_name(save_name)
    story = request.app.state.story
    path = save_path(save_name)

    with open(path) as f:
        data = json.load(f)

    state = Character(**data)

    request.app.state.sessions[session_id] = state

    node = story[state.current_node]

    return {
        "session_id": session_id,
        "node": node.model_dump(),
        "state": state.model_dump()
    }

@router.post("/save/{save_name}")
def save_game(save_name: str, session_id: str, request: Request):
    save_name = sanitize_save_name(save_name)

    state = request.app.state.sessions[session_id]
    if not state:
        raise ValueError("Invalid session")
    
    os.makedirs("saves", exist_ok=True)
    path = save_path(save_name)

    with open(path, "w") as f:
        f.write(state.model_dump_json())

    return {"status": "saved", "file": path}

@router.delete("/save/{save_name}")
def delete_save(save_name: str):
    save_name = sanitize_save_name(save_name)
    path = save_path(save_name)

    if os.path.exists(path):
        os.remove(path)

    return {"status": "deleted"}

@router.post("/choose")
def choose(session_id: str, choice_index: int, request: Request):

    story = request.app.state.story
    state = request.app.state.sessions[session_id]
    if not state:
        raise ValueError("Invalid session")

    node = story[state.current_node]
    if choice_index < 0 or choice_index >= len(node.choices):
        raise ValueError("Invalid choice index")
    choice = node.choices[choice_index]

    apply_effect(node.effects, state)

    next_node = resolve_next(choice, state)
    state.current_node = next_node

    is_end = len(story[next_node].choices) == 0

    return {
        "node": story[next_node].model_dump(),
        "state": state.model_dump(),
        "is_end": is_end
    }

@router.post("/autosave")
def autosave(session_id :str, request: Request):
    
    state = request.app.state.sessions[session_id]
    if not state:
        raise ValueError("Invalid session")
    
    path = os.path.join(BASE_DIR, "autosave.json")
    with open(path, "w") as f:
        f.write(state.model_dump_json())

    return{"status": "autosaved"}


@router.post("/close-session")
def close_session(session_id: str, request: Request):
    sessions = request.app.state.sessions

    state = sessions.pop(session_id, None)

    if not state:
        return {"status": "session_not_found"}

    return {"status": "closed"}