"""
Full-screen metadata editor modal with 8D sound vector sliders.

Press M in audio editor to open.
Edit category, tags, description, and 8D sound manifold vector.
"""

import pygame
from audio.sound_manifold import SoundManifold, SoundVector


class MetadataModal:
    """
    Full-screen modal for editing sample metadata and sound vector.

    Features:
    - Category selection with prototype loading
    - 8D sound vector sliders (attack, decay, brightness, etc.)
    - Tags input
    - Description textarea
    - Save/Cancel buttons
    """

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Modal state
        self.active = False
        self.current_sample = None

        # Editable fields
        self.category = ""
        self.tags_text = ""
        self.description = ""
        self.sound_vector = SoundVector()

        # Category prototypes
        self.categories = SoundManifold.list_categories()
        self.selected_category_index = 0

        # 8D sliders
        self.slider_names = [
            'attack', 'decay', 'brightness', 'richness',
            'texture', 'density', 'intensity', 'temperature'
        ]
        self.active_slider = None
        self.dragging_slider = False

        # Colors
        self.overlay_color = (0, 0, 0, 180)  # Semi-transparent black
        self.panel_color = (30, 30, 40)
        self.field_bg = (45, 45, 55)
        self.slider_track = (60, 60, 70)
        self.slider_fill = (100, 200, 255)
        self.text_color = (220, 220, 220)
        self.label_color = (150, 150, 170)
        self.button_color = (60, 120, 200)
        self.button_hover = (80, 140, 220)

        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Layout
        self.panel_width = 900
        self.panel_height = 650
        self.panel_x = (screen_width - self.panel_width) // 2
        self.panel_y = (screen_height - self.panel_height) // 2

        self._setup_ui_rects()

    def _setup_ui_rects(self):
        """Setup UI element positions"""
        margin = 30
        left_x = self.panel_x + margin
        right_x = self.panel_x + self.panel_width // 2 + 10
        y = self.panel_y + 60

        # Left column: Category + Tags + Description
        self.category_rect = pygame.Rect(left_x, y, 350, 35)
        y += 50

        self.tags_rect = pygame.Rect(left_x, y, 350, 35)
        y += 50

        self.desc_rect = pygame.Rect(left_x, y, 350, 120)
        y += 140

        # Prototype button
        self.load_prototype_btn = pygame.Rect(left_x, y, 170, 35)

        # Right column: 8D Sliders
        slider_y = self.panel_y + 60
        slider_width = 350
        slider_height = 20
        slider_spacing = 60

        self.sliders = {}
        for i, name in enumerate(self.slider_names):
            self.sliders[name] = {
                'rect': pygame.Rect(right_x, slider_y + i * slider_spacing, slider_width, slider_height),
                'label_y': slider_y + i * slider_spacing - 22,
                'value': getattr(self.sound_vector, name)
            }

        # Bottom buttons
        btn_y = self.panel_y + self.panel_height - 60
        btn_width = 120
        btn_spacing = 20

        self.save_btn = pygame.Rect(
            self.panel_x + self.panel_width - btn_width * 2 - btn_spacing - margin,
            btn_y, btn_width, 40
        )
        self.cancel_btn = pygame.Rect(
            self.panel_x + self.panel_width - btn_width - margin,
            btn_y, btn_width, 40
        )

    def open(self, audio_sample):
        """
        Open modal for editing sample.

        Args:
            audio_sample: AudioSample to edit
        """
        self.active = True
        self.current_sample = audio_sample

        # Load current values
        self.category = audio_sample.category or ""
        self.tags_text = ', '.join(audio_sample.tags) if audio_sample.tags else ""
        self.description = audio_sample.description or ""
        self.sound_vector = SoundVector(
            attack=audio_sample.sound_vector.attack,
            decay=audio_sample.sound_vector.decay,
            brightness=audio_sample.sound_vector.brightness,
            richness=audio_sample.sound_vector.richness,
            texture=audio_sample.sound_vector.texture,
            density=audio_sample.sound_vector.density,
            intensity=audio_sample.sound_vector.intensity,
            temperature=audio_sample.sound_vector.temperature
        )

        # Sync slider values
        for name in self.slider_names:
            self.sliders[name]['value'] = getattr(self.sound_vector, name)

    def close(self):
        """Close modal without saving"""
        self.active = False
        self.current_sample = None

    def save_and_close(self):
        """Save changes and close"""
        if not self.current_sample:
            return

        # Update sample
        self.current_sample.category = self.category
        self.current_sample.tags = [t.strip() for t in self.tags_text.split(',') if t.strip()]
        self.current_sample.description = self.description

        # Update sound vector
        self.current_sample.sound_vector = SoundVector(
            attack=self.sliders['attack']['value'],
            decay=self.sliders['decay']['value'],
            brightness=self.sliders['brightness']['value'],
            richness=self.sliders['richness']['value'],
            texture=self.sliders['texture']['value'],
            density=self.sliders['density']['value'],
            intensity=self.sliders['intensity']['value'],
            temperature=self.sliders['temperature']['value']
        )

        # Save to JSON
        self.current_sample.save_metadata()
        print(f"✓ Saved metadata for {self.current_sample.get_display_info()['filename']}")

        self.close()

    def load_category_prototype(self):
        """Load sound vector from category prototype"""
        if not self.category:
            return

        prototype = SoundManifold.get_category_prototype(self.category)
        if prototype:
            self.sound_vector = SoundVector(
                attack=prototype.attack,
                decay=prototype.decay,
                brightness=prototype.brightness,
                richness=prototype.richness,
                texture=prototype.texture,
                density=prototype.density,
                intensity=prototype.intensity,
                temperature=prototype.temperature
            )

            # Sync sliders
            for name in self.slider_names:
                self.sliders[name]['value'] = getattr(self.sound_vector, name)

            print(f"Loaded '{self.category}' prototype")

    def handle_event(self, event):
        """
        Handle input events.

        Returns:
            True if event was handled, False otherwise
        """
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True
            elif event.key == pygame.K_RETURN:
                self.save_and_close()
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Check buttons
            if self.save_btn.collidepoint(mouse_x, mouse_y):
                self.save_and_close()
                return True
            elif self.cancel_btn.collidepoint(mouse_x, mouse_y):
                self.close()
                return True
            elif self.load_prototype_btn.collidepoint(mouse_x, mouse_y):
                self.load_category_prototype()
                return True

            # Check sliders
            for name, slider in self.sliders.items():
                if slider['rect'].collidepoint(mouse_x, mouse_y):
                    self.active_slider = name
                    self.dragging_slider = True
                    self._update_slider_value(name, mouse_x)
                    return True

            # Check text fields (simple click detection)
            if self.category_rect.collidepoint(mouse_x, mouse_y):
                # Cycle through categories
                self.selected_category_index = (self.selected_category_index + 1) % len(self.categories)
                self.category = self.categories[self.selected_category_index]
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_slider:
                self.dragging_slider = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_slider and self.active_slider:
                mouse_x, _ = event.pos
                self._update_slider_value(self.active_slider, mouse_x)
                return True

        return False

    def _update_slider_value(self, slider_name, mouse_x):
        """Update slider value from mouse position"""
        slider = self.sliders[slider_name]
        rect = slider['rect']

        # Calculate normalized value (0-1)
        normalized = (mouse_x - rect.x) / rect.width
        normalized = max(0.0, min(1.0, normalized))

        slider['value'] = normalized

    def render(self, screen):
        """Render modal overlay"""
        if not self.active:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Main panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(screen, self.panel_color, panel_rect)
        pygame.draw.rect(screen, (100, 100, 120), panel_rect, 2)

        # Title
        title = self.title_font.render("Sound Metadata Editor", True, (255, 200, 100))
        screen.blit(title, (self.panel_x + 30, self.panel_y + 15))

        # Instructions
        hint = self.small_font.render("ESC: cancel | ENTER: save | Click category to cycle", True, (150, 150, 150))
        screen.blit(hint, (self.panel_x + 30, self.panel_y + self.panel_height - 25))

        # Left column
        self._draw_left_column(screen)

        # Right column (8D sliders)
        self._draw_sliders(screen)

        # Buttons
        self._draw_buttons(screen)

    def _draw_left_column(self, screen):
        """Draw category, tags, description fields"""
        y_offset = self.panel_y + 60

        # Category
        label = self.font.render("Category:", True, self.label_color)
        screen.blit(label, (self.category_rect.x, y_offset - 25))

        pygame.draw.rect(screen, self.field_bg, self.category_rect)
        pygame.draw.rect(screen, (100, 150, 255), self.category_rect, 2)

        cat_text = self.font.render(self.category or "(click to select)", True, self.text_color)
        screen.blit(cat_text, (self.category_rect.x + 10, self.category_rect.y + 8))

        y_offset += 50

        # Tags
        label = self.font.render("Tags (comma-separated):", True, self.label_color)
        screen.blit(label, (self.tags_rect.x, y_offset - 25))

        pygame.draw.rect(screen, self.field_bg, self.tags_rect)
        pygame.draw.rect(screen, (80, 80, 100), self.tags_rect, 1)

        tags_text = self.small_font.render(self.tags_text[:40], True, self.text_color)
        screen.blit(tags_text, (self.tags_rect.x + 10, self.tags_rect.y + 10))

        y_offset += 50

        # Description
        label = self.font.render("Description:", True, self.label_color)
        screen.blit(label, (self.desc_rect.x, y_offset - 25))

        pygame.draw.rect(screen, self.field_bg, self.desc_rect)
        pygame.draw.rect(screen, (80, 80, 100), self.desc_rect, 1)

        # Word wrap description
        words = self.description.split()
        lines = []
        current_line = []
        for word in words[:50]:  # Limit words
            test_line = ' '.join(current_line + [word])
            if self.small_font.size(test_line)[0] < self.desc_rect.width - 20:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        for i, line in enumerate(lines[:5]):  # Max 5 lines
            text = self.small_font.render(line, True, self.text_color)
            screen.blit(text, (self.desc_rect.x + 10, self.desc_rect.y + 10 + i * 20))

        # Load Prototype button
        btn_color = self.button_hover if self.category else self.button_color
        pygame.draw.rect(screen, btn_color, self.load_prototype_btn)
        btn_text = self.font.render("Load Prototype", True, (255, 255, 255))
        btn_text_rect = btn_text.get_rect(center=self.load_prototype_btn.center)
        screen.blit(btn_text, btn_text_rect)

    def _draw_sliders(self, screen):
        """Draw 8D sound vector sliders"""
        title = self.font.render("8D Sound Vector", True, (255, 200, 100))
        screen.blit(title, (self.sliders['attack']['rect'].x, self.panel_y + 60 - 35))

        for name, slider in self.sliders.items():
            rect = slider['rect']
            value = slider['value']

            # Label
            label_text = f"{name.capitalize()}: {value:.2f}"
            label = self.small_font.render(label_text, True, self.label_color)
            screen.blit(label, (rect.x, slider['label_y']))

            # Track
            pygame.draw.rect(screen, self.slider_track, rect)

            # Fill
            fill_width = int(value * rect.width)
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
            pygame.draw.rect(screen, self.slider_fill, fill_rect)

            # Border
            border_color = (150, 200, 255) if name == self.active_slider else (100, 100, 120)
            pygame.draw.rect(screen, border_color, rect, 2)

    def _draw_buttons(self, screen):
        """Draw save/cancel buttons"""
        mouse_pos = pygame.mouse.get_pos()

        # Save button
        save_hover = self.save_btn.collidepoint(mouse_pos)
        save_color = self.button_hover if save_hover else self.button_color
        pygame.draw.rect(screen, save_color, self.save_btn)
        save_text = self.font.render("Save", True, (255, 255, 255))
        save_text_rect = save_text.get_rect(center=self.save_btn.center)
        screen.blit(save_text, save_text_rect)

        # Cancel button
        cancel_hover = self.cancel_btn.collidepoint(mouse_pos)
        cancel_color = (120, 60, 60) if cancel_hover else (80, 40, 40)
        pygame.draw.rect(screen, cancel_color, self.cancel_btn)
        cancel_text = self.font.render("Cancel", True, (255, 255, 255))
        cancel_text_rect = cancel_text.get_rect(center=self.cancel_btn.center)
        screen.blit(cancel_text, cancel_text_rect)
