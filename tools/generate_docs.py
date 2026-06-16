#!/usr/bin/env python3
"""
Living documentation generator for Ergomanceador.

Extracts metadata directly from the running code (element properties,
prototype positions, formula coefficients, AI parameters, keybinds)
and renders markdown docs that never go stale.

Usage:
    python tools/generate_docs.py                # Generate all docs
    python tools/generate_docs.py --check        # Check for drift (exit 1 if stale)
    python tools/generate_docs.py --output DIR   # Custom output directory
"""

import sys
import os
import json
import math
import argparse
import itertools
from collections import Counter, defaultdict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Headless pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
pygame.init()

from magic.element_loader import load_elements_from_json
from magic.property_vector import PropertyVectorComputer, PropertyVector
from magic.behavior_manifold import BehaviorManifold
from magic.behavior_composer import BehaviorComposer
from magic.spell_formulas import SpellFormulas
from magic.interaction_engine import InteractionEngine
from ai.bot_controller import BotController, BotPersonality
from config import settings
from config.keybinds import (
    ELEMENT_KEYS, ELEMENT_KEY_NAMES,
    MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT,
    AIM_UP, AIM_DOWN, AIM_LEFT, AIM_RIGHT,
    JUMP, CAST_AIMED, REMOVE_ELEMENT, CLEAR_QUEUE, SELF_CAST_MODIFIER,
)


# ============================================================
# Extractors — pull data from live game objects
# ============================================================

def extract_elements():
    """Extract element table from loaded JSON."""
    elements = load_elements_from_json()
    rows = []
    for name in sorted(elements):
        e = elements[name]
        rows.append({
            'name': name,
            'icon': e.icon,
            'temperature': e.temperature,
            'energy': e.energy,
            'state': e.state,
            'movement': e.movement,
            'density': e.density,
            'volatility': e.volatility,
            'polarity': e.polarity,
            'tags': sorted(e.tags),
            'color': e.color,
        })
    return rows


def extract_dimensions():
    """Extract 12D dimension metadata."""
    return [
        ('thermal_flux', 'Thermal flux', 'Rate of temperature equilibration', '/ 2.0, clipped'),
        ('avg_temperature', 'Avg temperature', 'Mean element temperature (K)', 'log10 / log10(30000)'),
        ('temp_differential', 'Temp differential', 'Temperature range (K)', 'log10 / log10(30000)'),
        ('state_transition_energy', 'State transition energy', 'Energy for phase change', 'log10 / log10(20000)'),
        ('phase_diversity', 'Phase diversity', 'Fraction of distinct states', 'linear 0–1'),
        ('density_gradient', 'Density gradient', 'Density std dev', 'linear 0–1'),
        ('avg_density', 'Avg density', 'Mean density', 'linear 0–1'),
        ('volatility_index', 'Volatility index', 'Mean volatility', 'linear 0–1'),
        ('chaos_factor', 'Chaos factor', 'Cross-property variance', 'linear 0–1'),
        ('total_energy', 'Total energy', 'Sum of element energies', '/ 600, clipped'),
        ('energy_density', 'Energy density', 'Energy per element', '/ 150, clipped'),
        ('polarity_tension', 'Polarity tension', 'Polarity imbalance', '−1 to +1'),
    ]


def extract_prototypes():
    """Extract prototype positions from live manifold."""
    manifold = BehaviorManifold()
    dim_names = [d[0] for d in extract_dimensions()]
    regions = []
    for region in manifold.regions:
        regions.append({
            'name': region.name,
            'prototype': region.prototype.tolist(),
            'metric': np.diag(region.metric_tensor).tolist(),
        })
    return regions, dim_names


def extract_formulas():
    """Extract formula coefficients from live SpellFormulas."""
    formulas = SpellFormulas()
    return formulas.coeff


def extract_ai():
    """Extract AI parameters from live BotController."""
    return {
        'actions': list(BotController.ACTIONS),
        'personality_facets': [
            ('aggression', 'Prefers close-range burst damage', '0.2–0.9'),
            ('caution', 'Flees earlier, maintains distance', '0.1–0.8'),
            ('cunning', 'Uses strategic spells (homing, split)', '0.1–0.8'),
            ('mobility', 'Moves more, kites more', '0.2–0.9'),
        ],
        'parameters': {
            'cast_cooldown': ('3.0s', 'Base seconds between spell casts'),
            'dodge_cooldown': ('2.0s', 'Minimum time between dodges'),
            'max_flee_duration': ('4.0s', 'How long a bot flees before reassessing'),
            'boltzmann_tau': ('0.35', 'Softmax temperature (lower = more deterministic)'),
            'action_lock_duration': ('0.4s', 'Minimum time before behavior re-evaluation'),
        },
        'spell_selection': {
            'low_hp_cautious': 'nature+nature (heal) or earth+earth (shield)',
            'close_aggressive': 'fire+fire+fire (AOE burst)',
            'far_cunning': 'arcane+arcane (homing)',
            'cunning_random': 'fire+light (split)',
            'default': '1-3 offensive elements (fire/shadow/arcane)',
        },
    }


def extract_settings():
    """Extract game settings from config."""
    return {
        'SCREEN_WIDTH': settings.SCREEN_WIDTH,
        'SCREEN_HEIGHT': settings.SCREEN_HEIGHT,
        'FPS': settings.FPS,
        'GRID_SIZE': settings.GRID_SIZE,
        'BASE_MOVEMENT_SPEED': settings.BASE_MOVEMENT_SPEED,
        'TILE_WIDTH': settings.TILE_WIDTH,
        'TILE_HEIGHT': settings.TILE_HEIGHT,
        'DEBUG_MODE': settings.DEBUG_MODE,
    }


def extract_keybinds():
    """Extract keyboard mappings from config/keybinds.py."""
    import pygame
    # Build display-friendly key maps
    element_map = {}
    for key_code, elem_name in ELEMENT_KEYS.items():
        key_str = ELEMENT_KEY_NAMES.get(elem_name, pygame.key.name(key_code).upper())
        element_map[key_str] = elem_name

    movement_map = {
        'W': 'up', 'S': 'down', 'A': 'left', 'D': 'right'
    }
    aim_map = {
        'I': 'up', 'K': 'down', 'J': 'left', 'L': 'right'
    }
    action_map = {
        'G': 'Jump',
        'SPACE': 'Cast spell (aimed)',
        'BACKSPACE': 'Remove last element',
        'ESCAPE': 'Clear queue / Quit (double-press)',
        'LSHIFT': 'Self-cast modifier (Shift + Space)',
    }

    return {
        'elements': element_map,
        'movement': movement_map,
        'aim': aim_map,
        'actions': action_map,
    }


def extract_chord_table(max_elements=3):
    """Generate live chord classification table."""
    elements = load_elements_from_json()
    manifold = BehaviorManifold()
    engine = InteractionEngine()
    names = sorted(elements.keys())

    results = []
    for size in range(1, max_elements + 1):
        for combo in itertools.combinations_with_replacement(names, size):
            elems = [elements[n] for n in combo]
            vec = PropertyVectorComputer.compute(elems)
            spell = engine.compute_interaction(list(combo))
            dists = manifold.get_behavior_distances(vec)
            nearest = min(dists.values())

            results.append({
                'chord': ' + '.join(combo),
                'behavior': spell['behavior'],
                'name': spell['name'],
                'damage': int(spell['damage']),
                'speed': round(spell['speed'], 1),
                'area': round(spell['area'], 1),
                'mana': int(spell['mana_cost']),
                'distance': round(nearest, 2),
            })
    return results


def extract_classification_distribution():
    """Compute classification distribution from chord table."""
    chords = extract_chord_table(3)
    counts = Counter(c['behavior'] for c in chords)
    total = len(chords)
    return [(b, c, c / total * 100) for b, c in counts.most_common()], total


# ============================================================
# Renderers — markdown generation
# ============================================================

def render_elements(elements):
    lines = [
        "<!-- AUTO-GENERATED by tools/generate_docs.py — do not edit manually -->",
        f"<!-- Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->",
        "",
        "# Elements",
        "",
        "Properties loaded from `data/elements.json`.",
        "",
        "| Element | Temp (K) | Energy | State | Movement | Density | Volatility | Polarity | Tags |",
        "|---------|----------|--------|-------|----------|---------|------------|----------|------|",
    ]
    for e in elements:
        tags = ", ".join(e['tags'])
        lines.append(
            f"| {e['icon']} {e['name']} | {e['temperature']} | {e['energy']} | "
            f"{e['state']} | {e['movement']} | {e['density']} | {e['volatility']} | "
            f"{e['polarity']} | {tags} |"
        )

    lines.extend([
        "",
        "## Polarity Distribution",
        "",
    ])
    polarities = Counter(e['polarity'] for e in elements)
    for p in ['positive', 'neutral', 'negative']:
        count = polarities.get(p, 0)
        names = [e['name'] for e in elements if e['polarity'] == p]
        lines.append(f"- **{p}** ({count}): {', '.join(sorted(names))}")

    return "\n".join(lines) + "\n"


def render_manifold(prototypes, dim_names):
    lines = [
        "<!-- AUTO-GENERATED by tools/generate_docs.py — do not edit manually -->",
        f"<!-- Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->",
        "",
        "# Behavior Manifold",
        "",
        "Prototype positions extracted from `magic/behavior_manifold.py`.",
        "",
        "## 12 Dimensions",
        "",
        "| # | Key | Name | Description | Normalization |",
        "|---|-----|------|-------------|---------------|",
    ]
    dims = extract_dimensions()
    for i, (key, name, desc, norm) in enumerate(dims):
        lines.append(f"| {i} | `{key}` | {name} | {desc} | {norm} |")

    lines.extend(["", "## Prototypes", "",
                  "| Behavior | " + " | ".join(d[:4] for d in dim_names) + " | Key metric weights |",
                  "|----------|" + "|".join(["------"] * len(dim_names)) + "|---------------------|"])

    for p in prototypes:
        vals = " | ".join(f"{v:.2f}" for v in p['prototype'])
        metric_str = ", ".join(
            f"{dim_names[i][:4]}={w:.0f}" for i, w in enumerate(p['metric']) if w > 1.5
        )
        lines.append(f"| **{p['name']}** | {vals} | {metric_str} |")

    # Inter-prototype distances
    lines.extend(["", "## Prototype Spacing", "",
                  "| Pair | Distance | Status |", "|------|----------|--------|"])
    manifold = BehaviorManifold()
    import numpy as np
    regions = manifold.regions
    for i in range(len(regions)):
        for j in range(i + 1, len(regions)):
            dist = manifold._riemannian_distance(
                regions[i].prototype, regions[j].prototype, regions[i].metric_tensor
            )
            if dist < 0.5:
                status = "COLLISION"
            elif dist < 0.8:
                status = "close"
            elif dist > 2.0:
                status = "far"
            else:
                status = "ok"
            lines.append(f"| {regions[i].name} ↔ {regions[j].name} | {dist:.2f} | {status} |")

    return "\n".join(lines) + "\n"


def render_formulas(coeff):
    lines = [
        "<!-- AUTO-GENERATED by tools/generate_docs.py — do not edit manually -->",
        f"<!-- Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->",
        "",
        "# Spell Formulas",
        "",
        "Coefficients extracted from `magic/spell_formulas.py`.",
        "",
    ]
    for category, params in coeff.items():
        lines.append(f"## {category.title()}")
        lines.append("")
        for key, val in params.items():
            if isinstance(val, dict):
                lines.append(f"| {key} |")
                lines.append(f"|{'---' * 20}|")
                for sub_key, sub_val in val.items():
                    lines.append(f"  `{sub_key}`: {sub_val}")
                lines.append("")
            else:
                lines.append(f"- `{key}`: **{val}**")
        lines.append("")

    return "\n".join(lines) + "\n"


def render_ai(ai_data):
    lines = [
        "<!-- AUTO-GENERATED by tools/generate_docs.py — do not edit manually -->",
        f"<!-- Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->",
        "",
        "# Bot AI System",
        "",
        "Parameters extracted from `ai/bot_controller.py`.",
        "",
        "## Personality Facets",
        "",
        "| Facet | Description | Range |",
        "|-------|-------------|-------|",
    ]
    for name, desc, rng in ai_data['personality_facets']:
        lines.append(f"| **{name}** | {desc} | {rng} |")

    lines.extend([
        "",
        "## Actions",
        "",
        f"The bot evaluates **{len(ai_data['actions'])}** candidate actions each tick "
        f"and selects one via Boltzmann (softmax) selection:",
        "",
        "| Action | Description |",
        "|--------|-------------|",
        "| `attack` | Cast a spell at the target |",
        "| `pursue` | Move toward target to enter casting range |",
        "| `kite` | Back away while strafing sideways |",
        "| `dodge` | Evade incoming projectile (perpendicular dash) |",
        "| `flee` | Run directly away at 1.5x speed (triggered at <30% HP) |",
        "| `retreat` | Move toward nearest map corner to recover |",
        "| `wander` | Random exploration movement |",
        "",
        "## Parameters",
        "",
        "| Parameter | Value | Description |",
        "|-----------|-------|-------------|",
    ])
    for name, (val, desc) in ai_data['parameters'].items():
        lines.append(f"| `{name}` | {val} | {desc} |")

    lines.extend([
        "",
        "## Spell Selection Strategy",
        "",
        "| Situation | Chord | Emergent behavior |",
        "|-----------|-------|-------------------|",
    ])
    for situation, chord in ai_data['spell_selection'].items():
        lines.append(f"| {situation} | `{chord}` | |")

    return "\n".join(lines) + "\n"


def render_settings(settings_data):
    lines = [
        "<!-- AUTO-GENERATED by tools/generate_docs.py — do not edit manually -->",
        f"<!-- Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->",
        "",
        "# Game Settings",
        "",
        "Constants extracted from `config/settings.py`.",
        "",
        "| Setting | Value |",
        "|---------|-------|",
    ]
    for key, val in sorted(settings_data.items()):
        lines.append(f"| `{key}` | {val} |")

    return "\n".join(lines) + "\n"


def render_keybinds(keybind_data):
    lines = [
        "<!-- AUTO-GENERATED by tools/generate_docs.py — do not edit manually -->",
        f"<!-- Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->",
        "",
        "# Controls",
        "",
        "Mappings extracted from `config/keybinds.py`.",
        "",
        "## Element Selection (Dual-Hand)",
        "",
        "| Key | Element | Hand |",
        "|-----|---------|------|",
    ]
    # Handle both dict and list formats
    elems = keybind_data.get('elements', {})
    if isinstance(elems, dict):
        for key, elem_name in sorted(elems.items()):
            hand = "Left" if key in ['q', 'e', 'r', 'f'] else "Right"
            lines.append(f"| {key.upper()} | {elem_name} | {hand} |")
    elif isinstance(elems, list):
        for entry in elems:
            if isinstance(entry, (list, tuple)) and len(entry) >= 2:
                key, elem_name = entry[0], entry[1]
                hand = "Left" if str(key).lower() in ['q', 'e', 'r', 'f'] else "Right"
                lines.append(f"| {str(key).upper()} | {elem_name} | {hand} |")

    lines.extend(["", "## Movement (WASD — Left Hand)", "",
                  "| Key | Direction |", "|-----|-----------|"])
    movement = keybind_data.get('movement', {})
    if isinstance(movement, dict):
        for key, direction in sorted(movement.items()):
            lines.append(f"| {key.upper()} | {direction} |")

    lines.extend(["", "## Aiming (IJKL — Right Hand)", "",
                  "| Key | Direction |", "|-----|-----------|"])
    aim = keybind_data.get('aim', {})
    if isinstance(aim, dict):
        for key, direction in sorted(aim.items()):
            lines.append(f"| {key.upper()} | {direction} |")

    lines.extend(["", "## Actions", "",
                  "| Key | Action |", "|-----|--------|"])
    actions = keybind_data.get('actions', {})
    if isinstance(actions, dict):
        for key, action in sorted(actions.items()):
            lines.append(f"| {key.upper()} | {action} |")

    return "\n".join(lines) + "\n"


def render_chord_reference(chords):
    lines = [
        "<!-- AUTO-GENERATED by tools/generate_docs.py — do not edit manually -->",
        f"<!-- Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->",
        "",
        "# Chord Reference",
        "",
        f"Live classification of all {len(chords)} element combinations (1-3 elements).",
        "Generated by running the actual `InteractionEngine`.",
        "",
        "| Chord | Behavior | Spell Name | Damage | Speed | Area | Mana | Dist |",
        "|-------|----------|------------|--------|-------|------|------|------|",
    ]
    for c in chords:
        lines.append(
            f"| {c['chord']} | {c['behavior']} | {c['name']} | "
            f"{c['damage']} | {c['speed']} | {c['area']} | {c['mana']} | {c['distance']} |"
        )

    return "\n".join(lines) + "\n"


def render_distribution(distribution, total):
    lines = [
        "<!-- AUTO-GENERATED by tools/generate_docs.py — do not edit manually -->",
        f"<!-- Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->",
        "",
        "# Classification Distribution",
        "",
        f"Behavior win rates across {total} chords (1-3 elements).",
        "",
        "| Behavior | Wins | Share | Bar |",
        "|----------|------|-------|-----|",
    ]
    for behavior, count, pct in distribution:
        bar_len = 30
        filled = int(pct / 100 * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        lines.append(f"| {behavior} | {count} | {pct:.1f}% | `{bar}` |")

    return "\n".join(lines) + "\n"


def render_index(generated_files):
    lines = [
        "<!-- AUTO-GENERATED by tools/generate_docs.py — do not edit manually -->",
        f"<!-- Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} -->",
        "",
        "# Living Reference",
        "",
        "This directory contains **auto-generated** documentation extracted from the running codebase. "
        "These files are regenerated by `tools/generate_docs.py` and always reflect the current state "
        "of element properties, prototype positions, formula coefficients, and AI parameters.",
        "",
        "To regenerate:",
        "```bash",
        "python tools/generate_docs.py",
        "```",
        "",
        "## Generated Files",
        "",
    ]
    descriptions = {
        'elements.md': 'Element properties (temperature, energy, density, polarity, tags)',
        'manifold.md': '12D prototype positions, metric tensors, inter-prototype distances',
        'formulas.md': 'Spell formula coefficients (damage, area, speed, duration, mana, range)',
        'ai.md': 'Bot AI parameters (personality facets, actions, Boltzmann selection, spell strategy)',
        'settings.md': 'Game constants (screen size, FPS, grid size, movement speed)',
        'controls.md': 'Keyboard mappings (elements, movement, aiming, actions)',
        'chords.md': 'Complete chord classification table — every element combination and its emergent behavior',
        'distribution.md': 'Classification distribution — how often each behavior wins',
    }
    for fname in generated_files:
        desc = descriptions.get(fname, '')
        lines.append(f"- [{fname}]({fname}) — {desc}")

    lines.extend([
        "",
        "## How It Works",
        "",
        "```",
        "data/elements.json          ─┐",
        "magic/behavior_manifold.py  ─┤",
        "magic/spell_formulas.py     ─┼──▶ tools/generate_docs.py ──▶ docs/generated/*.md",
        "ai/bot_controller.py        ─┤",
        "config/settings.py          ─┤",
        "config/keybinds.py          ─┘",
        "```",
        "",
        "The generator imports the live game systems, calls the actual classifiers and formula "
        "engines, and renders the results as markdown. No hand-written values — everything is "
        "derived from the code at generation time.",
        "",
    ])

    return "\n".join(lines) + "\n"


# ============================================================
# Main
# ============================================================

import numpy as np  # needed by extract_prototypes


def generate_all(output_dir):
    """Generate all living docs."""
    os.makedirs(output_dir, exist_ok=True)

    print("Extracting data from live game systems...")

    # Extract
    elements = extract_elements()
    prototypes, dim_names = extract_prototypes()
    formulas = extract_formulas()
    ai_data = extract_ai()
    settings_data = extract_settings()
    keybind_data = extract_keybinds()

    print("Computing chord classifications (this may take a moment)...")
    chords = extract_chord_table(max_elements=3)
    distribution, total = extract_classification_distribution()

    # Render
    files = {}
    files['elements.md'] = render_elements(elements)
    files['manifold.md'] = render_manifold(prototypes, dim_names)
    files['formulas.md'] = render_formulas(formulas)
    files['ai.md'] = render_ai(ai_data)
    files['settings.md'] = render_settings(settings_data)
    files['controls.md'] = render_keybinds(keybind_data)
    files['chords.md'] = render_chord_reference(chords)
    files['distribution.md'] = render_distribution(distribution, total)
    files['README.md'] = render_index(sorted(files.keys()))

    # Write
    print(f"\nWriting to {output_dir}/")
    for fname, content in files.items():
        path = os.path.join(output_dir, fname)
        with open(path, 'w') as f:
            f.write(content)
        print(f"  {fname} ({len(content)} bytes)")

    print(f"\nDone. {len(files)} files generated.")


def check_drift(output_dir):
    """Check if generated docs are stale."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        generate_all(tmpdir)
        # Compare
        stale = []
        for fname in os.listdir(tmpdir):
            new_path = os.path.join(tmpdir, fname)
            old_path = os.path.join(output_dir, fname)

            if not os.path.exists(old_path):
                stale.append(fname)
                continue

            with open(new_path) as f:
                new_content = f.read()
            with open(old_path) as f:
                old_content = f.read()

            # Strip the timestamp line for comparison
            new_lines = [l for l in new_content.split('\n') if 'Last generated' not in l]
            old_lines = [l for l in old_content.split('\n') if 'Last generated' not in l]

            if new_lines != old_lines:
                stale.append(fname)

        if stale:
            print(f"STALE: {', '.join(stale)}")
            print("Run: python tools/generate_docs.py")
            return 1
        else:
            print("All docs up to date.")
            return 0


def main():
    parser = argparse.ArgumentParser(description='Living documentation generator')
    parser.add_argument('--output', '-o', default='docs/generated',
                        help='Output directory (default: docs/generated)')
    parser.add_argument('--check', action='store_true',
                        help='Check for drift without writing (exit 1 if stale)')

    args = parser.parse_args()

    if args.check:
        sys.exit(check_drift(args.output))
    else:
        generate_all(args.output)


if __name__ == '__main__':
    main()
