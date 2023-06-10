# Imports
import os
import pygame

# Function to return list of images, loaded into memory
def knight_folder(path):
    try:
        list_items = [x for x in os.listdir(path) if ".png" or ".PNG" or ".Png" in x]
        list_surface = []
        for item in list_items:
            full_path = os.path.join(str(path), str(item))
            top_image = pygame.image.load(full_path).convert_alpha()
            list_surface.append(top_image)
        return list_surface
    except FileNotFoundError:
        return []

# Function to return list of images, loaded into memory
def game_logo(path):
    try:
        list_items = [x for x in os.listdir(path) if ".png" or ".PNG" or ".Png" in x]
        list_surface = []
        for item in list_items:
            full_path = os.path.join(str(path), str(item))
            top_image = pygame.transform.scale(pygame.image.load(full_path), (1024*0.7, 768*0.7)).convert_alpha()
            list_surface.append(top_image)
        return list_surface
    except FileNotFoundError:
        return []

def getImage(path):
    try:
        full_path = os.path.join(str(path))
        top_image = pygame.image.load(full_path).convert_alpha()
        return top_image
    except FileNotFoundError:
        return None
