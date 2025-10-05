"""
Standalone audio editor - no programming required!

Simple GUI tool for sound designers to:
1. Drop audio files in data/sounds/
2. Auto-generate metadata
3. Edit tags/category/description in UI
4. Assign to game behaviors
5. Preview with ADSR envelopes

No JSON editing, no command line, no programming!
"""

import pygame
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio.sample_loader import SampleLibrary
from audio.adsr_envelope import ADSREnvelope, PRESETS
from audio.metadata_generator import MetadataGenerator
from rendering.ui.sample_grid import SampleGrid
from rendering.ui.waveform_display import WaveformDisplay
from rendering.ui.metadata_editor import MetadataEditor


class StandaloneAudioEditor:
    """
    Standalone audio editor application.

    Friendly interface for non-programmers to manage game sounds.
    """

    def __init__(self):
        """Initialize standalone editor"""
        pygame.init()
        pygame.mixer.init()

        # Screen
        self.screen_width = 1400
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Karaokeficador - Audio Editor")

        self.clock = pygame.time.Clock()
        self.running = True

        # Sample library
        self.library = SampleLibrary()
        self.library.scan_directory()

        # Auto-generate missing metadata
        self.generator = MetadataGenerator()
        generated = self.generator.batch_generate(self.library, overwrite=False)
        if generated:
            # Reload samples to pick up new metadata
            self.library.scan_directory()

        # UI Components
        # Left side: Sample grid browser
        self.sample_grid = SampleGrid(10, 10, 600, 780)
        self.sample_grid.set_samples(self.library.get_all_samples_with_info())

        # Right side: Waveform + metadata + ADSR
        self.waveform_display = WaveformDisplay(630, 10, 760, 200)
        self.metadata_editor = MetadataEditor(630, 220, 360, 350)
        self.adsr_panel_x = 1000
        self.adsr_panel_y = 220

        # Current state
        self.current_sample = None
        self.current_envelope = ADSREnvelope()

        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # ADSR sliders
        self._setup_adsr_sliders()

        # Colors
        self.bg_color = (20, 20, 30)
        self.panel_bg_color = (30, 30, 40)

        # Help text
        self.show_help = True

    def _setup_adsr_sliders(self):
        """Setup ADSR slider positions"""
        slider_width = 350
        slider_height = 20
        slider_spacing = 50

        self.sliders = {
            'attack': {
                'x': self.adsr_panel_x + 10,
                'y': self.adsr_panel_y + 40,
                'width': slider_width,
                'height': slider_height,
                'min': 0.0,
                'max': 1.0,
                'value': self.current_envelope.attack_time,
                'label': 'Attack (s)'
            },
            'decay': {
                'x': self.adsr_panel_x + 10,
                'y': self.adsr_panel_y + 90,
                'width': slider_width,
                'height': slider_height,
                'min': 0.0,
                'max': 1.0,
                'value': self.current_envelope.decay_time,
                'label': 'Decay (s)'
            },
            'sustain': {
                'x': self.adsr_panel_x + 10,
                'y': self.adsr_panel_y + 140,
                'width': slider_width,
                'height': slider_height,
                'min': 0.0,
                'max': 1.0,
                'value': self.current_envelope.sustain_level,
                'label': 'Sustain (level)'
            },
            'release': {
                'x': self.adsr_panel_x + 10,
                'y': self.adsr_panel_y + 190,
                'width': slider_width,
                'height': slider_height,
                'min': 0.0,
                'max': 1.0,
                'value': self.current_envelope.release_time,
                'label': 'Release (s)'
            }
        }

    def run(self):
        """Main loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    self.handle_keypress(event)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0]:  # Left button held
                        self._handle_slider_drag(event.pos)

                # Pass events to metadata editor
                self.metadata_editor.handle_event(event)

            # Update
            self.metadata_editor.update(dt)

            # Render
            self.render()

            pygame.display.flip()

        pygame.quit()

    def handle_keypress(self, event):
        """Handle keyboard input"""
        if event.key == pygame.K_ESCAPE:
            self.running = False

        elif event.key == pygame.K_F1:
            self.show_help = not self.show_help

        elif event.key == pygame.K_SPACE:
            # Preview sample
            if self.current_sample:
                self.current_sample.play()

        elif event.key == pygame.K_r:
            # Rescan directory
            self.library.scan_directory()
            self.sample_grid.set_samples(self.library.get_all_samples_with_info())

        elif event.key == pygame.K_g:
            # Auto-generate metadata for current sample
            if self.current_sample:
                self.metadata_editor.auto_generate()

        elif event.key == pygame.K_UP:
            self.sample_grid.move_selection(0, -1)
            self._load_selected_sample()

        elif event.key == pygame.K_DOWN:
            self.sample_grid.move_selection(0, 1)
            self._load_selected_sample()

        elif event.key == pygame.K_LEFT:
            self.sample_grid.move_selection(-1, 0)
            self._load_selected_sample()

        elif event.key == pygame.K_RIGHT:
            self.sample_grid.move_selection(1, 0)
            self._load_selected_sample()

        elif event.key == pygame.K_BACKSPACE:
            self.sample_grid.backspace_search()

        elif event.unicode and event.unicode.isprintable() and not self.metadata_editor.active_field:
            # Type to search (only if not editing metadata)
            self.sample_grid.add_search_char(event.unicode)

    def handle_click(self, mouse_pos):
        """Handle mouse clicks"""
        # Check sample grid
        if self.sample_grid.handle_click(mouse_pos[0], mouse_pos[1]):
            self._load_selected_sample()

        # Check ADSR sliders
        self._handle_slider_click(mouse_pos[0], mouse_pos[1])

    def _load_selected_sample(self):
        """Load currently selected sample from grid"""
        sample_name = self.sample_grid.get_selected_sample_name()
        if sample_name:
            self.current_sample = self.library.get_sample(sample_name)
            if self.current_sample:
                # Load in metadata editor
                self.metadata_editor.load_sample(self.current_sample)

    def _handle_slider_click(self, mouse_x, mouse_y):
        """Handle clicks on ADSR sliders"""
        for param, slider in self.sliders.items():
            if (slider['x'] <= mouse_x <= slider['x'] + slider['width'] and
                slider['y'] <= mouse_y <= slider['y'] + slider['height']):
                # Calculate new value
                normalized = (mouse_x - slider['x']) / slider['width']
                slider['value'] = slider['min'] + normalized * (slider['max'] - slider['min'])
                self._update_envelope()

    def _handle_slider_drag(self, mouse_pos):
        """Handle dragging ADSR sliders"""
        mouse_x, mouse_y = mouse_pos
        for param, slider in self.sliders.items():
            if (slider['x'] <= mouse_x <= slider['x'] + slider['width'] and
                slider['y'] - 10 <= mouse_y <= slider['y'] + slider['height'] + 10):
                # Calculate new value
                normalized = max(0.0, min(1.0, (mouse_x - slider['x']) / slider['width']))
                slider['value'] = slider['min'] + normalized * (slider['max'] - slider['min'])
                self._update_envelope()

    def _update_envelope(self):
        """Update ADSR envelope from slider values"""
        self.current_envelope = ADSREnvelope(
            attack_time=self.sliders['attack']['value'],
            decay_time=self.sliders['decay']['value'],
            sustain_level=self.sliders['sustain']['value'],
            release_time=self.sliders['release']['value']
        )

    def render(self):
        """Render UI"""
        # Background
        self.screen.fill(self.bg_color)

        # Title bar
        title = self.font.render("Audio Editor - Sound Designer Tool", True, (255, 200, 100))
        self.screen.blit(title, (10, self.screen_height - 35))

        # Sample count
        count_text = self.small_font.render(
            f"{len(self.library.samples)} samples loaded | Press F1 for help",
            True, (150, 150, 150)
        )
        self.screen.blit(count_text, (self.screen_width - 300, self.screen_height - 30))

        # Sample grid (left side)
        self.sample_grid.draw(self.screen)

        # Waveform (top right)
        waveform = self.current_sample.waveform if self.current_sample else None
        self.waveform_display.draw(self.screen, waveform, self.current_envelope)

        # Metadata editor (middle right)
        self.metadata_editor.draw(self.screen)

        # ADSR panel (bottom right)
        self._draw_adsr_panel()

        # Help overlay
        if self.show_help:
            self._draw_help()

    def _draw_adsr_panel(self):
        """Draw ADSR envelope editor panel"""
        panel_width = 390
        panel_height = 350
        panel_rect = pygame.Rect(self.adsr_panel_x, self.adsr_panel_y, panel_width, panel_height)

        # Background
        pygame.draw.rect(self.screen, self.panel_bg_color, panel_rect)

        # Title
        title = self.font.render("ADSR Envelope", True, (100, 200, 255))
        self.screen.blit(title, (self.adsr_panel_x + 10, self.adsr_panel_y + 10))

        # Sliders
        for param, slider in self.sliders.items():
            # Label
            label = self.small_font.render(slider['label'], True, (200, 200, 200))
            self.screen.blit(label, (slider['x'], slider['y'] - 20))

            # Slider track
            pygame.draw.rect(self.screen, (60, 60, 70),
                           (slider['x'], slider['y'], slider['width'], slider['height']))

            # Slider fill
            normalized = (slider['value'] - slider['min']) / (slider['max'] - slider['min'])
            fill_width = int(normalized * slider['width'])
            pygame.draw.rect(self.screen, (100, 200, 255),
                           (slider['x'], slider['y'], fill_width, slider['height']))

            # Value text
            value_text = self.small_font.render(f"{slider['value']:.3f}", True, (255, 255, 255))
            self.screen.blit(value_text, (slider['x'] + slider['width'] + 10, slider['y'] + 2))

        # Preset buttons
        preset_y = self.adsr_panel_y + 260
        presets = ['instant', 'pluck', 'pad']
        for i, preset_name in enumerate(presets):
            btn_x = self.adsr_panel_x + 10 + i * 125
            self._draw_button(self.screen, preset_name.capitalize(), btn_x, preset_y, 115, 30)

        # Preview button
        self._draw_button(self.screen, "Preview (Space)", self.adsr_panel_x + 10, preset_y + 40, 380, 35,
                         color=(80, 150, 100))

        # Border
        pygame.draw.rect(self.screen, (80, 80, 100), panel_rect, 2)

    def _draw_button(self, screen, text, x, y, width, height, color=(60, 80, 120)):
        """Draw button"""
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, color, button_rect)

        text_surf = self.small_font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=button_rect.center)
        screen.blit(text_surf, text_rect)

        pygame.draw.rect(screen, (120, 120, 140), button_rect, 2)

    def _draw_help(self):
        """Draw help overlay"""
        overlay = pygame.Surface((500, 400))
        overlay.set_alpha(230)
        overlay.fill((20, 20, 30))

        help_text = [
            "AUDIO EDITOR HELP",
            "",
            "Basic Controls:",
            "  Arrow Keys - Navigate sample grid",
            "  Type - Search samples",
            "  Space - Preview current sample",
            "  ESC - Quit",
            "",
            "Workflow:",
            "1. Drop .wav/.ogg/.opus files in data/sounds/",
            "2. Press R to rescan folder",
            "3. Click sample or use arrow keys",
            "4. Click 'Auto-Generate' for metadata",
            "5. Edit category/tags/description",
            "6. Adjust ADSR sliders",
            "7. Press Space to preview",
            "8. Click 'Save' to save metadata",
            "",
            "Press F1 to toggle this help"
        ]

        y = 20
        for line in help_text:
            if line.startswith("AUDIO"):
                surf = self.font.render(line, True, (255, 200, 100))
            elif line.startswith(" "):
                surf = self.small_font.render(line, True, (180, 180, 180))
            else:
                surf = self.small_font.render(line, True, (220, 220, 220))

            overlay.blit(surf, (20, y))
            y += 22 if line else 10

        # Draw overlay
        overlay_x = (self.screen_width - 500) // 2
        overlay_y = (self.screen_height - 400) // 2
        self.screen.blit(overlay, (overlay_x, overlay_y))

        # Border
        pygame.draw.rect(self.screen, (255, 200, 100),
                        (overlay_x, overlay_y, 500, 400), 3)


if __name__ == "__main__":
    print("=" * 60)
    print("Karaokeficador - Standalone Audio Editor")
    print("=" * 60)
    print()
    print("Sound Designer Tool - No Programming Required!")
    print()
    print("1. Drop audio files (.wav, .ogg, .opus) in data/sounds/")
    print("2. Use this tool to add metadata and configure sounds")
    print("3. Sounds will automatically work in the game")
    print()
    print("Press F1 in the editor for help")
    print("=" * 60)
    print()

    editor = StandaloneAudioEditor()
    editor.run()
