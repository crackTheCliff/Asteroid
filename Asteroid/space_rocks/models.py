from pygame.math import Vector2
from pygame.transform import rotozoom
from utils import get_random_velocity, load_sound, load_sprite, wrap_position

# established UP movement parameters
UP = Vector2(0, -1)

# General game logic
class GameObject:
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = Vector2(velocity)

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

# wraps game objects
    def move(self, surface):
        self.position = wrap_position(self.position + self.velocity, surface)

# establish collision
    def collides_with(self, other_obj):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius

# Spaceship functionality
class Spaceship(GameObject):
    # general logic values
    MANEUVERABILITY = 3
    ACCELERATION = 0.25
    BULLET_SPEED = 3

# positioning
    def __init__(self, position, create_bullet_callback):
        self.create_bullet_callback = create_bullet_callback
        self.laser_sound = load_sound("laser")
        self.direction = Vector2(UP)
        super().__init__(position, load_sprite("spaceship"), Vector2(0))

# rotation of ship
    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

# re-draws ship at new angle
    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

# acceleration of ship
    def accelerate(self):
        self.velocity += self.direction * self.ACCELERATION

# Firing ability
    def shoot(self):
        bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
        bullet = Bullet(self.position, bullet_velocity)
        self.create_bullet_callback(bullet)
        self.laser_sound.play()

# bullets for ship
class Bullet(GameObject):
    def __init__(self, position, velocity):
        super().__init__(position, load_sprite("bullet"), velocity)

# overrides wrap for bullets
    def move(self, surface):
        self.position = self.position + self.velocity

# general asteroid class
class Asteroid(GameObject):
    def __init__(self, position, create_asteroid_callback, size=3):
        self.create_asteroid_callback = create_asteroid_callback
        self.size = size

        size_to_scale = {
            3: 1,
            2: 0.5,
            1: 0.25,
        }
        scale = size_to_scale[size]
        sprite = rotozoom(load_sprite("asteroid"), 0, scale)

        super().__init__(
            position, sprite, get_random_velocity(1, 3)
        )

    # splits asteroid 
    def split(self):
        if self.size > 1:
            for _ in range(2):
                asteroid = Asteroid(
                    self.position, self.create_asteroid_callback, self.size - 1
                )
                self.create_asteroid_callback(asteroid)