
# Expected structure:

# choices:
#
# - Simple choice
# -> a_node_id
#
# - A choice with conditions
# requires: flag:a, item:b, item:c...
# excludes: flag:d, item:e, flag:f...
# -> another_node_id
#
# - Skill check 
# skill: strength:n
# -> (pass: success_id, fail: fail_id)
#
# - Example choice 
# requires: item:key, flag:knows_password
# excludes: flag:banned
# skill: intelligence:2 
# -> (pass: thieves_guild, fail: turned_away)

from parser.primitives import parse_item_key_pair, parse_skill_check


def split_choice_blocks(lines: list[str]) -> list[list[str]]:
    blocks = []
    current = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        current.append(line)

        if line.startswith("->"):
            blocks.append(current)
            current = []
            continue

    if current:
        blocks.append(current)

    return blocks

def parse_items(raw: str):
    items = []

    for pair in raw.split(","):
        if not pair:
            continue
        items.append(parse_item_key_pair(pair))

    return items

def parse_next_node_id(choice: dict, line: str):
    line = line.strip().removeprefix("-> ")

    # Case 1: simple node
    if not line.startswith("("):
        choice["next_node"] = line
        return

    # Case 2: skill check result
    # format: (pass: a, fail: b)
    content = line.strip("()")

    parts = content.split(",")
    for part in parts:
        key, value = part.split(":")
        key = key.strip()
        value = value.strip()

        if key == "pass":
            choice["success_node"] = value
        elif key == "fail":
            choice["failure_node"] = value


def parse_choice_block(block: list[str]) -> dict:
    choice = {
        "text": None,
        "requires": [],
        "excludes": [],
        "skill_check": None,
        "next_node": None,
        "success_node": None,
        "failure_node": None,
    }

    if not block[0].startswith("- "):
        raise ValueError(f"Invalid choice text format: {block[0]}")
    choice["text"] = block[0].removeprefix("- ")
    destination_line = None

    for line in block[1:]:
        if line.strip().startswith("->"):
            destination_line = line.strip()
            continue

        if line.startswith("requires:"):
            raw = line.replace("requires:", "").strip()
            choice["requires"] = parse_items(raw)

        elif line.startswith("excludes:"):
            raw = line.replace("excludes:", "").strip()
            choice["excludes"] = parse_items(raw)

        elif line.startswith("skill:"):
            raw = line.replace("skill:", "").strip()
            choice["skill_check"] = parse_skill_check(raw)

    if not destination_line:
        raise ValueError(f"No destination for {choice.text}")
    parse_next_node_id(choice, destination_line)

    return choice

def parse_choices(lines: list[str]):
    blocks = split_choice_blocks(lines)

    return [parse_choice_block(block) for block in blocks]