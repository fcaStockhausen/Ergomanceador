"""
Waveform display with scrolling to set start point.

Scroll to trim the beginning - what you see starting at 0 is what plays.
"""

import pygame
import numpy as np


class WaveformDisplay:
    """
    Waveform with scroll to set start point.
    
    - Left edge is always time 0 (where sound starts)
    - Scroll with wheel or drag to move which part of audio is at time 0
    - ADSR always starts at time 0 (left edge)
    - Waveform shows ADSR effect baked in
    """

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Scroll offset - which part of audio starts at time 0
        self.scroll_offset = 0.0  # Seconds into the audio file
        self.view_duration = 3.0  # How many seconds to show

        # Dragging state
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_offset = 0.0

        # Colors
        self.bg_color = (20, 20, 30)
        self.grid_color = (40, 40, 50)
        self.waveform_color = (100, 200, 255)
        self.waveform_processed_color = (255, 150, 100)
        self.center_line_color = (60, 60, 70)
        self.time_marker_color = (150, 150, 170)
        self.zero_line_color = (255, 100, 100)

    def handle_wheel(self, mouse_y, wheel_y, fine_adjust=False):
        """
        Scroll to adjust start point.

        Args:
            mouse_y: Mouse Y position
            wheel_y: Wheel delta
            fine_adjust: If True, use fine adjustment (0.01s instead of 0.1s)
        """
        if not (self.y <= mouse_y <= self.y + self.height):
            return False

        # Fine adjustment with Cmd/Ctrl, normal with just wheel
        step = 0.01 if fine_adjust else 0.1

        # Scroll (negative for natural scroll direction)
        self.scroll_offset -= wheel_y * step
        self.scroll_offset = max(0.0, self.scroll_offset)
        return True

    def handle_mouse_down(self, mouse_x, mouse_y):
        """Start dragging to scroll"""
        if not (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height):
            return False

        self.dragging = True
        self.drag_start_x = mouse_x
        self.drag_start_offset = self.scroll_offset
        return True

    def handle_mouse_up(self):
        """Stop dragging"""
        self.dragging = False

    def handle_mouse_motion(self, mouse_x, mouse_y):
        """Drag to scroll (very fine control)"""
        if not self.dragging:
            return False

        # Convert pixel drag to time offset
        # More pixels = more precise control
        drag_delta_pixels = self.drag_start_x - mouse_x
        
        # Each pixel = 0.005 seconds (very fine)
        time_delta = drag_delta_pixels * 0.005
        
        self.scroll_offset = max(0.0, self.drag_start_offset + time_delta)
        return True

    def draw(self, screen, waveform, adsr_envelope=None, sample_rate=22050):
        """
        Draw waveform starting from scroll_offset with ADSR baked in.
        """
        # Background
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.width, self.height))

        if waveform is None or len(waveform) == 0:
            font = pygame.font.Font(None, 24)
            text = font.render("No sample loaded", True, (100, 100, 100))
            text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(text, text_rect)
            pygame.draw.rect(screen, (100, 100, 120), (self.x, self.y, self.width, self.height), 2)
            return

        total_duration = len(waveform) / sample_rate
        
        # Get visible portion starting from scroll offset
        start_sample = int(self.scroll_offset * sample_rate)
        end_sample = int((self.scroll_offset + self.view_duration) * sample_rate)
        end_sample = min(end_sample, len(waveform))
        
        visible_waveform = waveform[start_sample:end_sample].copy()

        if len(visible_waveform) == 0:
            return

        # Apply ADSR starting from time 0 (left edge)
        if adsr_envelope:
            # ADSR envelope always starts at 0, regardless of scroll
            envelope_duration = len(visible_waveform) / sample_rate
            envelope_curve = adsr_envelope.generate_envelope(envelope_duration, sample_rate)
            
            min_len = min(len(visible_waveform), len(envelope_curve))
            # MULTIPLY waveform by envelope - you SEE the effect!
            visible_waveform = visible_waveform[:min_len] * envelope_curve[:min_len]

        # Draw grid
        self._draw_grid(screen)

        # Center line
        center_y = self.y + self.height // 2
        pygame.draw.line(screen, self.center_line_color,
                        (self.x, center_y), (self.x + self.width, center_y), 2)

        # Time 0 marker (left edge - where sound starts)
        pygame.draw.line(screen, self.zero_line_color,
                       (self.x, self.y), (self.x, self.y + self.height), 3)

        # Draw waveform (color shows if ADSR is active)
        color = self.waveform_processed_color if adsr_envelope else self.waveform_color
        self._draw_waveform(screen, visible_waveform, color)

        # Time markers
        self._draw_time_markers(screen, total_duration)

        # Border
        border_color = (255, 255, 100) if self.dragging else (100, 100, 120)
        pygame.draw.rect(screen, border_color, (self.x, self.y, self.width, self.height), 2)

    def _draw_grid(self, screen):
        """Grid lines"""
        # Horizontal
        for i in range(5):
            y = self.y + int(i * self.height / 4)
            pygame.draw.line(screen, self.grid_color, (self.x, y), (self.x + self.width, y), 1)

        # Vertical
        for i in range(7):
            x = self.x + int(i * self.width / 6)
            pygame.draw.line(screen, self.grid_color, (x, self.y), (x, self.y + self.height), 1)

    def _draw_waveform(self, screen, visible_waveform, color):
        """Draw waveform"""
        if len(visible_waveform) < 2:
            return

        # Downsample
        samples_per_pixel = max(1, len(visible_waveform) // self.width)
        if samples_per_pixel > 1:
            num_pixels = len(visible_waveform) // samples_per_pixel
            chunks = visible_waveform[:num_pixels * samples_per_pixel].reshape(num_pixels, samples_per_pixel)
            downsampled = np.max(np.abs(chunks), axis=1) * np.sign(np.mean(chunks, axis=1))
        else:
            downsampled = visible_waveform

        # Convert to points
        points = []
        center_y = self.y + self.height // 2
        for i, sample in enumerate(downsampled):
            x = self.x + int(i * self.width / len(downsampled))
            y = center_y - int(sample * (self.height // 2) * 0.9)
            points.append((x, y))

        if len(points) > 1:
            pygame.draw.lines(screen, color, False, points, 2)

    def _draw_time_markers(self, screen, total_duration):
        """Show scroll offset info"""
        font = pygame.font.Font(None, 18)
        
        # Show start offset (where time 0 is in the original file)
        text = font.render(f"Start: {self.scroll_offset:.3f}s", True, (255, 255, 100))
        screen.blit(text, (self.x + 5, self.y + 5))
        
        # Show instructions if dragging
        if self.dragging:
            hint = font.render("Dragging...", True, (255, 255, 100))
            screen.blit(hint, (self.x + self.width - 100, self.y + 5))

    def clear_selection(self):
        """Reset to beginning"""
        self.scroll_offset = 0.0

    def get_selection_range(self, total_samples, sample_rate):
        """Get start/end time"""
        total_duration = total_samples / sample_rate
        end_time = min(self.scroll_offset + self.view_duration, total_duration)
        return self.scroll_offset, end_time
