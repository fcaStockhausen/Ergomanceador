"""Manual test for smooth keyboard aiming - Press IJKL to test"""

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import pygame
import sys
sys.path.insert(0, '/Users/fcaraneda/Documents/8_Proyectos_4/Karaokeficador')

from entities.player import Player
from entities.target_cursor import Target
from core.camera import Camera
from rendering.isometric import cart_to_iso
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from config.colors import BLACK, WHITE, GREEN, YELLOW
from config import keybinds

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Smooth Aiming Test - Use IJKL to aim, WASD to move")
clock = pygame.time.Clock()

# Create entities
player = Player()
target = Target()
camera = Camera()

# Instructions
font = pygame.font.Font(None, 24)

print("=" * 60)
print("SMOOTH AIMING TEST")
print("=" * 60)
print("Controls:")
print("  WASD - Move player")
print("  IJKL - Aim cursor (should be SMOOTH now!)")
print("  ESC  - Quit")
print("")
print("Watch the cursor - it should smoothly glide to the")
print("direction you're aiming, not jump instantly!")
print("=" * 60)

running = True
while running:
    dt = clock.get_time() / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Get keyboard input
    keys = pygame.key.get_pressed()

    # Player movement (WASD)
    dx = dy = 0
    if keys[keybinds.MOVE_UP]:
        dy = -1
    if keys[keybinds.MOVE_DOWN]:
        dy = 1
    if keys[keybinds.MOVE_LEFT]:
        dx = -1
    if keys[keybinds.MOVE_RIGHT]:
        dx = 1
    player.move(dx, dy)

    # Target aiming (IJKL) - SMOOTH
    tdx = tdy = 0
    if keys[keybinds.AIM_UP]:
        tdy = -1
    if keys[keybinds.AIM_DOWN]:
        tdy = 1
    if keys[keybinds.AIM_LEFT]:
        tdx = -1
    if keys[keybinds.AIM_RIGHT]:
        tdx = 1

    if tdx != 0 or tdy != 0:
        target.set_aim_direction(tdx, tdy, smooth=True)  # SMOOTH
    elif dx != 0 or dy != 0:
        target.set_aim_direction(*player.facing_direction, smooth=True)
    else:
        target.set_aim_direction(0, 0, smooth=True)

    # Update
    camera.follow(player)
    target.update(dt)  # This does the smooth interpolation!
    target.follow_player(player)

    # Render
    screen.fill(BLACK)
    camera_offset_x, camera_offset_y = camera.get_offset()

    # Draw grid reference
    for x in range(0, 21, 5):
        for y in range(0, 21, 5):
            iso_x, iso_y = cart_to_iso(x, y)
            sx = SCREEN_WIDTH // 2 + iso_x + camera_offset_x
            sy = SCREEN_HEIGHT // 2 + iso_y + camera_offset_y
            pygame.draw.circle(screen, (50, 50, 50), (int(sx), int(sy)), 3)

    # Draw player and target
    player.draw(screen, camera_offset_x, camera_offset_y)
    target.draw(screen, camera_offset_x, camera_offset_y)

    # Draw instructions
    instructions = [
        "WASD = Move | IJKL = Aim (SMOOTH!) | ESC = Quit",
        f"Aim direction: ({target.aim_direction[0]:.2f}, {target.aim_direction[1]:.2f})",
        f"Target direction: ({target.target_direction[0]:.2f}, {target.target_direction[1]:.2f})",
        f"Lerp speed: {target.keyboard_lerp_speed}"
    ]

    y_offset = 10
    for text in instructions:
        surface = font.render(text, True, YELLOW if "SMOOTH" in text else WHITE)
        screen.blit(surface, (10, y_offset))
        y_offset += 25

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\nTest complete!")
