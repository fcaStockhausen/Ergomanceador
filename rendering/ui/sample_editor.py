"""
Sample editor UI - Grid-based audio editor with metadata support.

Drum-machine style interface for sound designers.
"""

import pygame
import json
import os
from audio.sample_loader import SampleLibrary
from audio.adsr_envelope import ADSREnvelope, PRESETS
from audio.metadata_generator import MetadataGenerator
from rendering.ui.sample_grid import SampleGrid
from rendering.ui.waveform_display import WaveformDisplay
from rendering.ui.metadata_editor import MetadataEditor
from rendering.ui.metadata_modal import MetadataModal


class SampleEditor:
    """
    Grid-based sample editor with auto-metadata generation.

    Features:
    - Drum machine grid layout
    - Fuzzy search
    - Auto-metadata generation
    - In-editor metadata editing
    - ADSR envelope editing
    - Preview playback
    """

    def __init__(self, screen_width, screen_height):
        """
        Create sample editor.

        Args:
            screen_width, screen_height: Screen dimensions
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Sample library
        self.library = SampleLibrary()
        self.library.scan_directory()

        # Auto-generate missing metadata
        self.generator = MetadataGenerator()
        generated = self.generator.batch_generate(self.library, overwrite=False)
        if generated:
            # Reload samples to pick up new metadata
            self.library.scan_directory()

        # Current sample
        self.current_sample = None

        # UI Components - adjust for game screen size (1280x720)
        # Left: Sample grid
        grid_width = int(screen_width * 0.45)  # 45% of screen
        self.sample_grid = SampleGrid(10, 50, grid_width, screen_height - 100)
        self.sample_grid.set_samples(self.library.get_all_samples_with_info())

        # Right: Waveform + metadata + ADSR
        right_x = grid_width + 20
        right_width = screen_width - right_x - 10

        self.waveform_display = WaveformDisplay(right_x, 50, right_width, 150)

        # Metadata editor below waveform
        meta_height = 250
        self.metadata_editor = MetadataEditor(right_x, 210, right_width, meta_height)

        # ADSR sliders below metadata
        self.adsr_y = 210 + meta_height + 10
        self.adsr_x = right_x
        self.current_envelope = ADSREnvelope()
        self._setup_adsr_sliders(right_width)

        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Colors
        self.bg_color = (20, 20, 30)

        # Save notification animation (particle explosion)
        self.save_particles = []  # List of {x, y, vx, vy, life, color}

        # Metadata modal (M key)
        self.metadata_modal = MetadataModal(screen_width, screen_height)

    def _setup_adsr_sliders(self, panel_width):
        """Setup ADSR slider positions"""
        slider_width = min(300, panel_width - 20)
        slider_height = 20
        slider_spacing = 40
        margin = 10
        first_slider_offset = 10  # From top of panel

        self.sliders = {
            'attack': {
                'x': self.adsr_x + margin,
                'y': self.adsr_y + first_slider_offset,
                'width': slider_width,
                'height': slider_height,
                'min': 0.0,
                'max': 1.0,
                'value': self.current_envelope.attack_time,
                'label': 'Attack (s)'
            },
            'decay': {
                'x': self.adsr_x + margin,
                'y': self.adsr_y + first_slider_offset + slider_spacing,
                'width': slider_width,
                'height': slider_height,
                'min': 0.0,
                'max': 1.0,
                'value': self.current_envelope.decay_time,
                'label': 'Decay (s)'
            },
            'sustain': {
                'x': self.adsr_x + margin,
                'y': self.adsr_y + first_slider_offset + slider_spacing * 2,
                'width': slider_width,
                'height': slider_height,
                'min': 0.0,
                'max': 1.0,
                'value': self.current_envelope.sustain_level,
                'label': 'Sustain (level)'
            },
            'release': {
                'x': self.adsr_x + margin,
                'y': self.adsr_y + first_slider_offset + slider_spacing * 3,
                'width': slider_width,
                'height': slider_height,
                'min': 0.0,
                'max': 1.0,
                'value': self.current_envelope.release_time,
                'label': 'Release (s)'
            }
        }

    def handle_event(self, event):
        """
        Handle input events.

        Returns:
            'exit' to close editor, None otherwise
        """
        # Modal takes priority
        if self.metadata_modal.active:
            self.metadata_modal.handle_event(event)
            return None

        if event.type == pygame.KEYDOWN:
            # Check for Cmd/Ctrl modifiers first
            mods = pygame.key.get_mods()
            cmd_or_ctrl = bool(mods & (pygame.KMOD_META | pygame.KMOD_CTRL))

            if event.key == pygame.K_ESCAPE:
                return 'exit'

            # Save settings (Cmd+S / Ctrl+S)
            elif event.key == pygame.K_s and cmd_or_ctrl:
                if self.current_sample:
                    self._save_sample_settings()

            # Open metadata modal (M key)
            elif event.key == pygame.K_m:
                if self.current_sample:
                    self.metadata_modal.open(self.current_sample)

            # Arrow keys for grid navigation
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

            # Preview with ADSR envelope and selection
            elif event.key == pygame.K_SPACE:
                if self.current_sample:
                    # Get selection range from waveform display
                    start_time, end_time = self.waveform_display.get_selection_range(
                        len(self.current_sample.waveform),
                        self.current_sample.sample_rate
                    )

                    # Play with ADSR envelope applied
                    self.current_sample.play(
                        volume=0.7,
                        adsr_envelope=self.current_envelope,
                        start_time=start_time if start_time is not None else 0.0,
                        end_time=end_time
                    )

            # Preset keys
            elif event.key == pygame.K_p:
                self._apply_preset('pluck')
            elif event.key == pygame.K_i:
                self._apply_preset('instant')
            elif event.key == pygame.K_o:
                self._apply_preset('organ')

            # Auto-generate metadata
            elif event.key == pygame.K_g:
                if self.current_sample:
                    self.metadata_editor.auto_generate()

            # Clear waveform selection
            elif event.key == pygame.K_c:
                self.waveform_display.clear_selection()

            # Backspace for search
            elif event.key == pygame.K_BACKSPACE:
                if not self.metadata_editor.active_field:
                    self.sample_grid.backspace_search()

            # Type to search (if not editing metadata)
            elif event.unicode and event.unicode.isprintable():
                if not self.metadata_editor.active_field:
                    self.sample_grid.add_search_char(event.unicode)

        elif event.type == pygame.MOUSEWHEEL:
            # Mouse wheel to scroll waveform (Cmd/Ctrl for fine adjustment)
            mouse_pos = pygame.mouse.get_pos()
            # Use Cmd on Mac, Ctrl on other platforms
            mods = pygame.key.get_mods()
            fine_adjust = bool(mods & (pygame.KMOD_META | pygame.KMOD_CTRL))
            self.waveform_display.handle_wheel(mouse_pos[1], event.y, fine_adjust)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Modal gets events first
            if self.metadata_modal.active:
                return None

            # Check sample grid click
            if self.sample_grid.handle_click(mouse_x, mouse_y):
                self._load_selected_sample()
                return None

            # Check waveform click (for dragging to scroll)
            if self.waveform_display.handle_mouse_down(mouse_x, mouse_y):
                return None

            # Check ADSR slider clicks
            self._handle_slider_click(mouse_x, mouse_y)

        elif event.type == pygame.MOUSEBUTTONUP:
            # Release waveform drag
            self.waveform_display.handle_mouse_up()

        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos

            # Handle waveform dragging to scroll
            if self.waveform_display.handle_mouse_motion(mouse_x, mouse_y):
                return None

            # Handle ADSR slider dragging
            if pygame.mouse.get_pressed()[0]:  # Left button held
                self._handle_slider_drag(event.pos)

        # Pass events to metadata editor
        self.metadata_editor.handle_event(event)

        return None

    def _save_sample_settings(self):
        """Save ADSR and trim settings to sample metadata"""
        if not self.current_sample:
            return

        # Save ADSR envelope
        self.current_sample.adsr = {
            'attack': self.current_envelope.attack_time,
            'decay': self.current_envelope.decay_time,
            'sustain': self.current_envelope.sustain_level,
            'release': self.current_envelope.release_time
        }

        # Save trim offset
        self.current_sample.trim_start = self.waveform_display.scroll_offset

        # Save metadata to JSON file
        if self.current_sample.save_metadata():
            print(f"✓ Saved settings for {self.current_sample.get_display_info()['filename']}")
            # Spawn particle explosion
            self._spawn_save_particles()

    def _spawn_save_particles(self):
        """Spawn particle explosion from center of screen"""
        import random
        import math

        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        num_particles = 60
        colors = [(100, 255, 100), (100, 200, 255), (255, 200, 100), (255, 255, 100)]

        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 400)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            self.save_particles.append({
                'x': center_x,
                'y': center_y,
                'vx': vx,
                'vy': vy,
                'life': 1.0,  # 1.0 = fully alive, 0.0 = dead
                'color': random.choice(colors),
                'size': random.randint(3, 7)
            })

    def _update_particles(self, dt):
        """Update particle physics"""
        gravity = 500  # Pixels per second squared

        # Update each particle
        for particle in self.save_particles[:]:
            # Physics
            particle['vy'] += gravity * dt  # Gravity
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt

            # Fade out
            particle['life'] -= dt * 1.5  # Die after ~0.67 seconds

            # Remove dead particles
            if particle['life'] <= 0:
                self.save_particles.remove(particle)

    def _load_selected_sample(self):
        """Load currently selected sample from grid"""
        sample_name = self.sample_grid.get_selected_sample_name()
        if sample_name:
            self.current_sample = self.library.get_sample(sample_name)
            if self.current_sample:
                # Load in metadata editor
                self.metadata_editor.load_sample(self.current_sample)

                # Load saved ADSR settings if available
                if self.current_sample.adsr:
                    adsr_data = self.current_sample.adsr
                    self.current_envelope = ADSREnvelope(
                        attack_time=adsr_data.get('attack', 0.01),
                        decay_time=adsr_data.get('decay', 0.1),
                        sustain_level=adsr_data.get('sustain', 0.7),
                        release_time=adsr_data.get('release', 0.3)
                    )
                    self._sync_sliders_to_envelope()

                # Load saved trim offset
                if self.current_sample.trim_start > 0.0:
                    self.waveform_display.scroll_offset = self.current_sample.trim_start

    def _apply_preset(self, preset_name):
        """Apply ADSR preset"""
        if preset_name in PRESETS:
            self.current_envelope = PRESETS[preset_name]
            self._sync_sliders_to_envelope()

    def _sync_sliders_to_envelope(self):
        """Update slider values from current envelope"""
        self.sliders['attack']['value'] = self.current_envelope.attack_time
        self.sliders['decay']['value'] = self.current_envelope.decay_time
        self.sliders['sustain']['value'] = self.current_envelope.sustain_level
        self.sliders['release']['value'] = self.current_envelope.release_time

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

    def update(self, dt):
        """Update animations"""
        self._update_particles(dt)

    def render(self, screen):
        """Render sample editor UI"""
        # Background
        screen.fill(self.bg_color)

        # Title
        title = self.font.render("Audio Sample Editor", True, (255, 200, 100))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 10))

        # Instructions
        instructions = [
            f"{len(self.library.samples)} samples | Type: search | Arrows: navigate | Space: preview | M: metadata | Cmd+S: save",
            "Wheel: scroll (0.1s) | Cmd+Wheel: fine (0.01s) | Drag: super fine | C: reset | ESC: exit"
        ]
        y_offset = self.screen_height - 40
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (150, 150, 150))
            screen.blit(text, (10, y_offset))
            y_offset += 15

        # Sample grid (left side)
        self.sample_grid.draw(screen)

        # Waveform (top right)
        waveform = self.current_sample.waveform if self.current_sample else None
        self.waveform_display.draw(screen, waveform, self.current_envelope)

        # ADSR panel (bottom right)
        self._draw_adsr_panel(screen)

        # Save particles (drawn last, on top)
        self._draw_particles(screen)

        # Metadata modal (drawn on top of everything)
        self.metadata_modal.render(screen)

    def _draw_particles(self, screen):
        """Draw save particles"""
        for particle in self.save_particles:
            # Fade out with alpha
            alpha = int(particle['life'] * 255)
            color = (*particle['color'], alpha)

            # Draw circle
            pos = (int(particle['x']), int(particle['y']))
            size = int(particle['size'] * particle['life'])  # Shrink as they die
            if size > 0:
                pygame.draw.circle(screen, particle['color'], pos, size)

    def _draw_adsr_panel(self, screen):
        """Draw ADSR envelope editor panel"""
        panel_height = 180
        panel_width = self.screen_width - self.adsr_x - 10
        panel_rect = pygame.Rect(self.adsr_x, self.adsr_y, panel_width, panel_height)

        # Background
        pygame.draw.rect(screen, (30, 30, 40), panel_rect)

        # Sliders
        for param, slider in self.sliders.items():
            # Label
            label = self.small_font.render(slider['label'], True, (200, 200, 200))
            screen.blit(label, (slider['x'], slider['y'] - 18))

            # Slider track
            pygame.draw.rect(screen, (60, 60, 70),
                           (slider['x'], slider['y'], slider['width'], slider['height']))

            # Slider fill
            normalized = (slider['value'] - slider['min']) / (slider['max'] - slider['min'])
            fill_width = int(normalized * slider['width'])
            pygame.draw.rect(screen, (100, 200, 255),
                           (slider['x'], slider['y'], fill_width, slider['height']))

            # Value text
            value_text = self.small_font.render(f"{slider['value']:.3f}", True, (255, 255, 255))
            screen.blit(value_text, (slider['x'] + slider['width'] + 10, slider['y'] + 2))

        # Border
        pygame.draw.rect(screen, (80, 80, 100), panel_rect, 2)
