import random
import tkinter as tk

# =====================================================================
# PART 1: ENVIRONMENT WITH PARTIAL OBSERVABILITY (Step 1.1)
# =====================================================================
class PartiallyObservableGridGame:
    """Environment modified to provide only local percepts (Partially Observable)."""

    DIRECTIONS = ['Up', 'Right', 'Down', 'Left']

    def __init__(self, width=10, height=10, num_food=10, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Global position (hidden from agent percept)
        self.agent_facing = 'Up' # Global orientation

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7), (0, 1), (1, 1)}

        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            if (fx, fy) != (0, 0) and (fx, fy) not in self.walls:
                self.food_positions.add((fx, fy))

        self.score = 0
        self.steps = 0

    def _get_adjacent_pos(self, facing_dir):
        x, y = self.agent_pos
        if facing_dir == 'Up':
            return (x, y + 1)
        elif facing_dir == 'Down':
            return (x, y - 1)
        elif facing_dir == 'Left':
            return (x - 1, y)
        elif facing_dir == 'Right':
            return (x + 1, y)
        return (x, y)

    def _is_wall_or_boundary(self, pos):
        x, y = pos
        out_of_bounds = x < 0 or x >= self.width or y < 0 or y >= self.height
        return out_of_bounds or (pos in self.walls)

    def get_percept(self) -> dict:
        """Step 1.1: Returns only local booleans relative to facing direction."""
        idx = self.DIRECTIONS.index(self.agent_facing)
        ahead_dir = self.DIRECTIONS[idx]
        left_dir = self.DIRECTIONS[(idx - 1) % 4]
        right_dir = self.DIRECTIONS[(idx + 1) % 4]

        pos_ahead = self._get_adjacent_pos(ahead_dir)
        pos_left = self._get_adjacent_pos(left_dir)
        pos_right = self._get_adjacent_pos(right_dir)

        return {
            'food_here': tuple(self.agent_pos) in self.food_positions,
            'wall_ahead': self._is_wall_or_boundary(pos_ahead),
            'left_wall_ahead': self._is_wall_or_boundary(pos_left),
            'right_wall_ahead': self._is_wall_or_boundary(pos_right),
            'score': self.score,
            'remaining_food': len(self.food_positions)
        }

    def execute_action(self, action: str):
        self.steps += 1
        idx = self.DIRECTIONS.index(self.agent_facing)

        if action == 'turn_left':
            self.agent_facing = self.DIRECTIONS[(idx - 1) % 4]
        elif action == 'turn_right':
            self.agent_facing = self.DIRECTIONS[(idx + 1) % 4]
        elif action == 'move_forward':
            next_pos = self._get_adjacent_pos(self.agent_facing)
            if self._is_wall_or_boundary(next_pos):
                self.score -= 5 # Bump penalty
            else:
                self.agent_pos = list(next_pos)
        elif action == 'suck':
            pos_tuple = tuple(self.agent_pos)
            if pos_tuple in self.food_positions:
                self.food_positions.remove(pos_tuple)
                self.score += 20

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60


# =====================================================================
# PART 2: AGENT ARCHITECTURES
# =====================================================================

class SimpleReflexAgent:
    """Step 1.2: Simple Reflex Agent (Stateless, purely Condition-Action rules)."""
    
    def sense_and_act(self, percept: dict) -> str:
        # Strict Condition-Action Rules
        if percept['food_here']:
            return 'suck'
        elif percept['wall_ahead']:
            return 'turn_left'
        else:
            return 'move_forward'


class ModelBasedAgent:
    """Step 1.3: Model-Based Agent with Memory & Internal State Tracking."""

    DIRECTIONS = ['Up', 'Right', 'Down', 'Left']

    def __init__(self):
        # Internal Memory / Belief State
        self.visited_cells = set([(0, 0)])
        self.rel_x = 0
        self.rel_y = 0
        self.facing_idx = 0 # Starts facing 'Up' (index 0)
        self.last_action = None

    def _get_ahead_rel_pos(self, facing_idx):
        facing = self.DIRECTIONS[facing_idx]
        if facing == 'Up':
            return (self.rel_x, self.rel_y + 1)
        elif facing == 'Right':
            return (self.rel_x + 1, self.rel_y)
        elif facing == 'Down':
            return (self.rel_x, self.rel_y - 1)
        elif facing == 'Left':
            return (self.rel_x - 1, self.rel_y)

    def sense_and_act(self, percept: dict) -> str:
        # 1. TRANSITION & SENSOR MODEL UPDATE (Update Internal State)
        if self.last_action == 'turn_left':
            self.facing_idx = (self.facing_idx - 1) % 4
        elif self.last_action == 'turn_right':
            self.facing_idx = (self.facing_idx + 1) % 4
        elif self.last_action == 'move_forward':
            self.rel_x, self.rel_y = self._get_ahead_rel_pos(self.facing_idx)
            self.visited_cells.add((self.rel_x, self.rel_y))

        # Check relative neighbor visit states
        ahead_pos = self._get_ahead_rel_pos(self.facing_idx)
        left_pos = self._get_ahead_rel_pos((self.facing_idx - 1) % 4)
        right_pos = self._get_ahead_rel_pos((self.facing_idx + 1) % 4)

        ahead_visited = ahead_pos in self.visited_cells
        left_visited = left_pos in self.visited_cells
        right_visited = right_pos in self.visited_cells

        # 2. CONDITION-ACTION RULES QUERYING INTERNAL MEMORY
        if percept['food_here']:
            action = 'suck'
        elif not percept['wall_ahead'] and not ahead_visited:
            action = 'move_forward'
        elif not percept['left_wall_ahead'] and not left_visited:
            action = 'turn_left'
        elif not percept['right_wall_ahead'] and not right_visited:
            action = 'turn_right'
        elif not percept['wall_ahead']:
            action = 'move_forward' # Fallback path
        else:
            action = 'turn_left'    # Escape wall maneuver

        self.last_action = action
        return action


# =====================================================================
# PART 3: GUI SIMULATOR
# =====================================================================

class GridGameGUI:
    def __init__(self, root, agent_type="ModelBased"):
        self.root = root
        self.root.title(f"IT3012 - Lab 02: {agent_type} Agent")

        # Custom grid with a U-shaped wall trap
        custom_walls = {(1, 0), (1, 1), (1, 2), (0, 2)}
        self.env = PartiallyObservableGridGame(width=8, height=8, num_food=6, custom_walls=custom_walls)

        if agent_type == "SimpleReflex":
            self.agent = SimpleReflexAgent()
        else:
            self.agent = ModelBasedAgent()

        self.cell_size = 50
        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 12))
        self.label.pack(pady=5)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 11), bg="#000066", fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#64748b" if (x, y) in self.env.walls else "#f1f5f9"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(300, step)
            else:
                self.label.config(text=f"Simulation Finished! Final Score: {self.env.score}")
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    # Toggle between "SimpleReflex" and "ModelBased" to observe agent behaviors
    app = GridGameGUI(root, agent_type="ModelBased")
    root.mainloop()