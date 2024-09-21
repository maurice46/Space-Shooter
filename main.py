import pygame
from random import randint, uniform 
from os.path import join

# classes

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join("images", "player.png")).convert_alpha() 
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2,WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2(0, 0)
        self.speed = 600
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400 
        self.mask = pygame.mask.from_surface(self.image) 
        self.score = 0 
        self.lives = 3

    def update_score(self, points):
        self.score += points

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()
    
class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000 
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(300,800)
        self.rotation_speed = randint(20, 50)
        self.rotation = 0

    def update(self, dt):
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rect.center += self.direction * self.speed * dt
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)
    
class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0 
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
    
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

# functions

def meteor_collision():
    global running
    collision_sprites = pygame.sprite.spritecollide(aircraft, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        aircraft.lives -= 1
        if aircraft.lives <= 0:
            running = False
        else:
            aircraft.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)

def laser_collision():
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()
            aircraft.update_score(len(collided_sprites))

def display_time():
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    text_surf = font.render(f"Time: {elapsed_time}s", True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 10).move(0, -8), 5, 10)

def display_score():
    text_surf = font.render(f"Score: {aircraft.score}", True, (240, 240, 240))
    text_rect = text_surf.get_frect(topleft = (20, 20))
    display_surface.blit(text_surf, text_rect)

def display_lives():
    text_surf = font.render(f"Lives: {aircraft.lives}", True, (240, 240, 240))
    text_rect = text_surf.get_frect(topleft = (20, 60))
    display_surface.blit(text_surf, text_rect)

# general setup

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Shooter")
running = True
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()

# imports

star_surf = pygame.image.load(join("images", "star.png")).convert_alpha()
meteor_surf = pygame.image.load(join("images", "meteor.png")).convert_alpha()
laser_surf = pygame.image.load(join("images", "laser.png")).convert_alpha()
# font (font style, size)
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
# 20 pictures to show the animated explosions
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]
# sounds
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)
game_music.play(loops= -1)


# sprites

all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()


# displays

for i in range(100):
    Star(all_sprites, star_surf)

aircraft = Player(all_sprites)

# custom events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

# game loop

while running:
    dt = clock.tick() / 1000 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

    display_surface.fill('black') 

    all_sprites.draw(display_surface)

    all_sprites.update(dt)
   
    meteor_collision()

    laser_collision()
    
    display_time()

    display_score()

    display_lives()

    pygame.display.update()

pygame.quit() 