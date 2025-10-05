"""
Prototype Editor: Visual editor for creating and tuning behavior prototypes.

Features:
- List all prototypes (scrollable)
- Select prototype to edit
- 12D property sliders
- Add/Update/Delete operations
- Validation warnings
- Save to custom_prototypes.json
"""

import pygame
import numpy as np
from typing import Optional
from config.colors import WHITE, BLACK


class Slider:
    """Interactive slider for editing property values"""

    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label

        self.dragging = False
        self.font = pygame.font.Font(None, 16)

    def update(self, mouse_pos, mouse_pressed):
        """Update slider state"""
        slider_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if mouse_pressed and slider_rect.collidepoint(mouse_pos):
            self.dragging = True

        if not mouse_pressed:
            self.dragging = False

        if self.dragging:
            # Calculate value from mouse position
            relative_x = mouse_pos[0] - self.x
            relative_x = max(0, min(self.width, relative_x))
            ratio = relative_x / self.width
            self.value = self.min_val + ratio * (self.max_val - self.min_val)

    def draw(self, screen):
        """Draw slider"""
        # Background track
        pygame.draw.rect(screen, (40, 40, 50), (self.x, self.y, self.width, self.height))

        # Fill (value)
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        fill_width = int(ratio * self.width)
        pygame.draw.rect(screen, (100, 150, 255), (self.x, self.y, fill_width, self.height))

        # Handle (drag point)
        handle_x = self.x + fill_width
        handle_rect = pygame.Rect(handle_x - 3, self.y - 2, 6, self.height + 4)
        color = (255, 200, 100) if self.dragging else (200, 200, 200)
        pygame.draw.rect(screen, color, handle_rect)

        # Border
        pygame.draw.rect(screen, (100, 100, 120), (self.x, self.y, self.width, self.height), 1)

    def get_value(self):
        """Get current value"""
        return self.value

    def set_value(self, value):
        """Set value"""
        self.value = max(self.min_val, min(self.max_val, value))


class PrototypeEditor:
    """Right panel for prototype editing"""

    def __init__(self, x, y, width, height, prototype_manager):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.prototype_manager = prototype_manager

        # Fonts
        self.font_title = pygame.font.Font(None, 32)
        self.font_section = pygame.font.Font(None, 24)
        self.font_text = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)

        # Colors
        self.bg_color = (20, 20, 30)
        self.border_color = (100, 100, 150)
        self.section_color = (30, 30, 50)

        # State
        self.selected_prototype = None
        self.editing_vector = None
        self.sliders = []
        self.scroll_offset = 0

        # Validation results
        self.validation = None

        # Create sliders for 12D editing
        self._create_sliders()

    def _create_sliders(self):
        """Create 12 sliders for property vector editing"""
        slider_labels = [
            'Thermal Flux',
            'Avg Temperature',
            'Temp Differential',
            'State Transition',
            'Phase Diversity',
            'Density Gradient',
            'Avg Density',
            'Volatility',
            'Chaos Factor',
            'Total Energy',
            'Energy Density',
            'Polarity'
        ]

        slider_x = self.x + 20
        slider_y_start = 200
        slider_width = 300
        slider_height = 12
        slider_spacing = 30

        for i, label in enumerate(slider_labels):
            # Most values are 0-1, polarity is -1 to 1
            if label == 'Polarity':
                min_val, max_val = -1.0, 1.0
            else:
                min_val, max_val = 0.0, 1.0

            slider = Slider(
                x=slider_x + 150,
                y=slider_y_start + i * slider_spacing,
                width=slider_width,
                height=slider_height,
                min_val=min_val,
                max_val=max_val,
                initial_val=0.5 if label != 'Polarity' else 0.0,
                label=label
            )
            self.sliders.append(slider)

    def render(self, screen):
        """Render the prototype editor"""
        # Background panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, panel_rect)
        pygame.draw.rect(screen, self.border_color, panel_rect, 2)

        # Title
        title = self.font_title.render("⚙️ Prototype Editor", True, (255, 200, 100))
        screen.blit(title, (self.x + 10, self.y + 10))

        y_offset = 60

        # Prototype list
        y_offset = self._draw_prototype_list(screen, y_offset)

        # Property sliders (if prototype selected)
        if self.selected_prototype:
            y_offset = self._draw_property_sliders(screen, y_offset)

            # Actions
            y_offset = self._draw_actions(screen, y_offset)

            # Validation warnings
            if self.validation:
                self._draw_validation(screen, y_offset)

    def _draw_prototype_list(self, screen, y_offset):
        """Draw list of prototypes"""
        # Section header
        section_rect = pygame.Rect(self.x + 10, self.y + y_offset, self.width - 20, 25)
        pygame.draw.rect(screen, self.section_color, section_rect)
        header = self.font_section.render("Select Prototype:", True, WHITE)
        screen.blit(header, (self.x + 15, self.y + y_offset + 2))
        y_offset += 35

        # List prototypes (show first 4, then scroll)
        all_protos = self.prototype_manager.get_all_prototypes()

        for i, proto in enumerate(all_protos[:6]):
            name = proto['name']
            is_core = proto.get('is_core', False)
            is_selected = self.selected_prototype == name

            # Background if selected
            item_rect = pygame.Rect(self.x + 15, self.y + y_offset, self.width - 30, 22)
            if is_selected:
                pygame.draw.rect(screen, (50, 80, 120), item_rect)

            # Name
            color = (150, 150, 150) if is_core else (255, 255, 255)
            name_text = f"{'▸ ' if is_selected else '  '}{name}"
            name_surf = self.font_text.render(name_text, True, color)
            screen.blit(name_surf, (self.x + 20, self.y + y_offset))

            # Label (core/custom)
            label = "[CORE]" if is_core else "[CUSTOM]"
            label_color = (100, 150, 200) if is_core else (100, 200, 100)
            label_surf = self.font_small.render(label, True, label_color)
            screen.blit(label_surf, (self.x + self.width - 100, self.y + y_offset + 3))

            y_offset += 25

        y_offset += 15

        hint = "Click prototype name to select (core prototypes read-only)"
        hint_surf = self.font_small.render(hint, True, (120, 120, 150))
        screen.blit(hint_surf, (self.x + 20, self.y + y_offset))
        y_offset += 30

        return y_offset

    def _draw_property_sliders(self, screen, y_offset):
        """Draw 12D property sliders"""
        # Section header
        section_rect = pygame.Rect(self.x + 10, self.y + y_offset, self.width - 20, 25)
        pygame.draw.rect(screen, self.section_color, section_rect)
        header_text = f"Edit: {self.selected_prototype}"
        header = self.font_section.render(header_text, True, WHITE)
        screen.blit(header, (self.x + 15, self.y + y_offset + 2))
        y_offset += 35

        # Draw sliders
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        for slider in self.sliders:
            # Label
            label_surf = self.font_small.render(slider.label + ":", True, (180, 180, 180))
            screen.blit(label_surf, (self.x + 20, self.y + y_offset))

            # Slider
            slider.y = self.y + y_offset
            slider.update(mouse_pos, mouse_pressed)
            slider.draw(screen)

            # Value
            value_text = f"{slider.get_value():.3f}"
            value_surf = self.font_small.render(value_text, True, (200, 200, 200))
            screen.blit(value_surf, (slider.x + slider.width + 10, self.y + y_offset))

            y_offset += 30

        y_offset += 20
        return y_offset

    def _draw_actions(self, screen, y_offset):
        """Draw action buttons"""
        # Section header
        section_rect = pygame.Rect(self.x + 10, self.y + y_offset, self.width - 20, 25)
        pygame.draw.rect(screen, self.section_color, section_rect)
        header = self.font_section.render("Actions:", True, WHITE)
        screen.blit(header, (self.x + 15, self.y + y_offset + 2))
        y_offset += 35

        # Action hints (buttons will be clickable in handle_input)
        actions = [
            "U - Update Prototype (save changes)",
            "N - New Prototype (create from current)",
            "D - Delete Prototype (custom only)",
            "V - Validate (check distances)",
            "F4 - Save All to JSON"
        ]

        for action in actions:
            action_surf = self.font_small.render(action, True, (150, 200, 255))
            screen.blit(action_surf, (self.x + 20, self.y + y_offset))
            y_offset += 22

        y_offset += 20
        return y_offset

    def _draw_validation(self, screen, y_offset):
        """Draw validation results"""
        if not self.validation:
            return

        # Section header
        section_rect = pygame.Rect(self.x + 10, self.y + y_offset, self.width - 20, 25)
        pygame.draw.rect(screen, self.section_color, section_rect)
        header = self.font_section.render("Validation:", True, WHITE)
        screen.blit(header, (self.x + 15, self.y + y_offset + 2))
        y_offset += 35

        # Errors
        for error in self.validation.get('errors', []):
            error_surf = self.font_small.render(f"❌ {error}", True, (255, 100, 100))
            screen.blit(error_surf, (self.x + 20, self.y + y_offset))
            y_offset += 20

        # Warnings
        for warning in self.validation.get('warnings', []):
            warn_surf = self.font_small.render(f"⚠️  {warning}", True, (255, 200, 100))
            screen.blit(warn_surf, (self.x + 20, self.y + y_offset))
            y_offset += 20

        # Closest prototype info
        if 'closest_prototype' in self.validation:
            closest = self.validation['closest_prototype']
            distance = self.validation['closest_distance']
            info = f"Closest: {closest} (distance {distance:.3f})"
            info_surf = self.font_small.render(info, True, (150, 150, 255))
            screen.blit(info_surf, (self.x + 20, self.y + y_offset))

    def handle_input(self, event):
        """Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicking on prototype name
            self._handle_prototype_selection(event.pos)

        if event.type == pygame.KEYDOWN:
            # Keyboard shortcuts
            if event.key == pygame.K_u:
                self._update_prototype()
            elif event.key == pygame.K_n:
                self._create_new_prototype()
            elif event.key == pygame.K_d:
                self._delete_prototype()
            elif event.key == pygame.K_v:
                self._validate_current()

    def _handle_prototype_selection(self, mouse_pos):
        """Handle clicking on prototype names"""
        all_protos = self.prototype_manager.get_all_prototypes()

        y_offset = self.y + 95  # Start of prototype list
        for proto in all_protos[:6]:
            item_rect = pygame.Rect(self.x + 15, y_offset, self.width - 30, 22)
            if item_rect.collidepoint(mouse_pos):
                self.selected_prototype = proto['name']
                # Load into sliders
                self._load_prototype_into_sliders(proto['prototype'])
                print(f"Selected prototype: {proto['name']}")
                break
            y_offset += 25

    def _load_prototype_into_sliders(self, vector):
        """Load prototype vector into sliders"""
        for i, slider in enumerate(self.sliders):
            if i < len(vector):
                slider.set_value(vector[i])

    def _get_current_vector(self):
        """Get current vector from sliders"""
        return np.array([slider.get_value() for slider in self.sliders])

    def _update_prototype(self):
        """Update selected prototype"""
        if not self.selected_prototype:
            print("No prototype selected")
            return

        # Check if core prototype (cannot edit)
        proto = self.prototype_manager.get_prototype_by_name(self.selected_prototype)
        if proto and proto.get('is_core', False):
            print(f"Cannot edit core prototype '{self.selected_prototype}'")
            return

        vector = self._get_current_vector()
        success = self.prototype_manager.update_prototype(self.selected_prototype, vector)
        if success:
            print(f"✓ Updated prototype '{self.selected_prototype}'")

    def _create_new_prototype(self):
        """Create new prototype from current sliders"""
        # TODO: Show dialog for name input
        # For now, use placeholder
        name = f"custom_{len(self.prototype_manager.custom_prototypes) + 1}"
        vector = self._get_current_vector()

        success = self.prototype_manager.add_prototype(name, vector)
        if success:
            self.selected_prototype = name
            print(f"✓ Created new prototype '{name}'")

    def _delete_prototype(self):
        """Delete selected custom prototype"""
        if not self.selected_prototype:
            print("No prototype selected")
            return

        success = self.prototype_manager.delete_prototype(self.selected_prototype)
        if success:
            self.selected_prototype = None
            print(f"✓ Deleted prototype")

    def _validate_current(self):
        """Validate current prototype"""
        if not self.selected_prototype:
            print("No prototype selected")
            return

        vector = self._get_current_vector()
        self.validation = self.prototype_manager.validate_prototype(
            self.selected_prototype, vector
        )
        print("✓ Validation complete")
