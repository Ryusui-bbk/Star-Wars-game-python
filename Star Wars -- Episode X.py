from pgzero.actor import Actor
import random

WIDTH = 600
HEIGHT = 450
TITLE = "Star Wars: Episode X"

ship = Actor("ship", (300, 400))
space = Actor("space", (WIDTH // 2, HEIGHT // 2))

enemies = []
bullets = []
enemy_bullets = []
explosions = []
stars = []

mode = "game"
score = 0
lives = 3
shoot_cooldown = 0
spawn_invulnerable = 0
enter_was_pressed = False


def reset_game():
    global enemies, bullets, enemy_bullets, explosions
    global mode, score, lives, shoot_cooldown, spawn_invulnerable
    global ship, enter_was_pressed

    ship.pos = (300, 400)

    enemies.clear()
    bullets.clear()
    enemy_bullets.clear()
    explosions.clear()

    mode = "game"
    score = 0
    lives = 3
    shoot_cooldown = 0
    spawn_invulnerable = 90
    enter_was_pressed = False

    for _ in range(3):
        new_enemy()


def create_stars():
    stars.clear()
    for _ in range(40):
        stars.append([
            random.randint(0, WIDTH),
            random.randint(0, HEIGHT),
            random.randint(1, 3)
        ])


def new_enemy():
    enemy = Actor("enemy", (random.randint(30, WIDTH - 30), random.randint(-300, -60)))
    enemy.speed = random.randint(2, 4)
    enemy.shoot_timer = random.randint(60, 70)
    enemies.append(enemy)


def create_explosion(x, y):
    for _ in range(12):
        explosions.append({
            "x": x,
            "y": y,
            "dx": random.uniform(-3, 3),
            "dy": random.uniform(-3, 3),
            "life": random.randint(12, 24),
            "size": random.randint(2, 5)
        })


def draw():
    screen.clear()
    space.draw()

    for star in stars:
        screen.draw.filled_circle((star[0], star[1]), star[2], "white")

    if mode == "game":
        ship.draw()

        # brilho visual enquanto invulnerável
        if spawn_invulnerable > 0 and spawn_invulnerable % 10 < 5:
            screen.draw.circle(ship.pos, 28, "cyan")

        for enemy in enemies:
            enemy.draw()

        for bullet in bullets:
            bullet.draw()

        for bullet in enemy_bullets:
            bullet.draw()

        for p in explosions:
            color = "yellow" if p["life"] > 8 else "orange" if p["life"] > 4 else "red"
            screen.draw.filled_circle((p["x"], p["y"]), p["size"], color)

        screen.draw.text(f"Score: {score}", (10, 10), color="white", fontsize=30)
        screen.draw.text(f"Vidas: {lives}", (10, 40), color="white", fontsize=30)

    elif mode == "end":
        screen.draw.text("GAME OVER", center=(WIDTH // 2, 170), fontsize=60, color="red")
        screen.draw.text(f"Score final: {score}", center=(WIDTH // 2, 240), fontsize=35, color="white")
        screen.draw.text("Pressione ENTER para reiniciar", center=(WIDTH // 2, 300), fontsize=28, color="yellow")


def update():
    global lives, mode, score, shoot_cooldown, spawn_invulnerable, enter_was_pressed

    update_stars()
    update_explosions()

    if mode == "end":
        # reinício robusto com Enter
        if keyboard.RETURN:
            if not enter_was_pressed:
                reset_game()
                enter_was_pressed = True
        else:
            enter_was_pressed = False
        return

    if spawn_invulnerable > 0:
        spawn_invulnerable -= 1

    if keyboard.w:
        ship.y -= 5
    if keyboard.s:
        ship.y += 5
    if keyboard.a:
        ship.x -= 5
    if keyboard.d:
        ship.x += 5

    ship.x = max(20, min(WIDTH - 20, ship.x))
    ship.y = max(20, min(HEIGHT - 20, ship.y))

    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    if keyboard.space and shoot_cooldown == 0:
        bullet = Actor("bullet", (ship.x, ship.y - 20))
        bullets.append(bullet)
        shoot_cooldown = 10

    for enemy in enemies[:]:
        enemy.y += enemy.speed
        enemy.shoot_timer -= 1

        if enemy.y > HEIGHT + 20:
            enemies.remove(enemy)
            new_enemy()
            continue

        if spawn_invulnerable == 0 and ship.colliderect(enemy):
            create_explosion(enemy.x, enemy.y)
            create_explosion(ship.x, ship.y)
            enemies.remove(enemy)
            lives -= 1
            spawn_invulnerable = 90
            ship.pos = (300, 400)
            new_enemy()

            if lives <= 0:
                mode = "end"
            continue

        if enemy.shoot_timer <= 0:
            e_bullet = Actor("bullet", (enemy.x, enemy.y + 20))
            e_bullet.speed = 5
            enemy_bullets.append(e_bullet)
            enemy.shoot_timer = random.randint(70, 150)

    for bullet in bullets[:]:
        bullet.y -= 8

        if bullet.y < -20:
            bullets.remove(bullet)
            continue

        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                create_explosion(enemy.x, enemy.y)
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 10
                new_enemy()
                break

    for bullet in enemy_bullets[:]:
        bullet.y += bullet.speed

        if bullet.y > HEIGHT + 20:
            enemy_bullets.remove(bullet)
            continue

        if spawn_invulnerable == 0 and bullet.colliderect(ship):
            create_explosion(ship.x, ship.y)
            enemy_bullets.remove(bullet)
            lives -= 1
            spawn_invulnerable = 90
            ship.pos = (300, 400)

            if lives <= 0:
                mode = "end"


def update_explosions():
    for p in explosions[:]:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["life"] -= 1
        if p["life"] <= 0:
            explosions.remove(p)


def update_stars():
    for star in stars:
        star[1] += star[2]
        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0
            star[2] = random.randint(1, 3)


create_stars()
reset_game()