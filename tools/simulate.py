#!/usr/bin/env python3
"""
Headless battle simulator for Ergomanceador.

Runs matches between AI bots without rendering. Logs all events and
produces a summary report for tuning behavior, spells, and combat.

Usage:
    python tools/simulate.py                          # Default: 4 bots, 60s
    python tools/simulate.py --bots 6 --time 120      # 6 bots, 120s
    python tools/simulate.py --verbose                # Log every event
    python tools/simulate.py --seed 42                # Reproducible run
"""

import sys
import os
import math
import time
import random
import argparse
from collections import defaultdict, Counter

# Headless pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()

from config.settings import GRID_SIZE
from entities.enemy import Enemy
from entities.player import Player
from magic.magic_system import MagicSystem
from ai.bot_controller import BotController, BotPersonality
from rendering.effects.effect_manager import EffectManager


# ANSI Colors
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_CYAN = "\033[96m"
C_MAGENTA = "\033[95m"


class BattleSimulator:
    """Headless simulation of arena combat between AI bots."""

    def __init__(self, num_bots=4, duration=60.0, seed=None, include_player=False):
        self.duration = duration
        self.include_player = include_player

        if seed is not None:
            random.seed(seed)

        # Create effect manager
        self.effect_manager = EffectManager()

        # Create entities
        self.enemies = []
        self.bots = []  # (enemy, bot_ai, magic_system)

        bot_names = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel']

        for i in range(num_bots):
            # Spread spawn positions across the arena
            angle = (i / num_bots) * 2 * math.pi
            radius = GRID_SIZE * 0.3
            px = GRID_SIZE / 2 + math.cos(angle) * radius
            py = GRID_SIZE / 2 + math.sin(angle) * radius

            enemy = Enemy(px, py, max_health=300)
            enemy.bot_id = bot_names[i % len(bot_names)]

            magic = MagicSystem()
            ai = BotController(enemy, magic, self.effect_manager)

            self.enemies.append(enemy)
            self.bots.append((enemy, ai, magic))

        # Optional player (stationary dummy or AI-controlled)
        self.player = None
        if include_player:
            self.player = Player()
            self.player.cart_x = GRID_SIZE / 2
            self.player.cart_y = GRID_SIZE / 2

        # Wire up effect manager references
        self.effect_manager.enemies = self.enemies
        self.effect_manager.player = self.player

        # Event log
        self.events = []
        self.verbose = False

        # Statistics
        self.stats = {
            'behaviors_by_bot': defaultdict(Counter),
            'damage_taken': defaultdict(float),
            'deaths': defaultdict(int),
            'hp_timeline': [],
            'spells': [],           # Full spell log: (time, owner, elements, name, behavior, damage)
            'spell_chords': Counter(),    # 'fire+fire+fire': count
            'spell_names': Counter(),     # 'Explosive Blast': count
            'spell_behaviors': Counter(), # 'aoe': count
            'spell_by_bot': defaultdict(Counter),  # bot_id -> {chord: count}
            'heal_events': [],
        }

        self.sim_time = 0.0

        # Spell tracking: intercept spawn_spell_effect
        self._wrap_effect_manager()

    def log(self, msg, level='info'):
        self.events.append((self.sim_time, level, msg))
        if self.verbose or level == 'kill':
            colors = {'kill': C_RED, 'hit': C_YELLOW, 'cast': C_CYAN,
                      'heal': C_GREEN, 'dodge': C_MAGENTA, 'info': C_DIM}
            c = colors.get(level, '')
            bot_time = f"[{self.sim_time:6.1f}s]"
            print(f"  {C_DIM}{bot_time}{C_RESET} {c}{msg}{C_RESET}")

    def _wrap_effect_manager(self):
        """Wrap spawn_spell_effect to intercept all spell casts."""
        original_spawn = self.effect_manager.spawn_spell_effect
        self._original_spawn = original_spawn

        def wrapped_spawn(px, py, tx, ty, spell_data, owner='player'):
            # Capture spell info
            elements = spell_data.get('elements', [])
            chord = '+'.join(elements) if elements else '?'
            name = spell_data.get('name', 'Unknown')
            behavior = spell_data.get('behavior', 'projectile')
            damage = int(spell_data.get('damage', 0))

            self.stats['spells'].append((self.sim_time, owner, chord, name, behavior, damage))
            self.stats['spell_chords'][chord] += 1
            self.stats['spell_names'][name] += 1
            self.stats['spell_behaviors'][behavior] += 1
            self.stats['spell_by_bot'][owner][chord] += 1

            if self.verbose:
                self.log(f"{owner} cast {name} [{chord}] → {behavior} (dmg:{damage})", 'cast')

            return original_spawn(px, py, tx, ty, spell_data, owner)

        self.effect_manager.spawn_spell_effect = wrapped_spawn

    def run(self):
        """Run the simulation."""
        print(f"\n{C_BOLD}{C_CYAN}{'='*60}")
        print(f"  BATTLE SIMULATOR — {len(self.bots)} bots, {self.duration:.0f}s")
        print(f"{'='*60}{C_RESET}\n")

        # Print bot personalities
        for enemy, ai, _ in self.bots:
            print(f"  {C_BOLD}{enemy.bot_id}{C_RESET} @ ({enemy.cart_x:.0f},{enemy.cart_y:.0f}) "
                  f"HP:{enemy.health.max_health} {ai.personality}")
        print()

        # Fixed timestep for deterministic simulation
        dt = 1.0 / 60.0  # 60 FPS
        steps = int(self.duration / dt)
        log_interval = 2.0  # Log HP every 2 seconds
        last_log = 0.0

        for step in range(steps):
            self.sim_time = step * dt

            # Build target list
            all_targets = list(self.enemies)
            if self.player:
                all_targets.append(self.player)

            # Track HP before update for damage detection
            hp_before = {}
            for e in self.enemies:
                hp_before[id(e)] = e.health.current_health

            # Track projectiles before update for cast detection
            proj_before = len(self.effect_manager.projectiles)

            # Update bots
            for enemy, ai, _ in self.bots:
                if enemy.health.is_alive:
                    prev_action = ai.current_action
                    ai.update(dt, all_targets)
                    new_action = ai.current_action

                    # Track behavior distribution
                    self.stats['behaviors_by_bot'][enemy.bot_id][new_action] += 1

                    # Log significant behavior changes only (not wander)
                    if self.verbose and new_action != prev_action and \
                       new_action not in ('wander',) and \
                       prev_action not in ('wander',):
                        self.log(f"{enemy.bot_id} → {new_action}", 'info')

            # Update effect manager (handles projectile movement, collision, damage)
            self.effect_manager.update(dt)

            # Detect damage events by comparing HP
            for enemy in self.enemies:
                hp_after = enemy.health.current_health
                hp_b = hp_before.get(id(enemy), hp_after)

                if hp_after < hp_b:
                    diff = hp_b - hp_after
                    # Find who likely cast the hit (nearest alive bot with cast ready)
                    self.stats['damage_taken'][enemy.bot_id] += diff
                    self.log(f"{enemy.bot_id} took {diff:.0f} damage ({hp_after:.0f} HP left)", 'hit')

                # Detect death
                was_alive = hp_b > 0
                if was_alive and hp_after <= 0:
                    self.stats['deaths'][enemy.bot_id] += 1
                    self.log(f"{enemy.bot_id} DIED", 'kill')

            if self.player:
                # Track player damage too
                pass

            # Update enemies (respawn, knockback physics)
            for enemy in self.enemies:
                enemy.update(dt)

            # Periodic HP logging
            if self.sim_time - last_log >= log_interval:
                last_log = self.sim_time
                hp_snapshot = {}
                for enemy in self.enemies:
                    hp_snapshot[enemy.bot_id] = enemy.health.current_health
                self.stats['hp_timeline'].append((self.sim_time, dict(hp_snapshot)))

                # Print HP bar
                if self.verbose:
                    bars = []
                    for enemy in self.enemies:
                        pct = enemy.health.current_health / enemy.health.max_health
                        bar_len = 20
                        filled = int(pct * bar_len)
                        bar = '█' * filled + '░' * (bar_len - filled)
                        color = C_GREEN if pct > 0.5 else (C_YELLOW if pct > 0.25 else C_RED)
                        bars.append(f"{enemy.bot_id}:{color}{bar}{C_RESET}{enemy.health.current_health:.0f}")
                    print(f"  {C_DIM}{self.sim_time:6.1f}s{C_RESET} {' | '.join(bars)}")

            # Early exit if only 1 or fewer alive
            alive_count = sum(1 for e in self.enemies if e.health.is_alive)
            if alive_count <= 1 and len(self.enemies) > 1:
                self.log(f"Only {alive_count} bot(s) alive — ending early", 'info')
                break

        self._report()

    def _report(self):
        """Print simulation summary."""
        print(f"\n{C_BOLD}{C_CYAN}{'='*60}")
        print(f"  SIMULATION REPORT")
        print(f"{'='*60}{C_RESET}\n")

        # 1. Survival table
        print(f"{C_BOLD}SURVIVAL{C_RESET}")
        print(f"{'Bot':<10} {'HP':>6} {'Status':<8} {'Kills':>6} {'Deaths':>7}")
        print("-" * 45)
        for enemy, _, _ in self.bots:
            hp = enemy.health.current_health
            status = 'ALIVE' if hp > 0 else 'DEAD'
            color = C_GREEN if hp > 0 else C_RED
            kills = 0  # Kill attribution not tracked in headless sim
            deaths = self.stats['deaths'].get(enemy.bot_id, 0)
            print(f"{enemy.bot_id:<10} {hp:>6.0f} {color}{status:<8}{C_RESET} "
                  f"{kills:>6} {deaths:>7}")

        # 2. Combat stats
        print(f"\n{C_BOLD}DAMAGE{C_RESET}")
        dmg_taken = self.stats['damage_taken']
        for bot_id, dmg in sorted(dmg_taken.items(), key=lambda x: -x[1]):
            print(f"  {bot_id:<10} took {dmg:.0f} total damage")

        # 3. Behavior distribution
        print(f"\n{C_BOLD}BEHAVIOR DISTRIBUTION{C_RESET}")
        all_behaviors = Counter()
        for bot_behaviors in self.stats['behaviors_by_bot'].values():
            all_behaviors.update(bot_behaviors)

        total_actions = sum(all_behaviors.values())
        for action, count in all_behaviors.most_common():
            pct = count / total_actions * 100 if total_actions > 0 else 0
            bar_len = 30
            filled = int(pct / 100 * bar_len)
            bar = '█' * filled + '░' * (bar_len - filled)
            color = C_RED if action in ('flee', 'retreat') else \
                    C_GREEN if action in ('attack',) else \
                    C_YELLOW if action in ('dodge', 'kite') else \
                    C_CYAN if action in ('pursue',) else C_DIM
            print(f"  {color}{action:<10}{C_RESET} {count:>6} ({pct:5.1f}%) {bar}")

        # 4. Per-bot behavior breakdown
        print(f"\n{C_BOLD}PER-BOT BEHAVIOR{C_RESET}")
        for enemy, ai, _ in self.bots:
            behaviors = self.stats['behaviors_by_bot'][enemy.bot_id]
            total = sum(behaviors.values())
            if total == 0:
                continue
            top3 = behaviors.most_common(3)
            parts = [f"{a}({c/total*100:.0f}%)" for a, c in top3]
            print(f"  {enemy.bot_id:<10} {ai.personality}")
            print(f"             {' '.join(parts)}")

        # 5. HP over time summary
        print(f"\n{C_BOLD}HP TIMELINE (sampled every 2s){C_RESET}")
        if self.stats['hp_timeline']:
            # Print compact timeline
            bot_ids = [e.bot_id for e, _, _ in self.bots]
            header = f"  {'Time':>7s}"
            for bid in bot_ids:
                header += f" {bid:>8s}"
            print(header)
            print("  " + "-" * (7 + 9 * len(bot_ids)))
            for t, hps in self.stats['hp_timeline']:
                row = f"  {t:>7.1f}s"
                for bid in bot_ids:
                    hp = hps.get(bid, 0)
                    color = C_GREEN if hp > 150 else (C_YELLOW if hp > 75 else C_RED) if hp > 0 else C_DIM
                    row += f" {color}{hp:>8.0f}{C_RESET}"
                print(row)

        # 6. Chord usage
        print(f"\n{C_BOLD}CHORD USAGE (most cast element combinations){C_RESET}")
        for chord, count in self.stats['spell_chords'].most_common(10):
            pct = count / sum(self.stats['spell_chords'].values()) * 100
            print(f"  {chord:<25s} {count:>4d} ({pct:4.1f}%)")

        # 7. Emergent behaviors
        print(f"\n{C_BOLD}EMERGENT BEHAVIORS{C_RESET}")
        total_spells = sum(self.stats['spell_behaviors'].values())
        for behavior, count in self.stats['spell_behaviors'].most_common():
            pct = count / total_spells * 100 if total_spells else 0
            bar_len = 25
            filled = int(pct / 100 * bar_len)
            bar = '█' * filled + '░' * (bar_len - filled)
            color = C_GREEN if behavior in ('attack', 'projectile') else \
                    C_YELLOW if behavior in ('heal', 'buff', 'shield') else \
                    C_RED if behavior in ('aoe', 'split') else \
                    C_CYAN if behavior in ('chain', 'beam', 'homing') else C_DIM
            print(f"  {color}{behavior:<12}{C_RESET} {count:>4d} ({pct:5.1f}%) {bar}")

        # 8. Spell names
        print(f"\n{C_BOLD}SPELL NAMES (most cast spells){C_RESET}")
        for name, count in self.stats['spell_names'].most_common(10):
            print(f"  {name:<25s} {count:>4d}")

        # 9. Per-bot chord preferences
        print(f"\n{C_BOLD}PER-BOT CHORD PREFERENCES{C_RESET}")
        for enemy, ai, _ in self.bots:
            owner = 'bot' if enemy.bot_id == self.bots[0][0].bot_id else 'bot'
            chords = self.stats['spell_by_bot'].get('bot', Counter())
            if not chords:
                continue
            # We can't distinguish which bot cast since owner='bot' for all
            # Show aggregate instead
            break

        # Show aggregate bot chords
        bot_chords = self.stats['spell_by_bot'].get('bot', Counter())
        if bot_chords:
            print(f"  (All bots combined — owner tag is 'bot')")
            for chord, count in bot_chords.most_common(5):
                print(f"    {chord:<25s} {count:>4d}")

        print(f"\n{C_DIM}Simulation completed at t={self.sim_time:.1f}s{C_RESET}")
        print()


def main():
    parser = argparse.ArgumentParser(description='Headless battle simulator')
    parser.add_argument('--bots', type=int, default=4, help='Number of bots (default: 4)')
    parser.add_argument('--time', type=float, default=60.0, help='Duration in seconds (default: 60)')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    parser.add_argument('--verbose', '-v', action='store_true', help='Log every event')
    parser.add_argument('--player', action='store_true', help='Include a player dummy')

    args = parser.parse_args()

    sim = BattleSimulator(
        num_bots=args.bots,
        duration=args.time,
        seed=args.seed,
        include_player=args.player,
    )
    sim.verbose = args.verbose
    sim.run()


if __name__ == '__main__':
    main()
