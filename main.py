"""
Escape the Dungeon - A Text-Based Adventure Game
Author: [Your Name]
Student ID: [Your Student ID]

A medieval dungeon escape game where players navigate through connected rooms,
collect items, solve puzzles, and find their way to freedom.
"""

import json
import os
from typing import Dict, List, Any, Optional

class Item:
    """Represents an item that can be found or used in the game."""
    
    def __init__(self, name: str, description: str, usable: bool = False, required_for: List[str] = None):
        self.name = name
        self.description = description
        self.usable = usable
        self.required_for = required_for or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'usable': self.usable,
            'required_for': self.required_for
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Create Item from dictionary."""
        return cls(data['name'], data['description'], data['usable'], data['required_for'])

class Room:
    """Represents a room in the dungeon with connections, items, and descriptions."""
    
    def __init__(self, name: str, description: str, items: List[Item] = None, 
                 connections: Dict[str, str] = None, locked: bool = False, 
                 unlock_item: str = None):
        self.name = name
        self.description = description
        self.items = items or []
        self.connections = connections or {}
        self.locked = locked
        self.unlock_item = unlock_item
        self.visited = False
    
    def add_connection(self, direction: str, room_name: str) -> None:
        """Add a connection to another room."""
        self.connections[direction] = room_name
    
    def remove_item(self, item_name: str) -> Optional[Item]:
        """Remove and return an item from the room."""
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert room to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'items': [item.to_dict() for item in self.items],
            'connections': self.connections,
            'locked': self.locked,
            'unlock_item': self.unlock_item,
            'visited': self.visited
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Room':
        """Create Room from dictionary."""
        room = cls(data['name'], data['description'], 
                   [Item.from_dict(item_data) for item_data in data['items']],
                   data['connections'], data['locked'], data['unlock_item'])
        room.visited = data['visited']
        return room

class Player:
    """Represents the player with inventory and current location."""
    
    def __init__(self, current_room: str = "Prison Cell"):
        self.inventory = []
        self.current_room = current_room
        self.health = 100
    
    def add_item(self, item: Item) -> None:
        """Add an item to the player's inventory."""
        self.inventory.append(item)
    
    def has_item(self, item_name: str) -> bool:
        """Check if player has a specific item."""
        return any(item.name.lower() == item_name.lower() for item in self.inventory)
    
    def get_item(self, item_name: str) -> Optional[Item]:
        """Get an item from inventory without removing it."""
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                return item
        return None
    
    def use_item(self, item_name: str) -> Optional[Item]:
        """Use (remove) an item from inventory."""
        for item in self.inventory:
            if item.name.lower() == item_name.lower() and item.usable:
                self.inventory.remove(item)
                return item
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for JSON serialization."""
        return {
            'inventory': [item.to_dict() for item in self.inventory],
            'current_room': self.current_room,
            'health': self.health
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create Player from dictionary."""
        player = cls(data['current_room'])
        player.inventory = [Item.from_dict(item_data) for item_data in data['inventory']]
        player.health = data['health']
        return player

class GameEngine:
    """Main game engine that handles game logic and user interaction."""
    
    def __init__(self):
        self.rooms = {}
        self.player = Player()
        self.game_over = False
        self.won = False
        self.load_default_scenario()
    
    def load_default_scenario(self) -> None:
        """Load the default dungeon scenario."""
        # Create items
        rusty_key = Item("Rusty Key", "An old, rusty key that might open something.", True, ["Armory"])
        torch = Item("Torch", "A burning torch that lights the way.", False)
        sword = Item("Iron Sword", "A sharp iron sword for protection.", True, ["Guard Post"])
        health_potion = Item("Health Potion", "Restores health when used.", True)
        golden_key = Item("Golden Key", "A pristine golden key.", True, ["Exit Gate"])
        
        # Create rooms and their connections
        prison_cell = Room("Prison Cell", 
                          "A damp, cold cell with stone walls. Water drips from the ceiling. There's a door to the NORTH.",
                          [torch], 
                          {"north": "Corridor"})
        
        corridor = Room("Corridor",
                       "A long, dark hallway with doors on both sides. You can go SOUTH to your cell, EAST to a locked armory, WEST to what looks like a guard post, or NORTH to another room.",
                       [],
                       {"south": "Prison Cell", "east": "Armory", "west": "Guard Post", "north": "Treasure Room"})
        
        # Guard Post is unlocked - this is where you get the key
        guard_post = Room("Guard Post",
                         "The guards' quarters with a table and chairs. The guards seem to have left in a hurry.",
                         [rusty_key],
                         {"east": "Corridor"})
        
        # Armory requires the rusty key
        armory = Room("Armory",
                     "A room filled with weapons and armor on the walls.",
                     [sword, health_potion],
                     {"west": "Corridor"},
                     locked=True,
                     unlock_item="Rusty Key")
        
        treasure_room = Room("Treasure Room",
                           "A glittering room filled with gold and jewels. There's a passage to the NORTH.",
                           [golden_key],
                           {"south": "Corridor", "north": "Exit Gate"})
        
        exit_gate = Room("Exit Gate",
                        "Heavy iron gates leading to freedom! The lock looks like it needs a special key.",
                        [],
                        {},
                        locked=True,
                        unlock_item="Golden Key")
        
        self.rooms = {
            "Prison Cell": prison_cell,
            "Corridor": corridor,
            "Armory": armory,     
            "Guard Post": guard_post,
            "Treasure Room": treasure_room,
            "Exit Gate": exit_gate
        }
    
    def save_game(self, filename: str = "savegame.json") -> bool:
        """Save the current game state to a file."""
        try:
            game_state = {
                'player': self.player.to_dict(),
                'rooms': {name: room.to_dict() for name, room in self.rooms.items()},
                'game_over': self.game_over,
                'won': self.won
            }
            
            with open(filename, 'w') as f:
                json.dump(game_state, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, filename: str = "savegame.json") -> bool:
        """Load a game state from a file."""
        try:
            if not os.path.exists(filename):
                print(f"Save file '{filename}' not found.")
                return False
            
            with open(filename, 'r') as f:
                game_state = json.load(f)
            
            self.player = Player.from_dict(game_state['player'])
            self.rooms = {name: Room.from_dict(room_data) 
                         for name, room_data in game_state['rooms'].items()}
            self.game_over = game_state['game_over']
            self.won = game_state['won']
            
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
    
    def get_current_room(self) -> Room:
        """Get the room the player is currently in."""
        return self.rooms[self.player.current_room]
    
    def display_room(self) -> None:
        """Display the current room's description and contents."""
        room = self.get_current_room()
        room.visited = True
        
        print(f"\n=== {room.name} ===")
        print(room.description)
        
        if room.items:
            print("\nItems here:")
            for item in room.items:
                print(f"  - {item.name}: {item.description}")
        
        if room.connections:
            print(f"\nExits: {', '.join(room.connections.keys())}")
    
    def display_inventory(self) -> None:
        """Display the player's inventory."""
        if not self.player.inventory:
            print("\nYour inventory is empty.")
        else:
            print(f"\nInventory (Health: {self.player.health}):")
            for item in self.player.inventory:
                print(f"  - {item.name}: {item.description}")
    
    def move_player(self, direction: str) -> bool:
        """Move the player in the specified direction."""
        room = self.get_current_room()
        direction = direction.lower()
        
        # Debugging output
        print(f"DEBUG: Trying to go {direction} from {room.name}")
        print(f"DEBUG: Available exits: {list(room.connections.keys())}")
        
        if direction not in room.connections:
            print(f"You can't go {direction}. Available directions: {', '.join(room.connections.keys())}")
            return False
        
        next_room_name = room.connections[direction]
        next_room = self.rooms[next_room_name]
        
        # Check if the room is locked
        if next_room.locked:
            if next_room.unlock_item and self.player.has_item(next_room.unlock_item):
                print(f"You use the {next_room.unlock_item} to unlock the door.")
                next_room.locked = False
            else:
                unlock_hint = f" You need a {next_room.unlock_item}." if next_room.unlock_item else ""
                print(f"The door to {next_room.name} is locked.{unlock_hint}")
                return False
        
        self.player.current_room = next_room_name
        print(f"You move {direction} to the {next_room_name}.")
        
        # Display the new room
        self.display_room()
        
        # Check win condition
        if next_room_name == "Exit Gate" and not next_room.locked:
            self.won = True
            self.game_over = True
            print("\nCongratulations! You have escaped the dungeon!")
        
        return True
    
    def take_item(self, item_name: str) -> bool:
        """Take an item from the current room."""
        room = self.get_current_room()
        item = room.remove_item(item_name)
        
        if item:
            self.player.add_item(item)
            print(f"You took the {item.name}.")
            return True
        else:
            # Show available items to help player
            if room.items:
                available_items = [item.name for item in room.items]
                print(f"That item is not here. Available items: {', '.join(available_items)}")
            else:
                print("There are no items here.")
            return False
    
    def use_item(self, item_name: str) -> bool:
        """Use an item from the player's inventory."""
        item = self.player.use_item(item_name)
        
        if item:
            if item.name.lower() == "health potion":
                self.player.health = min(100, self.player.health + 50)
                print(f"You used the {item.name}. Health restored to {self.player.health}!")
            else:
                print(f"You used the {item.name}.")
            return True
        else:
            print("You don't have that item or it can't be used.")
            return False
    
    def process_command(self, command: str) -> None:
        """Process a user command using a simple search algorithm."""
        command = command.strip().lower()
        words = command.split()
        
        if not words:
            print("Please enter a command.")
            return
        
        # Extract the action from the command
        action = words[0]
        
        if action in ["go", "move", "walk"]:
            if len(words) > 1:
                direction = words[1]
                self.move_player(direction)
            else:
                print("Go where? Available directions: north, south, east, west")
        
        elif action in ["take", "get", "pick"]:
            if len(words) > 1:
                item_name = " ".join(words[1:])
                self.take_item(item_name)
            else:
                print("Take what?")
        
        elif action in ["use"]:
            if len(words) > 1:
                item_name = " ".join(words[1:])
                self.use_item(item_name)
            else:
                print("Use what?")
        
        elif action in ["look", "examine", "l"]:
            self.display_room()
        
        elif action in ["inventory", "inv", "i"]:
            self.display_inventory()
        
        elif action in ["help", "h"]:
            self.display_help()
        
        elif action in ["save"]:
            if self.save_game():
                print("Game saved successfully!")
            else:
                print("Failed to save game.")
        
        elif action in ["load"]:
            if self.load_game():
                print("Game loaded successfully!")
            else:
                print("Failed to load game.")
        
        elif action in ["quit", "exit", "q"]:
            self.game_over = True
            print("Thanks for playing!")
        
        else:
            print("I don't understand that command. Type 'help' for available commands.")
    
    def display_help(self) -> None:
        """Display available commands."""
        help_text = """
Available Commands:
  go <direction>     - Move in a direction (north, south, east, west)
  take <item>        - Pick up an item
  use <item>         - Use an item from your inventory
  look               - Look around the current room
  inventory (inv)    - Show your inventory
  save               - Save the game
  load               - Load a saved game
  help               - Show this help message
  quit               - Exit the game
        """
        print(help_text)
    
    def run(self) -> None:
        """Main game loop."""
        print("Welcome to 'Escape the Dungeon'!")
        print("You wake up in a dark, cold dungeon cell...")
        print("Type 'help' for available commands.")
        
        self.display_room()
        
        while not self.game_over:
            try:
                command = input("\n> ").strip()
                if command:
                    self.process_command(command)
                    
                    if not self.game_over:
                        # Random events or health checks could go here
                        pass
                        
            except KeyboardInterrupt:
                print("\n\nGame interrupted. Thanks for playing!")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                print("Please try again.")
        
        if self.won:
            print("\nYou are free! The sunlight blinds you as you step outside.")
            print("Your adventure ends here, but freedom is yours!")

def main():
    """Main function to start the game."""
    try:
        game = GameEngine()
        game.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        print("The game has encountered an unexpected error and must close.")

if __name__ == "__main__":
    main()
