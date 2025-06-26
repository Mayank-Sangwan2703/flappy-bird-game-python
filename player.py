import pygame

class Player:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.velocity_y = -9
        self.max_vel_y = 10
        self.min_vel_y = -8
        self.acc_y = 1
        self.flap_acc = -8
        self.flapped = False

    def flap(self):
        self.velocity_y = self.flap_acc
        self.flapped = True

    def move(self, ground_y):
        if self.velocity_y < self.max_vel_y and not self.flapped:
            self.velocity_y += self.acc_y
        if self.flapped:
            self.flapped = False
        player_height = self.image.get_height()
        self.y = self.y + min(self.velocity_y, ground_y - self.y - player_height)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
