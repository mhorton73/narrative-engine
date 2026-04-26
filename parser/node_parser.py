
# Expected structure:

# node_id
# 
# ## Text
# text line 1
# text line 2
# ...
# text line last
# 
# ## Effects
# add: flag:a
# add: item:b
# remove: flag:c
# remove: item:d
# gold: n OR -n
# stat: stat_name:n OR -n
# 
# ## Choices
#
# list of choices (explained in choice_parser.py)

from parser.primitives import parse_item_key_pair, parse_stat_change
from parser.choice_parser import parse_choices

def parse_effects(lines: list[str]) -> dict:
    add = []
    remove = []
    gold_change = 0
    stat_change = []

    for line in lines:
        line = line.lstrip("- ").strip()

        # add_flag / add_item
        if line.startswith("add:"):
            pair = line.removeprefix("add:").strip()
            add.append(parse_item_key_pair(pair))

        # remove
        elif line.startswith("remove:"):
            pair = line.removeprefix("remove:").strip()
            remove.append(parse_item_key_pair(pair))

        # gold
        elif line.startswith("gold:"):
            gold_change = int(line.split(":")[1].strip())

        # stat
        elif line.startswith("stat:"):
            pair = line.removeprefix("stat:").strip()
            stat_change.append(parse_stat_change(pair))

    return {
        "add": add,
        "remove": remove,
        "gold_change": gold_change,
        "stat_change": stat_change
    }


def parse_markdown_node(content: str) -> dict:
    
    lines = [l.rstrip() for l in content.split("\n")]

    # Split into sections
    node_id = None
    text_lines = []
    effect_lines = []
    choice_lines = []

    mode = None

    for line in lines:
        stripped = line.strip()

        # preserve blank lines for text, but ditch them for other sections
        if not stripped:
            if mode == "text":
                text_lines.append("")
            continue
        if stripped.startswith("id:"):
            if node_id is not None:
                raise ValueError("Duplicate id in node")
            node_id = stripped.removeprefix("id:").strip()
            continue
        if stripped.startswith("## Text"):
            mode = "text"
            continue
        if stripped.startswith("## Effects"):
            mode = "effects"
            continue
        if stripped.startswith("## Choices"):
            mode = "choices"
            continue

        # some basic validation
        if mode == "effects" and not stripped.startswith(("add:", "remove:", "gold:", "stat:")):
            raise ValueError(f"Invalid effects line: {line}")
        if mode == "choices" and not stripped.startswith(("- ", "requires:", "excludes:", "skill:", "->")):
            raise ValueError(f"Invalid choices line: {line}")

        if mode == "text":
            text_lines.append(line)
        elif mode == "effects":
            effect_lines.append(stripped)
        elif mode == "choices":
            choice_lines.append(stripped)

    if node_id is None:
        raise ValueError("Missing id")

    if not text_lines:
        raise ValueError("Missing text")
    
    # Parse sections

    text = "\n".join(text_lines)
    effects = parse_effects(effect_lines)    
    choices = parse_choices(choice_lines)

    return {
        "id": node_id,
        "text": text,
        "choices": choices,
        "effects": effects
    }

