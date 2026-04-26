
from schemas import Choice, Condition, Effect, StoryItem, SkillCheck
from models import Character

def get_collections(state: Character):
    return {
        "item": state.inventory,
        "flag": state.flags,
        "spell": state.spells,
    }

# --------- CONDITION CHECK ---------
def check_condition(condition: Condition, state: Character):
    
    collections = get_collections(state)

    def check_item(item: StoryItem):
        collection = collections.get(item.type)
        if collection is None:
            raise ValueError(f"Unknown StoryItem type: {item.type}")
        return item.key in collection

    # required
    for item in condition.required:
        if not check_item(item):
            return False

    # excluded
    for item in condition.excluded:
        if check_item(item):
            return False

    return True


# --------- APPLY EFFECT ---------
def apply_effect(effect: Effect, state: Character):
    
    collections = get_collections(state)
    for item in effect.add:
        collection = collections.get(item.type)
        if collection is None:
            raise ValueError(f"Unknown StoryItem type: {item.type}")
        collection.append(item.key)


    for item in effect.remove:
        collection = collections.get(item.type)
        if collection is None:
            raise ValueError(f"Unknown StoryItem type: {item.type}")
        if item.key in collection:
            collection.remove(item.key)
            
    state.gold += effect.gold_change

    for s in effect.stat_change:
        current_value = getattr(state.stats, s.stat.value)
        setattr(state.stats, s.stat.value, max(0, current_value + s.delta))


# Skill Check

def resolve_skill_check(skill_check: SkillCheck, state: Character):
    stat_value = getattr(state.stats, skill_check.stat.value)
    return stat_value >= skill_check.difficulty

# --------- RESOLVE NEXT NODE ---------
def resolve_next(choice: Choice, state: Character):
    if choice.skill_check:
        if resolve_skill_check(choice.skill_check, state): 
            return choice.success_node 
        else:
            return choice.failure_node

    return choice.next_node

