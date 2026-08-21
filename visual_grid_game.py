import random
import tkinter as tk

from agent import SearchAgent


class VisualGridHuntGame:
    """
    Pacman-style grid environment for IT3012 Practical 03.
    """

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=2,
        custom_walls=None
    ):

        self.width = width
        self.height = height

        # ------------------------------------------------------
        # Agent starting position
        # ------------------------------------------------------

        self.agent_pos = [0, 0]

        # ------------------------------------------------------
        # Walls
        # ------------------------------------------------------

        if custom_walls is not None:

            self.walls = set(custom_walls)

        else:

            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        # ------------------------------------------------------
        # Generate food
        # ------------------------------------------------------

        self.food_positions = set()

        while len(self.food_positions) < num_food:

            fx = random.randint(
                0,
                self.width - 1
            )

            fy = random.randint(
                0,
                self.height - 1
            )

            position = (fx, fy)

            if (
                position != (0, 0)
                and position not in self.walls
            ):

                self.food_positions.add(
                    position
                )

        # ------------------------------------------------------
        # Generate opponents
        # ------------------------------------------------------

        self.opponents = []

        while len(self.opponents) < num_opponents:

            ox = random.randint(
                0,
                self.width - 1
            )

            oy = random.randint(
                0,
                self.height - 1
            )

            position = (ox, oy)

            if (
                position != (0, 0)
                and position not in self.walls
                and position not in self.food_positions
            ):

                self.opponents.append(
                    [ox, oy]
                )

        # ------------------------------------------------------
        # Game variables
        # ------------------------------------------------------

        self.score = 0
        self.steps = 0
        self.collision = False

    # ==========================================================
    # PERCEPT
    # ==========================================================

    def get_percept(self):
        """
        Return the information available to the agent.

        Practical 03 requires the global state:
            grid_size
            walls
            all_food
        """

        x, y = self.agent_pos

        return {

            # Existing percept information
            "wall_ahead": self.check_wall_ahead(),

            "food_here": (
                x,
                y
            ) in self.food_positions,

            "opponent_nearby":
                self.check_opponent_nearby(),

            "score":
                self.score,

            # --------------------------------------------------
            # Practical 03 global state
            # --------------------------------------------------

            "grid_size": (
                self.width,
                self.height
            ),

            "walls":
                list(self.walls),

            "all_food":
                list(self.food_positions),

            # Current position
            "position":
                tuple(self.agent_pos)
        }

    # ==========================================================
    # CHECK WALL
    # ==========================================================

    def check_wall_ahead(self):

        possible_moves = [

            (
                self.agent_pos[0],
                self.agent_pos[1] + 1
            ),

            (
                self.agent_pos[0],
                self.agent_pos[1] - 1
            ),

            (
                self.agent_pos[0] - 1,
                self.agent_pos[1]
            ),

            (
                self.agent_pos[0] + 1,
                self.agent_pos[1]
            )
        ]

        return any(

            position in self.walls

            or position[0] < 0
            or position[0] >= self.width

            or position[1] < 0
            or position[1] >= self.height

            for position in possible_moves
        )

    # ==========================================================
    # CHECK OPPONENT NEARBY
    # ==========================================================

    def check_opponent_nearby(self):

        for opponent in self.opponents:

            distance = (
                abs(
                    opponent[0]
                    - self.agent_pos[0]
                )

                +

                abs(
                    opponent[1]
                    - self.agent_pos[1]
                )
            )

            if distance <= 1:

                return True

        return False

    # ==========================================================
    # EXECUTE ACTION
    # ==========================================================

    def execute_action(self, action):

        self.steps += 1

        new_pos = list(
            self.agent_pos
        )

        # ------------------------------------------------------
        # Convert action to new position
        # ------------------------------------------------------

        if action == "Up":

            new_pos[1] += 1

        elif action == "Down":

            new_pos[1] -= 1

        elif action == "Left":

            new_pos[0] -= 1

        elif action == "Right":

            new_pos[0] += 1

        elif action == "Stay":

            pass

        # ------------------------------------------------------
        # Check wall / boundary
        # ------------------------------------------------------

        if (

            tuple(new_pos)
            in self.walls

            or new_pos[0] < 0
            or new_pos[0] >= self.width

            or new_pos[1] < 0
            or new_pos[1] >= self.height

        ):

            # Penalty for invalid movement
            self.score -= 5

        else:

            self.agent_pos = new_pos

        # ------------------------------------------------------
        # Collect food
        # ------------------------------------------------------

        position = tuple(
            self.agent_pos
        )

        if position in self.food_positions:

            self.food_positions.remove(
                position
            )

            self.score += 20

        # ------------------------------------------------------
        # Move opponents
        # ------------------------------------------------------

        for opponent in self.opponents:

            move = random.choice(
                [
                    "Up",
                    "Down",
                    "Left",
                    "Right",
                    "Stay"
                ]
            )

            if (
                move == "Up"
                and opponent[1] < self.height - 1
            ):

                opponent[1] += 1

            elif (
                move == "Down"
                and opponent[1] > 0
            ):

                opponent[1] -= 1

            elif (
                move == "Left"
                and opponent[0] > 0
            ):

                opponent[0] -= 1

            elif (
                move == "Right"
                and opponent[0] < self.width - 1
            ):

                opponent[0] += 1

            # --------------------------------------------------
            # Collision
            # --------------------------------------------------

            if opponent == self.agent_pos:

                self.score -= 50

                self.collision = True

    # ==========================================================
    # GAME OVER
    # ==========================================================

    def is_done(self):

        return (

            len(
                self.food_positions
            ) == 0

            or self.steps >= 60

            or self.collision
        )


# ==============================================================
# GUI
# ==============================================================

class GridGameGUI:

    def __init__(
        self,
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0,
        walls=None,
        algorithm="BFS"
    ):

        self.root = root

        # ------------------------------------------------------
        # Window
        # ------------------------------------------------------

        self.root.title(
            "IT3012 - Practical 03 - Uninformed Search"
        )

        self.root.geometry(
            "700x850"
        )

        self.root.resizable(
            False,
            False
        )

        # ------------------------------------------------------
        # Environment
        # ------------------------------------------------------

        self.env = VisualGridHuntGame(

            width=width,

            height=height,

            num_food=num_food,

            num_opponents=num_opponents,

            custom_walls=walls
        )

        # ------------------------------------------------------
        # Search Agent
        # ------------------------------------------------------

        self.agent = SearchAgent()

        self.agent.active_algo = algorithm

        # ------------------------------------------------------
        # Canvas size
        # ------------------------------------------------------

        max_canvas_dim = 500

        self.cell_size = max(

            20,

            min(

                max_canvas_dim // width,

                max_canvas_dim // height
            )
        )

        # ------------------------------------------------------
        # Canvas
        # ------------------------------------------------------

        self.canvas = tk.Canvas(

            root,

            width=width * self.cell_size,

            height=height * self.cell_size,

            bg="white"
        )

        self.canvas.pack(
            pady=5
        )

        # ------------------------------------------------------
        # Status label
        # ------------------------------------------------------

        self.label = tk.Label(

            root,

            text=(
                f"Algorithm: {algorithm} | "
                f"Score: 0 | "
                f"Steps: 0"
            ),

            font=("Arial", 14)
        )

        self.label.pack(
            pady=5
        )

        # ------------------------------------------------------
        # Algorithm buttons
        # ------------------------------------------------------

        self.algorithm_frame = tk.Frame(
            root
        )

        self.algorithm_frame.pack(
            pady=5
        )

        self.bfs_button = tk.Button(

            self.algorithm_frame,

            text="BFS",

            width=8,

            command=lambda:
                self.change_algorithm("BFS")
        )

        self.bfs_button.pack(
            side=tk.LEFT,
            padx=5
        )

        self.dfs_button = tk.Button(

            self.algorithm_frame,

            text="DFS",

            width=8,

            command=lambda:
                self.change_algorithm("DFS")
        )

        self.dfs_button.pack(
            side=tk.LEFT,
            padx=5
        )

        self.ucs_button = tk.Button(

            self.algorithm_frame,

            text="UCS",

            width=8,

            command=lambda:
                self.change_algorithm("UCS")
        )

        self.ucs_button.pack(
            side=tk.LEFT,
            padx=5
        )

        # ------------------------------------------------------
        # Start button
        # ------------------------------------------------------

        self.btn = tk.Button(

            root,

            text="Start Simulation",

            width=20,

            height=2,

            command=self.run_loop
        )

        self.btn.pack(
            pady=8
        )

        # ------------------------------------------------------
        # Draw initial grid
        # ------------------------------------------------------

        self.draw_grid()

    # ==========================================================
    # CHANGE ALGORITHM
    # ==========================================================

    def change_algorithm(self, algorithm):

        # Change selected algorithm
        self.agent.active_algo = algorithm

        # Clear previous plan
        self.agent.plan = []

        self.label.config(

            text=(
                f"Algorithm: {algorithm} | "
                f"Score: {self.env.score} | "
                f"Steps: {self.env.steps}"
            )
        )

    # ==========================================================
    # DRAW GRID
    # ==========================================================

    def draw_grid(self):

        self.canvas.delete(
            "all"
        )

        # ------------------------------------------------------
        # Draw cells
        # ------------------------------------------------------

        for x in range(
            self.env.width
        ):

            for y in range(
                self.env.height
            ):

                x1 = (
                    x * self.cell_size
                )

                y1 = (
                    self.env.height
                    - 1
                    - y
                ) * self.cell_size

                x2 = (
                    x1
                    + self.cell_size
                )

                y2 = (
                    y1
                    + self.cell_size
                )

                # Wall
                if (
                    x,
                    y
                ) in self.env.walls:

                    color = "#64748b"

                # Empty cell
                else:

                    color = "#f1f5f9"

                self.canvas.create_rectangle(

                    x1,
                    y1,
                    x2,
                    y2,

                    fill=color,

                    outline="#cbd5e1"
                )

        # ------------------------------------------------------
        # Draw food
        # ------------------------------------------------------

        for fx, fy in (
            self.env.food_positions
        ):

            x1 = (
                fx * self.cell_size
                + self.cell_size // 4
            )

            y1 = (
                (
                    self.env.height
                    - 1
                    - fy
                )
                * self.cell_size
                + self.cell_size // 4
            )

            x2 = (
                fx * self.cell_size
                + 3 * self.cell_size // 4
            )

            y2 = (
                (
                    self.env.height
                    - 1
                    - fy
                )
                * self.cell_size
                + 3 * self.cell_size // 4
            )

            self.canvas.create_oval(

                x1,
                y1,
                x2,
                y2,

                fill="orange",

                outline="black"
            )

        # ------------------------------------------------------
        # Draw opponents
        # ------------------------------------------------------

        for ox, oy in (
            self.env.opponents
        ):

            x1 = (
                ox * self.cell_size
                + 5
            )

            y1 = (
                (
                    self.env.height
                    - 1
                    - oy
                )
                * self.cell_size
                + 5
            )

            x2 = (
                ox * self.cell_size
                + self.cell_size
                - 5
            )

            y2 = (
                (
                    self.env.height
                    - 1
                    - oy
                )
                * self.cell_size
                + self.cell_size
                - 5
            )

            self.canvas.create_rectangle(

                x1,
                y1,
                x2,
                y2,

                fill="red"
            )

        # ------------------------------------------------------
        # Draw agent
        # ------------------------------------------------------

        ax, ay = (
            self.env.agent_pos
        )

        x1 = (
            ax * self.cell_size
            + 5
        )

        y1 = (
            (
                self.env.height
                - 1
                - ay
            )
            * self.cell_size
            + 5
        )

        x2 = (
            ax * self.cell_size
            + self.cell_size
            - 5
        )

        y2 = (
            (
                self.env.height
                - 1
                - ay
            )
            * self.cell_size
            + self.cell_size
            - 5
        )

        self.canvas.create_oval(

            x1,
            y1,
            x2,
            y2,

            fill="blue",

            outline="black"
        )

    # ==========================================================
    # RUN LOOP
    # ==========================================================

    def run_loop(self):

        # Disable Start button
        self.btn.config(
            state="disabled"
        )

        # Disable algorithm buttons
        self.bfs_button.config(
            state="disabled"
        )

        self.dfs_button.config(
            state="disabled"
        )

        self.ucs_button.config(
            state="disabled"
        )

        def step():

            # --------------------------------------------------
            # Continue while game is running
            # --------------------------------------------------

            if not self.env.is_done():

                # Get percept
                percept = (
                    self.env.get_percept()
                )

                # --------------------------------------------------
                # Agent chooses action
                # --------------------------------------------------

                action = (
                    self.agent.sense_and_act(
                        percept
                    )
                )

                # --------------------------------------------------
                # Execute action
                # --------------------------------------------------

                self.env.execute_action(
                    action
                )

                # --------------------------------------------------
                # Redraw grid
                # --------------------------------------------------

                self.draw_grid()

                # --------------------------------------------------
                # Update status
                # --------------------------------------------------

                self.label.config(

                    text=(

                        f"Algorithm: "
                        f"{self.agent.active_algo} | "

                        f"Score: "
                        f"{self.env.score} | "

                        f"Steps: "
                        f"{self.env.steps} | "

                        f"Action: "
                        f"{action} | "

                        f"Plan remaining: "
                        f"{len(self.agent.plan)}"
                    )
                )

                # --------------------------------------------------
                # Run next step after 300 ms
                # --------------------------------------------------

                self.root.after(
                    300,
                    step
                )

            # --------------------------------------------------
            # Game over
            # --------------------------------------------------

            else:

                self.label.config(

                    text=(

                        f"Game Over! | "

                        f"Algorithm: "
                        f"{self.agent.active_algo} | "

                        f"Score: "
                        f"{self.env.score} | "

                        f"Steps: "
                        f"{self.env.steps}"
                    )
                )

                # Re-enable buttons
                self.btn.config(
                    state="normal"
                )

                self.bfs_button.config(
                    state="normal"
                )

                self.dfs_button.config(
                    state="normal"
                )

                self.ucs_button.config(
                    state="normal"
                )

        # Start first step
        step()


# ==============================================================
# MAIN
# ==============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = GridGameGUI(

        root,

        width=12,

        height=12,

        num_food=15,

        num_opponents=0,

        algorithm="BFS"
    )

    root.mainloop()