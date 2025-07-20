from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

ROWS, COLS = 5, 5
MAX_WRONG_MOVES = 3

# Game state
maze = []
player_pos = (0, 0)
goal_pos = (ROWS - 1, COLS - 1)
wrong_moves = 0
game_active = True

def generate_maze():
    global maze, player_pos, goal_pos, wrong_moves, game_active
    maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]
    stack = [(0, 0)]
    visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
    maze[0][0] = 0
    visited[0][0] = True

    directions = [(0,1),(1,0),(0,-1),(-1,0)]
    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx*2, y + dy*2
            if 0 <= nx < ROWS and 0 <= ny < COLS and not visited[nx][ny]:
                neighbors.append((nx, ny, dx, dy))
        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            maze[x + dx][y + dy] = 0
            maze[nx][ny] = 0
            visited[nx][ny] = True
            stack.append((nx, ny))
        else:
            stack.pop()

    player_pos = (0, 0)
    goal_pos = (ROWS - 1, COLS - 1)
    wrong_moves = 0
    game_active = True

@app.route("/")
def index():
    generate_maze()
    return render_template("index.html", maze=maze, player=player_pos, goal=goal_pos)

@app.route("/move", methods=["POST"])
def move():
    global player_pos, wrong_moves, game_active
    
    if not game_active:
        return jsonify({
            "result": "game_over",
            "message": "Game over! Please refresh to play again.",
            "sound": "game_over"
        })
    
    data = request.get_json()
    direction = data.get("direction")
    x, y = player_pos
    dx, dy = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}.get(direction, (0, 0))
    nx, ny = x + dx, y + dy

    # Sound variations
    wrong_sounds = ["wrong1", "wrong2", "wrong3"]
    win_sounds = ["win1", "win2", "win3"]
    move_sounds = {
        "up": "move_up",
        "down": "move_down", 
        "left": "move_left",
        "right": "move_right"
    }
    
    if 0 <= nx < ROWS and 0 <= ny < COLS:
        if maze[nx][ny] == 0:
            player_pos = (nx, ny)
            if (nx, ny) == goal_pos:
                generate_maze()
                return jsonify({
                    "result": "goal",
                    "maze": maze,
                    "player": player_pos,
                    "goal": goal_pos,
                    "message": random.choice([
                        "Fantastic! New maze unlocked!",
                        "You're amazing! Next challenge!",
                        "Maze Master! Here's another!"
                    ]),
                    "sound": random.choice(win_sounds),
                    "new_maze": True
                })
            else:
                return jsonify({
                    "result": "move",
                    "player": player_pos,
                    "message": random.choice([
                        "Great move!",
                        "Nice going!",
                        "You're doing great!"
                    ]),
                    "sound": move_sounds[direction]
                })
        else:
            wrong_moves += 1
            if wrong_moves >= MAX_WRONG_MOVES:
                game_active = False
                return jsonify({
                    "result": "game_over",
                    "message": random.choice([
                        "Oh no! Game over!",
                        "Better luck next time!",
                        "Don't give up! Try again!"
                    ]),
                    "sound": "game_over"
                })
            return jsonify({
                "result": "wall",
                "message": random.choice([
                    "Oops! That's a wall!",
                    "Bonk! Can't go that way!",
                    "Nope, that's blocked!"
                ]),
                "sound": random.choice(wrong_sounds),
                "remaining_attempts": MAX_WRONG_MOVES - wrong_moves
            })
    else:
        wrong_moves += 1
        if wrong_moves >= MAX_WRONG_MOVES:
            game_active = False
            return jsonify({
                "result": "game_over",
                "message": random.choice([
                    "Game over! Out of bounds!",
                    "Whoops! Too many wrong turns!",
                    "The maze defeated you this time!"
                ]),
                "sound": "game_over"
            })
        return jsonify({
            "result": "invalid",
            "message": random.choice([
                "You can't leave the maze!",
                "That's outside the boundaries!",
                "Stay inside the maze!"
            ]),
            "sound": random.choice(wrong_sounds),
            "remaining_attempts": MAX_WRONG_MOVES - wrong_moves
        })

if __name__ == "__main__":
    app.run(debug=True)