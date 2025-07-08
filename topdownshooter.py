import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 1000
FPS = 60
# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0,255,0)
# Set tracks switched to false

switched_track = False
soundplayed = True

# Set boss to dead

is_boss_ded = True
current_boss = 2

# Session high score
Session_high_Score = 0

# Import Sound

pygame.mixer.music.load('Audio/menu.mp3')
bullet_sound = pygame.mixer.Sound('Audio/fwop.mp3')
powerup_sound = pygame.mixer.Sound('Audio/power-up.mp3')
menu_scroll = pygame.mixer.Sound('Audio/menu_scroll.mp3')
menu_select = pygame.mixer.Sound('Audio/menu_select.mp3')
ship_destroyed = pygame.mixer.Sound('Audio/ship_destroy.mp3')
gameover_sound = pygame.mixer.Sound('Audio/gameover.mp3')
highscore_beaten = pygame.mixer.Sound('Audio/newhs.mp3')

# Play sound

pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)

# Player settings
player_size = 30
player_speed = 6
bullet_speed = 7
shoot_cooldown = 250  # in milliseconds
ispoweredup = 0

# Game over
gameover1 = pygame.image.load('Images/gameover.jpg')
gameover = pygame.transform.scale(gameover1, (1000, 1000))
gameover_rect = gameover.get_rect()
gameover_rect.center = (WIDTH //2, HEIGHT //2)

# Menu images
menu_image1 = pygame.image.load('Images/Menu.PNG')
menu_image = pygame.transform.scale(menu_image1, (1000, 1000))
menu_image_rect = menu_image.get_rect()
menu_image_rect.center = (WIDTH //2, HEIGHT //2)

class EnemySettings:
    def __init__(self, size, formation_size, spacing, delay, enemy_bullet_speed, health):
        self.size = size
        self.formation_size = formation_size
        self.spacing = spacing
        self.delay = delay
        self.enemy_bullet_speed = enemy_bullet_speed
        self.health = health
class BossSettings:
    def __init__(self, size, delay, enemy_bullet_speed, health):
        self.size = size
        self.delay = delay
        self.enemy_bullet_speed = enemy_bullet_speed
        self.health = health
        self.direction = 1
# Enemy settings instances for different types
enemy_type1_settings = EnemySettings(size=30, formation_size=3, spacing=50, delay=2500, enemy_bullet_speed=5, health=1)
enemy_type2_settings = EnemySettings(size=70, formation_size=2, spacing=100, delay=3500, enemy_bullet_speed=8, health=3)
enemy_type3_settings = EnemySettings(size=40, formation_size=5, spacing=90, delay=6000, enemy_bullet_speed=4, health=1)
enemy_type4_settings = EnemySettings(size=40, formation_size=5, spacing=90, delay=9900, enemy_bullet_speed=4, health=1)
boss_settings = BossSettings(size =100,delay=2500,enemy_bullet_speed=9,health=170) 

# Options menu settings
menu_font = pygame.font.Font(None, 36)
menu_selected_color = (0, 255, 0)
menu_unselected_color = WHITE

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down Shooter")
clock = pygame.time.Clock()

# Load images
custom_player_img = pygame.image.load('Images/PlayerIMG.png')
custom_player_img_l = pygame.image.load('Images/PlayerIMG_l.png')
custom_player_img_r = pygame.image.load('Images/PlayerIMG_r.png')
custom_player_bullet = pygame.image.load('Images/PlayerBullet.png')
custom_enemy_bullet = pygame.image.load('Images/EnemyBullet.png')

background_img = pygame.image.load('Images/BackgroundIMG.png')
background_surface = pygame.Surface((WIDTH, HEIGHT))

enemy1_img = pygame.image.load('Images/Enemy1.png')
enemy2_img = pygame.image.load('Images/Enemy2.png')
enemy3_img = pygame.image.load('Images/Enemy3.png')
enemy5_img = pygame.image.load('Images/Enemy5.png')

bullet_img = pygame.Surface((5, 10))
bullet_img.fill(WHITE)

# Save scores
def save_score(name, score):
    with open('scores.txt', 'a') as file:
        file.write(f"{name}: {score}\n")

# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []  # List to store explosion frames
        self.index = 0
        self.load_images()  # Load explosion frames
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.duration = 5  # Adjust the duration of each frame
        self.frame_delay = 5  # Adjust the delay between frames

    def load_images(self):
        # Load your explosion frames here (replace these paths with your actual image paths)
        explosion_frame_paths = ['Images/Explosion1.png',
                                 'Images/Explosion2.png',
                                 'Images/Explosion3.png',
                                 'Images/Explosion4.png',
                                 'Images/Explosion5.png']

        for path in explosion_frame_paths:
            original_image = pygame.image.load(path).convert_alpha()
            scaled_image = pygame.transform.scale(original_image, (50, 50))
            self.images.append(scaled_image)

    def update(self):
        self.duration -= 1

        if self.duration <= 0:
            self.index += 1

            if self.index < len(self.images):
                self.image = self.images[self.index]
                self.duration = self.frame_delay
            else:
                self.kill()

def draw_health(player):
        health_text = font.render(f"Health: {player.health}", True, WHITE)
        screen.blit(health_text, (10, HEIGHT-100))

# Create player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(custom_player_img, (60, 60))  # Adjust the size as needed
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.last_shot = pygame.time.get_ticks()
        self.num_bullets = 1  # Initial number of bullets
        self.health = 3
        
    def update(self):
        keys = pygame.key.get_pressed()
        self.image = pygame.transform.scale(custom_player_img, (60, 60))
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= player_speed
            self.image = pygame.transform.scale(custom_player_img_l, (60, 60))
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += player_speed
            self.image = pygame.transform.scale(custom_player_img_r, (60, 60))
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= player_speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += player_speed
            
        # Shoot bullets with cooldown
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and current_time - self.last_shot > shoot_cooldown:
            if self.num_bullets == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                bullet_sound.play()
                   
            elif self.num_bullets == 2:
                bullet1 = Bullet(self.rect.centerx - 22, self.rect.top)
                bullet2 = Bullet(self.rect.centerx + 22, self.rect.top)
                
                all_sprites.add(bullet1, bullet2)
                bullets.add(bullet1, bullet2)
                bullet_sound.play()
            
            elif self.num_bullets == 3:
                bullet1 = Bullet(self.rect.centerx, self.rect.top)
                bullet2 = Bullet(self.rect.centerx - 22, self.rect.top + 20)
                bullet3 = Bullet(self.rect.centerx + 22, self.rect.top + 20)

                all_sprites.add(bullet1, bullet2, bullet3)
                bullets.add(bullet1, bullet2, bullet3)
                bullet_sound.play()
               

            self.last_shot = current_time
    
    def take_damage(self, damage):
        self.health -= damage

        if self.health <= 0:
            ship_destroyed.play()  # You can play the "Player died!" sound here
            # Display the game over screen, reset the game, etc.
            self.kill()  # Player dies if health drops to or below zero

# EnemyType1 class
class EnemyType1(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, settings):
        super().__init__()
        self.image = pygame.transform.scale(enemy1_img, (30, 30))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.shot = False
        self.settings = settings
        self.health = settings.health

    def shoot(self):
        if not self.shot:
            enemy_bullet = EnemyType1Bullet(self.rect.centerx, self.rect.bottom, self.settings)
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)
            self.shot = True
            
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

        if not self.shot and self.rect.top > 0:
            self.shoot()

# EnemyType2 class
class EnemyType2(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, settings):
        super().__init__()
        self.image = pygame.transform.scale(enemy2_img, (70, 70))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed * 1.2
        self.shot = False
        self.settings = settings
        self.health = settings.health

    def shoot(self):
        if not self.shot:
            enemy_bullet1 = EnemyType2Bullet(self.rect.centerx - 10, self.rect.bottom, self.settings)
            enemy_bullet2 = EnemyType2Bullet(self.rect.centerx + 10, self.rect.bottom, self.settings)

            all_sprites.add(enemy_bullet1, enemy_bullet2)
            enemy_bullets.add(enemy_bullet1, enemy_bullet2)

            self.shot = True
            
    def take_damage(self, damage):
        self.health -= damage
        self.shot = False
        if self.health <= 0:
            self.kill()

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

        if not self.shot and self.rect.top > 0:
            self.shoot()

# EnemyType3 class
class EnemyType3(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, settings):
        super().__init__()
        self.image = pygame.transform.scale(enemy3_img, (40, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.shot = False
        self.settings = settings
        self.health = settings.health

    def shoot(self):
        if not self.shot and self.rect.top > 0:
            player_position = player.rect.center
            bullet = EnemyType3Bullet(self.rect.centerx, self.rect.bottom, player_position, self.settings)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
            self.shot = True
            
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()

        # Start shooting when the enemy reaches the middle of the screen
        if self.rect.centerx >= WIDTH / 2 and not self.shot:
            self.shoot()
            self.shot = True  # Ensure the enemy shoots only once

# EnemyType4 class
class EnemyType4(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, settings):
        super().__init__()
        self.image = pygame.transform.scale(enemy3_img, (40, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -speed
        self.shot = False
        self.settings = settings
        self.health = settings.health

    def shoot(self):
        if not self.shot and self.rect.top > 0:
            player_position = player.rect.center
            bullet = EnemyType4Bullet(self.rect.centerx, self.rect.bottom, player_position, self.settings)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
            self.shot = True
            
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()

        # Start shooting when the enemy reaches the middle of the screen
        if self.rect.centerx <= WIDTH / 2 and not self.shot:
            self.shoot()
            self.shot = True  # Ensure the enemy shoots only once
            
class Boss1(pygame.sprite.Sprite):
    def __init__(self,x , y, speed, settings):
        super().__init__()
        self.image = pygame.transform.scale(enemy2_img, (100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -speed *1.5
        self.settings = settings
        self.health = settings.health
        self.direction = 1  # Initial horizontal direction
        self.shooting_cooldown_1 = 0  # Cooldown timer for the first attack pattern
        self.shooting_cooldown_2 = 0  # Cooldown timer for the second attack pattern
        self.shooting_interval_1 = 200  # Cooldown interval for the first attack pattern (in milliseconds)
        self.shooting_interval_2 = 50  # Cooldown interval for the second attack pattern (in milliseconds)
        
    def draw_health_bar(self):
        # Calculate the width of the health bar
        health_bar_width = int(self.rect.width * (self.health / 170))
        if health_bar_width < 0:
            health_bar_width = 0

        # Create a red health bar background
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 10, self.rect.width, 5))

        # Create a green health bar based on boss's health
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 10, health_bar_width, 5))
        
    
    def attack_pattern(self):
        # Implement a specific attack pattern for the boss
        # For example, shooting in a zigzag pattern
        for i in range(5):
            bullet = EnemyType1Bullet(self.rect.centerx - 30 + i * 15, self.rect.bottom - 5, self.settings)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
            
    def attack_pattern2(self):
        # Implement the second attack pattern for the boss
        # For example, firing a spread of bullets towards the player
        if self.shooting_cooldown_2 <= 0:
            player_position = player.rect.center
            bullet = EnemyType3Bullet(self.rect.centerx, self.rect.bottom, player_position, self.settings)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
            self.shooting_cooldown_2 = self.shooting_interval_2
        else:
            self.shooting_cooldown_2 -= 1
        
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()
            
    def update(self):
        # Start shooting when the enemy reaches the middle of the screen
        if self.health < 70:
                self.shooting_interval_1 = 80
                self.shooting_interval_2 = 20
        if self.rect.centerx != WIDTH / 2:
            # Handle first attack pattern
            if self.shooting_cooldown_1 <= 0:
                self.attack_pattern()
                self.shooting_cooldown_1 = self.shooting_interval_1
            else:
                self.shooting_cooldown_1 -= 1
            # Handle second attack pattern
            if self.shooting_cooldown_2 <= 0:
                self.attack_pattern2()
                self.shooting_cooldown_2 = self.shooting_interval_2
            else:
                self.shooting_cooldown_2 -= 1

        # Move the boss horizontally
        self.rect.x += self.speed * self.direction
        
        # Check if the boss has reached the screen edges horizontally
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            # Reverse the horizontal direction
            self.direction *= -1
class Boss(pygame.sprite.Sprite):
    def __init__(self,x , y, speed, settings):
        super().__init__()
        self.image = pygame.transform.scale(enemy1_img, (100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -speed *0.7
        self.shot = False
        self.settings = settings
        self.health = settings.health
        self.direction = 1
        self.tookdamage = 0
        self.shooting_cooldown_2 = 0
        self.shooting_interval_2 = 50
        
    def draw_health_bar(self):
        # Calculate the width of the health bar
        health_bar_width = int(self.rect.width * (self.health / 170))
        if health_bar_width < 0:
            health_bar_width = 0

        # Create a red health bar background
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 10, self.rect.width, 5))

        # Create a green health bar based on boss's health
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 10, health_bar_width, 5))
        

    def shoot(self):
        if self.shooting_cooldown_2 <= 0:
            bullet1 =  EnemyType1Bullet(self.rect.centerx -30, self.rect.bottom-5, self.settings)
            bullet2 = EnemyType1Bullet(self.rect.centerx +30, self.rect.bottom-5, self.settings)
            all_sprites.add(bullet1,bullet2)
            enemy_bullets.add(bullet1, bullet2)
            self.shooting_cooldown_2 = self.shooting_interval_2
        else:
            self.shooting_cooldown_2 -= 1
    def laser(self):
        if  self.rect.top > 0:
            player_position = player.rect.center
            bullet = EnemyType4Bullet(self.rect.centerx-1, self.rect.bottom -50, player_position, self.settings)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
            
            
    def take_damage(self, damage):
        self.health -= damage
        self.tookdamage += 1
        if self.tookdamage > 3:
            self.shot = False
            self.tookdamage = 0
        if self.health <= 0:
            self.kill()
            
            

    def update(self):
         # Move the boss left or right
        self.rect.x += self.speed * self.direction
        
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction *= -1

        if self.rect.centerx != WIDTH / 2:
            # Handle first attack pattern
            if self.shooting_cooldown_2 <= 0:
                self.shoot()
                self.shooting_cooldown_2 = self.shooting_interval_2
            else:
                self.shooting_cooldown_2 -= 1


        if self.health < 70:
            if self.rect.centerx <= WIDTH / 2:
                self.laser()


# Create bullet classes for each enemy type
class EnemyType1Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, settings):
        super().__init__()
        self.image = pygame.transform.scale(custom_enemy_bullet, (10, 10))
        self.rect = self.image.get_rect(center=(x, y))
        self.settings = settings

    def update(self):
        self.rect.y += self.settings.enemy_bullet_speed
        if self.rect.top > HEIGHT:
            self.kill()

class EnemyType2Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, settings):
        super().__init__()
        self.image = pygame.transform.scale(custom_enemy_bullet, (10, 10))
        self.rect = self.image.get_rect(center=(x, y))
        self.settings = settings

    def update(self):
        self.rect.y += self.settings.enemy_bullet_speed
        if self.rect.top > HEIGHT:
            self.kill()

class EnemyType3Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, player_position, settings):
        super().__init__()
        self.image = pygame.transform.scale(custom_enemy_bullet, (10, 10))
        self.rect = self.image.get_rect(center=(x, y))
        self.settings = settings
        self.direction = pygame.math.Vector2(player_position[0] - x, player_position[1] - y).normalize()

    def update(self):
        self.rect.x += self.direction.x * self.settings.enemy_bullet_speed
        self.rect.y += self.direction.y * self.settings.enemy_bullet_speed

        # Check if the bullet is still within the visible screen
        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()

class EnemyType4Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, player_position, settings):
        super().__init__()
        self.image = pygame.transform.scale(custom_enemy_bullet, (10, 10))
        self.rect = self.image.get_rect(center=(x, y))
        self.settings = settings
        self.direction = pygame.math.Vector2(player_position[0] - x, player_position[1] - y).normalize()

    def update(self):
        self.rect.x += self.direction.x * self.settings.enemy_bullet_speed
        self.rect.y += self.direction.y * self.settings.enemy_bullet_speed

        # Check if the bullet is still within the visible screen
        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()

# Create bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(custom_player_bullet, (10, 10))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= bullet_speed
        if self.rect.bottom < 0:
            self.kill()

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Score
score = 0
font = pygame.font.Font(None, 36)

# Initialize last formation time
last_formation_time = pygame.time.get_ticks()

# Difficulty settings
current_difficulty = {
    'Easy': {'enemy_speed': 2},
    'Medium': {'enemy_speed': 3},
    'Hard': {'enemy_speed': 4 }
}

# Set initial difficulty
global enemy_speed
enemy_speed = current_difficulty['Medium']['enemy_speed']
if enemy_speed == 2:
    selected_difficulty = "Difficulty: Easy"
elif enemy_speed == 3:
    selected_difficulty = "Difficulty: Medium" 
elif enemy_speed == 4:
    selected_difficulty = "Difficulty: Hard"
elif enemy_speed == 9:
    selected_difficulty = "Difficulty: Insane"

# Options menu function
def options_menu(in_game):
    global enemy_speed
    selected_option = 0
    #screen.blit(menu_image,menu_image_rect.topleft)
    #pygame.display.flip()
    #pygame.time.delay(2000)

    options = ["Start Game",selected_difficulty, "Close Game"] 
    if in_game:
        options = ["Resume Game",selected_difficulty, "Close game"]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                    menu_scroll.play()
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                    menu_scroll.play()
                elif event.key == pygame.K_RETURN:
                    menu_select.play()
                    if selected_option == 0:
                        #Code to play song after resuming the game (OPTIONAL I CANT GET IT TO RESUME)
                       # if  switched_track:
                            
                          #  pygame.mixer.music.load('harvester.mp3')  # Change 'new_track.ogg' to the desired new track
                          #  pygame.mixer.music.play()
                          #  pygame.mixer.music.set_volume(0.1)
                        if not switched_track:
                             
                            pygame.mixer.music.load('Audio/bgm.mp3')  # Change 'new_track.ogg' to the desired new track
                            pygame.mixer.music.play()
                            pygame.mixer.music.set_volume(0.1)
                             
                        return in_game  # Return the current in_game state
                    elif selected_option == 1:
                        difficulty_selected = difficulty_menu()
                        if difficulty_selected:
                            enemy_speed = current_difficulty[difficulty_selected]['enemy_speed']
                            options[1] = f"Difficulty: {difficulty_selected}"
                    elif selected_option == 2:
                        pygame.quit()
                        sys.exit()

        screen.fill((0, 0, 0))
        draw_menu(options, selected_option)
        pygame.display.flip()
        clock.tick(FPS)

# Difficulty menu function
def difficulty_menu():
    global enemy_speed
    selected_option = 1  # Start with the current difficulty selected
    options = ["Easy", "Medium", "Hard"]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    menu_scroll.play()
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    menu_scroll.play()
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    menu_select.play()
                    return options[selected_option]

        screen.fill((0, 0, 0))
        draw_menu(options, selected_option)
        pygame.display.flip()
        clock.tick(FPS)

# Draw menu
def draw_menu(options, selected_option):
    screen.blit(menu_image,menu_image_rect.topleft)
    menu_height = len(options) * 50
    menu_start_y = (HEIGHT - menu_height) // 2

    for i, option in enumerate(options):
        text_color = menu_selected_color if i == selected_option else menu_unselected_color
        text = menu_font.render(option, True, text_color)
        text_rect = text.get_rect(center=(WIDTH // 2, menu_start_y + i * 50))
        screen.blit(text, text_rect)

# Show options menu at the beginning
options_menu(False)

# Initialize last formation times for each enemy type
last_formation_time_enemy = pygame.time.get_ticks()
last_formation_time_enemy_type2 = pygame.time.get_ticks()
last_formation_time_enemy_type3 = pygame.time.get_ticks()
last_formation_time_enemy_type4 = pygame.time.get_ticks()

ship_destroyed.set_volume(0.3)
powerup_sound.set_volume(0.3)

# Main game loop
spawned = False
start_time = pygame.time.get_ticks()
boss_spawn_delay = 30000
in_game = False
temp_score = 0
scores = []
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                
                in_game = options_menu(True)  # Pass the in_game flag to options_menu
                
    # Draw the repeating background
    for x in range(0, WIDTH, background_img.get_width()):
        for y in range(0, HEIGHT, background_img.get_height()):
            screen.blit(background_img, (x, y))

    # Calculate time since last formation for each enemy type
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - start_time
    time_since_last_formation_enemy = current_time - last_formation_time_enemy
    time_since_last_formation_enemy_type2 = current_time - last_formation_time_enemy_type2
    time_since_last_formation_enemy_type3 = current_time - last_formation_time_enemy_type3
    time_since_last_formation_enemy_type4 = current_time - last_formation_time_enemy_type4

    if is_boss_ded:
    # Spawn enemies in small formations for EnemyType1
        if time_since_last_formation_enemy > enemy_type1_settings.delay:
            last_formation_time_enemy = current_time
            formation_x = random.randint(0, WIDTH - enemy_type1_settings.formation_size * enemy_type1_settings.spacing)
            for i in range(enemy_type1_settings.formation_size):
                enemy = EnemyType1(formation_x + i * enemy_type1_settings.spacing, 0, enemy_speed, enemy_type1_settings)
                all_sprites.add(enemy)
                enemies.add(enemy)

    # Spawn enemies in small formations for EnemyType2
        if time_since_last_formation_enemy_type2 > enemy_type2_settings.delay:
            last_formation_time_enemy_type2 = current_time
            formation_x = random.randint(0, WIDTH - enemy_type2_settings.formation_size * enemy_type2_settings.spacing)
            for i in range(enemy_type2_settings.formation_size):
                enemy_type2 = EnemyType2(formation_x + i * enemy_type2_settings.spacing, 0, enemy_speed, enemy_type2_settings)
                all_sprites.add(enemy_type2)
                enemies.add(enemy_type2)
            
    # Spawn enemies in small formations for EnemyType3
        if time_since_last_formation_enemy_type3 > enemy_type3_settings.delay:
            last_formation_time_enemy_type3 = current_time
            formation_x = -enemy_type3_settings.formation_size * enemy_type3_settings.spacing
            formation_y = random.randint(0, HEIGHT // 2)

            for i in range(enemy_type3_settings.formation_size):
                x_position = formation_x + i * enemy_type3_settings.spacing
                enemy_type3 = EnemyType3(x_position, formation_y, enemy_speed, enemy_type3_settings)
                all_sprites.add(enemy_type3)
                enemies.add(enemy_type3)
            
    # Spawn enemies in small formations for EnemyType4
        if time_since_last_formation_enemy_type4 > enemy_type4_settings.delay:
            last_formation_time_enemy_type4 = current_time
            formation_x = WIDTH + enemy_type4_settings.formation_size * enemy_type4_settings.spacing
            formation_y = random.randint(0, HEIGHT // 2)

            for i in range(enemy_type4_settings.formation_size):
                x_position = formation_x - i * enemy_type4_settings.spacing
                enemy_type4 = EnemyType4(x_position, formation_y, enemy_speed, enemy_type4_settings)
                all_sprites.add(enemy_type4)
                enemies.add(enemy_type4)

     # Update sprites
        all_sprites.update()
        
    elif not is_boss_ded:
        boss_time = pygame.time.get_ticks()
        if current_boss == 1:
        #Boss music
            if not is_boss_ded and not switched_track:
                    pygame.mixer.music.load('Audio/harvester.mp3')
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(0.1)
                    switched_track = True
            #Spawn boss
            if not spawned:
                print ('banana')
                temp_score = score
                boss = Boss1(WIDTH //2 , HEIGHT // 4, enemy_speed,boss_settings)
                all_sprites.add(boss)
                enemies.add(boss)
                spawned = True
            if score > temp_score+100:
                is_boss_ded = True
                boss_spawn_delay += 80000
                elapsed_time -= boss_time
                spawned = False
                current_boss = 2
                boss_time = 0
            all_sprites.update()
            boss.draw_health_bar()
            

        elif current_boss == 2:
            if not is_boss_ded and not switched_track:
                pygame.mixer.music.load('Audio/boss2.mp3')
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.1)
                switched_track = True
            #Spawn boss
            if not spawned:
                temp_score = score
                boss = Boss(WIDTH //2 , HEIGHT // 4, enemy_speed,boss_settings)
                all_sprites.add(boss)
                enemies.add(boss)
                spawned = True
            if score > temp_score + 100:
                is_boss_ded = True
                boss_spawn_delay += 80000
                elapsed_time -= boss_time
                spawned = False
                current_boss = 1
                boss_time = 0
            all_sprites.update()
            boss.draw_health_bar()
        
    if elapsed_time >= boss_spawn_delay:
        is_boss_ded = False
    # Check for collisions (enemy vs. player)
    hits = pygame.sprite.spritecollide(player, enemies, True)
    for enemy in hits:
        ship_destroyed.play()
        # Create an explosion at the enemy's position
        explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
        all_sprites.add(explosion)
    if hits:
        if isinstance(enemy, Boss) or isinstance(enemy, Boss1):
            player.take_damage(5)
        else:
            player.take_damage(1)
        if player.health <= 0:
            print("Player died!")
            ship_destroyed.play()  # Play the "Player died!" sound

            # Add any other actions you want to perform when the player dies
            switched_track = False
            is_boss_ded = True
            spawned = False
            soundplayed = False
            boss_spawn_delay = 30000
            start_time = pygame.time.get_ticks()
            pygame.mixer_music.fadeout(1000)
            #current_time = 0
            
            gameover_sound.play()
            screen.blit(gameover, gameover_rect.topleft)
            pygame.display.flip()
            pygame.time.delay(2000)

            pygame.mixer.music.load('Audio/menu.mp3')  # Change 'new_track.ogg' to the desired new track
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(0.1)
            
            score, ispoweredup = 0,0

            # Clear sprite groups
            all_sprites.empty()
            enemies.empty()
            enemy_bullets.empty()
            bullets.empty()

            # Recreate player sprite
            player = Player()
            all_sprites.add(player)

            in_game = options_menu(False)  # Pass the in_game flag to options_menu

    # Check for collisions (bullet vs. enemy)
    bullet_hits = pygame.sprite.groupcollide(bullets, enemies, True, False)
    for bullet, enemy_hit in bullet_hits.items():
        for enemy in enemy_hit:
            enemy.take_damage(1)  # Adjust the damage value as needed

            # Check if the enemy is still alive after taking damage
            if enemy.health <= 0:
                # Enemy is defeated
                ship_destroyed.play()
            
                # Create an explosion at the enemy's position
                explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                all_sprites.add(explosion)
            
                # Add any additional logic related to scoring or other effects
                if isinstance(enemy, Boss) or isinstance(enemy, Boss1):  # Check if the enemy is a boss
                    score += 500  # Award 500 points for defeating the boss
                    player.health+=1
                else:
                    if enemy_speed == 2:
                        score += 1
                        if score > Session_high_Score:
                            Session_high_Score = score
                            if not soundplayed:
                                highscore_beaten.play()
                                soundplayed = True
                    elif enemy_speed == 3:
                        score += 2
                        if score > Session_high_Score:
                            Session_high_Score = score
                            if not soundplayed:
                                highscore_beaten.play()
                                soundplayed = True
                    elif enemy_speed == 4:
                        score += 3
                        if score > Session_high_Score:
                            Session_high_Score = score
                            if not soundplayed:
                                highscore_beaten.play()
                                soundplayed = True

                    # Check if the player's score is greater than 100 and update num_bullets
                    if score >= 40 and score < 100:
                        player.num_bullets = 2
                        if ispoweredup == 0:
                            powerup_sound.play()
                            ispoweredup += 1

                    if score >= 100:
                        player.num_bullets = 3
                        if ispoweredup == 1:
                            powerup_sound.play()
                            ispoweredup += 1


                    if is_boss_ded and switched_track:
                        pygame.mixer.music.load('Audio/bgm.mp3')
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(0.1)
                        switched_track = False

    # Check for collisions (player vs. enemy bullet)
    player_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
    if player_hits:
        player.take_damage(1)
        if player.health <= 0:
            print("Player died!")
            ship_destroyed.play()  # Play the "Player died!" sound

            # Add any other actions you want to perform when the player dies
            switched_track = False
            is_boss_ded = True
            spawned = False
            soundplayed = False
            boss_spawn_delay = 30000
            start_time = pygame.time.get_ticks()
            pygame.mixer_music.fadeout(1000)
            #current_time = 0
            gameover_sound.play()
            
            screen.blit(gameover, gameover_rect.topleft)
            pygame.display.flip()
            pygame.time.delay(2000)

            pygame.mixer.music.load('Audio/menu.mp3')  # Change 'new_track.ogg' to the desired new track
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(0.1)
            
            score, ispoweredup = 0,0

            # Clear sprite groups
            all_sprites.empty()
            enemies.empty()
            enemy_bullets.empty()
            bullets.empty()

            # Recreate player sprite
            player = Player()
            all_sprites.add(player)

            in_game = options_menu(False)  # Pass the in_game flag to options_menu

    # Draw everything
    all_sprites.draw(screen)

    # Draw the scoreboard
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    High_score_text = font.render(f"High Score: {Session_high_Score}", True, WHITE)
    screen.blit(High_score_text, (10, 30))
    
    # Draw player health
    draw_health(player)
    
    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)    