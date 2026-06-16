#!/usr/bin/env python3
"""Audit element properties and manifold space coverage."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from magic.element_loader import load_elements_from_json
from magic.property_vector import PropertyVectorComputer
from magic.behavior_manifold import BehaviorManifold
import numpy as np
import itertools

R = "\033[91m"
Y = "\033[93m"
G = "\033[92m"
N = "\033[0m"

elements = load_elements_from_json()
manifold = BehaviorManifold()

print("=" * 80)
print("ELEMENT PROPERTY AUDIT")
print("=" * 80)

# Raw properties table
print()
print(f"{'Element':<12} {'Temp(K)':>8} {'log_T':>6} {'Energy':>7} {'Density':>7} "
      f"{'Volat':>6} {'Polar':<8} {'State':<8} {'Move':<10} Tags")
print("-" * 100)
for name, e in sorted(elements.items()):
    log_t = np.log10(max(e.temperature, 1)) / np.log10(30000)
    tags_str = ",".join(e.tags)
    print(f"{name:<12} {e.temperature:>8.0f} {log_t:>6.2f} {e.energy:>7} "
          f"{e.density:>7.2f} {e.volatility:>6.2f} {e.polarity:<8} "
          f"{e.state:<8} {e.movement:<10} {tags_str}")

# Consistency checks
print()
print("=" * 80)
print("CONSISTENCY CHECKS")
print("=" * 80)

issues = []
for name, e in sorted(elements.items()):
    if "hot" in e.tags and e.temperature < 500:
        issues.append(f"  {R}⚠{N} {name}: tagged 'hot' but temp={e.temperature}K")
    if "cold" in e.tags and e.temperature > 300:
        issues.append(f"  {R}⚠{N} {name}: tagged 'cold' but temp={e.temperature}K")
    if e.state == "plasma" and e.temperature < 1000:
        issues.append(f"  {R}⚠{N} {name}: state=plasma but temp={e.temperature}K")
    if e.state == "solid" and e.density < 0.7:
        issues.append(f"  {R}⚠{N} {name}: state=solid but density={e.density}")
    if e.state == "gas" and e.density > 0.5:
        issues.append(f"  {R}⚠{N} {name}: state=gas but density={e.density}")
    if "destructive" in e.tags and e.energy < 80:
        issues.append(f"  {R}⚠{N} {name}: tagged 'destructive' but energy={e.energy}")
    if "defensive" in e.tags and e.volatility > 0.4:
        issues.append(f"  {R}⚠{N} {name}: tagged 'defensive' but volatility={e.volatility}")
    if "healing" in e.tags and e.polarity != "positive":
        issues.append(f"  {R}⚠{N} {name}: tagged 'healing' but polarity={e.polarity}")
    log_t = np.log10(max(e.temperature, 1)) / np.log10(30000)
    if log_t > 1.0:
        issues.append(f"  {R}⚠{N} {name}: log_temp norm = {log_t:.2f} (exceeds 1.0)")

# Soft observations
if elements["shadow"].temperature < 200:
    issues.append(f"  {Y}~{N} shadow: temp={elements['shadow'].temperature}K < ice 253K. "
                  "Conceptually shadow=absence of energy?")
if elements["nature"].state == "liquid":
    issues.append(f"  {Y}~{N} nature: state=liquid. Organic/life. Consider 'liquid' OK as sap.")

for issue in issues:
    print(issue)
if not issues:
    print("  No issues found")

# Single-element positions
print()
print("=" * 80)
print("SINGLE-ELEMENT NORMALIZED 12D POSITIONS")
print("=" * 80)
dims = ["flux", "logT", "logdT", "logSTE", "phase", "dgrad", "dens",
        "volat", "chaos", "nrg", "edns", "polar"]
print(f"{'Elem':<10}", end="")
for d in dims:
    print(f" {d[:5]:>5}", end="")
print("  → Behavior")
print("-" * 90)

for name in sorted(elements.keys()):
    vec = PropertyVectorComputer.compute([elements[name]])
    arr = manifold._vector_to_array(vec)
    behavior = manifold.classify(vec)
    print(f"{name:<10}", end="")
    for v in arr:
        if v > 1.0 or v < -0.5:
            print(f" {R}{v:5.2f}{N}", end="")
        elif v < 0 or v > 0.9:
            print(f" {Y}{v:5.2f}{N}", end="")
        else:
            print(f" {v:5.2f}", end="")
    print(f"  → {behavior}")

# All pairs positions
print()
print("=" * 80)
print("PAIR HEATMAP — which behavior wins for each element pair")
print("=" * 80)
names = sorted(elements.keys())
print(f"{'':>10}", end="")
for n in names:
    print(f" {n[:4]:>5}", end="")
print()
for n1 in names:
    print(f"{n1[:10]:<10}", end="")
    for n2 in names:
        vec = PropertyVectorComputer.compute([elements[n1], elements[n2]])
        b = manifold.classify(vec)
        print(f" {b[:4]:>5}", end="")
    print()

# Prototype positions
print()
print("=" * 80)
print("PROTOTYPE POSITIONS (normalized 12D)")
print("=" * 80)
print(f"{'Behavior':<15}", end="")
for d in dims:
    print(f" {d[:5]:>5}", end="")
print()
print("-" * 80)
for region in manifold.regions:
    print(f"{region.name:<15}", end="")
    for v in region.prototype:
        print(f" {v:5.2f}", end="")
    # Also show metric tensor weights (diagonal)
    diag = np.diag(region.metric_tensor)
    print(f"  metric: [{','.join(f'{d:.0f}' for d in diag)}]")
print()

# Prototype spacing
print("=" * 80)
print("PROTOTYPE INTER-DISTANCES")
print("=" * 80)
regions = manifold.regions
for i in range(len(regions)):
    for j in range(i + 1, len(regions)):
        dist = manifold._riemannian_distance(
            regions[i].prototype, regions[j].prototype, regions[i].metric_tensor
        )
        flag = ""
        if dist < 0.5:
            flag = f"  {R}COLLISION{N}"
        elif dist < 0.8:
            flag = f"  {Y}close{N}"
        elif dist > 2.0:
            flag = f"  {Y}far{N}"
        print(f"  {regions[i].name:<15} ↔ {regions[j].name:<15} "
              f"dist={dist:.3f}{flag}")

# Coverage: where do real chords cluster?
print()
print("=" * 80)
print("REAL CHORD COVERAGE — distance to nearest prototype")
print("=" * 80)
all_chords = []
for size in range(1, 4):
    for combo in itertools.combinations_with_replacement(names, size):
        elems = [elements[n] for n in combo]
        vec = PropertyVectorComputer.compute(elems)
        dists = manifold.get_behavior_distances(vec)
        nearest = min(dists.values())
        winner = min(dists, key=dists.get)
        all_chords.append((combo, nearest, winner, dists))

# Distribution of nearest distances
nearest_dists = [c[1] for c in all_chords]
print(f"\n  Total chords analyzed: {len(all_chords)}")
print(f"  Nearest distance stats: min={min(nearest_dists):.2f} "
      f"max={max(nearest_dists):.2f} "
      f"mean={np.mean(nearest_dists):.2f} "
      f"median={np.median(nearest_dists):.2f}")

# Dead zones: chords very far from everything
print(f"\n  {Y}Dead zones (nearest dist > 1.0):{N}")
dead = [c for c in all_chords if c[1] > 1.0]
if dead:
    for combo, nd, w, _ in dead[:15]:
        print(f"    {' + '.join(combo):<30} → {w} (dist={nd:.2f})")
    if len(dead) > 15:
        print(f"    ... and {len(dead) - 15} more")
else:
    print(f"    {G}None — all chords within 1.0 of nearest prototype{N}")

# Which behaviors are reachable as primary?
print(f"\n  Reachability (can real chords produce each behavior as winner):")
for region in regions:
    best = min(
        (c[1] for c in all_chords if c[2] == region.name),
        default=999,
    )
    count = sum(1 for c in all_chords if c[2] == region.name)
    if count == 0:
        print(f"    {R}✗{N} {region.name:<15} NEVER wins (0/{len(all_chords)})")
    elif best > 0.8:
        print(f"    {Y}~{N} {region.name:<15} wins {count}/{len(all_chords)} "
              f"(best dist={best:.2f}, weak)")
    else:
        print(f"    {G}✓{N} {region.name:<15} wins {count}/{len(all_chords)} "
              f"(best dist={best:.2f})")

# Dimension utilization: which dimensions actually vary across chords?
print()
print("=" * 80)
print("DIMENSION UTILIZATION — how much does each axis vary?")
print("=" * 80)
all_vectors = []
for combo, _, _, _ in all_chords:
    elems = [elements[n] for n in combo]
    vec = PropertyVectorComputer.compute(elems)
    all_vectors.append(manifold._vector_to_array(vec))

all_vectors = np.array(all_vectors)
print(f"\n  {'Dim':<8} {'Min':>6} {'Max':>6} {'Mean':>6} {'Std':>6}  "
      f"{'Effective range':<20} Verdict")
for i, d in enumerate(dims):
    col = all_vectors[:, i]
    rng = col.max() - col.min()
    if rng < 0.1:
        verdict = f"{R}DEAD (no variation){N}"
    elif rng < 0.3:
        verdict = f"{Y}weak{N}"
    else:
        verdict = f"{G}healthy{N}"
    print(f"  {d:<8} {col.min():>6.2f} {col.max():>6.2f} "
          f"{col.mean():>6.2f} {col.std():>6.2f}  [{col.min():.2f} - {col.max():.2f}]  "
          f"{verdict}")

# Prototype coverage per dimension
print()
print("=" * 80)
print("PROTOTYPE vs REAL CHORD OVERLAP per dimension")
print("=" * 80)
proto_arr = np.array([r.prototype for r in manifold.regions])
print(f"\n  {'Dim':<8} {'Chord range':<18} {'Proto range':<18} {'Overlap?':<10}")
for i, d in enumerate(dims):
    chord_lo, chord_hi = all_vectors[:, i].min(), all_vectors[:, i].max()
    proto_lo, proto_hi = proto_arr[:, i].min(), proto_arr[:, i].max()
    overlap = chord_hi >= proto_lo and proto_hi >= chord_lo
    gap = ""
    if not overlap:
        gap = f"{R}GAP{N}"
    elif chord_hi > proto_hi + 0.3 or chord_lo < proto_lo - 0.3:
        gap = f"{Y}partial{N}"
    else:
        gap = f"{G}ok{N}"
    print(f"  {d:<8} [{chord_lo:.2f} - {chord_hi:.2f}]   "
          f"[{proto_lo:.2f} - {proto_hi:.2f}]   {gap}")
