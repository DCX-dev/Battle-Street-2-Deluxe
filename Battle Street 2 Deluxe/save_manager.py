import json
import os

SAVE_FILE = "battle_street_save.json"

def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading save: {e}")
        return None

def save_game(player):
    data = {
        "username": player.username,
        "coins": player.coins,
        "inventory": player.inventory,
        "current_weapon": player.current_weapon_name
    }
    
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)
        print("Game saved!")
    except Exception as e:
        print(f"Error saving game: {e}")

