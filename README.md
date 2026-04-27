# Narrative Engine (Markdown DSL + FastAPI)

A data-driven narrative engine powered by a custom Markdown-based DSL, built with FastAPI and Pydantic.

This project focuses on backend system design: parsing, validation, state management, and deterministic execution of branching logic.

## **Overview**

This engine allows stories to be written in a custom Markdown format, which are:

1. Parsed into structured data
2. Validated using strict schemas
3. Executed by a deterministic game engine
4. Exposed through a REST API

The result is a clean separation between content and logic.

## **Key Concepts:**

### Custom DSL (Domain-Specific Language)

Story content is defined using a purpose-built Markdown format:

```
id: start

## Text
You wake in a dark room.

## Effects
add: flag:awake
gold: 5

## Choices

- Open the door
-> hallway

- Search the room
requires: flag:awake
skill: intelligence:2
-> (pass: secret_room, fail: nothing)
```

This DSL supports:

Conditional choices (requires, excludes)
Skill checks with branching outcomes
State mutation (items, flags, stats, gold)

### Parsing Pipeline

The system uses a structured, multi-stage pipeline:

```
Markdown Files
    ↓
Primitive Parsers
    ↓
Choice / Node Parsers
    ↓
Structured Dictionaries
    ↓
Pydantic Validation
    ↓
Runtime Engine
```

This design allows:

- Flexible parsing with strict validation
- Early error detection
- Clean separation of responsibilities

### Engine (Core Logic)

The engine is responsible for:

* Evaluating conditions (inventory, flags, spells)
* Applying effects (state mutation)
* Resolving skill checks
* Determining node transitions

All logic is:

Deterministic
Stateless per request (state stored in session)
Fully decoupled from content format

### API Layer (FastAPI)

The engine is exposed via a REST API:

* Start a game: POST /start
* Make a choice: POST /choose?session_id=...&choice_index=...
* Save / Load: POST /save/{name}, POST /load/{name}
* Session management: POST /autosave, POST /close-session

### Data Model

Player State

* Stats: strength, dexterity, intelligence, faith
* Inventory system (items, flags, spells)
* Gold and HP
* Current story node

Story Structure

* Node → text + effects + choices
* Choice → condition + outcome
* Effect → state mutation
* Condition → gating logic
* SkillCheck → stat-based branching

All enforced via Pydantic schemas.

### Validation & Safety
Strong schema validation via Pydantic
Cross-node validation (ensures all references exist)
Input sanitisation for save files
Path traversal protection

### Project Structure
/parser     → Markdown → structured data

/story      → story content (DSL)

/frontend   → minimal UI

engine.py   → core logic

schemas.py  → validation layer

models.py   → player state

api.py      → REST endpoints

loader.py   → story loading + validation

### Running the Project

Run the backend:
```
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open the frontend with VSCode Live server.
You can also run a python server:
```
cd frontend
python -m http.server 5500
```

Or go to
```
http://127.0.0.1:8000/docs
```
