import copy
import time

# --- OBJECTS ---

couch = {"name": "couch", "type": "furniture"}
door_a = {"name": "door a", "type": "door"}
key_a = {"name": "key for door a", "type": "key", "target": door_a}
piano = {"name": "piano", "type": "furniture"}
game_room = {"name": "game room", "type": "room"}

# BEDROOM 1
queen_bed = {"name": "queen bed", "type": "furniture"}
door_b = {"name": "door b", "type": "door"}
key_b = {"name": "key for door b", "type": "key", "target": door_b}
door_c = {"name": "door c", "type": "door"}
bedroom_1 = {"name": "bedroom 1", "type": "room"}

# BEDROOM 2
double_bed = {"name": "double bed", "type": "furniture"}
dresser = {"name": "dresser", "type": "furniture"}
key_c = {"name": "key for door c", "type": "key", "target": door_c}
bedroom_2 = {"name": "bedroom 2", "type": "room"}

# LIVING ROOM
dining_table = {"name": "dining table", "type": "furniture"}
door_d = {"name": "door d", "type": "door"}
key_d = {"name": "key for door d", "type": "key", "target": door_d}
outside = {"name": "outside"}
living_room = {"name": "living room", "type": "room"}

# --- OBJECT LISTS ---
all_rooms = [game_room, outside, bedroom_1, bedroom_2, living_room]
all_doors = [door_a, door_b, door_c, door_d]

# --- RELATIONS ---
object_relations = {
    "game room": [couch, piano, door_a],
    "piano": [key_a],
    "outside": [door_d],
    "door a": [game_room, bedroom_1],
    "bedroom 1": [door_a, door_b, door_c, queen_bed],
    "queen bed": [key_b],
    "door b": [bedroom_1, bedroom_2],
    "bedroom 2": [door_b, double_bed, dresser],
    "dresser": [key_d],
    "double bed": [key_c],
    "door c": [bedroom_1, living_room],
    "living room": [door_c, door_d, dining_table],
    "door d": [living_room, outside],
}

# --- INITIAL STATE ---
INIT_GAME_STATE = {
    "current_room": game_room,
    "keys_collected": [],
    "target_room": outside
}

# Global state
game_state = copy.deepcopy(INIT_GAME_STATE)
start_time = None


# --- FUNCTIONS ---
def linebreak():
    """
    Print a line break
    """
    print("\n")

def start_game():

    #split the message in 3 paragraphs so it's more readable to the user

    print("You wake up on a couch and find yourself in a strange house with no windows that you never been before.")
    print("You don't remember why you are here and what had happened before. You feel some unknown danger is approaching..")
    print("You must get out of the house, NOW!")
    play_room(game_state["current_room"])


def restart_game():
    global game_state, object_relations, start_time
    game_state = copy.deepcopy(INIT_DATA["game_state"])
    object_relations = copy.deepcopy(INIT_DATA["object_relations"])
    start_time = None
    start_game()


def end_game(message):

    print("\n" + message)
    choice = input("🔁 Do you want to play again? (yes/no): ").strip().lower()

    if choice in ("yes"):
        restart_game()
    else:
        print("👋 Thanks for playing! Goodbye.")


def timer():
    global start_time  # persist changes across function calls

    if start_time is None:
        start_time = time.time()
        linebreak()
        print("⏱️ Timer started! You have 10 minutes to escape!")
        print("👻 Type 'Exit' if you are too afraid!")

    # Timer logic
    elapsed = time.time() - start_time
    remaining = max(0, 600 - int(elapsed))
    mins, secs = divmod(remaining, 60)
    print(f"⌛ Time remaining: {mins:02d}:{secs:02d}")

    if remaining <= 0:
        end_game("⌛ Time's up! Game over!")
        return False
    return True

def print_inventory():
    inv = game_state["keys_collected"]
    if inv:
        print(f"📦 Inventory: {len(inv)} key(s) — " + ", ".join(k["name"].upper() for k in inv))
    else:
        print("📦 Inventory: (empty)")


#Elba's updated version with quit\exit and when the time ends the games finishes

def play_room(room):
    """
    Play a room. First check if the room being played is the target room.
    If it is, the game will end with success. Otherwise, let player either
    explore (list all items in this room) or examine an item found here.
    """
    game_state["current_room"] = room
    if(game_state["current_room"] == game_state["target_room"]):
        end_game(f"\n🎉 Congrats! You escaped the room!")
        return
    else:
        print("You are now in " + room["name"].upper())
        if not timer():
          return
        linebreak()
        explore_room(room)
        item=(input("What would you like to examine?🔎 ").strip())
        if item=="quit" or item=="exit":
            end_game("Game Over❌")
            return
        else:
            examine_item(item)




def explore_room(room):
    """
    Explore a room. List all items belonging to this room.
    """
    items = [i["name"] for i in object_relations[room["name"]]]
    print("You explore the room 👣 This is " + room["name"].upper() + ".  👀You find " + ", ".join(items).upper())

def get_next_room_of_door(door, current_room):
    """
    From object_relations, find the two rooms connected to the given door.
    Return the room that is not the current_room.
    """
    connected_rooms = object_relations[door["name"]]
    for room in connected_rooms:
        if(not current_room == room):
            return room


def examine_item(item_name):
    """
    Examine an item which can be a door or furniture.
    First make sure the intended item belongs to the current room.
    Then check if the item is a door. Tell player if key hasn't been
    collected yet. Otherwise ask player if they want to go to the next
    room. If the item is not a door, then check if it contains keys.
    Collect the key if found and update the game state. At the end,
    play either the current or the next room depending on the game state
    to keep playing.
    """
    current_room = game_state["current_room"]
    next_room = ""
    output = None
    for item in object_relations[current_room["name"]]:
        if(item["name"].lower() == item_name.lower().strip()):
            output = "You examine " + item_name.upper() + ". "
            if(item["type"] == "door"):
                have_key = False
                for key in game_state["keys_collected"]:
                    if(key["target"] == item):
                        have_key = True
                if(have_key):
                    output += "You unlock it 🔓 with a key you have."
                    next_room = get_next_room_of_door(item, current_room)
                else:
                    output += "It is locked 🔒 but you don't have the key."
                    print(output)
            else:
                if(item["name"] in object_relations and len(object_relations[item["name"]])>0):
                    item_found = object_relations[item["name"]].pop()
                    game_state["keys_collected"].append(item_found)
                    output += "You find " + item_found["name"].upper() + "🗝."
                    print(output)
                    print_inventory()
                else:
                    output += "There isn't anything interesting about it 🤷‍♂️."
                    print(output)
            break
    if(output is None):
        print("🤦‍♀️The item you requested is not found in the current room.")
    if(next_room and input("You don't know what's behind that door😨. Are you sure you want to open it to find out? Enter 'yes' or 'no'.").strip().lower() == 'yes'):
        play_room(next_room)
    else:
         next_item = input("What would you like to examine?🔎 ").strip()
         if next_item in ("quit", "exit"):
            end_game("👋 You gave up. Game over!")
            return
         examine_item(next_item)
