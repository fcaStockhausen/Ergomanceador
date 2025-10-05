"""
Sample browser UI for audio editor.

Browse available sound samples with documentation/metadata display.
"""

import pygame


class SampleBrowser:
    """
    Browser UI for selecting audio samples.
    Shows list of samples with metadata, descriptions, tags.
    """

    def __init__(self, x, y, width, height):
        """
        Create sample browser.

        Args:
            x, y: Top-left position
            width, height: Dimensions
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Sample list
        self.samples = []  # List of dicts with sample info
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_count = 8  # Number of samples visible at once

        # Colors
        self.bg_color = (20, 20, 30)
        self.selected_color = (60, 80, 120)
        self.hover_color = (45, 50, 70)
        self.text_color = (200, 200, 200)
        self.highlight_color = (255, 255, 100)
        self.border_color = (100, 100, 120)

        # Fonts
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)

    def set_samples(self, samples_info):
        """
        Set available samples to browse.

        Args:
            samples_info: List of dicts with sample info from SampleLibrary.get_all_samples_with_info()
        """
        self.samples = samples_info
        self.selected_index = min(self.selected_index, len(self.samples) - 1)
        if self.selected_index < 0:
            self.selected_index = 0

    def get_selected_sample_name(self):
        """Get name of currently selected sample"""
        if 0 <= self.selected_index < len(self.samples):
            return self.samples[self.selected_index]['name']
        return None

    def move_selection(self, delta):
        """
        Move selection up/down.

        Args:
            delta: -1 for up, +1 for down
        """
        if not self.samples:
            return

        self.selected_index = (self.selected_index + delta) % len(self.samples)

        # Adjust scroll to keep selection visible
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_count:
            self.scroll_offset = self.selected_index - self.visible_count + 1

    def handle_click(self, mouse_x, mouse_y):
        """
        Handle mouse click on browser.

        Returns:
            True if clicked inside browser
        """
        if not (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height):
            return False

        # Determine which item was clicked
        item_height = self.height // self.visible_count
        relative_y = mouse_y - self.y
        clicked_index = self.scroll_offset + int(relative_y / item_height)

        if 0 <= clicked_index < len(self.samples):
            self.selected_index = clicked_index

        return True

    def draw(self, screen):
        """Draw sample browser UI"""
        # Background
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))

        if not self.samples:
            # No samples loaded
            text = self.font.render("No samples found", True, (100, 100, 100))
            text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(text, text_rect)
            pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 2)
            return

        # Draw visible samples
        item_height = self.height // self.visible_count
        end_index = min(self.scroll_offset + self.visible_count, len(self.samples))

        for i in range(self.scroll_offset, end_index):
            sample = self.samples[i]
            y_pos = self.y + (i - self.scroll_offset) * item_height

            # Background highlight if selected
            if i == self.selected_index:
                pygame.draw.rect(screen, self.selected_color,
                               (self.x, y_pos, self.width, item_height))

            # Sample name
            name_text = self.font.render(sample['name'], True,
                                        self.highlight_color if i == self.selected_index else self.text_color)
            screen.blit(name_text, (self.x + 10, y_pos + 5))

            # Duration and category
            info_text = f"{sample['duration']} | {sample['category']}"
            info_surf = self.small_font.render(info_text, True, (150, 150, 150))
            screen.blit(info_surf, (self.x + 10, y_pos + 25))

            # Tags (if any)
            if sample.get('tags') and sample['tags'] != 'No tags':
                tags_text = f"Tags: {sample['tags']}"
                tags_surf = self.small_font.render(tags_text, True, (120, 150, 180))
                screen.blit(tags_surf, (self.x + 10, y_pos + 40))

            # Separator line
            pygame.draw.line(screen, (40, 40, 50),
                           (self.x, y_pos + item_height),
                           (self.x + self.width, y_pos + item_height), 1)

        # Scrollbar (if needed)
        if len(self.samples) > self.visible_count:
            self._draw_scrollbar(screen)

        # Border
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 2)

    def _draw_scrollbar(self, screen):
        """Draw scrollbar indicator"""
        scrollbar_x = self.x + self.width - 10
        scrollbar_width = 8

        # Track
        pygame.draw.rect(screen, (40, 40, 50),
                        (scrollbar_x, self.y, scrollbar_width, self.height))

        # Thumb
        thumb_height = max(20, int(self.height * self.visible_count / len(self.samples)))
        thumb_y = self.y + int(self.height * self.scroll_offset / len(self.samples))

        pygame.draw.rect(screen, (100, 100, 120),
                        (scrollbar_x, thumb_y, scrollbar_width, thumb_height))

    def draw_description_panel(self, screen, panel_x, panel_y, panel_width, panel_height):
        """
        Draw description panel showing details of selected sample.

        Args:
            screen: Pygame surface
            panel_x, panel_y: Position of description panel
            panel_width, panel_height: Dimensions of description panel
        """
        if not self.samples or self.selected_index >= len(self.samples):
            return

        sample = self.samples[self.selected_index]

        # Background
        pygame.draw.rect(screen, self.bg_color,
                        (panel_x, panel_y, panel_width, panel_height))

        # Title
        title = self.font.render("Sample Info", True, self.highlight_color)
        screen.blit(title, (panel_x + 10, panel_y + 10))

        # Description
        y_offset = panel_y + 40
        description = sample.get('description', 'No description available')

        # Word wrap description
        words = description.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if self.small_font.size(test_line)[0] > panel_width - 20:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(test_line)
                    current_line = []

        if current_line:
            lines.append(' '.join(current_line))

        # Draw wrapped description
        for line in lines[:10]:  # Max 10 lines
            text = self.small_font.render(line, True, (180, 180, 180))
            screen.blit(text, (panel_x + 10, y_offset))
            y_offset += 18

        # Metadata at bottom
        y_offset = panel_y + panel_height - 80
        meta_lines = [
            f"Filename: {sample['filename']}",
            f"Duration: {sample['duration']}",
            f"Format: {sample['channels']}, {sample['sample_rate']}",
            f"Category: {sample['category']}"
        ]

        for line in meta_lines:
            text = self.small_font.render(line, True, (150, 150, 150))
            screen.blit(text, (panel_x + 10, y_offset))
            y_offset += 18

        # Border
        pygame.draw.rect(screen, self.border_color,
                        (panel_x, panel_y, panel_width, panel_height), 2)
