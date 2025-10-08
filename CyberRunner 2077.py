import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Colors - Cyberpunk palette
BLACK = (0, 0, 0)
NEON_BLUE = (0, 191, 255)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)
NEON_PURPLE = (138, 43, 226)
DARK_BLUE = (10, 10, 40)
DARK_PURPLE = (30, 10, 50)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
CYBER_YELLOW = (255, 223, 0)

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3

class Button:
    def __init__(self, x, y, width, height, text_key, action, game):
        self.rect = pygame.Rect(x, y, width, height)
        self.text_key = text_key
        self.action = action
        self.game = game

    def draw(self):
        pygame.draw.rect(self.game.screen, NEON_PINK, self.rect, border_radius=10)
        if self.text_key == 'level':
            text_str = self.game.texts[self.game.language]['level'] + str(self.game.selected_level)
        elif self.text_key == 'change_char':
            text_str = self.game.texts[self.game.language]['change_char'] + f" ({self.game.selected_shape})"
        else:
            text_str = self.game.texts[self.game.language][self.text_key]
        text = self.game.font_small.render(text_str, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        self.game.screen.blit(text, text_rect)

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.action()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.velocity_y = 0
        self.jump_power = -15
        self.gravity = 0.8
        self.is_jumping = False
        self.speed = 8
        self.invincible = False
        self.invincible_timer = 0
        self.color = NEON_BLUE
        self.trail_particles = []
        self.shape = 'rect'

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True

    def update(self):
        # Apply gravity
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # Check if landed on ground
        if self.y >= SCREEN_HEIGHT - self.height - 50:
            self.y = SCREEN_HEIGHT - self.height - 50
            self.velocity_y = 0
            self.is_jumping = False

        # Update invincibility (5 seconds)
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        # Add trail particles when moving
        if (pygame.key.get_pressed()[pygame.K_LEFT] or 
            pygame.key.get_pressed()[pygame.K_RIGHT]) and random.random() < 0.3:
            self.trail_particles.append({
                'x': self.x + self.width // 2,
                'y': self.y + self.height,
                'size': random.randint(2, 5),
                'life': 20
            })

        # Update trail particles
        for particle in self.trail_particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.trail_particles.remove(particle)

    def draw(self, screen):
        # Draw trail particles
        for particle in self.trail_particles:
            alpha = min(255, particle['life'] * 12)
            color = (*NEON_BLUE, alpha) if len(NEON_BLUE) == 3 else NEON_BLUE
            pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), particle['size'])

        # Flash effect when invincible
        flash_color = NEON_GREEN if self.invincible and pygame.time.get_ticks() % 200 < 100 else self.color

        # Draw based on shape
        if self.shape == 'rect':
            pygame.draw.rect(screen, flash_color, (self.x, self.y, self.width, self.height), border_radius=8)
            # Add details
            pygame.draw.rect(screen, NEON_PINK, (self.x + 5, self.y + 5, self.width - 10, 10), border_radius=4)
            pygame.draw.rect(screen, CYBER_YELLOW, (self.x + 15, self.y + 20, 10, 20), border_radius=2)
        elif self.shape == 'circle':
            radius = min(self.width, self.height) // 2
            center = (self.x + self.width // 2, self.y + self.height // 2)
            pygame.draw.circle(screen, flash_color, center, radius)
        elif self.shape == 'ellipse':
            pygame.draw.ellipse(screen, flash_color, (self.x, self.y, self.width, self.height))
        elif self.shape == 'triangle':
            points = [(self.x, self.y + self.height), (self.x + self.width, self.y + self.height), (self.x + self.width // 2, self.y)]
            pygame.draw.polygon(screen, flash_color, points)
        elif self.shape == 'square':
            size = min(self.width, self.height)
            pygame.draw.rect(screen, flash_color, (self.x, self.y + (self.height - size), size, size))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def activate_invincibility(self):
        self.invincible = True
        self.invincible_timer = 300  # 5 seconds at 60 FPS

class Obstacle:
    def __init__(self, x, y, obstacle_type):
        self.x = x
        self.y = y
        self.type = obstacle_type
        self.speed = 5

        # Set color based on type
        if obstacle_type == "red":
            self.width = 50
            self.height = 50
            self.color = RED
        elif obstacle_type == "green":
            self.width = 40
            self.height = 40
            self.color = NEON_GREEN
        elif obstacle_type == "purple":
            self.width = 40
            self.height = 40
            self.color = NEON_PURPLE
        else:  # neutral
            self.width = 40
            self.height = 40
            self.color = (100, 100, 100)  # Gray

    def update(self, game_speed):
        self.x -= self.speed + game_speed

    def draw(self, screen):
        # Draw different shapes based on type
        if self.type == "red":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=10)
            pygame.draw.polygon(screen, BLACK, [
                (self.x + 10, self.y + 15),
                (self.x + self.width - 10, self.y + 15),
                (self.x + self.width // 2, self.y + self.height - 10)
            ])
        elif self.type == "green":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=15)
            pygame.draw.rect(screen, BLACK, (self.x + 5, self.y + 5, self.width - 10, self.height - 10), border_radius=10)
            pygame.draw.rect(screen, self.color, (self.x + 15, self.y + 10, self.width - 30, self.height - 20), border_radius=5)
        elif self.type == "purple":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=15)
            pygame.draw.rect(screen, BLACK, (self.x + 5, self.y + 5, self.width - 10, self.height - 10), border_radius=10)
            font = pygame.font.SysFont('arial', 20, bold=True)
            text = font.render("X2", True, self.color)
            text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(text, text_rect)
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("CyberRunner 2077")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont('arial', 48, bold=True)
        self.font_medium = pygame.font.SysFont('arial', 32)
        self.font_small = pygame.font.SysFont('arial', 24)

        self.language = 'en'
        self.texts = {
            'en': {
                'title': "CYBERRUNNER 2077",
                'subtitle': "A PREMIUM CYBERPUNK EXPERIENCE",
                'press_space': "PRESS SPACE TO START",
                'controls': "ARROWS TO MOVE, SPACE TO JUMP",
                'powerups': "GREEN = INVINCIBILITY | PURPLE = SCORE x2 | RED = DANGER",
                'score': "SCORE: ",
                'score_x': "SCORE x",
                'invincible': "INVINCIBLE",
                'speed': "SPEED: ",
                'game_paused': "GAME PAUSED",
                'press_p_continue': "PRESS P TO CONTINUE",
                'game_over': "GAME OVER",
                'final_score': "FINAL SCORE: ",
                'press_r_restart': "PRESS R TO RESTART",
                'play': "Play",
                'change_char': "Change Character",
                'change_lang': "Change Language",
                'level': "Level: ",
                'press_l_lang': "Press L to change language"
            },
            'az': {
                'title': "SAYBERRUNNER 2077",
                'subtitle': "PREMİUM SAYBERPUNK TƏCRÜBƏSİ",
                'press_space': "BAŞLAMAK ÜÇÜN SPACE BASIN",
                'controls': "HƏRƏKƏT ÜÇÜN OKLAR, ATLAMA ÜÇÜN SPACE",
                'powerups': "YAŞIL = QORUNMA | BƏNÖVŞƏ = XAL x2 | QIRMIZI = TƏHLÜKƏ",
                'score': "XAL: ",
                'score_x': "XAL x",
                'invincible': "QORUNAN",
                'speed': "SÜRƏT: ",
                'game_paused': "OYUN DAYANDIRILDI",
                'press_p_continue': "DAVAM ETMƏK ÜÇÜN P BASIN",
                'game_over': "OYUN BİTDİ",
                'final_score': "SON XAL: ",
                'press_r_restart': "YENİDƏN BAŞLAMAK ÜÇÜN R BASIN",
                'play': "Oyna",
                'change_char': "Karakteri Dəyiş",
                'change_lang': "Dili Dəyiş",
                'level': "Səviyyə: ",
                'press_l_lang': "Dili dəyişmək üçün L basın"
            }
        }

        self.selected_shape = 'rect'
        self.shapes = ['rect', 'circle', 'ellipse', 'triangle', 'square']
        self.selected_level = 1

        self.menu_buttons = []
        self.menu_buttons.append(Button(SCREEN_WIDTH // 2 - 100, 200, 200, 50, 'play', self.start_game, self))
        self.menu_buttons.append(Button(SCREEN_WIDTH // 2 - 100, 260, 200, 50, 'change_char', self.change_character, self))
        self.menu_buttons.append(Button(SCREEN_WIDTH // 2 - 100, 320, 200, 50, 'change_lang', self.change_language, self))
        self.menu_buttons.append(Button(SCREEN_WIDTH // 2 - 100, 380, 200, 50, 'level', self.change_level, self))

        self.day_time = 0
        self.cycle_period = 3600  # 60 seconds cycle

        self.reset_game()

    def start_game(self):
        self.reset_game()
        self.game_state = PLAYING

    def change_character(self):
        idx = self.shapes.index(self.selected_shape)
        self.selected_shape = self.shapes[(idx + 1) % len(self.shapes)]

    def change_language(self):
        self.language = 'az' if self.language == 'en' else 'en'

    def change_level(self):
        self.selected_level = (self.selected_level % 10) + 1

    def reset_game(self):
        self.player = Player(100, SCREEN_HEIGHT - 200)
        self.player.shape = self.selected_shape
        self.obstacles = []
        self.score = 0
        self.starting_speed = (self.selected_level - 1) * 0.5
        self.game_speed = self.starting_speed
        self.game_state = MENU
        self.obstacle_timer = 0
        self.multiplier = 1
        self.multiplier_timer = 0
        self.background_stars = self.generate_stars(100)
        self.day_time = 0

    def generate_stars(self, count):
        stars = []
        for _ in range(count):
            stars.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.1, 0.5)
            })
        return stars

    def update_background(self):
        for star in self.background_stars:
            star['x'] -= star['speed'] + self.game_speed * 0.1
            if star['x'] < 0:
                star['x'] = SCREEN_WIDTH
                star['y'] = random.randint(0, SCREEN_HEIGHT)

    def draw_background(self):
        # Compute brightness for day/night
        angle = (self.day_time / self.cycle_period) * 2 * math.pi
        brightness = (math.sin(angle) + 1) / 2  # 0 to 1

        # Draw gradient background adjusted for brightness
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            base_r = int(DARK_BLUE[0] * (1 - ratio) + DARK_PURPLE[0] * ratio)
            base_g = int(DARK_BLUE[1] * (1 - ratio) + DARK_PURPLE[1] * ratio)
            base_b = int(DARK_BLUE[2] * (1 - ratio) + DARK_PURPLE[2] * ratio)
            r = min(255, int(base_r * (0.5 + brightness * 1.5)))
            g = min(255, int(base_g * (0.5 + brightness * 1.5)))
            b = min(255, int(base_b * (0.5 + brightness * 1.5)))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Draw stars (more visible at night)
        for star in self.background_stars:
            alpha = int(255 * (1 - brightness))
            color = (255, 255, 255)  # White
            pygame.draw.circle(self.screen, color, (int(star['x']), int(star['y'])), star['size'])

        # Draw ground
        pygame.draw.rect(self.screen, (40, 40, 40), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))

        # Draw neon grid lines on ground
        for i in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(self.screen, NEON_BLUE, (i, SCREEN_HEIGHT - 50), (i, SCREEN_HEIGHT), 2)

    def spawn_obstacle(self):
        obstacle_types = ["red", "green", "purple", "neutral"]
        weights = [0.4, 0.2, 0.2, 0.2]
        obstacle_type = random.choices(obstacle_types, weights=weights)[0]
        y_pos = SCREEN_HEIGHT - 50

        if obstacle_type == "red":
            y_pos = random.randint(SCREEN_HEIGHT - 200, SCREEN_HEIGHT - 60)
        elif obstacle_type in ["green", "purple"]:
            y_pos = random.randint(SCREEN_HEIGHT - 180, SCREEN_HEIGHT - 80)
        else:
            y_pos = SCREEN_HEIGHT - 110

        self.obstacles.append(Obstacle(SCREEN_WIDTH, y_pos, obstacle_type))

    def check_collisions(self):
        player_rect = self.player.get_rect()

        for obstacle in self.obstacles[:]:
            if player_rect.colliderect(obstacle.get_rect()):
                if obstacle.type == "red":
                    if not self.player.invincible:
                        self.game_state = GAME_OVER
                    else:
                        self.obstacles.remove(obstacle)
                elif obstacle.type == "green":
                    self.player.activate_invincibility()
                    self.obstacles.remove(obstacle)
                elif obstacle.type == "purple":
                    self.multiplier = 2
                    self.multiplier_timer = 300
                    self.obstacles.remove(obstacle)
                else:
                    self.obstacles.remove(obstacle)

    def update_multiplier(self):
        if self.multiplier_timer > 0:
            self.multiplier_timer -= 1
            if self.multiplier_timer <= 0:
                self.multiplier = 1

    def draw_ui(self):
        score_text = self.font_medium.render(self.texts[self.language]['score'] + str(int(self.score)), True, NEON_BLUE)
        self.screen.blit(score_text, (20, 20))

        if self.multiplier > 1:
            multiplier_text = self.font_small.render(self.texts[self.language]['score_x'] + str(self.multiplier), True, NEON_PURPLE)
            self.screen.blit(multiplier_text, (SCREEN_WIDTH - 150, 20))
            timer_width = (self.multiplier_timer / 300) * 100
            pygame.draw.rect(self.screen, NEON_PURPLE, (SCREEN_WIDTH - 150, 50, timer_width, 10))

        if self.player.invincible:
            inv_text = self.font_small.render(self.texts[self.language]['invincible'], True, NEON_GREEN)
            self.screen.blit(inv_text, (SCREEN_WIDTH - 150, 70))
            timer_width = (self.player.invincible_timer / 300) * 100
            pygame.draw.rect(self.screen, NEON_GREEN, (SCREEN_WIDTH - 150, 100, timer_width, 10))

        speed_text = self.font_small.render(self.texts[self.language]['speed'] + str(int(self.game_speed * 10)), True, NEON_PINK)
        self.screen.blit(speed_text, (SCREEN_WIDTH - 150, 120))

    def draw_menu(self):
        self.draw_background()

        title_text = self.font_large.render(self.texts[self.language]['title'], True, NEON_BLUE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)

        lang_text = self.font_small.render(self.texts[self.language]['press_l_lang'], True, WHITE)
        self.screen.blit(lang_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 30))

        for button in self.menu_buttons:
            button.draw()

    def draw_pause_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font_large.render(self.texts[self.language]['game_paused'], True, NEON_BLUE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(pause_text, pause_rect)

        continue_text = self.font_medium.render(self.texts[self.language]['press_p_continue'], True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(continue_text, continue_rect)

        # Draw two pause lines ||
        pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 100, 10, 200))
        pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 - 100, 10, 200))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font_large.render(self.texts[self.language]['game_over'], True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(game_over_text, game_over_rect)

        score_text = self.font_medium.render(self.texts[self.language]['final_score'] + str(int(self.score)), True, NEON_BLUE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)

        restart_text = self.font_medium.render(self.texts[self.language]['press_r_restart'], True, NEON_GREEN)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.game_state == MENU:
                        if event.key == pygame.K_l:
                            self.change_language()
                        if event.key == pygame.K_SPACE:
                            self.start_game()
                    elif self.game_state == PLAYING:
                        if event.key == pygame.K_SPACE:
                            self.player.jump()
                        if event.key == pygame.K_p:
                            self.game_state = PAUSED
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = MENU
                    elif self.game_state == PAUSED:
                        if event.key == pygame.K_p:
                            self.game_state = PLAYING
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = MENU
                    elif self.game_state == GAME_OVER:
                        if event.key == pygame.K_r:
                            self.reset_game()
                            self.game_state = PLAYING
                        if event.key == pygame.K_ESCAPE:
                            self.game_state = MENU

                if event.type == pygame.MOUSEBUTTONDOWN and self.game_state == MENU:
                    pos = pygame.mouse.get_pos()
                    for button in self.menu_buttons:
                        button.handle_click(pos)

            keys = pygame.key.get_pressed()
            if self.game_state == PLAYING:
                if keys[pygame.K_LEFT]:
                    self.player.move("left")
                if keys[pygame.K_RIGHT]:
                    self.player.move("right")

            if self.game_state == PLAYING:
                self.player.update()
                self.update_background()
                for obstacle in self.obstacles[:]:
                    obstacle.update(self.game_speed)
                    if obstacle.x < -obstacle.width:
                        self.obstacles.remove(obstacle)
                        self.score += 10 * self.multiplier
                self.obstacle_timer += 1
                level_factor = (self.selected_level - 1) * 2
                if self.obstacle_timer > 60 - min(50, self.game_speed * 5 + level_factor):
                    self.spawn_obstacle()
                    self.obstacle_timer = 0
                self.check_collisions()
                self.update_multiplier()
                self.score += 0.1 * self.multiplier
                self.game_speed = self.starting_speed + min(10, self.score / 1000)
                self.day_time += 1

            self.draw_background()

            if self.game_state == PLAYING or self.game_state == PAUSED:
                for obstacle in self.obstacles:
                    obstacle.draw(self.screen)
                self.player.draw(self.screen)
                self.draw_ui()

            if self.game_state == MENU:
                self.draw_menu()

            if self.game_state == PAUSED:
                self.draw_pause_screen()

            if self.game_state == GAME_OVER:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()