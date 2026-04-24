import json, os
from schemas import Node, Choice, Condition, Effect, StoryItem, SkillCheck
from models import Character


# Validation

def validate_story(story: dict):
    errors = []

    for node_id, node in story.items():

        # check choices exist
        if node.choices is None:
            errors.append(f"{node_id}: choices is None")

        for i, choice in enumerate(node.choices):
            label = f"{node_id} -> choice[{i}]"

            # check normal next_node
            if choice.next_node:
                if choice.next_node not in story:
                    errors.append(f"{label}: next_node '{choice.next_node}' not found")

            # check skill check paths
            if choice.skill_check:
                if not choice.success_node or not choice.failure_node:
                    errors.append(f"{label}: skill_check missing success/failure nodes")

                else:
                    if choice.success_node not in story:
                        errors.append(f"{label}: success_node '{choice.success_node}' not found")

                    if choice.failure_node not in story:
                        errors.append(f"{label}: failure_node '{choice.failure_node}' not found")

    if errors:
        print("\n--- STORY VALIDATION ERRORS ---")
        for err in errors:
            print(err)
        raise ValueError("Story validation failed")

    print("Story validation passed.")

# --------- LOAD STORY ---------
def load_story(folder="story"):
    base_dir = os.path.dirname(__file__)  # folder where engine.py lives
    story_path = os.path.join(base_dir, folder)

    story = {}

    for filename in os.listdir(story_path):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(story_path, filename)

        with open(path) as f:
            raw = json.load(f)

        for node_id, node_data in raw.items():
            if node_id in story:
                raise ValueError(f"Duplicate node id: {node_id}")

            story[node_id] = Node(**node_data)

    validate_story(story)
    return story


# --------- CONDITION CHECK ---------
def check_condition(condition: Condition, state: Character):
    def check_item(item: StoryItem):
        if item.type == "item":
            return item.key in state.inventory
        elif item.type == "flag":
            return item.key in state.flags
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


    for item in effect.remove:
        if item.type == "item" and item.key in state.inventory:
            state.inventory.remove(item.key)
        elif item.type == "flag" and item.key in state.flags:
            state.flags.remove(item.key)

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


# --------- GAME LOOP ---------
def run_game():
    story = load_story()

    # initialize player
    state = Character(
        name="Player",
        rpgClass="Adventurer",
        stats={"strength": 3, "dexterity": 3, "intelligence": 3},
        current_node="start"
    )

    while True:
        node = story[state.current_node]

        print("\n" + node.text)

        # apply node effects
        apply_effect(node.effects, state)

        # filter choices
        available_choices = [
            c for c in node.choices
            if check_condition(c.condition, state)
        ]

        if not available_choices:
            print("\n[No more choices. Game over.]")
            break

        # display choices
        for i, choice in enumerate(available_choices):
            print(f"{i+1}. {choice.text}")

        # player input
        selection = int(input("> ")) - 1
        choice = available_choices[selection]

        # resolve next node
        next_node = resolve_next(choice, state)

        if not next_node:
            print("\n[No next node defined. Game over.]")
            break

        state.current_node = next_node

