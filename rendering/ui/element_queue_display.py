"""Element queue display - shows queued elements with icons"""

import pygame
from config.colors import ELEMENT_COLORS
from config.keybinds import ELEMENT_KEY_NAMES
from magic.element_loader import load_elements_from_json


# Load element data for icons
_elements_data = load_elements_from_json()


def draw_element_queue(screen, font, magic_system, x=10, y=220):
    """
    Draw element queue with visual icons and colors.
    Shows up to 5 elements in queue with emoji icons.
    """
    queue_font = pygame.font.Font(None, 28)
    label_font = pygame.font.Font(None, 22)

    # Draw label
    label = label_font.render("Element Queue (max 5):", True, (200, 200, 200))
    screen.blit(label, (x, y))

    # Draw queue slots (5 slots)
    slot_width = 60
    slot_height = 60
    slot_spacing = 5
    slot_y = y + 30

    for i in range(magic_system.max_queue_size):
        slot_x = x + i * (slot_width + slot_spacing)

        # Draw slot background
        if i < len(magic_system.element_queue):
            # Filled slot - use element color
            element_name = magic_system.element_queue[i]
            color = ELEMENT_COLORS.get(element_name, (100, 100, 100))
            pygame.draw.rect(screen, color, (slot_x, slot_y, slot_width, slot_height))
            pygame.draw.rect(screen, (255, 255, 255), (slot_x, slot_y, slot_width, slot_height), 2)

            # Draw element icon (emoji)
            if element_name in _elements_data:
                icon = _elements_data[element_name].icon
                icon_surface = queue_font.render(icon, True, (255, 255, 255))
                icon_rect = icon_surface.get_rect(center=(slot_x + slot_width//2, slot_y + slot_height//2 - 5))
                screen.blit(icon_surface, icon_rect)

                # Draw element key below icon
                key_name = ELEMENT_KEY_NAMES.get(element_name, '?')
                key_surface = label_font.render(key_name, True, (255, 255, 255))
                key_rect = key_surface.get_rect(center=(slot_x + slot_width//2, slot_y + slot_height - 12))
                screen.blit(key_surface, key_rect)
        else:
            # Empty slot
            pygame.draw.rect(screen, (50, 50, 50), (slot_x, slot_y, slot_width, slot_height))
            pygame.draw.rect(screen, (100, 100, 100), (slot_x, slot_y, slot_width, slot_height), 1)

            # Draw slot number
            num_surface = label_font.render(str(i + 1), True, (80, 80, 80))
            num_rect = num_surface.get_rect(center=(slot_x + slot_width//2, slot_y + slot_height//2))
            screen.blit(num_surface, num_rect)

    # Draw queue info (count)
    info_text = f"{len(magic_system.element_queue)}/{magic_system.max_queue_size} elements"
    info_surface = label_font.render(info_text, True, (150, 150, 150))
    screen.blit(info_surface, (x, slot_y + slot_height + 10))


def draw_available_elements(screen, font, magic_system, x=400, y=10):
    """
    Draw all available (unlocked) elements with their keybinds.
    Shows which elements the player can currently use.
    """
    label_font = pygame.font.Font(None, 22)
    element_font = pygame.font.Font(None, 24)

    # Title
    title = label_font.render("Available Elements:", True, (200, 200, 200))
    screen.blit(title, (x, y))

    # Draw elements in grid (2 rows of 4)
    elem_width = 80
    elem_height = 40
    elem_spacing = 5
    start_y = y + 30

    for i, element in enumerate(magic_system.unlocked_elements):
        col = i % 4
        row = i // 4
        elem_x = x + col * (elem_width + elem_spacing)
        elem_y = start_y + row * (elem_height + elem_spacing)

        # Background
        color = ELEMENT_COLORS.get(element, (100, 100, 100))
        pygame.draw.rect(screen, color, (elem_x, elem_y, elem_width, elem_height))
        pygame.draw.rect(screen, (255, 255, 255), (elem_x, elem_y, elem_width, elem_height), 1)

        # Icon + Key
        if element in _elements_data:
            icon = _elements_data[element].icon
            key_name = ELEMENT_KEY_NAMES.get(element, '?')

            # Draw icon
            icon_surface = element_font.render(icon, True, (255, 255, 255))
            icon_rect = icon_surface.get_rect(center=(elem_x + 20, elem_y + elem_height//2))
            screen.blit(icon_surface, icon_rect)

            # Draw key
            key_surface = label_font.render(key_name, True, (255, 255, 255))
            key_rect = key_surface.get_rect(center=(elem_x + elem_width - 20, elem_y + elem_height//2))
            screen.blit(key_surface, key_rect)
