
from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum

class Stat(str, Enum):
    strength = "strength"
    dexterity = "dexterity"
    intelligence = "intelligence"
    faith = "faith"

class StoryItem(BaseModel):
    key: str
    type: Literal["item", "flag"]

class StatChange(BaseModel):
    stat: Stat
    delta: int

# Write only
class Effect(BaseModel):
    add: List[StoryItem] = Field(default_factory=list)
    remove: List[StoryItem] = Field(default_factory=list)
    gold_change: int = 0 
    stat_change: List[StatChange] = Field(default_factory=list)

# Read only
class Condition(BaseModel):
    required: List[StoryItem] = Field(default_factory=list)
    excluded: List[StoryItem] = Field(default_factory=list)

class SkillCheck(BaseModel):
    stat: Stat
    difficulty: int

class Choice(BaseModel):
    text: str
    condition: Condition = Field(default_factory=Condition)
    
    next_node: str | None = None
    skill_check: SkillCheck | None = None
    success_node: str | None = None
    failure_node: str | None = None

class Node(BaseModel):
    id: str
    text: str
    effects: Effect = Field(default_factory=Effect)
    choices: List[Choice]
