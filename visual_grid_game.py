import random
import tkinter as tk


class VisualGridHuntGame:
    """Partially observable Pacman-style grid environment."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        self.food_positions = set()

        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)

            if (fx, fy) != (0, 0) and (fx, fy) not in self.walls:
                self.food_positions.add((fx, fy))

        self.opponents = []

        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)

            if ((ox, oy) != (0, 0)
                    and (ox, oy) not in self.walls
                    and (ox, oy) not in self.food_positions):
                self.opponents.append([ox, oy])

        self.score = 0
        self.steps = 0
        self.collision = False


    # PARTIALLY OBSERVABLE PERCEPT
    def get_percept(self):

        x, y = self.agent_pos

        return {
            "wall_ahead": self.check_wall_ahead(),
            "food_here": (x, y) in self.food_positions,
            "opponent_nearby": self.check_opponent_nearby(),
            "score": self.score
        }


    def check_wall_ahead(self):

        possible_moves = [
            (self.agent_pos[0], self.agent_pos[1] + 1),
            (self.agent_pos[0], self.agent_pos[1] - 1),
            (self.agent_pos[0] - 1, self.agent_pos[1]),
            (self.agent_pos[0] + 1, self.agent_pos[1])
        ]

        return any(
            pos in self.walls or
            pos[0] < 0 or
            pos[0] >= self.width or
            pos[1] < 0 or
            pos[1] >= self.height
            for pos in possible_moves
        )


    def check_opponent_nearby(self):

        for op in self.opponents:
            distance = abs(op[0] - self.agent_pos[0]) + abs(op[1] - self.agent_pos[1])

            if distance <= 1:
                return True

        return False



    def execute_action(self, action):

        self.steps += 1

        new_pos = list(self.agent_pos)

        if action == "Up":
            new_pos[1] += 1

        elif action == "Down":
            new_pos[1] -= 1

        elif action == "Left":
            new_pos[0] -= 1

        elif action == "Right":
            new_pos[0] += 1


        if (tuple(new_pos) in self.walls or
                new_pos[0] < 0 or
                new_pos[0] >= self.width or
                new_pos[1] < 0 or
                new_pos[1] >= self.height):

            self.score -= 5

        else:
            self.agent_pos = new_pos


        position = tuple(self.agent_pos)


        if position in self.food_positions:
            self.food_positions.remove(position)
            self.score += 20


        # opponent movement
        for op in self.opponents:

            move = random.choice(
                ["Up", "Down", "Left", "Right", "Stay"]
            )

            if move == "Up" and op[1] < self.height - 1:
                op[1] += 1

            elif move == "Down" and op[1] > 0:
                op[1] -= 1

            elif move == "Left" and op[0] > 0:
                op[0] -= 1

            elif move == "Right" and op[0] < self.width - 1:
                op[0] += 1


            if op == self.agent_pos:
                self.score -= 50
                self.collision = True



    def is_done(self):

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )



# SIMPLE REFLEX AGENT
class SimpleReflexAgent:

    def sense_and_act(self, percept):

        if percept["food_here"]:
            return random.choice(
                ["Up", "Down", "Left", "Right"]
            )

        elif percept["wall_ahead"]:
            return random.choice(
                ["Left", "Right"]
            )

        elif percept["opponent_nearby"]:
            return "Down"

        else:
            return random.choice(
                ["Up", "Down", "Left", "Right"]
            )



# MODEL BASED AGENT
class ModelBasedAgent:

    def __init__(self):

        self.visited = set()


    def sense_and_act(self, percept):

        # store current state in memory
        current_position = tuple(percept.get("position", (0, 0)))

        self.visited.add(current_position)


        # IF-THEN rules using memory

        if percept["food_here"]:
            return "Up"


        if percept["opponent_nearby"]:
            return "Down"


        possible_actions = [
            "Up",
            "Down",
            "Left",
            "Right"
        ]


        action = random.choice(possible_actions)


        # avoid repeating visited paths
        if current_position in self.visited:

            action = random.choice(
                ["Left", "Right", "Up"]
            )


        return action




class GridGameGUI:

    def __init__(self, root, width=10, height=10,
                 num_food=12, num_opponents=2, walls=None):

        self.root = root

        self.root.title(
            "IT3012 - Model Based Grid Hunt"
        )


        self.env = VisualGridHuntGame(
            width,
            height,
            num_food,
            num_opponents,
            walls
        )


        # Replace agent here
        self.agent = ModelBasedAgent()


        max_canvas_dim = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dim // width,
                max_canvas_dim // height
            )
        )


        self.canvas = tk.Canvas(
            root,
            width=width*self.cell_size,
            height=height*self.cell_size,
            bg="white"
        )

        self.canvas.pack()


        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Arial",14)
        )

        self.label.pack()


        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop
        )

        self.btn.pack()


        self.draw_grid()



    def draw_grid(self):

        self.canvas.delete("all")


        for x in range(self.env.width):

            for y in range(self.env.height):

                x1 = x*self.cell_size
                y1 = (self.env.height-1-y)*self.cell_size

                x2 = x1+self.cell_size
                y2 = y1+self.cell_size


                color = (
                    "#64748b"
                    if (x,y) in self.env.walls
                    else "#f1f5f9"
                )


                self.canvas.create_rectangle(
                    x1,y1,x2,y2,
                    fill=color
                )


        for fx,fy in self.env.food_positions:

            self.canvas.create_oval(
                fx*self.cell_size+10,
                (self.env.height-1-fy)*self.cell_size+10,
                fx*self.cell_size+30,
                (self.env.height-1-fy)*self.cell_size+30,
                fill="orange"
            )


        for ox,oy in self.env.opponents:

            self.canvas.create_rectangle(
                ox*self.cell_size+5,
                (self.env.height-1-oy)*self.cell_size+5,
                ox*self.cell_size+25,
                (self.env.height-1-oy)*self.cell_size+25,
                fill="red"
            )


        ax,ay=self.env.agent_pos


        self.canvas.create_oval(
            ax*self.cell_size+5,
            (self.env.height-1-ay)*self.cell_size+5,
            ax*self.cell_size+30,
            (self.env.height-1-ay)*self.cell_size+30,
            fill="blue"
        )



    def run_loop(self):

        self.btn.config(state="disabled")


        def step():

            if not self.env.is_done():

                percept = self.env.get_percept()

                # add current location temporarily for memory
                percept["position"] = tuple(
                    self.env.agent_pos
                )


                action = self.agent.sense_and_act(
                    percept
                )


                self.env.execute_action(action)


                self.draw_grid()


                self.label.config(
                    text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}"
                )


                self.root.after(
                    300,
                    step
                )


            else:

                self.label.config(
                    text=f"Game Over! Score: {self.env.score}"
                )

                self.btn.config(
                    state="normal"
                )


        step()



if __name__ == "__main__":

    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0
    )

    root.mainloop()