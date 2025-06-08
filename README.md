Escape the Dungeon - Text-Based Game
Student: [Adam ElTarabishy]
Student ID: [P487525]
Course: [IY499]

Declaration: I declare that this work is my own and has not been copied from any other source.

Description

"Escape the Dungeon" is a text adventure game where the player must escape from a medieval dungeon to freedom. The player is originally in the cell and must navigate chained rooms like corridors, armories, guards' rooms, and the treasure room. The game features an in-game inventory system, special keys to unlock locked doors, as well as game persistence with save/load features.
The game employs the conventional adventure game mechanics where the players collect items, solve puzzles through the application of the correct items in the correct locations, and navigate an interconnecting world with the ultimate objective to escape the dungeon.

Features

Interactive Room System: Navigate 6 interconnecting rooms with distinct details and items
Inventory Management: Collect and use items strategically to progress through the game
Problem Solving: Locked doors require specific items to unlock, creating a sequence of events
Save/Load System


Save the game and reload saved games in the form of JSON files
Error Handling: Robust input validation & error recovery

Classes and Architecture

Item Class: Represents collectible items with properties for usability and requirements
Room Class: Manages room descriptions, connections, items, and lock status
Player Class: Tracks inventory, location, and health status
GameEngine Class: Core game logic, command processing, and file operations


Game Commands

go <direction> - Move in a direction (north, south, east, west)
take <item> - Pick up an item from the current room
use <item> - Use an item from your inventory
look - Examine the current room
inventory or inv - Display your inventory
save - Save the current game state
load - Load a previously saved game
help - Display available commands
quit - Exit the game

Libraries Used

json: For save/load game state serialization
os: For file system operations and save file validation
typing: For type hints and better code documentation

Game Flow

Start in the Prison Cell with a torch
Explore the Corridor to access other rooms
Find the Rusty Key in the Guard Post (requires Iron Sword)
Use the Rusty Key to unlock the Armory
Collect the Iron Sword and Health Potion from the Armory
Access the Treasure Room to find the Golden Key
Use the Golden Key to unlock the Exit Gate and escape

File Structure
IY499/
├── main.py             # Main game file
├── README.md           # This file
├── savegame.json       # Generated save file (created when saving)
└── .git/               # Git repository files

Repository
GitHub Repository: []

Testing
The game has been tested for:

Invalid user inputs and command handling
File I/O error scenarios (missing files, permissions)
Game state consistency across save/load cycles
All possible game paths and win conditions
