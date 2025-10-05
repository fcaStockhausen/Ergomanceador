"""
In-editor metadata editing panel.

Edit sample metadata (category, tags, description) directly in the audio editor UI.
"""

import pygame
import json
import os


class MetadataEditor:
    """
    Panel for editing sample metadata in-place.

    Allows editing:
    - Category (dropdown/text input)
    - Tags (comma-separated input)
    - Description (multiline text area)
    """

    def __init__(self, x, y, width, height):
        """
        Create metadata editor panel.

        Args:
            x, y: Top-left position
            width, height: Panel dimensions
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Current sample being edited
        self.current_sample = None
        self.sample_file_path = None

        # Editable fields
        self.category = ""
        self.tags_text = ""  # Comma-separated string
        self.description = ""

        # UI state
        self.active_field = None  # 'category', 'tags', or 'description'
        self.cursor_visible = True
        self.cursor_blink_timer = 0

        # Predefined categories (for quick selection)
        self.category_options = [
            'impact', 'spell_cast', 'projectile', 'explosion', 'electric',
            'heal', 'shield', 'ambient', 'loop', 'effect', 'voice'
        ]
        self.category_dropdown_open = False

        # Colors
        self.bg_color = (25, 25, 35)
        self.field_bg_color = (40, 40, 50)
        self.field_active_color = (50, 60, 80)
        self.text_color = (200, 200, 200)
        self.label_color = (150, 150, 170)
        self.border_color = (80, 80, 100)
        self.highlight_color = (100, 150, 255)

        # Fonts
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        self.label_font = pygame.font.Font(None, 18)

    def load_sample(self, audio_sample):
        """
        Load sample for editing.

        Args:
            audio_sample: AudioSample instance
        """
        self.current_sample = audio_sample
        self.sample_file_path = audio_sample.file_path

        # Load existing metadata
        self.category = audio_sample.category or 'effect'
        self.tags_text = ', '.join(audio_sample.tags) if audio_sample.tags else ''
        self.description = audio_sample.description or ''

    def save_metadata(self):
        """
        Save metadata to .json sidecar file.

        Returns:
            True if saved successfully
        """
        if not self.sample_file_path:
            return False

        base_path = os.path.splitext(self.sample_file_path)[0]
        json_path = base_path + '.json'

        # Parse tags from comma-separated string
        tags = [tag.strip() for tag in self.tags_text.split(',') if tag.strip()]

        # Create metadata dict
        metadata = {
            'category': self.category,
            'tags': tags,
            'description': self.description,
            'metadata': {
                'edited_in_editor': True
            }
        }

        # Write to file
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            print(f"Saved metadata to {os.path.basename(json_path)}")
            return True
        except Exception as e:
            print(f"Failed to save metadata: {e}")
            return False

    def auto_generate(self):
        """
        Auto-generate metadata using MetadataGenerator.

        Returns:
            True if generated successfully
        """
        if not self.current_sample:
            return False

        from audio.metadata_generator import MetadataGenerator

        generator = MetadataGenerator()
        analysis = generator.analyze_waveform(
            self.current_sample.waveform,
            self.current_sample.sample_rate
        )

        filename = os.path.splitext(os.path.basename(self.sample_file_path))[0]
        self.category = generator.detect_category(filename, analysis)
        tags = generator.generate_tags(filename, self.category)
        self.tags_text = ', '.join(tags)
        self.description = generator.generate_description(filename, self.category, analysis)

        return True

    def handle_event(self, event):
        """
        Handle input events.

        Returns:
            True if event was consumed
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_click(event.pos)

        elif event.type == pygame.KEYDOWN:
            if self.active_field:
                return self._handle_keypress(event)

        return False

    def _handle_click(self, mouse_pos):
        """Handle mouse click on editor fields"""
        mouse_x, mouse_y = mouse_pos

        # Check if click is inside panel
        if not (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height):
            self.active_field = None
            self.category_dropdown_open = False
            return False

        # Category field
        category_y = self.y + 40
        if self.y + 40 <= mouse_y <= self.y + 70:
            self.active_field = 'category'
            self.category_dropdown_open = not self.category_dropdown_open
            return True

        # Tags field
        if self.y + 90 <= mouse_y <= self.y + 120:
            self.active_field = 'tags'
            self.category_dropdown_open = False
            return True

        # Description field
        if self.y + 140 <= mouse_y <= self.y + 280:
            self.active_field = 'description'
            self.category_dropdown_open = False
            return True

        # Auto-generate button
        if self.y + self.height - 40 <= mouse_y <= self.y + self.height - 10:
            if self.x + 10 <= mouse_x <= self.x + 130:
                self.auto_generate()
                return True

        # Save button
        if self.y + self.height - 40 <= mouse_y <= self.y + self.height - 10:
            if self.x + 140 <= mouse_x <= self.x + 240:
                self.save_metadata()
                return True

        # Category dropdown options
        if self.category_dropdown_open:
            dropdown_y = self.y + 70
            for i, option in enumerate(self.category_options):
                option_y = dropdown_y + i * 25
                if option_y <= mouse_y <= option_y + 25:
                    self.category = option
                    self.category_dropdown_open = False
                    return True

        return True

    def _handle_keypress(self, event):
        """Handle keyboard input for active field"""
        if event.key == pygame.K_ESCAPE:
            self.active_field = None
            return True

        elif event.key == pygame.K_TAB:
            # Cycle through fields
            fields = ['category', 'tags', 'description']
            current_idx = fields.index(self.active_field) if self.active_field in fields else -1
            self.active_field = fields[(current_idx + 1) % len(fields)]
            return True

        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            if self.active_field == 'description':
                # Allow newlines in description
                self.description += '\n'
            else:
                # Save on Enter for other fields
                self.save_metadata()
            return True

        elif event.key == pygame.K_BACKSPACE:
            if self.active_field == 'category':
                self.category = self.category[:-1]
            elif self.active_field == 'tags':
                self.tags_text = self.tags_text[:-1]
            elif self.active_field == 'description':
                self.description = self.description[:-1]
            return True

        elif event.unicode and event.unicode.isprintable():
            # Add character to active field
            if self.active_field == 'category':
                self.category += event.unicode
            elif self.active_field == 'tags':
                self.tags_text += event.unicode
            elif self.active_field == 'description':
                self.description += event.unicode
            return True

        return False

    def update(self, dt):
        """Update cursor blink animation"""
        self.cursor_blink_timer += dt
        if self.cursor_blink_timer > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_timer = 0

    def draw(self, screen):
        """Draw metadata editor panel"""
        # Background
        pygame.draw.rect(screen, self.bg_color,
                        (self.x, self.y, self.width, self.height))

        if not self.current_sample:
            # No sample loaded
            text = self.font.render("No sample selected", True, (100, 100, 100))
            text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(text, text_rect)
            pygame.draw.rect(screen, self.border_color,
                           (self.x, self.y, self.width, self.height), 2)
            return

        # Title
        title = self.label_font.render("Metadata Editor", True, self.highlight_color)
        screen.blit(title, (self.x + 10, self.y + 10))

        # Category field
        self._draw_field(screen, "Category", self.category,
                        self.x + 10, self.y + 40, self.width - 20, 30,
                        self.active_field == 'category')

        # Category dropdown
        if self.category_dropdown_open:
            self._draw_category_dropdown(screen)

        # Tags field
        self._draw_field(screen, "Tags (comma-separated)", self.tags_text,
                        self.x + 10, self.y + 90, self.width - 20, 30,
                        self.active_field == 'tags')

        # Description field (multiline)
        self._draw_multiline_field(screen, "Description", self.description,
                                   self.x + 10, self.y + 140, self.width - 20, 140,
                                   self.active_field == 'description')

        # Buttons
        self._draw_button(screen, "Auto-Generate", self.x + 10, self.y + self.height - 40, 120, 30)
        self._draw_button(screen, "Save", self.x + 140, self.y + self.height - 40, 100, 30,
                         color=(80, 150, 100))

        # Border
        pygame.draw.rect(screen, self.border_color,
                        (self.x, self.y, self.width, self.height), 2)

    def _draw_field(self, screen, label, text, x, y, width, height, is_active):
        """Draw single-line text input field"""
        # Label
        label_surf = self.small_font.render(label, True, self.label_color)
        screen.blit(label_surf, (x, y - 18))

        # Field background
        bg_color = self.field_active_color if is_active else self.field_bg_color
        pygame.draw.rect(screen, bg_color, (x, y, width, height))

        # Text
        text_surf = self.font.render(text, True, self.text_color)
        screen.blit(text_surf, (x + 5, y + 5))

        # Cursor (if active and visible)
        if is_active and self.cursor_visible:
            cursor_x = x + 5 + text_surf.get_width()
            pygame.draw.line(screen, self.highlight_color,
                           (cursor_x, y + 5), (cursor_x, y + height - 5), 2)

        # Border
        border_color = self.highlight_color if is_active else self.border_color
        pygame.draw.rect(screen, border_color, (x, y, width, height), 2)

    def _draw_multiline_field(self, screen, label, text, x, y, width, height, is_active):
        """Draw multiline text area"""
        # Label
        label_surf = self.small_font.render(label, True, self.label_color)
        screen.blit(label_surf, (x, y - 18))

        # Field background
        bg_color = self.field_active_color if is_active else self.field_bg_color
        pygame.draw.rect(screen, bg_color, (x, y, width, height))

        # Word-wrap text
        lines = text.split('\n')
        y_offset = y + 5
        for line in lines[:8]:  # Max 8 lines visible
            if line:
                line_surf = self.small_font.render(line[:60], True, self.text_color)  # Truncate long lines
                screen.blit(line_surf, (x + 5, y_offset))
            y_offset += 16

        # Border
        border_color = self.highlight_color if is_active else self.border_color
        pygame.draw.rect(screen, border_color, (x, y, width, height), 2)

    def _draw_category_dropdown(self, screen):
        """Draw category selection dropdown"""
        dropdown_x = self.x + 10
        dropdown_y = self.y + 70
        dropdown_width = self.width - 20

        for i, option in enumerate(self.category_options):
            option_y = dropdown_y + i * 25
            option_rect = pygame.Rect(dropdown_x, option_y, dropdown_width, 25)

            # Background
            pygame.draw.rect(screen, self.field_bg_color, option_rect)

            # Text
            text = self.small_font.render(option, True, self.text_color)
            screen.blit(text, (dropdown_x + 5, option_y + 5))

            # Border
            pygame.draw.rect(screen, self.border_color, option_rect, 1)

    def _draw_button(self, screen, text, x, y, width, height, color=(60, 80, 120)):
        """Draw clickable button"""
        button_rect = pygame.Rect(x, y, width, height)

        # Background
        pygame.draw.rect(screen, color, button_rect)

        # Text
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=button_rect.center)
        screen.blit(text_surf, text_rect)

        # Border
        pygame.draw.rect(screen, (120, 120, 140), button_rect, 2)
