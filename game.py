import pygame
import sys
import random
import json
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Style")

clock = pygame.time.Clock()

SKY_BLUE = (107, 140, 255)
GROUND_BROWN = (139, 69, 19)
BRICK_RED = (200, 80, 60)
BLOCK_YELLOW = (255, 200, 50)
PIPE_GREEN = (0, 168, 0)
PIPE_DARK = (0, 128, 0)
MARIO_RED = (255, 0, 0)
MARIO_SKIN = (255, 200, 150)
MARIO_BROWN = (139, 69, 19)
GOOMBA_BROWN = (165, 42, 42)
COIN_GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CLOUD_WHITE = (255, 255, 255)

font = pygame.font.SysFont("Arial", 24, bold=True)
big_font = pygame.font.SysFont("Arial", 48, bold=True)
small_font = pygame.font.SysFont("Arial", 14)
med_font = pygame.font.SysFont("Arial", 18, bold=True)

WORLD_WIDTH = 3200
GROUND_Y = 500

HISTORY_FILE = "mario_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def add_run(history, score, coins, lives, outcome):
    run = {
        "run": len(history) + 1,
        "score": score,
        "coins": coins,
        "lives": lives,
        "outcome": outcome
    }
    history.append(run)
    save_history(history)
    return history

def draw_history(surface, history):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))

    panel_w, panel_h = 620, 440
    panel_x = WIDTH // 2 - panel_w // 2
    panel_y = HEIGHT // 2 - panel_h // 2
    pygame.draw.rect(surface, (25, 25, 35), (panel_x, panel_y, panel_w, panel_h), border_radius=14)
    pygame.draw.rect(surface, (90, 90, 120), (panel_x, panel_y, panel_w, panel_h), 2, border_radius=14)

    title = big_font.render("Game History", True, WHITE)
    surface.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2, panel_y + 12))

    sorted_runs = sorted(history, key=lambda r: r["score"], reverse=True)
    medals = ["GOLD", "SILV", "BRON"]
    medal_colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]

    if not history:
        msg = font.render("No runs yet - finish a game first!", True, (180, 180, 180))
        surface.blit(msg, (panel_x + panel_w // 2 - msg.get_width() // 2, panel_y + 190))
    else:
        best = sorted_runs[0]
        max_coins = max(r["coins"] for r in history)
        wins = sum(1 for r in history if r["outcome"] == "win")

        stats_y = panel_y + 70
        stats = [
            ("Best Score", str(best["score"])),
            ("Most Coins", str(max_coins)),
            ("Total Runs", str(len(history))),
            ("Wins", str(wins)),
        ]
        box_w = (panel_w - 50) // 4
        for i, (label, val) in enumerate(stats):
            bx = panel_x + 20 + i * (box_w + 6)
            pygame.draw.rect(surface, (45, 45, 60), (bx, stats_y, box_w, 54), border_radius=8)
            lbl_s = small_font.render(label, True, (160, 160, 180))
            val_s = med_font.render(val, True, WHITE)
            surface.blit(lbl_s, (bx + 8, stats_y + 6))
            surface.blit(val_s, (bx + 8, stats_y + 28))

        col_y = stats_y + 66
        col_labels = ["Rank", "Run #", "Score", "Coins", "Lives", "Result"]
        col_xs = [panel_x + 20, panel_x + 80, panel_x + 150, panel_x + 300, panel_x + 400, panel_x + 470]
        for cl, cx in zip(col_labels, col_xs):
            cl_s = small_font.render(cl, True, (130, 130, 160))
            surface.blit(cl_s, (cx, col_y))

        pygame.draw.line(surface, (70, 70, 100),
                         (panel_x + 16, col_y + 18), (panel_x + panel_w - 16, col_y + 18), 1)

        row_y = col_y + 26
        for i, run in enumerate(sorted_runs[:6]):
            ry = row_y + i * 42
            rx = panel_x + 14
            rw = panel_w - 28
            row_bg = (55, 44, 10) if i == 0 else (38, 38, 52)
            pygame.draw.rect(surface, row_bg, (rx, ry, rw, 36), border_radius=7)

            if i < 3:
                rank_s = med_font.render(medals[i], True, medal_colors[i])
            else:
                rank_s = font.render(f"#{i+1}", True, (140, 140, 160))
            surface.blit(rank_s, (col_xs[0], ry + 7))

            surface.blit(font.render(str(run["run"]), True, WHITE), (col_xs[1], ry + 7))

            score_color = COIN_GOLD if i == 0 else WHITE
            surface.blit(font.render(str(run["score"]), True, score_color), (col_xs[2], ry + 7))

            surface.blit(font.render(str(run["coins"]), True, COIN_GOLD), (col_xs[3], ry + 7))

            surface.blit(font.render(str(run["lives"]), True, WHITE), (col_xs[4], ry + 7))

            res_color = (80, 220, 120) if run["outcome"] == "win" else (220, 80, 80)
            surface.blit(font.render(run["outcome"].upper(), True, res_color), (col_xs[5], ry + 7))

    hint = small_font.render("Press H to close", True, (110, 110, 140))
    surface.blit(hint, (panel_x + panel_w // 2 - hint.get_width() // 2, panel_y + panel_h - 24))


class Mario:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 48)
        self.vel_x = 0
        self.vel_y = 0
        self.accel = 0.15
        self.decel = 0.1
        self.max_walk_speed = 4
        self.max_run_speed = 7
        self.gravity = 0.4
        self.jump_power = -12
        self.jump_hold_gravity = 0.2
        self.max_fall_speed = 12
        self.on_ground = False
        self.facing_right = True
        self.is_running = False
        self.is_jumping = False
        self.jump_held = False
        self.is_big = False
        self.is_invincible = False
        self.invincible_timer = 0
        self.walk_frame = 0
        self.walk_timer = 0
        self.coins = 0
        self.score = 0
        self.lives = 3

    def update(self, keys, platforms, enemies, items):
        self.is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        max_speed = self.max_run_speed if self.is_running else self.max_walk_speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel_x += self.accel
            if self.vel_x > max_speed:
                self.vel_x = max_speed
            self.facing_right = True
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel_x -= self.accel
            if self.vel_x < -max_speed:
                self.vel_x = -max_speed
            self.facing_right = False
        else:
            if self.vel_x > 0:
                self.vel_x -= self.decel
                if self.vel_x < 0:
                    self.vel_x = 0
            elif self.vel_x < 0:
                self.vel_x += self.decel
                if self.vel_x > 0:
                    self.vel_x = 0

        jump_pressed = keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]

        if jump_pressed and self.on_ground and not self.jump_held:
            self.vel_y = self.jump_power
            self.on_ground = False
            self.is_jumping = True
            self.jump_held = True

        if not jump_pressed:
            self.jump_held = False

        if self.is_jumping and jump_pressed and self.vel_y < 0:
            self.vel_y += self.jump_hold_gravity
        else:
            self.vel_y += self.gravity

        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed

        self.rect.x += int(self.vel_x)
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_x > 0:
                    self.rect.right = plat.rect.left
                elif self.vel_x < 0:
                    self.rect.left = plat.rect.right
                self.vel_x = 0

        self.rect.y += int(self.vel_y)
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                elif self.vel_y < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0
                    if hasattr(plat, 'hit_from_below'):
                        plat.hit_from_below(items)

        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = 0
        if self.rect.right > WORLD_WIDTH:
            self.rect.right = WORLD_WIDTH

        if self.rect.top > HEIGHT + 100:
            return "dead"

        if not self.is_invincible:
            for enemy in enemies[:]:
                if self.rect.colliderect(enemy.rect):
                    if self.vel_y > 0 and self.rect.bottom < enemy.rect.centery:
                        enemy.stomped()
                        self.vel_y = self.jump_power * 0.6
                        self.score += 100
                    else:
                        if self.is_big:
                            self.is_big = False
                            self.is_invincible = True
                            self.invincible_timer = 120
                            self.rect.height = 48
                        else:
                            return "dead"

        if self.is_invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.is_invincible = False

        for item in items[:]:
            if self.rect.colliderect(item.rect):
                if item.item_type == "coin":
                    self.coins += 1
                    self.score += 200
                    items.remove(item)
                elif item.item_type == "mushroom":
                    if not self.is_big:
                        self.is_big = True
                        self.rect.height = 64
                        self.rect.y -= 16
                    self.score += 1000
                    items.remove(item)

        if abs(self.vel_x) > 0.5:
            self.walk_timer += abs(self.vel_x)
            if self.walk_timer > 8:
                self.walk_timer = 0
                self.walk_frame = (self.walk_frame + 1) % 3
        else:
            self.walk_frame = 0
            self.walk_timer = 0

        return None

    def draw(self, surface, camera_x):
        if self.is_invincible and self.invincible_timer % 4 < 2:
            return
        x = self.rect.x - camera_x
        y = self.rect.y
        w = self.rect.width
        h = self.rect.height
        pygame.draw.rect(surface, MARIO_RED, (x + 4, y + h // 3, w - 8, h // 2))
        pygame.draw.ellipse(surface, MARIO_SKIN, (x + 6, y + 4, w - 12, h // 3))
        pygame.draw.rect(surface, MARIO_RED, (x + 4, y, w - 8, h // 6))
        eye_x = x + w // 2 + (4 if self.facing_right else -8)
        pygame.draw.circle(surface, BLACK, (eye_x, y + h // 5), 3)
        pygame.draw.rect(surface, MARIO_BROWN, (x + 6, y + h - 12, 8, 12))
        pygame.draw.rect(surface, MARIO_BROWN, (x + w - 14, y + h - 12, 8, 12))


class Platform:
    def __init__(self, x, y, width, height, platform_type="ground"):
        self.rect = pygame.Rect(x, y, width, height)
        self.platform_type = platform_type
        self.has_item = False
        self.item_type = None
        self.hit = False
        self.bump_offset = 0

    def hit_from_below(self, items):
        if self.platform_type == "question" and not self.hit:
            self.hit = True
            self.bump_offset = -8
            if self.item_type == "coin":
                items.append(Item(self.rect.centerx - 8, self.rect.top - 20, "coin"))
            elif self.item_type == "mushroom":
                items.append(Item(self.rect.centerx - 12, self.rect.top - 24, "mushroom"))

    def update(self):
        if self.bump_offset < 0:
            self.bump_offset += 2
            if self.bump_offset > 0:
                self.bump_offset = 0

    def draw(self, surface, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y + self.bump_offset
        w = self.rect.width
        h = self.rect.height
        if self.platform_type == "ground":
            pygame.draw.rect(surface, GROUND_BROWN, (x, y, w, h))
            for i in range(0, w, 32):
                pygame.draw.line(surface, BLACK, (x + i, y), (x + i, y + h), 1)
        elif self.platform_type == "brick":
            pygame.draw.rect(surface, BRICK_RED, (x, y, w, h))
            pygame.draw.rect(surface, BLACK, (x, y, w, h), 2)
            pygame.draw.line(surface, BLACK, (x, y + h // 2), (x + w, y + h // 2), 1)
            pygame.draw.line(surface, BLACK, (x + w // 2, y), (x + w // 2, y + h // 2), 1)
        elif self.platform_type == "question":
            color = BLOCK_YELLOW if not self.hit else GROUND_BROWN
            pygame.draw.rect(surface, color, (x, y, w, h))
            pygame.draw.rect(surface, BLACK, (x, y, w, h), 2)
            if not self.hit:
                text = font.render("?", True, BLACK)
                surface.blit(text, (x + w // 2 - 6, y + h // 2 - 10))
        elif self.platform_type == "pipe":
            pygame.draw.rect(surface, PIPE_GREEN, (x, y, w, h))
            pygame.draw.rect(surface, PIPE_DARK, (x, y, 8, h))
            pygame.draw.rect(surface, PIPE_DARK, (x + w - 8, y, 8, h))
            pygame.draw.rect(surface, PIPE_GREEN, (x - 8, y, w + 16, 32))
            pygame.draw.rect(surface, BLACK, (x - 8, y, w + 16, 32), 2)


class Enemy:
    def __init__(self, x, y, enemy_type="goomba"):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.enemy_type = enemy_type
        self.vel_x = -1.5
        self.vel_y = 0
        self.alive = True
        self.death_timer = 0
        self.walk_frame = 0
        self.walk_timer = 0

    def update(self, platforms):
        if not self.alive:
            self.death_timer -= 1
            return self.death_timer <= 0
        self.vel_y += 0.4
        if self.vel_y > 10:
            self.vel_y = 10
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                elif self.vel_x > 0:
                    self.rect.right = plat.rect.left
                    self.vel_x *= -1
                elif self.vel_x < 0:
                    self.rect.left = plat.rect.right
                    self.vel_x *= -1
        self.walk_timer += 1
        if self.walk_timer > 10:
            self.walk_timer = 0
            self.walk_frame = 1 - self.walk_frame
        return False

    def stomped(self):
        self.alive = False
        self.death_timer = 30
        self.rect.height = 16
        self.rect.y += 16

    def draw(self, surface, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y
        if self.enemy_type == "goomba":
            if self.alive:
                pygame.draw.ellipse(surface, GOOMBA_BROWN, (x, y + 8, 32, 24))
                pygame.draw.ellipse(surface, GOOMBA_BROWN, (x + 2, y, 28, 20))
                pygame.draw.ellipse(surface, WHITE, (x + 6, y + 6, 8, 8))
                pygame.draw.ellipse(surface, WHITE, (x + 18, y + 6, 8, 8))
                pygame.draw.circle(surface, BLACK, (x + 10, y + 10), 3)
                pygame.draw.circle(surface, BLACK, (x + 22, y + 10), 3)
                offset = 2 if self.walk_frame else -2
                pygame.draw.ellipse(surface, BLACK, (x + 2 + offset, y + 26, 12, 8))
                pygame.draw.ellipse(surface, BLACK, (x + 18 - offset, y + 26, 12, 8))
            else:
                pygame.draw.ellipse(surface, GOOMBA_BROWN, (x, y, 32, 16))


class Item:
    def __init__(self, x, y, item_type):
        self.rect = pygame.Rect(x, y, 24, 24)
        self.item_type = item_type
        self.vel_y = -5 if item_type == "coin" else 0
        self.vel_x = 2 if item_type == "mushroom" else 0
        self.lifetime = 30 if item_type == "coin" else 999

    def update(self, platforms):
        self.lifetime -= 1
        if self.lifetime <= 0:
            return True
        if self.item_type == "mushroom":
            self.vel_y += 0.3
            self.rect.x += self.vel_x
            self.rect.y += int(self.vel_y)
            for plat in platforms:
                if self.rect.colliderect(plat.rect):
                    if self.vel_y > 0:
                        self.rect.bottom = plat.rect.top
                        self.vel_y = 0
                    else:
                        self.vel_x *= -1
        elif self.item_type == "coin":
            self.rect.y += self.vel_y
            self.vel_y += 0.5
        return False

    def draw(self, surface, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y
        if self.item_type == "coin":
            pygame.draw.ellipse(surface, COIN_GOLD, (x + 4, y, 16, 24))
            pygame.draw.ellipse(surface, (200, 160, 0), (x + 8, y + 4, 8, 16))
        elif self.item_type == "mushroom":
            pygame.draw.rect(surface, WHITE, (x + 6, y + 12, 12, 12))
            pygame.draw.ellipse(surface, MARIO_RED, (x, y, 24, 16))
            pygame.draw.circle(surface, WHITE, (x + 6, y + 8), 4)
            pygame.draw.circle(surface, WHITE, (x + 18, y + 8), 4)


def draw_cloud(surface, x, y):
    pygame.draw.ellipse(surface, CLOUD_WHITE, (x, y, 60, 40))
    pygame.draw.ellipse(surface, CLOUD_WHITE, (x + 20, y - 15, 50, 40))
    pygame.draw.ellipse(surface, CLOUD_WHITE, (x + 40, y, 60, 40))


def draw_bush(surface, x, y):
    pygame.draw.ellipse(surface, (0, 180, 0), (x, y, 80, 40))
    pygame.draw.ellipse(surface, (0, 180, 0), (x + 30, y - 10, 60, 40))
    pygame.draw.ellipse(surface, (0, 180, 0), (x + 60, y, 80, 40))


def create_level():
    platforms = []
    enemies = []
    items = []

    for i in range(0, WORLD_WIDTH, 200):
        if i not in [800, 1600, 2400]:
            platforms.append(Platform(i, GROUND_Y, 200, 100, "ground"))

    platforms.append(Platform(300, 380, 32, 32, "brick"))
    platforms.append(Platform(332, 380, 32, 32, "question"))
    platforms[-1].item_type = "coin"
    platforms.append(Platform(364, 380, 32, 32, "brick"))
    platforms.append(Platform(396, 380, 32, 32, "question"))
    platforms[-1].item_type = "mushroom"
    platforms.append(Platform(428, 380, 32, 32, "brick"))

    platforms.append(Platform(500, GROUND_Y - 64, 64, 64, "pipe"))
    platforms.append(Platform(700, GROUND_Y - 96, 64, 96, "pipe"))

    platforms.append(Platform(1000, 350, 32, 32, "question"))
    platforms[-1].item_type = "coin"
    platforms.append(Platform(1100, 280, 32, 32, "brick"))
    platforms.append(Platform(1132, 280, 32, 32, "brick"))
    platforms.append(Platform(1164, 280, 32, 32, "question"))
    platforms[-1].item_type = "mushroom"
    platforms.append(Platform(1196, 280, 32, 32, "brick"))

    for i in range(5):
        for j in range(i + 1):
            platforms.append(Platform(1400 + i * 32, GROUND_Y - (j + 1) * 32, 32, 32, "brick"))

    platforms.append(Platform(1900, 380, 32, 32, "question"))
    platforms[-1].item_type = "coin"
    platforms.append(Platform(1932, 380, 32, 32, "question"))
    platforms[-1].item_type = "coin"
    platforms.append(Platform(2000, GROUND_Y - 128, 64, 128, "pipe"))

    for i in range(8):
        for j in range(i + 1):
            platforms.append(Platform(2600 + i * 32, GROUND_Y - (j + 1) * 32, 32, 32, "brick"))

    enemies.append(Enemy(400, GROUND_Y - 32, "goomba"))
    enemies.append(Enemy(650, GROUND_Y - 32, "goomba"))
    enemies.append(Enemy(900, GROUND_Y - 32, "goomba"))
    enemies.append(Enemy(1050, GROUND_Y - 32, "goomba"))
    enemies.append(Enemy(1200, GROUND_Y - 32, "goomba"))
    enemies.append(Enemy(1800, GROUND_Y - 32, "goomba"))
    enemies.append(Enemy(2200, GROUND_Y - 32, "goomba"))
    enemies.append(Enemy(2500, GROUND_Y - 32, "goomba"))

    for x in [350, 380, 410, 1120, 1150, 1180, 2700, 2732, 2764]:
        items.append(Item(x, 300, "coin"))

    return platforms, enemies, items


def reset_game():
    mario = Mario(100, GROUND_Y - 64)
    platforms, enemies, items = create_level()
    return mario, platforms, enemies, items


# --- Game init ---
game_history = load_history()
show_history = False
new_record_banner = 0

mario, platforms, enemies, items = reset_game()
camera_x = 0
game_state = "playing"

clouds = [(random.randint(0, WORLD_WIDTH), random.randint(50, 150)) for _ in range(15)]
bushes = [(random.randint(0, WORLD_WIDTH), GROUND_Y - 20) for _ in range(20)]

# --- Main loop ---
while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                mario, platforms, enemies, items = reset_game()
                camera_x = 0
                game_state = "playing"
                show_history = False
                new_record_banner = 0
            if event.key == pygame.K_h:
                show_history = not show_history

    keys = pygame.key.get_pressed()

    if game_state == "playing" and not show_history:
        result = mario.update(keys, platforms, enemies, items)

        if result == "dead":
            mario.lives -= 1
            if mario.lives <= 0:
                prev_best = max((r["score"] for r in game_history), default=-1)
                game_history = add_run(game_history, mario.score, mario.coins, 0, "gameover")
                if mario.score > prev_best and len(game_history) > 1:
                    new_record_banner = 240
                game_state = "gameover"
            else:
                mario.rect.x = 100
                mario.rect.y = GROUND_Y - 64
                mario.vel_x = 0
                mario.vel_y = 0
                mario.is_big = False
                mario.rect.height = 48

        if mario.rect.x >= WORLD_WIDTH - 200 and game_state == "playing":
            prev_best = max((r["score"] for r in game_history), default=-1)
            game_history = add_run(game_history, mario.score, mario.coins, mario.lives, "win")
            if mario.score > prev_best and len(game_history) > 1:
                new_record_banner = 240
            game_state = "win"

        for plat in platforms:
            plat.update()

        for enemy in enemies[:]:
            if enemy.update(platforms):
                enemies.remove(enemy)

        for item in items[:]:
            if item.update(platforms):
                items.remove(item)

        target_camera = mario.rect.x - WIDTH // 3
        camera_x += (target_camera - camera_x) * 0.1
        if camera_x < 0:
            camera_x = 0
        if camera_x > WORLD_WIDTH - WIDTH:
            camera_x = WORLD_WIDTH - WIDTH

    # --- Draw ---
    screen.fill(SKY_BLUE)

    for cx, cy in clouds:
        draw_cloud(screen, cx - camera_x * 0.5, cy)

    for bx, by in bushes:
        if -100 < bx - camera_x < WIDTH + 100:
            draw_bush(screen, bx - camera_x, by)

    for plat in platforms:
        if -100 < plat.rect.x - camera_x < WIDTH + 100:
            plat.draw(screen, camera_x)

    for item in items:
        if -50 < item.rect.x - camera_x < WIDTH + 50:
            item.draw(screen, camera_x)

    for enemy in enemies:
        if -50 < enemy.rect.x - camera_x < WIDTH + 50:
            enemy.draw(screen, camera_x)

    mario.draw(screen, camera_x)

    # HUD bar
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 40))
    screen.blit(font.render(f"SCORE: {mario.score}", True, WHITE), (20, 8))
    screen.blit(font.render(f"COINS: {mario.coins}", True, COIN_GOLD), (210, 8))
    screen.blit(font.render(f"LIVES: {mario.lives}", True, WHITE), (400, 8))
    screen.blit(font.render(f"{int(mario.rect.x / 6)}m", True, WHITE), (550, 8))
    screen.blit(small_font.render("H = History   R = Restart", True, (150, 150, 160)), (630, 14))

    # Best score display below HUD
    if game_history:
        best = max(r["score"] for r in game_history)
        screen.blit(small_font.render(f"BEST: {best}", True, COIN_GOLD), (20, 44))

    # New record banner (fades out)
    if new_record_banner > 0:
        new_record_banner -= 1
        alpha = min(255, new_record_banner * 2)
        bw, bh = 300, 40
        bx = WIDTH // 2 - bw // 2
        banner_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        banner_surf.fill((20, 18, 5, min(210, alpha)))
        screen.blit(banner_surf, (bx, 48))
        rec_text = med_font.render("** NEW RECORD! **", True, COIN_GOLD)
        screen.blit(rec_text, (WIDTH // 2 - rec_text.get_width() // 2, 56))

    # Game over screen
    if game_state == "gameover":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        go_text = big_font.render("GAME OVER", True, MARIO_RED)
        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, 170))
        screen.blit(font.render(f"Score: {mario.score}   Coins: {mario.coins}", True, WHITE),
                    (WIDTH // 2 - 165, 255))
        if game_history:
            best = max(r["score"] for r in game_history)
            screen.blit(font.render(f"Best Score: {best}", True, COIN_GOLD),
                        (WIDTH // 2 - 110, 295))
        screen.blit(font.render("R = Restart     H = History", True, WHITE),
                    (WIDTH // 2 - 175, 345))

    # Win screen
    elif game_state == "win":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        win_text = big_font.render("YOU WIN!", True, COIN_GOLD)
        screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, 170))
        screen.blit(font.render(f"Score: {mario.score}   Coins: {mario.coins}", True, WHITE),
                    (WIDTH // 2 - 165, 255))
        if game_history:
            best = max(r["score"] for r in game_history)
            screen.blit(font.render(f"Best Score: {best}", True, COIN_GOLD),
                        (WIDTH // 2 - 110, 295))
        screen.blit(font.render("R = Play Again     H = History", True, WHITE),
                    (WIDTH // 2 - 195, 345))

    # History overlay (press H)
    if show_history:
        draw_history(screen, game_history)

    pygame.display.flip()