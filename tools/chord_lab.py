#!/usr/bin/env python3
"""
Chord Laboratory - Standalone diagnostic tool for the magic system.

Tests chord classification, property vectors, and manifold distances
WITHOUT launching the game. Runs entirely in the terminal.

Usage:
    python tools/chord_lab.py                    # Full diagnostic sweep
    python tools/chord_lab.py fire               # Test single chord
    python tools/chord_lab.py fire fire fire     # Test multi-element chord
    python tools/chord_lab.py --sweep            # All single + pairs + triples
    python tools/chord_lab.py --heatmap          # ASCII heatmap of distances
    python tools/chord_lab.py --compare          # Single vs Multi-label comparison
"""

import sys
import os
import itertools
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from magic.element_loader import load_elements_from_json
from magic.property_vector import PropertyVectorComputer
from magic.behavior_manifold import BehaviorManifold
from magic.behavior_composer import BehaviorComposer
from magic.spell_formulas import SpellFormulas


# ============================================================
# ANSI Colors
# ============================================================
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN = "\033[96m"

DIM_NAMES = [
    "thermal_flux", "avg_temp", "temp_diff", "state_trans",
    "phase_div", "density_grad", "avg_density", "volatility",
    "chaos", "total_energy", "energy_density", "polarity"
]

def color_strength(s):
    if s >= 0.7:
        return f"{C_GREEN}{s:.2f}{C_RESET}"
    elif s >= 0.4:
        return f"{C_YELLOW}{s:.2f}{C_RESET}"
    elif s >= 0.2:
        return f"{C_DIM}{s:.2f}{C_RESET}"
    else:
        return f"{C_DIM}{s:.2f}{C_RESET}"

def color_value(v, ideal_min=0.0, ideal_max=1.0):
    if v < ideal_min - 0.5 or v > ideal_max + 0.5:
        return f"{C_RED}{v:.2f}{C_RESET}"
    elif v < ideal_min or v > ideal_max:
        return f"{C_YELLOW}{v:.2f}{C_RESET}"
    else:
        return f"{v:.2f}"


class ChordLab:
    def __init__(self):
        self.elements = load_elements_from_json()
        self.manifold = BehaviorManifold()
        self.composer = BehaviorComposer(self.manifold)
        self.formulas = SpellFormulas()
        self.element_names = list(self.elements.keys())

    def build_chord(self, names):
        elems = [self.elements[n] for n in names if n in self.elements]
        return elems

    def analyze_chord(self, names):
        elems = self.build_chord(names)
        if not elems:
            print(f"{C_RED}No valid elements found.{C_RESET}")
            return

        vector = PropertyVectorComputer.compute(elems)
        v_array = self.manifold._vector_to_array(vector)
        distances = self.manifold.get_behavior_distances(vector)
        activations = self.composer.classify_multi(vector)
        single_label = self.manifold.classify(vector)
        primary = self.composer.get_primary_behavior(activations)

        # Header
        chord_str = " ".join(f"{e.icon}{e.name}" for e in elems)
        print(f"\n{'='*72}")
        print(f"  {C_BOLD}CHORD:{C_RESET} {chord_str}")
        print(f"{'='*72}")

        # 12D Property Vector
        print(f"\n{C_BOLD}12D Property Vector (normalized):{C_RESET}")
        raw_values = [
            vector.thermal_flux, vector.avg_temperature, vector.temp_differential,
            vector.state_transition_energy, vector.phase_diversity, vector.density_gradient,
            vector.avg_density, vector.volatility_index, vector.chaos_factor,
            vector.total_energy, vector.energy_density, vector.polarity_tension
        ]
        norm_values = [
            vector.thermal_flux / 2.0, vector.avg_temperature / 2000.0,
            vector.temp_differential / 2000.0, vector.state_transition_energy / 1000.0,
            vector.phase_diversity, vector.density_gradient, vector.avg_density,
            vector.volatility_index, vector.chaos_factor,
            vector.total_energy / 400.0, vector.energy_density / 150.0,
            vector.polarity_tension
        ]
        for i, (name, raw, norm) in enumerate(zip(DIM_NAMES, raw_values, norm_values)):
            flag = ""
            if norm < -0.5 or norm > 1.5:
                flag = f" {C_RED}⚠ OUT OF RANGE{C_RESET}"
            elif norm < 0.0 or norm > 1.0:
                flag = f" {C_YELLOW}~ outside [0,1]{C_RESET}"
            bar = self._ascii_bar(norm)
            print(f"  {name:15s} raw={raw:12.1f}  norm={color_value(norm):>20s}  {bar}{flag}")
        print()

        # Distances to all prototypes
        print(f"{C_BOLD}Distances to prototypes:{C_RESET}")
        sorted_dist = sorted(distances.items(), key=lambda x: x[1])
        nearest = sorted_dist[0][0]
        for name, dist in sorted_dist:
            marker = "★" if name == nearest else " "
            bar = self._ascii_bar(1.0 - min(dist / 3.0, 1.0), width=30)
            flag = ""
            if dist > 2.0:
                flag = f" {C_RED}(very far){C_RESET}"
            elif dist > 1.6:
                flag = f" {C_YELLOW}(far){C_RESET}"
            print(f"  {marker} {name:15s} dist={dist:.3f}  {bar}{flag}")

        # Multi-label activations
        print(f"\n{C_BOLD}Multi-label activations (strength > {self.composer.MIN_STRENGTH}):{C_RESET}")
        if activations:
            for i, act in enumerate(activations):
                marker = "★" if i == 0 else "○"
                bar = self._ascii_bar(act.strength, width=30)
                print(f"  {marker} {act.behavior:15s} str={color_strength(act.strength)}  "
                      f"dist={act.distance:.3f}  {bar}")
            modifiers = self.composer.get_modifiers(activations)
            if modifiers:
                print(f"\n  Primary: {C_CYAN}{primary}{C_RESET}  "
                      f"Modifiers: {C_MAGENTA}{', '.join(modifiers)}{C_RESET}")
            else:
                print(f"\n  Primary: {C_CYAN}{primary}{C_RESET}  (no modifiers)")
        else:
            print(f"  {C_RED}No behaviors activated!{C_RESET}")

        # Consistency check
        if single_label != primary:
            print(f"\n  {C_YELLOW}⚠ MISMATCH: single-label='{single_label}' "
                  f"vs multi-label='{primary}'{C_RESET}")

        # Spell stats
        print(f"\n{C_BOLD}Computed spell stats:{C_RESET}")
        if activations:
            weights = self.composer.get_behavior_weights(activations)
            dmg = sum(weights[b] * self.formulas.compute_damage(vector, b) for b in weights)
            spd = sum(weights[b] * self.formulas.compute_speed(vector, b) for b in weights)
            area = sum(weights[b] * self.formulas.compute_area(vector, b) for b in weights)
            dur = sum(weights[b] * self.formulas.compute_duration(vector, b) for b in weights)
            mana = sum(weights[b] * self.formulas.compute_mana_cost(vector, b) for b in weights)
        else:
            dmg = self.formulas.compute_damage(vector, 'projectile')
            spd = self.formulas.compute_speed(vector, 'projectile')
            area = self.formulas.compute_area(vector, 'projectile')
            dur = self.formulas.compute_duration(vector, 'projectile')
            mana = self.formulas.compute_mana_cost(vector, 'projectile')

        print(f"  damage={dmg}  speed={spd}  area={area}  duration={dur}  mana={mana}")

    def _ascii_bar(self, value, width=20):
        value = max(0.0, min(1.0, value))
        filled = int(value * width)
        return f"[{'█' * filled}{'░' * (width - filled)}]"

    def sweep(self, max_elements=3):
        """Sweep all combinations up to max_elements."""
        print(f"\n{'='*72}")
        print(f"  {C_BOLD}FULL CHORD SWEEP (1-{max_elements} elements){C_RESET}")
        print(f"{'='*72}\n")

        results = []
        element_list = sorted(self.elements.keys())

        for size in range(1, max_elements + 1):
            for combo in itertools.combinations_with_replacement(element_list, size):
                elems = self.build_chord(combo)
                vector = PropertyVectorComputer.compute(elems)
                distances = self.manifold.get_behavior_distances(vector)
                activations = self.composer.classify_multi(vector)
                primary = self.composer.get_primary_behavior(activations)
                single = self.manifold.classify(vector)
                nearest_dist = min(distances.values())

                results.append({
                    'chord': combo,
                    'primary': primary,
                    'single': single,
                    'match': single == primary,
                    'nearest_dist': nearest_dist,
                    'activations': activations,
                    'vector': vector,
                })

        # Print summary table
        print(f"{'Chord':<30s} {'Single':<12s} {'Multi':<12s} {'Dist':>6s} {'#Act':>4s}  Match")
        print("-" * 80)
        for r in results:
            chord_str = " ".join(r['chord'])
            n_act = len(r['activations'])
            match_str = f"{C_GREEN}✓{C_RESET}" if r['match'] else f"{C_RED}✗{C_RESET}"
            dist_str = f"{r['nearest_dist']:.2f}"
            if r['nearest_dist'] > 2.0:
                dist_str = f"{C_RED}{dist_str}{C_RESET}"
            elif r['nearest_dist'] > 1.6:
                dist_str = f"{C_YELLOW}{dist_str}{C_RESET}"

            print(f"{chord_str:<30s} {r['single']:<12s} {r['primary']:<12s} "
                  f"{dist_str:>20s} {n_act:>4d}  {match_str}")

        return results

    def diagnostic_report(self):
        """Run comprehensive diagnostic of the magic system."""
        print(f"\n{'='*72}")
        print(f"  {C_BOLD}{C_CYAN}MAGIC SYSTEM DIAGNOSTIC REPORT{C_RESET}")
        print(f"{'='*72}\n")

        # 1. Check element properties for normalization issues
        print(f"{C_BOLD}1. ELEMENT NORMALIZATION CHECK{C_RESET}")
        print(f"   Checking if element properties stay in [0,1] after normalization...\n")
        issues = []
        for name, elem in sorted(self.elements.items()):
            import math as _m
            avg_temp_norm = _m.log10(max(elem.temperature, 1)) / _m.log10(30000)
            if avg_temp_norm > 1.0:
                issues.append(f"   {C_RED}⚠ {name}.temperature={elem.temperature}K "
                            f"→ log_norm={avg_temp_norm:.1f} (blowout!){C_RESET}")
            elif avg_temp_norm > 0.8:
                issues.append(f"   {C_YELLOW}~ {name}.temperature={elem.temperature}K "
                            f"→ normalized={avg_temp_norm:.2f} (high){C_RESET}")

        if issues:
            for issue in issues:
                print(issue)
        else:
            print(f"   {C_GREEN}✓ All elements normalize correctly{C_RESET}")

        # 2. Check prototype coverage
        print(f"\n{C_BOLD}2. PROTOTYPE SPACING ANALYSIS{C_RESET}")
        print(f"   Checking distances between prototype centers...\n")
        regions = self.manifold.regions
        min_spacing = float('inf')
        closest_pair = None
        for i in range(len(regions)):
            for j in range(i + 1, len(regions)):
                dist = self.manifold._riemannian_distance(
                    regions[i].prototype, regions[j].prototype, regions[i].metric_tensor
                )
                if dist < min_spacing:
                    min_spacing = dist
                    closest_pair = (regions[i].name, regions[j].name)
                if dist < 0.5:
                    print(f"   {C_RED}⚠ {regions[i].name} ↔ {regions[j].name}: "
                          f"dist={dist:.3f} (COLLISION!){C_RESET}")
                elif dist < 0.8:
                    print(f"   {C_YELLOW}~ {regions[i].name} ↔ {regions[j].name}: "
                          f"dist={dist:.3f} (close){C_RESET}")

        print(f"\n   Closest prototypes: {closest_pair[0]} ↔ {closest_pair[1]} "
              f"(dist={min_spacing:.3f})")
        if min_spacing < 0.5:
            print(f"   {C_RED}⚠ Prototypes are too close — classification will be noisy{C_RESET}")

        # 3. Check which behaviors are reachable
        print(f"\n{C_BOLD}3. BEHAVIOR REACHABILITY (can real chords activate each behavior?){C_RESET}\n")
        results = self.sweep(max_elements=3)
        reachable = defaultdict(float)
        for r in results:
            for act in r['activations']:
                if act.strength > reachable[act.behavior]:
                    reachable[act.behavior] = act.strength

        print()
        for region in regions:
            name = region.name
            best = reachable.get(name, 0.0)
            if best > 0.5:
                print(f"   {C_GREEN}✓ {name:15s} best_strength={best:.2f}{C_RESET}")
            elif best > 0.1:
                print(f"   {C_YELLOW}~ {name:15s} best_strength={best:.2f} (weak){C_RESET}")
            else:
                print(f"   {C_RED}✗ {name:15s} best_strength={best:.2f} (UNREACHABLE!){C_RESET}")

        # 4. Single vs multi-label consistency
        print(f"\n{C_BOLD}4. SINGLE-LABEL vs MULTI-LABEL CONSISTENCY{C_RESET}\n")
        mismatches = [r for r in results if not r['match']]
        if mismatches:
            print(f"   {C_RED}⚠ {len(mismatches)}/{len(results)} chords disagree between methods:{C_RESET}")
            for r in mismatches:
                chord_str = " ".join(r['chord'])
                print(f"     '{chord_str}': single='{r['single']}' vs multi='{r['primary']}'")
        else:
            print(f"   {C_GREEN}✓ All chords agree between single and multi-label{C_RESET}")

        # 5. Classification distribution
        print(f"\n{C_BOLD}5. CLASSIFICATION DISTRIBUTION (which behaviors win most?){C_RESET}\n")
        counts = defaultdict(int)
        for r in results:
            counts[r['primary']] += 1
        total = len(results)
        for behavior, count in sorted(counts.items(), key=lambda x: -x[1]):
            pct = count / total * 100
            bar = self._ascii_bar(pct / 100, width=30)
            print(f"   {behavior:15s} {count:3d}/{total} ({pct:5.1f}%)  {bar}")

        unreachable_behaviors = [r.name for r in regions if r.name not in counts]
        if unreachable_behaviors:
            print(f"\n   {C_RED}Never classified as primary: {unreachable_behaviors}{C_RESET}")

        # 6. Distance statistics
        print(f"\n{C_BOLD}6. DISTANCE STATISTICS{C_RESET}")
        all_dists = [r['nearest_dist'] for r in results]
        print(f"\n   Nearest-prototype distance across all chords:")
        print(f"     min={min(all_dists):.3f}  max={max(all_dists):.3f}  "
              f"mean={np.mean(all_dists):.3f}  median={np.median(all_dists):.3f}")

        far_chords = [r for r in results if r['nearest_dist'] > 1.5]
        if far_chords:
            print(f"\n   {C_RED}⚠ {len(far_chords)} chords are very far from ALL prototypes (>1.5):{C_RESET}")
            for r in far_chords[:10]:
                print(f"     {' '.join(r['chord']):<30s} dist={r['nearest_dist']:.3f}")
            if len(far_chords) > 10:
                print(f"     ... and {len(far_chords) - 10} more")

        print(f"\n{'='*72}")
        print(f"  {C_BOLD}Diagnostic complete.{C_RESET}")
        print(f"{'='*72}\n")

    def interactive(self):
        """Interactive REPL for testing chords."""
        print(f"\n{C_BOLD}{C_CYAN}Chord Lab — Interactive Mode{C_RESET}")
        print(f"Available elements: {', '.join(self.element_names)}")
        print(f"Type element names separated by spaces. 'quit' to exit.\n")

        while True:
            try:
                user_input = input(f"{C_BOLD}chord> {C_RESET}").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if user_input.lower() in ('quit', 'exit', 'q'):
                break
            if not user_input:
                continue

            names = user_input.split()
            invalid = [n for n in names if n not in self.elements]
            if invalid:
                print(f"{C_RED}Unknown elements: {', '.join(invalid)}{C_RESET}")
                print(f"Available: {', '.join(self.element_names)}")
                continue

            self.analyze_chord(names)


def main():
    lab = ChordLab()

    args = sys.argv[1:]

    if not args:
        lab.diagnostic_report()

    elif args[0] == '--interactive' or args[0] == '-i':
        lab.interactive()

    elif args[0] == '--sweep':
        max_n = int(args[1]) if len(args) > 1 else 3
        lab.sweep(max_elements=max_n)

    elif args[0] == '--report' or args[0] == '--diagnostic':
        lab.diagnostic_report()

    else:
        for arg_set in [args]:
            lab.analyze_chord(arg_set)


if __name__ == '__main__':
    main()
