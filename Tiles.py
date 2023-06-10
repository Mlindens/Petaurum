import pygame
from aniSupport import getImage

# Create Tile class
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size, sprite="", color="", trigger="", path="", collision=True, deadly=False):
        super().__init__()  # Inherit from super
        self.collision = collision
        self.image = pygame.Surface((size, size))
        self.imagetint = pygame.Surface((size, size))
        if color != "":
            self.image.fill(str(color))
        else:
            self.image = sprite.copy()
        # Darken image if no collision
        if not collision:
            self.tintsurface(self.image, 0.3)
        self.trigger = trigger
        self.deadly = deadly
        # self.image.load("/images/logo/Logo.png")
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.orig_location = self.rect.topleft

    def tintsurface(self, surface, tintfactor):
        w, h = surface.get_size()
        for x in range(w):
            for y in range(h):
                r_temp = surface.get_at((x, y))[0]
                r = max((r_temp)*tintfactor, 0)
                g_temp = surface.get_at((x, y))[1]
                g = max((g_temp)*tintfactor, 0)
                b_temp = surface.get_at((x, y))[2]
                b = max((b_temp)*tintfactor, 0)
                a = surface.get_at((x, y))[3]
                surface.set_at((x, y), pygame.Color(int(r), int(g), int(b), a))

    def update(self, y_offset):
        self.rect.y += y_offset

    def origlocation(self, y_offset):
        if self.trigger == "stalactite":
            self.hide(True)
            self.deadly = False
            self.collision = False
            # self.rect.y = self.orig_location[1] - 128 + y_offset

    def getmask(self):
        return self.mask

    def getcollision(self):
        return self.collision

    def get_deadly(self):
        return self.deadly

    def returnTrigger(self):
        return self.trigger

    def setCollision(self, bool):
        self.collision = bool

    def setTrigger(self, trigger):
        self.trigger = trigger

    def hide(self, bool):
        if bool:
            self.image.set_alpha(0)
        else:
            self.image.set_alpha(255)