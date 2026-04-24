
from pydantic import BaseModel, Field
from typing import List

STARTER_HP = 10

class Stats(BaseModel):
    
    strength: int
    dexterity: int
    intelligence: int
    faith: int

class Character(BaseModel):
    
    name: str
    rpgClass: str

    stats: Stats = Field(default_factory=Stats)
    hp: int = STARTER_HP
    max_hp: int = STARTER_HP
    gold: int = 0

    inventory: List[str] = Field(default_factory=list)
    flags: List[str] = Field(default_factory=list)

    current_node: str

