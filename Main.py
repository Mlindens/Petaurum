# MIT License

# Copyright (c) 2022 MAMBA

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Game version number [YEAR.MONTH.BUILDNUMBER]
VERSION_INFO = "22.4.1"

# Try to import necessary libraries
try:
    import os
    import os.path
    import json
    import sys
    import math
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"  # Hide Pygame welcome message
    import pygame
    import random
    from math import pi
    import PIL
    from PIL import Image
    # import pygame_widgets
    # from FILE import *
    from FakePlayer import FakePlayer
    from Tiles import Tile
    from Levels import Levels
    from aniSupport import game_logo
    from Player import Player
except ImportError:
    print("[WARN] You are missing one or more libraries. This script cannot continue.")
    print("Try running in terminal >> python3 -m pip install -r Requirements.txt")
    quit()

# Identify working directory
maindirectory = os.path.dirname(os.path.abspath(__file__))

# Show logo
print("--- Hello from MAMBA ---\n")

# Global vars
global level

# Prepend any string with tag "[INFO]"
def printInfo(string):
    print("[INFO] " + str(string))


# Return list of level options
def getLevelInfo(json_name):
    try:
        filepath = os.path.join(str(maindirectory), "levels", str(json_name))
        with open(str(filepath), 'r') as json_file:
            json_dict = json.load(json_file)
        # Create list to store level info
        level_info_list = []

        # [INFO ABOUT LEVELS]
        # level_layout is one giant string, delimited by commas. The layout is sixteen chars long and is X sets tall

        # Read [list of] option(s) from JSON file and store in level_info_list

        # Level layout. Converts from STRING to LIST
        # level_info_list.append(str(json_dict["level_layout"]).replace("\n", "").replace("\t","").split(","))
        level_info_list.append("SPOT IS CURRENTLY UNUSED")
        # Level name. STRING
        level_info_list.append(str(json_dict["level_name"]))
        # Level background music. STRING
        level_info_list.append(str(json_dict["background_music"]))
        # Next level trigger
        level_info_list.append(str(json_dict["next_level"]))
        # Background
        level_info_list.append(str(json_dict["background_image"]))

        # Return the list of level info
        return level_info_list
    except FileNotFoundError:
        print("[WARN] \"" + str(json_name) + "\" file cannot be found. Please check files. Script cannot continue.")
        testinput = input("")
        quit()

# Init Pygame
printInfo("Init Pygame with specified options")

# Pygame options
pygame.init()
GAME_TITLE = "Petaurum"
screen_width = 1024
screen_height = 768
background_y = 0
global globalvolume
globalvolume = 0.5
global transition
transition = 0
timesincejump = 0

global levelJumps, fullJumps, totalJumps # grabbing num of jumps per level
levelJumps = [] # grab jumps per level
totalJumps = 0 # add them up
jumps = [] # use level # and add text w/ # of jumps
cnt = 0
fullJumpsTrigger = True
endTrigger = True
coin = []

orig_screen = pygame.display.set_mode((screen_width, screen_height))
screen = orig_screen.copy()
pygame.display.set_caption(str(GAME_TITLE))
clock = pygame.time.Clock()
showscreen = True
# test_tile = pygame.sprite.Group(Tile((100,100), 64))

# Init audio engine with 2 channels
mixer = pygame.mixer
mixer.pre_init(44100, -16, 2, 64)
mixer.init()
mixer.set_num_channels(8)

# Load the animated game logo
full_path = os.path.join(str(maindirectory), "images", "logo", "game")
animatedgamelogo = game_logo(full_path)

# Function to load a new level
def loadlevel(level_name):
    # Load level
    printInfo("Loading new level")
    level_dict = getLevelInfo(str(level_name)+".json")
    try:
        filepath = os.path.join(str(maindirectory), "levels", str(level_name)+".png")
        level_image = PIL.Image.open(str(filepath))
    except FileNotFoundError:
        print("[WARN] Level image file cannot be found. Please check files. Script cannot continue.")
        testinput = input("")
        quit()
    global level
    global mainbackground
    level = Levels(level_dict, screen, level_image, 64, (1024, 768), directory=str(maindirectory))  # Create class Levels from level_layout portion of list
    pygame.display.set_caption(str(GAME_TITLE) + " - " + str(level_dict[1]))

    # Load background
    mainbackground = pygame.image.load(str(maindirectory) + "/images/backgrounds/" + str(level_dict[4]))

    # Attempt to play specified audio track
    try:
        if level_dict[2] != "":
            music = mixer.Sound(str(maindirectory) + "/audio/music/" + str(level_dict[2]))
            music.set_volume(globalvolume)
            mixer.Channel(0).play(music, fade_ms=1000, loops=999)
    except IndexError:
        pass

    global transition
    if level_dict[1] != "Main Menu":
        transition = 1

# Animation-related step vars go here
introstep = 120
introstep2 = 0
introstep3 = 0
framec = 0

# Used to manage how fast the screen updates
frame_count = 0
frame_rate = 60
start_time = 0

# Scene vars go here
showmainmenu = True
firsttime = True
exit = False
creditscroll = 0
playmusic = True
transition = 0
transition_count = 0

# Score vars
coincount = 0
finaltime = ""

# Load any additional assets here
logo = pygame.image.load(str(maindirectory) + "/images/logo/Logo.gif")
group = pygame.image.load(str(maindirectory) + "/images/logo/Group.png")
mamba = pygame.transform.scale(pygame.image.load(str(maindirectory) + "/images/logo/Mamba.png"), (1024*0.8, 768*0.8))
gamelogo = pygame.transform.scale(pygame.image.load(str(maindirectory) + "/images/logo/Logo.gif"), (1024*0.7, 768*0.7))
helplogo = pygame.transform.scale(pygame.image.load(str(maindirectory) + "/images/logo/Help.png"), (512, 256))

# Load main menu level
loadlevel("MainMenu")

def screenBlit(var, num, horizShift):
    screen.blit(var, (
        (screen_width * 0.5) - (var.get_width() / 2) + horizShift,
        (screen_height * 0.35) + num - creditscroll - (var.get_height() / 2)))

# Loop forever
while not exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill("black")

    # Transition animation
    if transition != 0:
        while transition != 0:
            if transition == 1:
                # screen.fill((255, 255, 255), (0, 0, screen_width, transition_count))
                pygame.draw.rect(orig_screen, (255, 255, 255), (0, 0, screen_width, transition_count))

                font = pygame.font.Font(os.path.join(str(maindirectory), 'slkscr.ttf'), 48)
                text = font.render(str(level.level_layout[1]), True, (0, 0, 0))
                orig_screen.blit(text, ((screen_width * 0.5) - (text.get_width() / 2),
                                   (screen_height * 0.35) + 64 - (text.get_height() / 2)))

                pygame.display.flip()
                pygame.display.update()
                clock.tick(60)

                if transition_count <= screen_height:
                    transition_count += 20
                else:
                    transition = 2
                    transition_count = 0
            else:
                # screen.fill((255, 255, 255), (0, transition_count, screen_width, screen_height))
                pygame.draw.rect(orig_screen, (0, 0, 0), (0, transition_count, screen_width, 100))
                # print((0, transition_count, screen_width, screen_height))
                # orig_screen.blit(screen, (0, 0))

                font = pygame.font.Font(os.path.join(str(maindirectory), 'slkscr.ttf'), 48)
                text = font.render(str(level.level_layout[1]), True, (0, 0, 0))
                orig_screen.blit(text, ((screen_width * 0.5) - (text.get_width() / 2),
                                        (screen_height * 0.35) + 64 - (text.get_height() / 2)))

                pygame.display.flip()
                pygame.display.update()
                clock.tick(60)

                if transition_count <= screen_height:
                    transition_count += 20
                else:
                    transition = 0
                    transition_count = 0

    if showscreen or level.getmenu() != 0:
        while introstep > 0:
            logo.set_alpha(max(0, introstep))
            # screen.blit(logo, ((screen_width * 0.45) - (logo.get_width()/2), (screen_height * 0.45) - (logo.get_height()/2)))
            screen.blit(mamba, ((screen_width * 0.5) - (mamba.get_width() / 2), (screen_height * 0.35) + 128 - (mamba.get_height() / 2)))
            pygame.display.flip()
            introstep -= 1
            if introstep <= 0:
                introstep2 = 120
            orig_screen.blit(screen, (0, 0))
            pygame.display.flip()
            pygame.display.update()
            clock.tick(60)

        if showmainmenu:
            # Draw the floating logo in the center of the screen, hovering with sin wave
            logo_y = int(screen_height / 2 + math.sin(frame_count / 10) * 10)
            if framec >= len(animatedgamelogo)-1:
                framec = 0
            else:
                framec += 0.2
            screen.blit(animatedgamelogo[round(framec)], (screen_width / 2 - gamelogo.get_width() / 2, logo_y - 350))
            font = pygame.font.Font(os.path.join(str(maindirectory), 'slkscr.ttf'), 32)
            text = font.render('PRESS ENTER', True, (255, 255, 255))
            screen.blit(text, ((screen_width * 0.5) - (text.get_width() / 2), (screen_height * 0.35) + 200 + 64 - (text.get_height() / 2)))
            pygame.display.flip()
            orig_screen.blit(screen, (0, 0))
            pygame.display.flip()
            pygame.display.update()
            clock.tick(60)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                sfx = mixer.Sound(str(maindirectory) + "/audio/sfx/" + "start.wav")
                sfx.set_volume(globalvolume)
                mixer.Channel(4).play(sfx, fade_ms=0, loops=0)

                transition = 1
                showscreen = False
                showmainmenu = False

        # Game over screen
        if level.getmenu() == 1:
            screen.fill("red")
            font = pygame.font.Font(os.path.join(str(maindirectory), 'slkscr.ttf'), 32)
            text = font.render('YOU DIED, PRESS ENTER', True, (255, 255, 255))
            screen.blit(text, (
            (screen_width * 0.5) - (text.get_width() / 2), (screen_height * 0.35) + 128 - (text.get_height() / 2)))
            pygame.display.flip()
            orig_screen.blit(screen, (0, 0))
            pygame.display.flip()
            pygame.display.update()
            clock.tick(60)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                # exit = True
                transition = 1
                level.reset()

        pygame.display.flip()
        pygame.display.update()
    else:
        # test_tile.draw(screen)
        screen.fill(level.getbackgroundcolor())
        background_y += level.getcamerayshift()
        # screen.blit(pygame.transform.scale(mainbackground, (screen_width, level.getmaxheight())), (0, background_y))
        level.run()

        # Calculate total seconds
        total_seconds = frame_count // frame_rate

        # Divide by 60 to get total minutes
        minutes = total_seconds // 60

        # Use modulus (remainder) to get seconds
        seconds = total_seconds % 60

        # Use python string formatting to format in leading zeros
        if finaltime == "":
            output_string = "{0:02}:{1:02}".format(minutes, seconds)

        # Calculate total seconds
        total_seconds = start_time - (frame_count // frame_rate)
        if total_seconds < 0:
            total_seconds = 0

        # Divide by 60 to get total minutes
        minutes = total_seconds // 60

        # Use modulus (remainder) to get seconds
        seconds = total_seconds % 60

        frame_count += 1

        if pygame.mouse.get_pressed(num_buttons=3)[2]:
            # dist = abs(math.hypot(level.player_sprite.getcoords()[0], pygame.mouse.get_pos()[0])) + abs(math.hypot(level.player_sprite.getcoords()[1], pygame.mouse.get_pos()[1]))
            # pygame.draw.arc(screen, (255, 255, 255), (level.player_sprite.getcoords()[0], level.player_sprite.getcoords()[1], pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]), 0, pi)
            # player_vector = pygame.math.Vector2(level.player_sprite.getcoords()[0] + 16, level.player_sprite.getcoords()[1] + 16)
            # mouse_vector = pygame.math.Vector2(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
            # final_vector = pygame.math.Vector2()
            # final_vector.from_polar((min(player_vector.distance_to(mouse_vector), 96), pygame.math.Vector2().angle_to(mouse_vector - player_vector)))
            # pygame.draw.line(screen, (0, 0, 255), player_vector, player_vector + final_vector, width=4)
            # print(timesincejump)
            if timesincejump == 0:
                fakeplayer_sprite = FakePlayer(level.player_sprite.getcoords(), maindirectory=str(maindirectory))
                fakeplayer = pygame.sprite.GroupSingle()
                fakeplayer.add(fakeplayer_sprite)
                fakeplayer_sprite.jump(mousetoggle=True)
            if timesincejump < 30:
                fakeplayer_sprite.update(0)
                fakeplayer.draw(screen)
                fakeplayer_sprite.applyGravity()
                timesincejump += 1
            else:
                timesincejump = 0

        avoidlist = ["quit", "coin", "end", "stalactite"]
        if level.triggerpass != "":
            firsttime = False
            if level.triggerpass not in avoidlist:
                levelJumps.append(level.player_sprite.getJumps())
                #print(levelJumps)
                nextlevel = level.triggerpass
                del level
                loadlevel(str(nextlevel))
            else:
                # Go through every other trigger command
                if level.triggerpass == "quit":
                    pygame.quit()
                    sys.exit()
                elif level.triggerpass == "coin":
                    coincount += 1
                    level.triggerpass = ""
                if level.triggerpass == "end":
                    if endTrigger:
                        # del level
                        # loadlevel("end")nd
                        #levelJumps.append(level.player_sprite.getJumps())
                        for item in levelJumps:
                            if cnt == 1:
                                totalJumps += item
                                jumps.append('lvl ' + str(cnt) + ' jumps: ' + str(levelJumps[cnt]))
                            elif cnt > 1:
                                totalJumps += item
                                jumps.append(' | lvl ' + str(cnt) + ' jumps: ' + str(levelJumps[cnt]))
                            cnt += 1
                        endTrigger = False
                    # if playmusic:
                    #     playmusic = False
                    #     music = mixer.Sound(str(maindirectory) + "/audio/music/end.mp3")
                    #     music.set_volume(0.5)
                    #     mixer.Channel(0).play(music, fade_ms=1000, loops=999)

                    if fullJumpsTrigger:
                        fullJumps = ''.join(jumps)
                        fullJumpsTrigger = False
                    # Draw the scrolling end credits text
                    if finaltime == "":
                        finaltime = str(output_string)
                    screen.fill("black")
                    font = pygame.font.Font(os.path.join(str(maindirectory), 'slkscr.ttf'), 24)
                    didIt = font.render('You did it! WOOOOOOOO', True, (255, 255, 255))
                    coins = font.render('Coins: ', True, (255, 255, 255))
                    coinCol = font.render(str(coincount), True, (255, 255, 0))
                    #coin = font.render(coins + coinCol, True)
                    time = font.render('Time: ' + finaltime, True, (255, 255, 255))
                    jumpRender = font.render(fullJumps, True, (255, 255, 255))
                    totalJump = font.render('Total Jumps: ' + str(totalJumps), True, (255, 255, 255))
                    credits = font.render('CREDITS', True, (255,255,255))
                    credProg = font.render('Programmers:', True, (0,230,0))
                    mattCred = font.render('Matt Curtis', True, (255,255,255))
                    aaronCred = font.render('Aaron Bryan', True, (255,255,255))
                    andrewCred = font.render('Andrew Pham', True, (255,255,255))
                    credScrum = font.render('Scrum Master:', True, (0,230,0))
                    credScrumMas = font.render('Magnus Linden', True, (255,255,255))
                    credProd = font.render('Product Owner:', True, (0,230,0))
                    credProdOwn = font.render('Benjamin Hackett', True, (255,255,255))
                    mamba = pygame.transform.scale(pygame.image.load(str(maindirectory) + "/images/logo/Mamba.png"), (1024*0.4, 768*0.4))
                    endlogo = pygame.transform.scale(pygame.image.load(str(maindirectory) + "/images/logo/Logo.gif"), (1024*0.35, 768*0.4))

                    screenBlit(endlogo, 25, 0)
                    screenBlit(didIt, 100, 0)
                    screenBlit(coins, 150, -30)
                    screenBlit(coinCol, 150, 30)
                    screenBlit(time, 125, 0)
                    screenBlit(jumpRender, 175, 0)
                    screenBlit(totalJump, 205, 0)
                    screenBlit(credits, 250, 0)
                    screenBlit(credProd, 290, 0)
                    screenBlit(credProdOwn, 315, 0)
                    screenBlit(credScrum, 355, 0)
                    screenBlit(credScrumMas, 380, 0)
                    screenBlit(credProg, 420, 0)
                    screenBlit(mattCred, 445, 0)
                    screenBlit(andrewCred, 470, 0)
                    screenBlit(aaronCred, 495, 0)
                    screenBlit(mamba, 650, 0)

                    creditscroll += 0.4

        if level.getshakepass():
            offset = (random.randint(0, 4), random.randint(0, 4))
        else:
            offset = (0, 0)
        orig_screen.blit(screen, offset)
        if level.player_sprite.getcoords()[0] < screen_width-200:  # and level.player_sprite.getcoords()[1] > 256:
            try:
                pygame.draw.rect(orig_screen, (255, 255, 255, 200), pygame.Rect(screen_width-128-24-4, 64+24-4, 128+8, 128+8))
                maxscreen = screen.subsurface((level.player_sprite.getcoords()[0]-48, level.player_sprite.getcoords()[1]-48, 128, 128))
                maxscreen.set_alpha(220)
                # test
                # maxscreen = pygame.transform.scale(maxscreen, (screen_width, screen_height))
                orig_screen.blit(maxscreen, (screen_width-128-24, 64+24))
            except (ValueError):
                pass

        if firsttime:
            # Draw the floating logo in the center of the screen, hovering with sin wave
            logo_y = int(screen_height / 2 + math.sin(frame_count / 10) * 10)
            orig_screen.blit(helplogo, (screen_width / 2 - helplogo.get_width() / 2, logo_y - 150))

        font = pygame.font.Font(os.path.join(str(maindirectory), 'slkscr.ttf'), 24)
        text = font.render('STOPWATCH: ' + str(output_string), True, (255, 255, 255))
        orig_screen.blit(text, (24, 24))

        text = font.render('VOLUME: ' + str(round(max(globalvolume, 0), 2)), True, (255, 255, 255))
        orig_screen.blit(text, (24, 48))

        # Draw the coin count
        text = font.render('COINS: ' + str(coincount), True, (255, 255, 255))
        orig_screen.blit(text, (24, 72))

        # Draw sprint meter
        text = font.render('SPRINTSPD: ', True, (255, 255, 255))
        orig_screen.blit(text, (24, 96))
        sprintrectouter = pygame.Rect(180+2, 96+2, 150-3.5, 25-3.5)
        sprintrectinner = pygame.Rect(180+5, 96+5, 150-10, 25-10)
        sprintrectinner2 = pygame.Rect(180 + 10, 96 + 10, (150 - 20)*Player.getacceleration(level.player_sprite), 25 - 20)
        sprintrectinner3 = pygame.Rect(180 + 10, 96 + 10, (150 - 20),25 - 20)
        #pygame.draw.rect(orig_screen, (255,255,255), sprintrectouter)  # white outer border
        pygame.draw.rect(orig_screen, (0, 0, 0), sprintrectinner)  # black inner border
        pygame.draw.rect(orig_screen, (100, 100, 100), sprintrectinner3)  # grey inner bar
        pygame.draw.rect(orig_screen, (255, 255, 255), sprintrectinner2)  # white inner bar (meter)

        font = pygame.font.Font(os.path.join(str(maindirectory), 'slkscr.ttf'), 14)
        text = font.render('Movement: WASD + SPACE or MOUSE L/R, Pause: P     CONTROLS', True, (255, 255, 255))
        orig_screen.blit(text, (screen_width - 540, 24))

        font = pygame.font.Font(os.path.join(str(maindirectory), 'slkscr.ttf'), 14)
        text = font.render('    HOLD SHIFT while moving to sprint', True, (255, 255, 255))
        orig_screen.blit(text, (screen_width - 475, 36))

        # Draw a giant quit button in the bottom right corner of the screen
        # pygame.draw.rect(orig_screen, (255, 255, 255), pygame.Rect(screen_width - 128 - 24 - 4, screen_height - 128 - 24 - 4, 128 + 8, 128 + 8))
        # pygame.draw.rect(orig_screen, (0, 0, 0), pygame.Rect(screen_width - 128 - 24, screen_height - 128 - 24, 128, 128))
        # font = pygame.font.Font(os.path.join(str(maindirectory), 'slkscr.ttf'), 24)
        # text = font.render('QUIT', True, (255, 255, 255))
        # orig_screen.blit(text, (screen_width - 128 - 24 + (128 - text.get_width()) / 2, screen_height - 128 - 24 + (128 - text.get_height()) / 2))
        # # If the user clicks the button, quit the game
        # if pygame.mouse.get_pressed()[0] and pygame.mouse.get_pos()[0] > screen_width - 128 - 24 and pygame.mouse.get_pos()[0] < screen_width - 24 and pygame.mouse.get_pos()[1] > screen_height - 128 - 24 and pygame.mouse.get_pos()[1] < screen_height - 24:
        #     pygame.quit()
        #     sys.exit()

        text = font.render('Volume: I/O', True, (255, 255, 255))
        orig_screen.blit(text, (screen_width - 116, 48))

        pygame.display.flip()

    pygame.display.update()
    clock.tick(60)

    # Set audio volume dynamically
    keys = pygame.key.get_pressed()
    if keys[pygame.K_i]:
        if globalvolume > 0:
            globalvolume -= 0.05
    if keys[pygame.K_o]:
        if globalvolume < 1:
            globalvolume += 0.05
    level.setglobalvolume(globalvolume)
    # global volume can be changed rather than music or sound fx
    # mixer.Channel(0).set_volume(min(1, globalvolume))

Player.setmainscreen(orig_screen)  # for pausing in Player

# Exit script
pygame.quit()
sys.exit()
# os.execv(sys.executable, ['python'] + sys.argv)
