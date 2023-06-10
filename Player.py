# Import necessary library
import pygame
from aniSupport import knight_folder
import os
import random

# Create Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, globalvolume=1, maindirectory=""):
        super().__init__()  # Inherit from super

        # Identify working directory
        self.maindirectory = maindirectory

        self.iframe = 0
        self.direction = pygame.math.Vector2(0, 0)
        self.characterAnimation()

        self.image = self.spriteTest

        self.rect = self.image.get_rect(topleft=pos)

        self.mask = pygame.mask.Mask(size=(self.rect.width, self.rect.height), fill=True)

        self.prevjumpstate = False

        self.jumpNum = 0

        self.collisioncheck = False

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
        self.accelerationleft = 0
        self.accelerationright = 0

        self.startx = pos[0]
        self.starty = pos[1]

        self.uppercollision = False

        # Input related vars
        self.mouseinput = True

        # Setup pygame audio mixer
        self.mixer = pygame.mixer
        self.mixer.pre_init(44100, -16, 2, 64)
        self.mixer.init()
        self.mixer.set_num_channels(8)

        # Audio-related vars
        self.fallsoundtoggle = False
        self.globalvolume = globalvolume

        # Load sfx
        self.jumpsfx = self.mixer.Sound("audio/sfx/Jump.wav")
        self.jumpsfx.set_volume(min(1, self.globalvolume))

        self.fallsfx = self.mixer.Sound("audio/sfx/Fall.wav")
        self.fallsfx.set_volume(min(1, self.globalvolume))

        self.deathsfx = self.mixer.Sound("audio/sfx/Death.wav")
        self.deathsfx.set_volume(min(1, self.globalvolume*0.2))

        self.coinsfx = self.mixer.Sound("audio/sfx/Coin.wav")
        self.coinsfx.set_volume(min(1, self.globalvolume * 0.5))

        self.mainscreen = pygame.display.set_mode((1024, 768))
        self.distancesprinted = 0

    def setmainscreen(scr):
        mainscreen = scr

    def getacceleration(self):
        accelval = abs(self.accelerationleft + self.accelerationright)
        return accelval

    def applyGravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def getbusychannel(self, channel):
        return self.mixer.Channel(channel).get_busy()

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

            if not self.mixer.Channel(1).get_busy():
                self.jumpNum += 1
                self.mixer.Channel(1).play(self.jumpsfx)

    def setdirectionx(self, direction):
        self.direction.x = direction

    def setcollisionstatus(self, collisionbool):
        self.collisioncheck = collisionbool

    def getdirectiony(self):
        return self.direction.y

    def setglobalvolume(self, volume):
        self.globalvolume = volume
        for item in range(self.mixer.get_num_channels()):
            self.mixer.Channel(item).set_volume(min(1, self.globalvolume))

    def getfallsoundtoggle(self):
        return self.fallsoundtoggle

    def setfallsoundtoggle(self, fallsoundtoggle):
        self.fallsoundtoggle = fallsoundtoggle

    def playfallsound(self):
        self.fallsoundtoggle = False
        if not self.mixer.Channel(2).get_busy():
            self.mixer.Channel(2).play(self.fallsfx)

    def playdeathsound(self):
        if not self.mixer.Channel(3).get_busy():
            self.mixer.Channel(3).play(self.deathsfx)

    def playcoinsound(self):
        if not self.mixer.Channel(3).get_busy():
            self.mixer.Channel(3).play(self.coinsfx)

    # pause quotes
    def pausequotes(self):
        value = random.randint(1, 9)
        if value == 1:
            return 'Practice is the path to mastery.'
        if value == 2:
            return 'Not as easy as it looks...'
        if value == 3:
            return 'Painfully pixel perfect platforming.'
        if value == 4:
            return 'Try again after having rested.'
        if value == 5:
            return 'Reaching the top has never been so satisfying.'
        if value == 6:
            return "Don't slip up!"
        if value == 7:
            return 'Every failure is a lesson.'
        if value == 8:
            return 'The greater the challenge, the greater the reward.'
        if value == 9:
            return '"' + "Don't give up, skeleton!" + '"'

    def paused(self):
        counter = 0
        transparencyflag = True

        font = pygame.font.Font(os.path.join(str(self.maindirectory), 'slkscr.ttf'), 24)
        quotetext = font.render(self.pausequotes(), True, (255, 255, 255))
        clock = pygame.time.Clock()
        pause = True
        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        pause = False

                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()

                    elif event.key == pygame.K_r:  #reset player position
                        pause = False
                        self.reset()
            font = pygame.font.Font(os.path.join(str(self.maindirectory), 'slkscr.ttf'), 24)
            jumpCntr = font.render('Current Level Jumps: ' + str(int((self.jumpNum))), True, (255, 255, 255))
            sprintdist = font.render('Current Level Distance Sprinted: ' + str(int((self.distancesprinted))) + 'm', True, (255, 255, 255))
            text = font.render('PAUSED: C to Continue, Q to Quit, R to Restart', True, (255, 255, 255))
            screen_width = 1024
            screen_height = 768
            counter += .1
            if counter > 5:  # randomize pausequote after interval
                quotetext = font.render(self.pausequotes(), True, (255, 255, 255))
                counter = 0
            text_screen = self.mainscreen
            quoterect = pygame.Rect(0,(screen_height * 0.35) + 64 - (text.get_height() / 2), 1024, 25)
            pygame.draw.rect(text_screen, (0,0,0), quoterect)
            text_screen.blit(text, ((screen_width * 0.5) - (text.get_width() / 2), (screen_height * 0.35) + 128 - (text.get_height() / 2)))
            text_screen.blit(jumpCntr, ((screen_width * 0.5) - (text.get_width() / 2), (screen_height * 0.35) + 155 - (text.get_height() / 2)))
            text_screen.blit(sprintdist, ((screen_width * 0.5) - (text.get_width() / 2), (screen_height * 0.35) + 182 - (text.get_height() / 2)))
            # print(self.jumpNum)
            text_screen.blit(quotetext, ((screen_width * 0.5) - (text.get_width() / 2), (screen_height * 0.35) + 64 - (text.get_height() / 2)))
            transparentwindow = pygame.Surface((screen_width,screen_height), pygame.SRCALPHA)  # per pixel alpha
            transparentwindow.convert_alpha()
            transparentwindow.fill((0,0,0,100))
            if transparencyflag:  # apply transparent window layer only ONCE
                text_screen.blit(transparentwindow, ((0,0)))
                transparencyflag = False
            pygame.display.update()
            clock.tick(5)

    # Process pressed keys
    def getInput(self):
        keys = pygame.key.get_pressed()
        # [DEBUG] ALLOW UP AND DOWN MOVEMENT
        # if keys[pygame.K_UP] or keys[pygame.K_w]:
        #     self.direction.y = -1
        # elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        #     self.direction.y = 1
        # if keys[pygame.K_DOWN] or keys[pygame.K_s]:  # Got rid of 'up' movement
        #     self.direction.y = 1
        # else:
        # self.direction.y = 0

        # Movement keys
        if not self.collisioncheck:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.mouseinput = False
                self.direction.x = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.mouseinput = False
                self.direction.x = 1
            else:
                if self.mouseinput == False:
                    self.direction.x = 0
        # if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        #     self.direction.x = -1
        #     # rChar = False
        #     # lChar = True
        # elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        #     self.direction.x = 1
        # else:
        #     self.direction.x = 0

        # [Possibly DEBUG] add jump key
        if keys[pygame.K_SPACE]:
            self.mouseinput = False
            self.jump(mousetoggle=self.mouseinput)

        if pygame.mouse.get_pressed(num_buttons=3)[0] and not self.prevjumpstate:
            self.mouseinput = True
            self.jump(mousetoggle=self.mouseinput)

        # pause
        if keys[pygame.K_p]:
            self.paused()

        # sprint
        maxaccelleft = -1
        maxaccelright = 1
        accelrate = .01
        if keys[pygame.K_a] and keys[pygame.K_LSHIFT] or keys[pygame.K_a] and keys[pygame.K_RSHIFT] or keys[pygame.K_LEFT] and keys[pygame.K_LSHIFT] or keys[pygame.K_LEFT] and keys[pygame.K_RSHIFT]:
            self.distancesprinted += abs(self.direction.x)  # track distance sprinted
            # increase spd/acceleration before breaching max acceleration, if not in air/jumping
            if self.accelerationleft > maxaccelleft and self.direction.y <= .8:
                self.accelerationleft -= accelrate
                self.direction.x = -1 + self.accelerationleft
            elif self.direction.y != .4 or self.direction.y != .8:  # stabilize speed if in air/jumping
                self.direction.x = -1 + self.accelerationleft
            elif self.accelerationleft <= maxaccelleft:  # stabilize speed after breaching max acceleration
                self.direction.x = -1 + maxaccelleft
        else:  # instantly reset acceleration if keys are not held
            self.accelerationleft = 0

        if keys[pygame.K_d] and keys[pygame.K_LSHIFT] or keys[pygame.K_d] and keys[pygame.K_RSHIFT] or keys[pygame.K_RIGHT] and keys[pygame.K_LSHIFT] or keys[pygame.K_RIGHT] and keys[pygame.K_RSHIFT]:
            self.distancesprinted += abs(self.direction.x)
            if self.accelerationright < maxaccelright and self.direction.y <= .8:
                self.accelerationright += accelrate
                self.direction.x = 1 + self.accelerationright
            elif self.direction.y != .4 or self.direction.y != .8:
                self.direction.x = 1 + self.accelerationright
            elif self.accelerationright >= maxaccelright:
                self.direction.x = 1 + maxaccelright
        else:
            self.accelerationright = 0

    # Update new position //and animation
        # if pygame.mouse.get_pressed(num_buttons=3)[0]:
        #     self.prevjumpstate = True
        # else:
        #     self.prevjumpstate = False

    def getcoords(self):
        return (self.rect.x, self.rect.y)

    def characterAnimation(self):
        char_animation_path = os.path.join(str(self.maindirectory), 'animation', 'characterAnimation')  # Actual animations
        # char_animation_path = os.path.join(str(self.maindirectory), 'animation', 'debugAnimation')  # DEBUG, solid animations
        self.animations = {'idle': [], 'run': [], 'jumper': [], 'falling': [], 'death': []}

        for animation in self.animations.keys():
            full_path = os.path.join(char_animation_path, animation)
            self.animations[animation] = knight_folder(full_path)

        self.spriteTest = []

        self.idleFrame = False
        self.runFrame = False
        self.jumpFrame = False
        self.fallFrame = False

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

        if (self.direction.x > 0):
            self.xFlip = False
        if (self.direction.x < 0):
            self.xFlip = True

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

        '''if self.deathFrame:
            if self.idleFrame or self.runFrame or self.jumpFrame or self.fallFrame:
                self.iframe = 0
            self.idleFrame = False
            self.runFrame = False
            self.jumpFrame = False
            self.fallFrame = False
            self.spriteTest = self.animations['death'][int(self.iframe)]'''

    def getJumps(self):
        return self.jumpNum

    # Update new position
    def update(self, y_offset=0):
        self.fulloffset = y_offset
        # print(self.fulloffset)
        self.getInput()

        # iframe as index for animations
        if self.idleFrame and self.iframe <= 9:
            self.iframe += 0.25
            if self.iframe == 9:
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

        '''if self.deathFrame:
            self.iframe += 0.25
            if self.iframe == 9:
                self.iframe = 0'''

        self.characterAnimation()

        # self.image = pygame.transform.scale(self.sprite, 45, 57 )
        if self.xFlip:
            self.image = pygame.transform.flip(self.spriteTest, True, False)
        else:
            self.image = self.spriteTest

        # self.image = self.spriteTest
        # self.image = pygame.Surface((16, 32))
        # self.image.fill("Red")

        self.mask.fill()
        self.rect.y += y_offset
