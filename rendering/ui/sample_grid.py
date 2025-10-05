"""
Grid-based sample browser with fuzzy search.

Displays samples in an infinite scrollable grid, with search filtering.
"""

import pygame


class SampleGrid:
    """
    Infinite grid browser for audio samples.

    Each cell shows a sample name and can be clicked/selected.
    Supports fuzzy search filtering.
    """

    def __init__(self, x, y, width, height):
        """
        Create sample grid.

        Args:
            x, y: Top-left position
            width, height: Grid dimensions
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Grid configuration
        self.cell_width = 180
        self.cell_height = 80
        self.padding = 5
        self.cols = max(1, (width - self.padding) // (self.cell_width + self.padding))

        # Sample data
        self.all_samples = []  # All available samples
        self.filtered_samples = []  # Currently displayed (after search filter)
        self.selected_index = 0

        # Scroll state
        self.scroll_offset = 0  # Row offset

        # Search filter
        self.search_query = ""
        self.search_active = False

        # Colors
        self.bg_color = (20, 20, 30)
        self.cell_bg_color = (35, 35, 45)
        self.cell_selected_color = (80, 120, 160)
        self.cell_hover_color = (50, 60, 80)
        self.cell_border_color = (60, 60, 70)
        self.text_color = (200, 200, 200)
        self.highlight_color = (255, 255, 100)
        self.search_bg_color = (40, 40, 50)
        self.search_text_color = (255, 255, 255)

        # Fonts
        self.font = pygame.font.Font(None, 18)
        self.small_font = pygame.font.Font(None, 14)
        self.search_font = pygame.font.Font(None, 24)

    def set_samples(self, samples_info):
        """
        Set available samples.

        Args:
            samples_info: List of dicts with sample info
        """
        self.all_samples = samples_info
        self._apply_filter()

    def _apply_filter(self):
        """Apply search filter to samples"""
        if not self.search_query:
            self.filtered_samples = self.all_samples
        else:
            query_lower = self.search_query.lower()
            self.filtered_samples = [
                s for s in self.all_samples
                if self._fuzzy_match(query_lower, s)
            ]

        # Reset selection if out of bounds
        if self.selected_index >= len(self.filtered_samples):
            self.selected_index = max(0, len(self.filtered_samples) - 1)

    def _fuzzy_match(self, query, sample):
        """
        Fuzzy match search query against sample.

        Matches against: name, category, tags, description
        """
        name = sample.get('name', '').lower()
        category = sample.get('category', '').lower()
        tags = sample.get('tags', '').lower()
        description = sample.get('description', '').lower()

        # Check if query appears in any field
        return (query in name or
                query in category or
                query in tags or
                query in description)

    def add_search_char(self, char):
        """Add character to search query"""
        self.search_query += char
        self._apply_filter()

    def backspace_search(self):
        """Remove last character from search query"""
        if self.search_query:
            self.search_query = self.search_query[:-1]
            self._apply_filter()

    def clear_search(self):
        """Clear search query"""
        self.search_query = ""
        self._apply_filter()

    def get_selected_sample_name(self):
        """Get name of currently selected sample"""
        if 0 <= self.selected_index < len(self.filtered_samples):
            return self.filtered_samples[self.selected_index]['name']
        return None

    def get_selected_sample(self):
        """Get currently selected sample dict"""
        if 0 <= self.selected_index < len(self.filtered_samples):
            return self.filtered_samples[self.selected_index]
        return None

    def move_selection(self, delta_x, delta_y):
        """
        Move selection within grid.

        Args:
            delta_x: -1 for left, +1 for right
            delta_y: -1 for up, +1 for down
        """
        if not self.filtered_samples:
            return

        # Calculate current row and column
        current_row = self.selected_index // self.cols
        current_col = self.selected_index % self.cols

        # Apply movement
        new_col = current_col + delta_x
        new_row = current_row + delta_y

        # Clamp column
        new_col = max(0, min(new_col, self.cols - 1))

        # Calculate new index
        new_index = new_row * self.cols + new_col

        # Clamp to valid range
        new_index = max(0, min(new_index, len(self.filtered_samples) - 1))

        self.selected_index = new_index

        # Adjust scroll to keep selection visible
        visible_rows = self.height // (self.cell_height + self.padding)
        selected_row = self.selected_index // self.cols

        if selected_row < self.scroll_offset:
            self.scroll_offset = selected_row
        elif selected_row >= self.scroll_offset + visible_rows:
            self.scroll_offset = selected_row - visible_rows + 1

    def handle_click(self, mouse_x, mouse_y):
        """
        Handle mouse click on grid.

        Returns:
            True if clicked inside grid
        """
        # Check if click is in search bar
        search_bar_height = 35
        if (self.x <= mouse_x <= self.x + self.width and
            self.y <= mouse_y <= self.y + search_bar_height):
            self.search_active = True
            return True

        # Check if click is in grid area
        grid_y_start = self.y + search_bar_height + 5
        if not (self.x <= mouse_x <= self.x + self.width and
                grid_y_start <= mouse_y <= self.y + self.height):
            return False

        # Calculate which cell was clicked
        relative_x = mouse_x - self.x
        relative_y = mouse_y - grid_y_start

        col = int(relative_x / (self.cell_width + self.padding))
        row = int(relative_y / (self.cell_height + self.padding)) + self.scroll_offset

        # Check if valid cell
        if 0 <= col < self.cols:
            index = row * self.cols + col
            if 0 <= index < len(self.filtered_samples):
                self.selected_index = index

        return True

    def draw(self, screen):
        """Draw sample grid"""
        # Background
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))

        # Draw search bar
        self._draw_search_bar(screen)

        # Draw grid
        grid_y_start = self.y + 40
        grid_height = self.height - 40
        visible_rows = (grid_height // (self.cell_height + self.padding)) + 1

        if not self.filtered_samples:
            # No samples (or all filtered out)
            msg = "No samples found" if self.search_query else "No samples loaded"
            text = self.font.render(msg, True, (100, 100, 100))
            text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(text, text_rect)
            return

        # Draw visible cells
        for row in range(self.scroll_offset, min(self.scroll_offset + visible_rows,
                        (len(self.filtered_samples) + self.cols - 1) // self.cols)):
            for col in range(self.cols):
                index = row * self.cols + col
                if index >= len(self.filtered_samples):
                    break

                sample = self.filtered_samples[index]

                # Calculate cell position
                cell_x = self.x + col * (self.cell_width + self.padding) + self.padding
                cell_y = grid_y_start + (row - self.scroll_offset) * (self.cell_height + self.padding)

                # Draw cell
                self._draw_cell(screen, sample, cell_x, cell_y, index == self.selected_index)

    def _draw_search_bar(self, screen):
        """Draw search input bar"""
        search_bar_height = 35
        search_bar_rect = pygame.Rect(self.x, self.y, self.width, search_bar_height)

        # Background
        pygame.draw.rect(screen, self.search_bg_color, search_bar_rect)

        # Search icon/label
        label = self.font.render("Search:", True, (150, 150, 150))
        screen.blit(label, (self.x + 10, self.y + 8))

        # Search text
        search_text = self.search_query
        if self.search_active and len(search_text) == 0:
            search_text = "_"  # Cursor placeholder

        text_surf = self.search_font.render(search_text, True, self.search_text_color)
        screen.blit(text_surf, (self.x + 80, self.y + 5))

        # Result count
        result_text = f"({len(self.filtered_samples)} samples)"
        result_surf = self.small_font.render(result_text, True, (120, 120, 120))
        screen.blit(result_surf, (self.x + self.width - 120, self.y + 10))

        # Border
        pygame.draw.rect(screen, (80, 80, 90), search_bar_rect, 2)

    def _draw_cell(self, screen, sample, x, y, is_selected):
        """Draw individual sample cell"""
        cell_rect = pygame.Rect(x, y, self.cell_width, self.cell_height)

        # Background
        if is_selected:
            pygame.draw.rect(screen, self.cell_selected_color, cell_rect)
        else:
            pygame.draw.rect(screen, self.cell_bg_color, cell_rect)

        # Sample name (truncated if too long)
        name = sample['name']
        if len(name) > 20:
            name = name[:17] + "..."

        name_color = self.highlight_color if is_selected else self.text_color
        name_surf = self.font.render(name, True, name_color)
        screen.blit(name_surf, (x + 5, y + 5))

        # Category
        category = sample.get('category', 'Unknown')
        category_surf = self.small_font.render(category, True, (150, 150, 180))
        screen.blit(category_surf, (x + 5, y + 25))

        # Duration
        duration = sample.get('duration', '?')
        duration_surf = self.small_font.render(duration, True, (120, 180, 150))
        screen.blit(duration_surf, (x + 5, y + 45))

        # Tags (if any and space permits)
        tags = sample.get('tags', '')
        if tags and tags != 'No tags':
            tags_short = tags[:15] + "..." if len(tags) > 15 else tags
            tags_surf = self.small_font.render(tags_short, True, (180, 120, 150))
            screen.blit(tags_surf, (x + 5, y + 60))

        # Border
        border_color = self.highlight_color if is_selected else self.cell_border_color
        border_width = 3 if is_selected else 1
        pygame.draw.rect(screen, border_color, cell_rect, border_width)
