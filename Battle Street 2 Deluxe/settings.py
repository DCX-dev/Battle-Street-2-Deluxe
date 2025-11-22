import pygame
import os

# Initialize Pygame for color constants etc
pygame.font.init()

# Constants
WIDTH = 1000
HEIGHT = 700
FPS = 60
TITLE = "Battle Street 2 Deluxe"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 100, 255)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 50)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
LIGHT_GRAY = (200, 200, 200)
ORANGE = (255, 165, 0)
PURPLE = (200, 50, 200)
CYAN = (0, 255, 255)
DARK_BLUE = (20, 20, 60)
DARK_GREEN = (20, 60, 20)
LIGHT_BLUE = (173, 216, 230)

# Fonts
FONT_NAME = "arial"

# Gameplay
STARTING_COINS = 0
WIN_REWARD = 50
LOSE_PENALTY = 20

# --- ORIGINAL GAME DATA ---

# Weapon data
WEAPONS_DATA = {
    "Fist": {"damage": 8, "cost": 0, "speed": 12, "color": (255, 220, 180), "explosion": False, "melee": True, "range": 40},
    "Water Gun": {"damage": 10, "cost": 30, "speed": 15, "color": (100, 150, 255), "explosion": False, "melee": False},
    "Splat Bomb": {"damage": 12, "cost": 40, "speed": 7, "color": (255, 100, 0), "explosion": True, "melee": False},
    "Cork Gun": {"damage": 13, "cost": 50, "speed": 16, "color": (200, 150, 100), "explosion": False, "melee": False},
    "Confetti Bomb": {"damage": 14, "cost": 60, "speed": 7, "color": (255, 200, 255), "explosion": True, "melee": False},
    "Squirt Gun": {"damage": 15, "cost": 70, "speed": 17, "color": (0, 200, 255), "explosion": False, "melee": False},
    "Pie Bomb": {"damage": 16, "cost": 80, "speed": 8, "color": (255, 230, 180), "explosion": True, "melee": False},
    "Nerf Blaster": {"damage": 17, "cost": 90, "speed": 18, "color": (255, 140, 0), "explosion": False, "melee": False},
    "Whoopee Cushion": {"damage": 18, "cost": 100, "speed": 9, "color": (200, 100, 200), "explosion": True, "melee": False},
    "Bubble Gun": {"damage": 19, "cost": 110, "speed": 14, "color": (200, 255, 255), "explosion": False, "melee": False},
    "Cartoon Grenade": {"damage": 20, "cost": 120, "speed": 8, "color": (50, 255, 50), "explosion": True, "melee": False},
    "Banana Gun": {"damage": 21, "cost": 130, "speed": 15, "color": (255, 255, 100), "explosion": False, "melee": False},
    "Glitter Grenade": {"damage": 22, "cost": 140, "speed": 8, "color": (255, 180, 255), "explosion": True, "melee": False},
    "Paint Gun": {"damage": 23, "cost": 150, "speed": 16, "color": (255, 100, 200), "explosion": False, "melee": False},
    "Smoke Bomb": {"damage": 24, "cost": 160, "speed": 7, "color": (150, 150, 150), "explosion": True, "melee": False},
    "Potato Gun": {"damage": 25, "cost": 170, "speed": 13, "color": (180, 140, 100), "explosion": False, "melee": False},
    "Bubble Mine": {"damage": 26, "cost": 180, "speed": 6, "color": (100, 255, 255), "explosion": True, "melee": False},
    "Ray Gun": {"damage": 27, "cost": 190, "speed": 20, "color": (0, 255, 100), "explosion": False, "melee": False},
    "Rubber Rocket": {"damage": 28, "cost": 200, "speed": 10, "color": (255, 100, 150), "explosion": True, "melee": False},
    "Laser Pistol": {"damage": 29, "cost": 210, "speed": 22, "color": (255, 0, 0), "explosion": False, "melee": False},
    "TNT Stick": {"damage": 30, "cost": 220, "speed": 8, "color": (255, 0, 0), "explosion": True, "melee": False},
    "Zap Gun": {"damage": 31, "cost": 230, "speed": 21, "color": (255, 255, 0), "explosion": False, "melee": False},
    "Foam Missile": {"damage": 32, "cost": 240, "speed": 11, "color": (255, 128, 0), "explosion": True, "melee": False},
    "Plasma Rifle": {"damage": 33, "cost": 250, "speed": 19, "color": (100, 100, 255), "explosion": False, "melee": False},
    "Sticky Bomb": {"damage": 34, "cost": 260, "speed": 7, "color": (100, 255, 100), "explosion": True, "melee": False},
    "Blaster Cannon": {"damage": 35, "cost": 270, "speed": 17, "color": (255, 50, 150), "explosion": False, "melee": False},
    "Super Grenade": {"damage": 36, "cost": 280, "speed": 9, "color": (255, 50, 255), "explosion": True, "melee": False},
    "Ion Blaster": {"damage": 38, "cost": 300, "speed": 23, "color": (150, 200, 255), "explosion": False, "melee": False},
    "Mega Rocket": {"damage": 40, "cost": 320, "speed": 12, "color": (255, 50, 50), "explosion": True, "melee": False},
    "Photon Cannon": {"damage": 42, "cost": 350, "speed": 24, "color": (255, 255, 255), "explosion": False, "melee": False},
    "Nuke Launcher": {"damage": 45, "cost": 400, "speed": 10, "color": (255, 255, 0), "explosion": True, "melee": False},
}

WEAPON_FILES = {
    "Fist": "fist.png",
    "Water Gun": "water_gun.png",
    "Splat Bomb": "splat_bomb.png",
    "Cork Gun": "cork_gun.png",
    "Confetti Bomb": "confetti_bomb.png",
    "Squirt Gun": "squirt_gun.png",
    "Pie Bomb": "pie_bomb.png",
    "Nerf Blaster": "nerf_blaster.png",
    "Whoopee Cushion": "whoopee_cushion.png",
    "Bubble Gun": "bubble_gun.png",
    "Cartoon Grenade": "cartoon_grenade.png",
    "Banana Gun": "banana_gun.png",
    "Glitter Grenade": "glitter_grenade.png",
    "Paint Gun": "paint_gun.png",
    "Smoke Bomb": "smoke_bomb.png",
    "Potato Gun": "potato_gun.png",
    "Bubble Mine": "bubble_mine.png",
    "Ray Gun": "ray_gun.png",
    "Rubber Rocket": "rubber_rocket.png",
    "Laser Pistol": "laser_pistol.png",
    "TNT Stick": "tnt_stick.png",
    "Zap Gun": "zap_gun.png",
    "Foam Missile": "foam_missile.png",
    "Plasma Rifle": "plasma_rifle.png",
    "Sticky Bomb": "sticky_bomb.png",
    "Blaster Cannon": "blaster_cannon.png",
    "Super Grenade": "super_grenade.png",
    "Ion Blaster": "ion_blaster.png",
    "Mega Rocket": "mega_rocket.png",
    "Photon Cannon": "photon_cannon.png",
    "Nuke Launcher": "nuke_launcher.png"
}

ROLES = {
    "Engineer": {
        "name": "Engineer",
        "description": "Build structures and hide in vents",
        "color": (255, 165, 0),  # Orange
        "abilities": ["build", "vent"],
        "resources": 100,  # Starting build resources
        "vent_duration": 600,  # 10 seconds at 60 FPS
        "vent_cooldown": 900,  # 15 seconds cooldown
    },
    "Fighter": {
        "name": "Fighter",
        "description": "Standard combat role",
        "color": (150, 150, 150),  # Gray
        "abilities": [],
    },
    "Trapper": {
        "name": "Trapper",
        "description": "Trap enemies in cages for 7 seconds",
        "color": (128, 0, 128),  # Purple
        "abilities": ["trap", "cage"],
        "trap_duration": 420,  # 7 seconds at 60 FPS
        "trap_cooldown": 600,  # 10 seconds cooldown
    }
}

VEHICLES = {
    "None": {
        "name": "No Vehicle (On Foot)",
        "cost": 0,
        "health_multiplier": 1.0,
        "speed_multiplier": 1.0,
        "can_fly": False,
        "size": (40, 60),
        "color": None,  # Uses player color
        "description": "Standard on-foot combat"
    },
    "Rocket": {
        "name": "Rocket Pack",
        "cost": 500,
        "health_multiplier": 1.5,
        "speed_multiplier": 1.3,
        "can_fly": True,
        "size": (50, 70),
        "color": (255, 100, 50),
        "description": "Fast flying vehicle with missile launcher"
    },
    "Tank": {
        "name": "Battle Tank",
        "cost": 1000,
        "health_multiplier": 3.0,
        "speed_multiplier": 0.7,
        "can_fly": False,
        "size": (80, 60),
        "color": (100, 120, 100),
        "description": "Heavy armor, powerful weapons, slow movement"
    },
    "Ship": {
        "name": "Battleship",
        "cost": 1000000,
        "health_multiplier": 40.0,
        "speed_multiplier": 0.5,
        "can_fly": True,
        "size": (150, 120),
        "color": (150, 150, 180),
        "description": "Massive flying fortress with incredible firepower"
    }
}

COSMETICS = {
    # Hats
    "Basic Cap": {"type": "hat", "cost": 50, "color": (255, 0, 0), "description": "A simple red cap"},
    "Cool Hat": {"type": "hat", "cost": 100, "color": (0, 100, 255), "description": "A stylish blue hat"},
    "Crown": {"type": "hat", "cost": 500, "color": (255, 215, 0), "description": "Royal gold crown"},
    
    # Skins
    "Blue Skin": {"type": "skin", "cost": 75, "color": (50, 150, 255), "description": "Cool blue appearance"},
    "Green Skin": {"type": "skin", "cost": 75, "color": (50, 255, 100), "description": "Fresh green look"},
    "Purple Skin": {"type": "skin", "cost": 100, "color": (200, 50, 255), "description": "Mysterious purple"},
    "Golden Skin": {"type": "skin", "cost": 1000, "color": (255, 215, 0), "description": "Legendary gold skin"},
    
    # Visors
    "Cool Shades": {"type": "visor", "cost": 150, "color": (50, 50, 50), "description": "Stylish sunglasses"},
    "Cyber Visor": {"type": "visor", "cost": 300, "color": (0, 255, 255), "description": "Futuristic visor"},
}

MAPS = {
    "Street": {
        "name": "City Street",
        "bg_color": (100, 100, 120),
        "ground_color": (60, 60, 60),
        "decoration": "buildings",
        "sky_color": (135, 206, 250)
    },
    "Desert": {
        "name": "Sandy Desert",
        "bg_color": (255, 220, 150),
        "ground_color": (194, 178, 128),
        "decoration": "cacti",
        "sky_color": (255, 200, 100)
    },
    "Grassland": {
        "name": "Green Fields",
        "bg_color": (100, 200, 100),
        "ground_color": (80, 180, 80),
        "decoration": "trees",
        "sky_color": (135, 206, 250)
    },
    "Arena": {
        "name": "Battle Arena",
        "bg_color": (120, 80, 80),
        "ground_color": (90, 60, 60),
        "decoration": "pillars",
        "sky_color": (60, 40, 40)
    }
}
