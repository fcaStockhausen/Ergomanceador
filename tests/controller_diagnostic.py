"""Xbox Controller Diagnostic Tool - Shows actual button indices"""

import pygame
import sys

pygame.init()
pygame.joystick.init()

# Check for controllers
if pygame.joystick.get_count() == 0:
    print("❌ No controllers detected!")
    sys.exit(1)

# Initialize first controller
controller = pygame.joystick.Joystick(0)
controller.init()

print("=" * 60)
print(f"✅ Controller Connected: {controller.get_name()}")
print(f"   Buttons: {controller.get_numbuttons()}")
print(f"   Axes: {controller.get_numaxes()}")
print(f"   Hats: {controller.get_numhats()}")
print("=" * 60)
print("\n🎮 Press buttons to see their indices (Ctrl+C to quit)\n")

screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Controller Diagnostic")
clock = pygame.time.Clock()

button_names = {
    0: "A (bottom)",
    1: "B (right)",
    2: "X (left)",
    3: "Y (top)",
    4: "LB",
    5: "RB",
    6: "BACK/VIEW",
    7: "START/MENU",
    8: "GUIDE/XBOX",
    9: "L3 (left stick click)",
    10: "R3 (right stick click)",
}

axis_names = {
    0: "Left Stick X",
    1: "Left Stick Y",
    2: "Right Stick X",
    3: "Right Stick Y",
    4: "Left Trigger",
    5: "Right Trigger",
}

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.JOYBUTTONDOWN:
            btn_name = button_names.get(event.button, "Unknown")
            print(f"🔘 BUTTON {event.button} pressed - {btn_name}")

        elif event.type == pygame.JOYBUTTONUP:
            btn_name = button_names.get(event.button, "Unknown")
            print(f"⚪ BUTTON {event.button} released - {btn_name}")

        elif event.type == pygame.JOYHATMOTION:
            print(f"🎯 D-PAD: {event.value}")

        elif event.type == pygame.JOYAXISMOTION:
            value = event.axis
            axis_name = axis_names.get(value, f"Axis {value}")
            # Only show significant movement
            if abs(event.value) > 0.3:
                print(f"📊 {axis_name} (axis {value}): {event.value:.2f}")

    screen.fill((30, 30, 30))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\n✅ Diagnostic complete!")
