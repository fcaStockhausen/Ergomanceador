"""Deathmatch scoreboard UI"""

import pygame
from config.colors import WHITE, CYAN, RED, GREEN, YELLOW


def draw_scoreboard(screen, scores, font):
    """Draw Quake 3-style scoreboard in top-right corner"""
    # Scoreboard position (top-right)
    x = screen.get_width() - 250
    y = 20

    # Background
    bg_rect = pygame.Rect(x - 10, y - 10, 240, 140)
    pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
    pygame.draw.rect(screen, WHITE, bg_rect, 2)

    # Title
    title_text = font.render("SCOREBOARD", True, CYAN)
    screen.blit(title_text, (x, y))
    y += 30

    # Sort scores by kills
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    # Draw each player's score
    for i, (player_id, kills) in enumerate(sorted_scores):
        # Color based on position
        if i == 0:
            color = YELLOW  # 1st place
        elif player_id == 'player':
            color = GREEN  # Player
        else:
            color = WHITE  # Bots

        # Format name
        name = "YOU" if player_id == 'player' else player_id.upper()

        # Draw score line
        score_text = font.render(f"{name}: {kills}", True, color)
        screen.blit(score_text, (x, y))
        y += 25


def draw_countdown(screen, countdown_time, font):
    """Draw countdown before game starts"""
    # Center of screen
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    if countdown_time > 0:
        countdown_num = int(countdown_time) + 1

        # Large countdown number
        big_font = pygame.font.Font(None, 120)
        countdown_text = big_font.render(str(countdown_num), True, CYAN)
        text_rect = countdown_text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(countdown_text, text_rect)

        # "GET READY" text
        ready_text = font.render("GET READY", True, WHITE)
        ready_rect = ready_text.get_rect(center=(screen_width // 2, screen_height // 2 - 80))
        screen.blit(ready_text, ready_rect)
    else:
        # "FIGHT!" text
        fight_font = pygame.font.Font(None, 100)
        fight_text = fight_font.render("FIGHT!", True, RED)
        text_rect = fight_text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(fight_text, text_rect)
