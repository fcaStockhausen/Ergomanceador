"""
Prototype Manager: CRUD operations for behavior prototypes.

Manages both core prototypes (read-only) and custom prototypes (editable).
Custom prototypes are saved to data/custom_prototypes.json.
"""

import json
import numpy as np
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from magic.behavior_manifold import BehaviorRegion, BehaviorManifold


@dataclass
class PrototypeData:
    """Serializable prototype data"""
    name: str
    prototype: List[float]  # 12D vector as list
    threshold: float = 1.0
    is_custom: bool = True  # True if user-created, False if core


class PrototypeManager:
    """Manages behavior prototypes with persistence"""

    def __init__(self, custom_prototypes_path='data/custom_prototypes.json'):
        self.custom_path = custom_prototypes_path
        self.manifold = BehaviorManifold()
        self.custom_prototypes: List[PrototypeData] = []
        self.load_custom_prototypes()

    def load_custom_prototypes(self):
        """Load custom prototypes from JSON"""
        if not os.path.exists(self.custom_path):
            self.custom_prototypes = []
            return

        try:
            with open(self.custom_path, 'r') as f:
                data = json.load(f)
                self.custom_prototypes = [
                    PrototypeData(**proto) for proto in data['prototypes']
                ]
                print(f"✓ Loaded {len(self.custom_prototypes)} custom prototypes")
        except Exception as e:
            print(f"✗ Failed to load custom prototypes: {e}")
            self.custom_prototypes = []

    def save_custom_prototypes(self):
        """Save custom prototypes to JSON"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.custom_path), exist_ok=True)

            data = {
                'prototypes': [asdict(proto) for proto in self.custom_prototypes]
            }

            with open(self.custom_path, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"✓ Saved {len(self.custom_prototypes)} custom prototypes")
            return True
        except Exception as e:
            print(f"✗ Failed to save custom prototypes: {e}")
            return False

    def get_all_prototypes(self) -> List[Dict]:
        """Get all prototypes (core + custom) with metadata"""
        prototypes = []

        # Core prototypes (from manifold)
        for region in self.manifold.regions:
            prototypes.append({
                'name': region.name,
                'prototype': region.prototype.tolist(),
                'threshold': region.threshold,
                'is_custom': False,
                'is_core': True
            })

        # Custom prototypes
        for proto in self.custom_prototypes:
            prototypes.append({
                'name': proto.name,
                'prototype': proto.prototype,
                'threshold': proto.threshold,
                'is_custom': proto.is_custom,
                'is_core': False
            })

        return prototypes

    def add_prototype(self, name: str, prototype_vector: np.ndarray, threshold: float = 1.0) -> bool:
        """Add a new custom prototype"""
        # Check if name already exists
        if self.get_prototype_by_name(name):
            print(f"✗ Prototype '{name}' already exists")
            return False

        # Validate dimension
        if len(prototype_vector) != 12:
            print(f"✗ Prototype must be 12-dimensional (got {len(prototype_vector)})")
            return False

        # Create and add
        proto = PrototypeData(
            name=name,
            prototype=prototype_vector.tolist(),
            threshold=threshold,
            is_custom=True
        )
        self.custom_prototypes.append(proto)

        # Also add to runtime manifold
        self.manifold.regions.append(BehaviorRegion(
            name=name,
            prototype=prototype_vector,
            metric_tensor=np.eye(12),
            threshold=threshold
        ))

        print(f"✓ Added custom prototype '{name}'")
        return True

    def update_prototype(self, name: str, prototype_vector: np.ndarray, threshold: float = 1.0) -> bool:
        """Update an existing custom prototype"""
        # Find in custom prototypes
        for i, proto in enumerate(self.custom_prototypes):
            if proto.name == name:
                self.custom_prototypes[i].prototype = prototype_vector.tolist()
                self.custom_prototypes[i].threshold = threshold

                # Update in runtime manifold
                for region in self.manifold.regions:
                    if region.name == name:
                        region.prototype = prototype_vector
                        region.threshold = threshold
                        break

                print(f"✓ Updated custom prototype '{name}'")
                return True

        print(f"✗ Custom prototype '{name}' not found")
        return False

    def delete_prototype(self, name: str) -> bool:
        """Delete a custom prototype (cannot delete core prototypes)"""
        # Find and remove from custom prototypes
        for i, proto in enumerate(self.custom_prototypes):
            if proto.name == name:
                self.custom_prototypes.pop(i)

                # Remove from runtime manifold
                self.manifold.regions = [
                    r for r in self.manifold.regions if r.name != name
                ]

                print(f"✓ Deleted custom prototype '{name}'")
                return True

        print(f"✗ Custom prototype '{name}' not found (or is core prototype)")
        return False

    def get_prototype_by_name(self, name: str) -> Optional[Dict]:
        """Get prototype data by name"""
        all_protos = self.get_all_prototypes()
        for proto in all_protos:
            if proto['name'] == name:
                return proto
        return None

    def validate_prototype(self, name: str, prototype_vector: np.ndarray) -> Dict:
        """
        Validate a prototype before adding/updating.
        Returns dict with validation results and warnings.
        """
        warnings = []
        errors = []

        # Check dimension
        if len(prototype_vector) != 12:
            errors.append(f"Must be 12-dimensional (got {len(prototype_vector)})")

        # Check value range (should be roughly 0-1)
        if np.any(prototype_vector < -1.0) or np.any(prototype_vector > 1.5):
            warnings.append("Some values outside typical range [-1, 1.5]")

        # Check distance to existing prototypes
        min_distance = float('inf')
        closest_name = None

        for region in self.manifold.regions:
            if region.name == name:
                continue  # Skip self when updating
            dist = np.linalg.norm(region.prototype - prototype_vector)
            if dist < min_distance:
                min_distance = dist
                closest_name = region.name

        if min_distance < 0.3:
            warnings.append(f"Very close to '{closest_name}' (distance {min_distance:.3f})")
        elif min_distance < 0.5:
            warnings.append(f"Close to '{closest_name}' (distance {min_distance:.3f})")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'closest_prototype': closest_name,
            'closest_distance': min_distance
        }

    def get_core_prototype_names(self) -> List[str]:
        """Get list of core (non-editable) prototype names"""
        return [r.name for r in BehaviorManifold().regions]

    def reset_custom_prototypes(self):
        """Delete all custom prototypes (keeps core prototypes)"""
        self.custom_prototypes = []
        # Rebuild manifold with only core prototypes
        self.manifold = BehaviorManifold()
        print("✓ Reset all custom prototypes")
