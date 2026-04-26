
from schemas import Choice, Condition, Effect, StoryItem, SkillCheck
from models import Character

# --------- CONDITION CHECK ---------
def check_condition(condition: Condition, state: Character):
    def check_item(item: StoryItem):
        if item.type == "item":
            return item.key in state.inventory
        elif item.type == "flag":
            return item.key in state.flags
        elif item.type == "spell":
            return item.key in state.spells
        return False

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
    for item in effect.add:
        if item.type == "item":
            state.inventory.append(item.key)
        elif item.type == "flag":
            state.flags.append(item.key)
        elif item.type == "spell":
            state.spells.append(item.key)


    for item in effect.remove:
        if item.type == "item" and item.key in state.inventory:
            state.inventory.remove(item.key)
        elif item.type == "flag" and item.key in state.flags:
            state.flags.remove(item.key)
        elif item.type == "spell" and item.key in state.spells:
            state.spells.remove(item.key)

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

