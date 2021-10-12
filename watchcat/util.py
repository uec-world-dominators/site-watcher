from typing import Dict


def recursive_update(base: Dict, update: Dict) -> Dict:
    for k, v in update.items():
        if isinstance(v, dict) and k in base:
            base[k] = recursive_update(base[k], v)
        else:
            base[k] = v
    return base
