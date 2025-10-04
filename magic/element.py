"""Element class for magic system"""

from dataclasses import dataclass, field
from typing import Set


@dataclass
class Element:
    """Represents an element with physical and magical properties for emergent spell interactions"""

    # Core identity
    name: str

    # Physical properties
    temperature: float       # Kelvin (affects phase-change interactions)
    energy: int              # Base damage contribution
    state: str               # 'solid', 'liquid', 'gas', 'plasma'
    movement: str            # 'static', 'flowing', 'expanding', 'rising', 'instant'

    # Enhanced properties (Phase 2)
    density: float           # 0.0-1.0 (affects projectile speed: 0=fast, 1=slow)
    volatility: float        # 0.0-1.0 (affects AoE size, chain reactions)
    polarity: str            # 'positive', 'negative', 'neutral'

    # Interaction tags
    tags: Set[str] = field(default_factory=set)  # Descriptive properties for synergies

    # Visual
    color: tuple = (255, 255, 255)  # RGB color
    icon: str = "•"                  # Unicode emoji or icon
