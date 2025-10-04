"""Element loader - loads elements from JSON file"""

import json
from pathlib import Path
from magic.element import Element


def load_elements_from_json(filepath="data/elements.json"):
    """Load elements from JSON file and return dict of Element objects"""
    # Get absolute path relative to project root
    project_root = Path(__file__).parent.parent
    full_path = project_root / filepath

    with open(full_path, 'r') as f:
        data = json.load(f)

    elements = {}
    for name, props in data.items():
        elements[name] = Element(
            name=props['name'],
            temperature=props['temperature'],
            energy=props['energy'],
            state=props['state'],
            movement=props['movement'],
            density=props['density'],
            volatility=props['volatility'],
            polarity=props['polarity'],
            tags=set(props['tags']),
            color=tuple(props['color']),
            icon=props['icon']
        )

    return elements
