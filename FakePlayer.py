# Import necessary library
import pygame
from aniSupport import knight_folder
import os

# Create Player class
class FakePlayer(pygame.sprite.Sprite):
    def __init__(self, pos, maindirectory=""):
        super().__init__()  # Inherit from super

        # Identify working directory
        self.maindirectory = maindirectory

        self.iframe = 0
        self.direction = pygame.math.Vector2(0, 0)
        self.characterAnimation()

        self.image = self.spriteTest

        self.rect = self.image.get_rect(topleft=pos)
        self.prevjumpstate = False

        # xFlip for flipping animations horizontally and deathFrame for once death occurs
        self.xFlip = False
        #self.deathFrame = False

        # Position and speed related vars
        self.horiz_speed = 4
        self.vert_speed = 8
        self.gravity = 0.4
        self.jump_speed = 10
        self.fulloffset = 0
        self.totalmovement = 0

        self.startx = pos[0]
        self.starty = pos[1]

        self.uppercollision = False

        # Input related vars
        self.mouseinput = True

    def applyGravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def reset(self):
        self.direction.x = 0
        self.direction.y = 0
        # print((self.startx, self.starty))
        # print(self.totalmovement)
        self.rect.x = self.startx + 4
        self.rect.y = self.starty + self.fulloffset - 32 + self.totalmovement

    def jump(self, mousetoggle=True):
        if self.direction.y == 0 and not self.uppercollision:
            if not mousetoggle:
                # Keyboard-based jumping
                self.direction.y = abs(self.jump_speed) - (2*abs(self.jump_speed))
            else:
                # Mouse-based jumping
                self.direction.y = 0 - min(abs((pygame.mouse.get_pos()[1] - self.rect.y)*0.1), self.jump_speed)
                if pygame.mouse.get_pos()[0] > self.rect.x:
                    self.direction.x = min(abs((pygame.mouse.get_pos()[0] - self.rect.x)*0.01), 1)
                else:
                    self.direction.x = 0 - min(abs((pygame.mouse.get_pos()[0] - self.rect.x) * 0.01), 1)


    def setdirectionx(self, direction):
        self.direction.x = direction

    def getdirectiony(self):
        return self.direction.y


    def getcoords(self):
        return (self.rect.x, self.rect.y)

    def characterAnimation(self):
        char_animation_path = os.path.join(str(self.maindirectory), 'animation', 'characterAnimation')
        self.animations = {'idle': [], 'run': [], 'jumper': [], 'falling': []}

        for animation in self.animations.keys():
            full_path = os.path.join(char_animation_path, animation)
            self.animations[animation] = knight_folder(full_path)

        self.spriteTest = []

        self.idleFrame = False
        self.runFrame = False
        self.jumpFrame = False
        self.fallFrame = False

        if (self.direction.x > 0):
            self.xFlip = False
        if (self.direction.x < 0):
            self.xFlip = True

        if (self.direction.x == 0.0):
            try:
                if self.runFrame or self.jumpFrame or self.fallFrame:
                    self.iframe = 0
                self.idleFrame = True
                self.runFrame = False
                self.jumpFrame = False
                self.fallFrame = False
                self.spriteTest = self.animations['idle'][int(self.iframe)]
            except(IndexError):
                self.iframe = 0
                self.spriteTest = self.animations['idle'][int(self.iframe)]
                pass

        if (self.direction.x > 0 or self.direction.x < 0):
            if self.idleFrame or self.jumpFrame or self.fallFrame:
                self.iframe = 0
            self.idleFrame = False
            self.runFrame = True
            self.jumpFrame = False
            self.fallFrame = False
            self.spriteTest = self.animations['run'][int(self.iframe)]

        if self.direction.y < 0:
            if self.idleFrame or self.runFrame or self.fallFrame:
                self.iframe = 0
            self.idleFrame = False
            self.runFrame = False
            self.jumpFrame = True
            self.fallFrame = False
            self.spriteTest = self.animations['jumper'][int(self.iframe)]

        if self.direction.y >= 1:
            if self.idleFrame or self.runFrame or self.jumpFrame:
                self.iframe = 0
            self.idleFrame = False
            self.runFrame = False
            self.jumpFrame = False
            self.fallFrame = True
            self.spriteTest = self.animations['falling'][int(self.iframe)]


    # Update new position
    def update(self, y_offset=0):
        self.fulloffset = y_offset
        # print(self.fulloffset)
        # self.getInput()

        self.rect.x += self.direction.x * self.horiz_speed

        # iframe as index for animations
        if self.idleFrame and self.iframe <= 9:
            self.iframe += 0.25
            if self.iframe == 8:
                self.iframe = 0

        if self.runFrame and self.iframe <= 10:
            self.iframe += 0.25
            if self.iframe == 10:
                self.iframe = 0

        if self.jumpFrame and self.iframe <= 3:
            self.iframe += 0.25
            if self.iframe == 3:
                self.iframe = 0

        if self.fallFrame and self.iframe <= 3:
            self.iframe += 0.25
            if self.iframe == 3:
                self.iframe = 0

        #FakePlayer does not die :)

        self.characterAnimation()

        # self.image = pygame.transform.scale(self.sprite, 45, 57 )
        if self.xFlip:
            self.image = pygame.transform.flip(self.spriteTest, True, False)
        else:
            self.image = self.spriteTest

        self.image.set_alpha(128)

        self.rect.y += y_offset
