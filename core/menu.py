"""
Main menu system for Karaokeficador.

Menu flow:
- Main Menu → Play Game | Designer Mode | Settings | Quit
- Pause Menu (in-game) → Resume | Designer Mode | Quit to Menu
"""

import pygame
import logging
from config.colors import BLACK, WHITE
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class MenuItem:
    """Single menu item with hover state"""

    def __init__(self, text, action, y_pos, font):
        self.text = text
        self.action = action  # Callback or action string
        self.y_pos = y_pos
        self.font = font
        self.hovered = False

        # Render text surfaces
        self.text_normal = font.render(text, True, (200, 200, 200))
        self.text_hover = font.render(text, True, (255, 255, 100))

        # Center horizontally
        self.x_pos = SCREEN_WIDTH // 2 - self.text_normal.get_width() // 2
        self.rect = pygame.Rect(
            self.x_pos - 20, self.y_pos - 5,
            self.text_normal.get_width() + 40, self.text_normal.get_height() + 10
        )

    def update(self, mouse_pos):
        """Update hover state"""
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """Draw menu item"""
        # Highlight if hovered
        if self.hovered:
            pygame.draw.rect(screen, (50, 50, 80), self.rect, border_radius=5)
            pygame.draw.rect(screen, (255, 255, 100), self.rect, 2, border_radius=5)
            screen.blit(self.text_hover, (self.x_pos, self.y_pos))
        else:
            screen.blit(self.text_normal, (self.x_pos, self.y_pos))

    def handle_click(self):
        """Handle click on this item"""
        if self.hovered:
            logging.info(f"Menu: {self.text} selected")
            return self.action
        return None


class Menu:
    """Base menu class"""

    def __init__(self, title, items):
        self.title = title
        self.items = items
        self.font_title = pygame.font.Font(None, 72)
        self.font_item = pygame.font.Font(None, 48)
        self.font_hint = pygame.font.Font(None, 24)

        # Create menu items
        self.menu_items = []
        y_start = 250
        y_spacing = 70
        for i, (text, action) in enumerate(items):
            item = MenuItem(text, action, y_start + i * y_spacing, self.font_item)
            self.menu_items.append(item)

        self.selected_action = None

        # Controller navigation
        self.selected_index = 0  # Currently selected item via controller
        self.using_controller = False  # Track if controller was last used

    def update(self, mouse_pos):
        """Update menu state"""
        # Update hover states for mouse
        for i, item in enumerate(self.menu_items):
            item.update(mouse_pos)
            # If mouse is hovering, switch to mouse mode
            if item.hovered and self.using_controller:
                self.using_controller = False

        # If using controller, force hover on selected item
        if self.using_controller:
            for i, item in enumerate(self.menu_items):
                item.hovered = (i == self.selected_index)

    def handle_event(self, event):
        """Handle menu input events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for item in self.menu_items:
                action = item.handle_click()
                if action:
                    self.selected_action = action
                    return action

        # Keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'back'

            # Arrow keys for navigation (also enables controller mode)
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.using_controller = True
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.using_controller = True
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Select current item
                if self.using_controller:
                    action = self.menu_items[self.selected_index].action
                    self.selected_action = action
                    return action

            # Number keys for quick selection
            if pygame.K_1 <= event.key <= pygame.K_9:
                index = event.key - pygame.K_1
                if index < len(self.menu_items):
                    action = self.menu_items[index].action
                    self.selected_action = action
                    return action

        # Controller D-pad navigation
        if event.type == pygame.JOYBUTTONDOWN:
            # A button (0 on Xbox controller) = select
            if event.button == 0:
                action = self.menu_items[self.selected_index].action
                self.selected_action = action
                logging.info(f"Controller selected: {self.menu_items[self.selected_index].text}")
                return action
            # B button (1) = back
            elif event.button == 1:
                return 'back'
            # D-pad up (11 on macOS)
            elif event.button == 11:
                self.using_controller = True
                self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                logging.info(f"Menu up: selected {self.menu_items[self.selected_index].text}")
            # D-pad down (12 on macOS)
            elif event.button == 12:
                self.using_controller = True
                self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                logging.info(f"Menu down: selected {self.menu_items[self.selected_index].text}")

        return None

    def draw(self, screen):
        """Draw menu"""
        screen.fill(BLACK)

        # Title
        title_surf = self.font_title.render(self.title, True, (255, 200, 100))
        title_x = SCREEN_WIDTH // 2 - title_surf.get_width() // 2
        screen.blit(title_surf, (title_x, 100))

        # Menu items
        for item in self.menu_items:
            item.draw(screen)

        # Hint
        hint = self.font_hint.render("Mouse/Arrows/D-pad to navigate | Enter/A to select | ESC/B to go back", True, (120, 120, 150))
        hint_x = SCREEN_WIDTH // 2 - hint.get_width() // 2
        screen.blit(hint, (hint_x, SCREEN_HEIGHT - 50))


class MainMenu(Menu):
    """Main menu (game start)"""

    def __init__(self):
        items = [
            ("Play Game", 'play'),
            ("Designer Mode", 'designer'),
            ("Settings", 'settings'),
            ("Quit", 'quit')
        ]
        super().__init__("KARAOKEFICADOR", items)


class PauseMenu(Menu):
    """Pause menu (in-game)"""

    def __init__(self):
        items = [
            ("Resume", 'resume'),
            ("Designer Mode", 'designer'),
            ("Quit to Menu", 'quit_to_menu'),
            ("Quit Game", 'quit')
        ]
        super().__init__("PAUSED", items)


class MenuManager:
    """Manages menu flow and transitions"""

    # Menu states
    STATE_NONE = None
    STATE_MAIN = 'main'
    STATE_PAUSE = 'pause'
    STATE_SETTINGS = 'settings'

    def __init__(self):
        self.current_state = self.STATE_MAIN
        self.menu_stack = []  # For nested menus
        self.current_menu = MainMenu()

    def push_menu(self, menu_state):
        """Push a new menu onto the stack"""
        self.menu_stack.append(self.current_state)
        self.current_state = menu_state
        self._create_current_menu()

    def pop_menu(self):
        """Return to previous menu"""
        if self.menu_stack:
            self.current_state = self.menu_stack.pop()
            self._create_current_menu()
        else:
            self.current_state = self.STATE_NONE

    def _create_current_menu(self):
        """Create menu object for current state"""
        if self.current_state == self.STATE_MAIN:
            self.current_menu = MainMenu()
        elif self.current_state == self.STATE_PAUSE:
            self.current_menu = PauseMenu()
        elif self.current_state == self.STATE_SETTINGS:
            # TODO: Settings menu
            self.current_menu = MainMenu()  # Placeholder
        else:
            self.current_menu = None

    def update(self):
        """Update current menu"""
        if self.current_menu:
            mouse_pos = pygame.mouse.get_pos()
            self.current_menu.update(mouse_pos)

    def handle_event(self, event):
        """Handle menu events, return action if any"""
        if self.current_menu:
            return self.current_menu.handle_event(event)
        return None

    def draw(self, screen):
        """Draw current menu"""
        if self.current_menu:
            self.current_menu.draw(screen)

    def show_main_menu(self):
        """Show main menu"""
        self.current_state = self.STATE_MAIN
        self._create_current_menu()

    def show_pause_menu(self):
        """Show pause menu"""
        self.current_state = self.STATE_PAUSE
        self._create_current_menu()

    def hide_menu(self):
        """Hide all menus"""
        self.current_state = self.STATE_NONE
        self.current_menu = None

    def is_active(self):
        """Check if any menu is active"""
        return self.current_state is not None
