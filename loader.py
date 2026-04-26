
import os

from parser.node_parser import parse_markdown_node
from schemas import Node  # your Pydantic model

def validate_story(story: dict):
    errors = []

    for node_id, node in story.items():

        for i, choice in enumerate(node.choices):
            label = f"{node_id} -> choice[{i}]"

            # check normal next_node
            if choice.next_node:
                if choice.next_node not in story:
                    errors.append(f"{label}: next_node '{choice.next_node}' not found")
            
            if choice.next_node and choice.skill_check:
                errors.append(f"{label}: has both normal progression and skill check")

            # check skill check paths
            if choice.skill_check:
                if not choice.success_node or not choice.failure_node:
                    errors.append(f"{label}: skill_check missing success/failure nodes")

                else:
                    if choice.success_node not in story:
                        errors.append(f"{label}: success_node '{choice.success_node}' not found")

                    if choice.failure_node not in story:
                        errors.append(f"{label}: failure_node '{choice.failure_node}' not found")

            if not choice.skill_check:
                if choice.success_node or choice.failure_node:
                    errors.append(f"{label}: has success/failure without skill_check")
    if errors:
        raise ValueError(
            "\n--- STORY VALIDATION ERRORS ---\n" + "\n".join(errors)
        )
    print("Story validation passed.")

def resolve_id(folder: str, target: str) -> str:
    if ":" in target:
        return target  # already full

    # otherwise, add folder prefix
    
    return f"{folder}:{target}" if folder else target

def load_story(folder="story"):
    base_dir = os.path.dirname(__file__)
    story_path = os.path.join(base_dir, folder)

    story = {}

    for root, _, files in os.walk(story_path):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            path = os.path.join(root, filename)

            with open(path, encoding="utf-8") as f:
                content = f.read()

            try:
                raw_node = parse_markdown_node(content)
                node = Node(**raw_node)
            except Exception as e:
                raise ValueError(f"Error in file {path}: {e}")

            # Add folder prefix to id
            relative_path = os.path.relpath(path, story_path)
            node_folder = os.path.dirname(relative_path).replace("\\", "/")
            if node_folder:
                full_id = f"{node_folder}:{node.id}"
            else:
                full_id = node.id

            node.id = full_id

            # Add folder prefix to choice ids 
            # (Note: choices leading to other folder md files must already include folder prefixes)
            for choice in node.choices:
                if choice.next_node:
                    choice.next_node = resolve_id(node_folder, choice.next_node)

                if choice.success_node:
                    choice.success_node = resolve_id(node_folder, choice.success_node)

                if choice.failure_node:
                    choice.failure_node = resolve_id(node_folder, choice.failure_node)

            if full_id in story:
                raise ValueError(f"Duplicate node id: {full_id} (file: {path})")

            story[full_id] = node

    validate_story(story)
    return story