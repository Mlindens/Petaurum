# Import necessary libraries
import random

import pygame
from Tiles import Tile
from Player import Player
import os
import PIL
from PIL import Image, ImageDraw
# Create Levels class
class Levels:
    def __init__(self, level_layout, surface, level_image, tile_size=64, screen_dimensions=(1024, 768), triggerpass="", shakepass="", globalvolume=1, directory=""):
        self.display_surface = surface
        self.tile_size = tile_size
        self.camera_y_shift = 0
        self.screen_width, self.screen_height = screen_dimensions
        self.level_layout = level_layout
        self.level_image = level_image
        self.triggerpass = triggerpass
        self.shakepass = shakepass
        self.maxheight = 0
        self.globalvolume = globalvolume
        self.collision = False
        self.mainfolder = directory
        self.playeracceleration = 0
        self.playerdeath = False
        self.initcamera = True
        self.tempcounter = 0
        self.generate = True

        # Toggle between collision systems
        self.collisionsystem = "old"

        self.totalmovement = 0

        # Level assets
        self.assets = []
        self.tileimages = []


        try:
            tilenames = []
            tilenames = [x for x in os.listdir(os.path.join(str(directory), "images", "tiles")) if ".png" or ".PNG" or ".Png" in x]
            newtilenames = []
            for item in tilenames:
                newtilenames.append(int(item.upper().replace(".PNG", "")))
            newtilenames.sort()
            for item in newtilenames:
                full_path = os.path.join(str(directory), "images", "tiles", str(item) + ".png")
                top_image = pygame.image.load(full_path).convert_alpha()
                self.tileimages.append(top_image)
        except FileNotFoundError:
            pass

        # # Open the image master.png from images > palette using PIL
        # old_image = Image.open(os.path.join(str(directory), "images", "palette", "master.png"))
        # old_image = old_image.convert("RGBA")
        #
        # # Generate color palette
        # new_image_size = ((self.tile_size*len(self.tileimages)) + 8, self.tile_size + 8)
        # new_image = Image.new("RGBA", new_image_size, (0, 0, 0, 0))
        # new_image1 = ImageDraw.Draw(new_image)
        # counter = 0
        # for item in self.tileimages:
        #     new_image1.rectangle(((counter - 4, 0), (counter + self.tile_size + 4, self.tile_size + 8)), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255))
        #     py_surface = pygame.image.tostring(item, "RGBA")
        #     new_image2 = Image.frombytes("RGBA", item.get_size(), py_surface)
        #     new_image.paste(new_image2, (counter, 4), mask=new_image2)
        #     counter += self.tile_size + 8
        #
        # # Save the new image
        # new_image.save(os.path.join(str(directory), "images", "palette", "master.png"))

        # full_path = os.path.join(str(path), str(sprite))
        # self.image = pygame.image.load(full_path).convert_alpha()

        self.drawLevelGeometry(level_layout[0], tile_size)

    # Solution from https://stackoverflow.com/questions/62058750/how-to-check-collisions-between-a-mask-and-rect-in-pygame
    def collide_mask_rect(self, left, right):
        xoffset = right.rect[0] - left.rect[0]
        yoffset = right.rect[1] - left.rect[1]
        try:
            leftmask = left.mask
        except AttributeError:
            leftmask = pygame.mask.Mask(left.size, True)
        try:
            rightmask = right.mask
        except AttributeError:
            rightmask = pygame.mask.Mask(right.size, True)
        return leftmask.overlap(rightmask, (xoffset, yoffset))

    # Create the level geometry (tiles, player, etc)
    def drawLevelGeometry(self, layout, tile_size=64):
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()

        # Go through every pixel in the level PNG
        # Convert to RGB (failsafe)
        self.level_image = self.level_image.convert("RGB")

        for row in range(self.level_image.height):
            for col in range(self.level_image.width):
                x = col
                y = row
                self.maxheight = max(abs(self.maxheight), abs(y * tile_size))

                # Collision tiles
                tilecolorlist = [16, 32, 48, 64, 80, 96, 112, 128, 144, 148, 152, 156, 160, 164, 168, 172, 176, 180, 184, 188, 192, 196, 200, 204, 208, 212, 216, 220, 224, 228, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245]
                tiledeadlylist = [False, False, False, False, False, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
                tilespriteindex = [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44]
                tiletriggerindex = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "TestLevel", "TestLevel", "TestLevel", "TestLevel", "quit", "quit", "quit", "quit", "", "", "", "", "", "", "", "", "", "", "", "", ""]

                index = 0
                for item in tilespriteindex:
                    # Regular tiles
                    if self.level_image.getpixel((x, y)) == (0, tilecolorlist[index], 0):
                        tile = Tile((x * tile_size, y * tile_size), tile_size, sprite=self.tileimages[tilespriteindex[index]], deadly=tiledeadlylist[index], trigger=str(tiletriggerindex[index]))
                        self.tiles.add(tile)
                    index += 1

                # NO-Collision tiles
                newtilecolorlist = [16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 164, 168, 172, 176, 180, 184, 188, 192, 196, 200, 204, 208, 212, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229]
                newtiledeadlylist = [False, False, False, False, False, True, True, False, False, False, False,
                                  False, False, False, False, False, False, False, False, False, False, False,
                                  False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
                newtilespriteindex = [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44]

                if self.generate:
                    self.generate = False
                    print("[INFO] Generating color palette for level")
                    # Open the image master.png from images > palette using PIL
                    old_image = Image.open(os.path.join(str(self.mainfolder), "images", "palette", "palette.png"))
                    old_image = old_image.convert("RGBA")

                    # Generate color palette
                    new_image_size = ((self.tile_size * len(tilespriteindex)) + (self.tile_size * len(newtilespriteindex)) + 8, self.tile_size + 8)
                    new_image = Image.new("RGBA", new_image_size, (0, 0, 0, 0))
                    new_image1 = ImageDraw.Draw(new_image)
                    counter = 0

                    # Collision tiles
                    othercounter = 0
                    for item in tilespriteindex:
                        new_image1.rectangle(((counter - 4, 0), (counter + self.tile_size + 4, self.tile_size + 8)), fill=(0, tilecolorlist[othercounter], 0, 255))
                        py_surface = pygame.image.tostring(self.tileimages[item], "RGBA")
                        new_image2 = Image.frombytes("RGBA", self.tileimages[item].get_size(), py_surface)
                        new_image.paste(new_image2, (counter, 4), mask=new_image2)
                        counter += self.tile_size + 8
                        othercounter += 1

                    # NO-collision tiles
                    othercounter = 0
                    for item in newtilespriteindex:
                        new_image1.rectangle(((counter - 4, 0), (counter + self.tile_size + 4, self.tile_size + 8)),
                                             fill=(newtilecolorlist[othercounter], 0, 0, 255))
                        py_surface = pygame.image.tostring(self.tileimages[item], "RGBA")
                        new_image2 = Image.frombytes("RGBA", self.tileimages[item].get_size(), py_surface)
                        new_image.paste(new_image2, (counter, 4), mask=new_image2)
                        counter += self.tile_size + 8
                        othercounter += 1

                    # Save the new image
                    new_image.save(os.path.join(str(self.mainfolder), "images", "palette", "palette.png"))


                index = 0
                for newitem in newtilespriteindex:
                    if self.level_image.getpixel((x, y)) == (newtilecolorlist[index], 0, 0):
                        tile = Tile((x * tile_size, y * tile_size), tile_size,
                                    sprite=self.tileimages[newtilespriteindex[index]], collision=False, deadly=newtiledeadlylist[index])
                        self.tiles.add(tile)
                    index += 1

                # Test tile
                if self.level_image.getpixel((x, y)) == (0, 0, 0):
                    tile = Tile((x * tile_size, y * tile_size), tile_size, color="RED")
                    self.tiles.add(tile)

                # Coin tile
                if self.level_image.getpixel((x, y)) == (255, 240, 0):
                    tile = Tile((x * tile_size, y * tile_size), tile_size, sprite=self.tileimages[32], trigger="coin")
                    self.tiles.add(tile)

                # Stalactite tile
                if self.level_image.getpixel((x, y)) == (0, 0, 240):
                    tile = Tile((x * tile_size, y * tile_size), tile_size, sprite=self.tileimages[6], trigger="stalactite", deadly=True)
                    self.tiles.add(tile)

                # Level trigger tile
                if self.level_image.getpixel((x, y)) == (255, 255, 0):
                    tile = Tile((x * tile_size, y * tile_size), tile_size, sprite=self.tileimages[4],
                                trigger=str(self.level_layout[3]))
                    self.tiles.add(tile)

                # Player tile
                if self.level_image.getpixel((x, y)) == (0, 0, 255):
                    self.player_sprite = Player((x * tile_size, y * tile_size), maindirectory=self.mainfolder)
                    self.player.add(self.player_sprite)
        self.origcamerashift = abs(self.maxheight * 0.01)

    def getmaxheight(self):
        return self.maxheight

    def setglobalvolume(self, volume):
        self.globalvolume = volume
        player = self.player.sprite
        player.setglobalvolume(volume)

    # Keep player in view of Window
    # (uses pseudo-camera where world moves around player)
    def scrollY(self):
        player = self.player.sprite
        player_y = player.rect.centery
        direction_y = player.direction.y

        # If player is near top of window, move "camera" up
        if player_y < (self.screen_height/4) and direction_y < 0:
            self.camera_y_shift = self.origcamerashift
            self.totalmovement += self.camera_y_shift
            player.vert_speed = 0
        # If player is near bottom of window, move "camera" down
        elif player_y > self.screen_height - (self.screen_height/4) and direction_y > 0:
            self.camera_y_shift = 0 - self.origcamerashift
            self.totalmovement += self.camera_y_shift
            player.vert_speed = 0
        # Stop camera movement
        else:
            self.camera_y_shift = 0
            player.vert_speed = 2

    def getcamerayshift(self):
        return self.camera_y_shift

    def horizCollision(self):
        player = self.player.sprite
        # player.mask = self.player.mask
        player.rect.x += player.direction.x * player.horiz_speed
        # player.rect.y += player.direction.y * player.vert_speed

        # player.direction.x = 0

        for sprite in self.tiles.sprites():
            if self.collisionsystem == "new":
                detectionbool = pygame.sprite.collide_mask(player, sprite)
            else:
                detectionbool = sprite.rect.colliderect(player.rect)
            if detectionbool:
                if sprite.getcollision():
                    self.fullcollisioncheck = True
                    # player.setdirectionx(0)
                    if player.direction.x < 0:
                        if self.collisionsystem == "new":
                            player.rect.left = player.rect.left - (pygame.sprite.collide_mask(player, sprite)[0] - player.rect.width + 20)
                            print("AAAAA")
                            print(player.rect.left)
                        else:
                            player.rect.left = sprite.rect.right
                        player.direction.x = 0
                        # player.rect.left += 4
                    elif player.direction.x > 0:
                        player.direction.x = 0
                        if self.collisionsystem == "new":
                            player.rect.right = player.rect.right - (player.rect.width - pygame.sprite.collide_mask(player, sprite)[0])
                            print("BBBBB")
                            print(player.rect.left)
                        else:
                            player.rect.right = sprite.rect.left
                        # player.rect.right -= 4
                if str(sprite.returnTrigger()) != "":
                    self.triggerpass = str(sprite.returnTrigger())
                if str(sprite.returnTrigger()) == "end":
                    player.playcoinsound()
                    sprite.setTrigger("")
                if str(sprite.returnTrigger()) == "coin":
                    sprite.setTrigger("")
                    sprite.hide(True)
                    sprite.setCollision(False)
                    player.playcoinsound()
                if sprite.get_deadly():
                    self.playerdeath = True
                    player.totalmovement = self.totalmovement
                    player.playdeathsound()

        # Wrap-around
        if player.direction.x > 0 and player.rect.x > 1024:
            player.rect.x = 0
            player.rect.y -= 1

        if player.direction.x < 0 and player.rect.x < 0:
            player.rect.x = 1024
            player.rect.y -= 1

    def getshakepass(self):
        player = self.player.sprite
        return player.getbusychannel(2)

    def getmenu(self):
        if self.playerdeath:
            return 1
        else:
            return 0

    def reset(self):
        # Reset camera speed variables
        self.initcamera = True
        self.tempcounter = 0
        self.origcamerashift = abs(self.maxheight * 0.01)

        for sprite in self.tiles.sprites():
            sprite.origlocation(self.camera_y_shift)

        self.playerdeath = 0
        player = self.player.sprite
        player.reset()

    def vertCollision(self):
        player = self.player.sprite
        if player.vert_speed != 0:
            player.applyGravity()
        # else:
        #     player.setdirectionx(0)

        self.prevcollision = self.collision
        self.playeracceleration = player.direction.y
        self.collision = False
        for sprite in self.tiles.sprites():
            # Check if x position of player is within 10 pixels of the sprite
            if abs(player.rect.centerx - sprite.rect.centerx) < 48:
                # Check if sprite trigger is stalactite
                if str(sprite.returnTrigger()) == "stalactite":
                    # Move sprite down 4px
                    sprite.rect.y += 4

            if self.collisionsystem == "new":
                detectionbool = pygame.sprite.collide_mask(player, sprite)
            else:
                detectionbool = sprite.rect.colliderect(player.rect)
            if detectionbool:
                if sprite.getcollision():
                    self.collision = True
                    player.setdirectionx(0)
                    player.uppercollision = False
                    self.fullcollisioncheck = True
                    if player.direction.y > 0:
                        if self.collisionsystem == "new":
                            player.rect.bottom = player.rect.bottom - (player.rect.height - pygame.sprite.collide_mask(player, sprite)[1])
                        else:
                            player.rect.bottom = sprite.rect.top
                        # print((player.rect.height - pygame.sprite.collide_mask(player, sprite)[1]))
                        # dx = mask.overlap_area(other, (x + 1, y)) - mask.overlap_area(other, (x - 1, y))
                        # dy = mask.overlap_area(other, (x, y + 1)) - mask.overlap_area(other, (x, y - 1))
                        # player.rect.bottom -= 1
                        player.direction.y = 0
                    elif player.direction.y < 0:
                        player.uppercollision = True
                        if self.collisionsystem == "new":
                            player.rect.top = player.rect.top - (pygame.sprite.collide_mask(player, sprite)[1] - player.rect.height)
                        else:
                            player.rect.top = sprite.rect.bottom
                        # print((pygame.sprite.collide_mask(player, sprite)[1] - player.rect.height))
                        # player.rect.bottom += 1
                        player.direction.y = 0
                if str(sprite.returnTrigger()) != "":
                    self.triggerpass = str(sprite.returnTrigger())
                if str(sprite.returnTrigger()) == "end":
                    player.playcoinsound()
                    sprite.setTrigger("")
                if str(sprite.returnTrigger()) == "coin":
                    sprite.setTrigger("")
                    sprite.hide(True)
                    sprite.setCollision(False)
                    player.playcoinsound()
                if sprite.get_deadly():
                    self.playerdeath = True
                    player.totalmovement = self.totalmovement
                    player.playdeathsound()

        if self.collision and self.collision != self.prevcollision and abs(self.playeracceleration) - abs(player.direction.y) >= 5:  # and player.direction.y <= 0 and player.direction.y >= 1
            player.playfallsound()
            self.collision = False

    # Get background color based on player's Y level
    def getbackgroundcolor(self):
        return 0, 130 * max(min((1-(abs(self.totalmovement) / abs(self.maxheight))), 1), 0), 180 * max(min((1-(abs(self.totalmovement) / abs(self.maxheight))), 1), 0)

    # Update tiles, camera, player
    def run(self):
        self.tiles.update(self.camera_y_shift)
        self.tiles.draw(self.display_surface)
        self.player.update(self.camera_y_shift)

        if self.initcamera and abs(self.camera_y_shift) < 1 and self.tempcounter > 10:
            self.origcamerashift = 12
            self.initcamera = False

        if self.initcamera:
            self.tempcounter += 1

        self.scrollY()
        self.fullcollisioncheck = False
        self.horizCollision()
        self.vertCollision()

        # player = self.player.sprite
        # player.setcollisionstatus(self.fullcollisioncheck)

        self.player.draw(self.display_surface)

