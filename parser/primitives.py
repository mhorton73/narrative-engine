
def parse_item_key_pair(pair:str):
    pair = pair.strip()
    item_type, key = pair.split(":")
    return {
        "type": item_type.strip(),
        "key": key.strip()
    }

def parse_skill_check(pair:str):
    stat, value = pair.strip().split(":")
    return {
        "stat": stat.strip(),
        "difficulty": int(value.strip())
    }

def parse_stat_change(pair:str):
    stat, value = pair.strip().split(":")
    return {
        "stat": stat.strip(),
        "delta": int(value.strip())
    }

