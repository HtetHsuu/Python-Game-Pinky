import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Jungle Jump")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("C:/Users/DELL/Downloads", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("C:/Users/DELL/Downloads", "C:/Users/DELL/Downloads/Terrain", "C:/Users/DELL/Downloads/Terrain/Terrain (16x16).png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("C:/Users/DELL/Downloads/Main Characters", "Pink Man", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        
        self.jump_sound = pygame.mixer.Sound("C:/Users/DELL/Downloads/audio_jump.mp3")
        self.jump_sound.set_volume(0.5)

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
            self.jump_sound.play()
            
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "Idle (32x32)"
        if self.hit:
            sprite_sheet = "Hit (32x32)"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "Jump (32x32)"
            elif self.jump_count == 2:
                sprite_sheet = "Double Jump (32x32)"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "Fall (32x32)"
        elif self.x_vel != 0:
            sprite_sheet = "Run (32x32)"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["Off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Off"

    def on(self):
        self.animation_name = "On (16x32)"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("C:/Users/DELL/Downloads", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Pink.png")

    block_size = 96

    player = Player(100, 100, 50, 50)
    fire = Fire(200, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire]

    bg_music = pygame.mixer.Sound('C:/Users/DELL/Downloads/music.wav')
    bg_music.play(loops = -1)

    new_block_x=380
    new_block_y=HEIGHT-block_size*4
    new_block=Block(new_block_x,new_block_y,block_size)
    objects.append(new_block)

    new_block1_x=380
    new_block1_y=HEIGHT-block_size*5
    new_block1=Block(new_block1_x,new_block1_y,block_size)
    objects.append(new_block1)
    
    new_block2_x=760
    new_block2_y=HEIGHT-block_size*5.5
    new_block2=Block(new_block2_x,new_block2_y,block_size)
    objects.append(new_block2)

    new_block3_x=670
    new_block3_y=HEIGHT-block_size*5.5
    new_block3=Block(new_block3_x,new_block3_y,block_size)
    objects.append(new_block3)

    new_block4_x=1100
    new_block4_y=HEIGHT-block_size*6
    new_block4=Block(new_block4_x,new_block4_y,block_size)
    objects.append(new_block4)
    
    new_block5_x=1200
    new_block5_y=HEIGHT-block_size*6
    new_block5=Block(new_block5_x,new_block5_y,block_size)
    objects.append(new_block5)

    new_block7_x=1350
    new_block7_y=HEIGHT-block_size*4.5
    new_block7=Block(new_block7_x,new_block7_y,block_size)
    objects.append(new_block7)

    new_block6_x=1700
    new_block6_y=HEIGHT-block_size*6.5
    new_block6=Block(new_block6_x,new_block6_y,block_size)
    objects.append(new_block6)

    new_block8_x=1800
    new_block8_y=HEIGHT-block_size*6.5
    new_block8=Block(new_block8_x,new_block8_y,block_size)
    objects.append(new_block8)

    new_block9_x=-320
    new_block9_y=HEIGHT-block_size*4
    new_block9=Block(new_block9_x,new_block9_y,block_size)
    objects.append(new_block9)
    
    new_block10_x=0
    new_block10_y=HEIGHT-block_size*5.5
    new_block10=Block(new_block10_x,new_block10_y,block_size)
    objects.append(new_block10)
    
    new_trap_x=500
    new_trap_y=HEIGHT-block_size-64
    new_trap_width=16
    new_trap_height=32
    new_trap=Fire(new_trap_x,new_trap_y,new_trap_width,new_trap_height)
    new_trap.on()
    objects.append(new_trap)


    new_trap1_x=700
    new_trap1_y=HEIGHT-block_size-64
    new_trap1_width=16
    new_trap1_height=32
    new_trap1=Fire(new_trap1_x,new_trap1_y,new_trap1_width,new_trap1_height)
    new_trap1.on()
    objects.append(new_trap1)

    new_trap2_x=1700
    new_trap2_y=HEIGHT-block_size-64
    new_trap2_width=16
    new_trap2_height=32
    new_trap2=Fire(new_trap2_x,new_trap2_y,new_trap2_width,new_trap2_height)
    new_trap2.on()
    objects.append(new_trap2)
    
    new_trap3_x=-315
    new_trap3_y=350
    new_trap3_width=16
    new_trap3_height=32
    new_trap3=Fire(new_trap3_x,new_trap3_y,new_trap3_width,new_trap3_height)
    new_trap3.on()
    objects.append(new_trap3)


    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        new_trap.loop()
        new_trap1.loop()
        new_trap2.loop()
        new_trap3.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
