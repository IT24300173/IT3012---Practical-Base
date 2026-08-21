from collections import deque
import heapq
import math


class SearchAgent:
    """
    Goal-Based / Planning Agent.

    Supports:
        BFS   - Breadth-First Search
        DFS   - Depth-First Search
        UCS   - Uniform-Cost Search
        AStar - A* Search
    """

    def __init__(self):
        # Stores the offline plan
        self.plan = []

        # Default algorithm
        self.active_algo = "BFS"

    # ==========================================================
    # GET VALID NEIGHBOURS
    # ==========================================================

    def get_neighbors(self, state, grid_size, walls):

        width, height = grid_size
        x, y = state

        possible_moves = [
            ("Up", (x, y + 1)),
            ("Down", (x, y - 1)),
            ("Left", (x - 1, y)),
            ("Right", (x + 1, y))
        ]

        neighbors = []

        for action, next_state in possible_moves:

            nx, ny = next_state

            # Check boundaries
            if nx < 0 or nx >= width:
                continue

            if ny < 0 or ny >= height:
                continue

            # Check walls
            if next_state in walls:
                continue

            neighbors.append((action, next_state))

        return neighbors

    # ==========================================================
    # BFS
    # ==========================================================

    def bfs_search(self, start, goal, grid_size, walls):

        frontier = deque()
        frontier.append((start, []))

        reached = {start}

        while frontier:

            current, path = frontier.popleft()

            # Goal test
            if current == goal:
                return path

            # Expand node
            for action, next_state in self.get_neighbors(
                current,
                grid_size,
                walls
            ):

                if next_state not in reached:

                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append(
                        (next_state, new_path)
                    )

        return []

    # ==========================================================
    # DFS
    # ==========================================================

    def dfs_search(self, start, goal, grid_size, walls):

        frontier = []
        frontier.append((start, []))

        reached = {start}

        while frontier:

            current, path = frontier.pop()

            # Goal test
            if current == goal:
                return path

            # Expand node
            for action, next_state in self.get_neighbors(
                current,
                grid_size,
                walls
            ):

                if next_state not in reached:

                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append(
                        (next_state, new_path)
                    )

        return []

    # ==========================================================
    # UCS
    # ==========================================================

    def ucs_search(self, start, goal, grid_size, walls):

        frontier = []

        counter = 0

        heapq.heappush(
            frontier,
            (0, counter, start, [])
        )

        # Store cheapest known cost
        reached = {
            start: 0
        }

        while frontier:

            cost, _, current, path = heapq.heappop(
                frontier
            )

            # Goal test
            if current == goal:
                return path

            # Ignore outdated paths
            if cost > reached.get(current, float("inf")):
                continue

            # Expand node
            for action, next_state in self.get_neighbors(
                current,
                grid_size,
                walls
            ):

                new_cost = cost + 1

                if (
                    next_state not in reached
                    or new_cost < reached[next_state]
                ):

                    reached[next_state] = new_cost

                    counter += 1

                    new_path = path + [action]

                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            counter,
                            next_state,
                            new_path
                        )
                    )

        return []

    # ==========================================================
    # MANHATTAN DISTANCE
    # ==========================================================

    def manhattan_distance(self, pos, goal):

        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    # ==========================================================
    # EUCLIDEAN DISTANCE
    # ==========================================================

    def euclidean_distance(self, pos, goal):

        return math.sqrt(
            (pos[0] - goal[0]) ** 2
            +
            (pos[1] - goal[1]) ** 2
        )

    # ==========================================================
    # A* SEARCH
    # ==========================================================

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type="manhattan"
    ):

        # Priority queue
        frontier = []

        # Counter prevents comparison problems
        counter = 0

        # Select heuristic
        if heuristic_type == "euclidean":

            start_h = self.euclidean_distance(
                start_pos,
                goal_pos
            )

        else:

            start_h = self.manhattan_distance(
                start_pos,
                goal_pos
            )

        # Starting node:
        # (f_cost, g_cost, counter, current_pos, path_taken)
        heapq.heappush(
            frontier,
            (
                start_h,
                0,
                counter,
                start_pos,
                []
            )
        )

        # Store best known g cost
        reached_states = {
            start_pos: 0
        }

        while frontier:

            (
                f_cost,
                g_cost,
                _,
                current_pos,
                path_taken
            ) = heapq.heappop(frontier)

            # Goal test
            if current_pos == goal_pos:
                return path_taken

            # Ignore outdated path
            if g_cost > reached_states.get(
                current_pos,
                float("inf")
            ):
                continue

            # Expand neighbors
            for action, neighbor in self.get_neighbors(
                current_pos,
                grid_size,
                walls
            ):

                # Calculate new g(n)
                g_new = g_cost + 1

                # Only continue if new path is better
                if (
                    neighbor not in reached_states
                    or g_new < reached_states[neighbor]
                ):

                    reached_states[neighbor] = g_new

                    # Calculate h(n)
                    if heuristic_type == "euclidean":

                        h_new = self.euclidean_distance(
                            neighbor,
                            goal_pos
                        )

                    else:

                        h_new = self.manhattan_distance(
                            neighbor,
                            goal_pos
                        )

                    # Calculate f(n) = g(n) + h(n)
                    f_new = g_new + h_new

                    counter += 1

                    new_path = path_taken + [action]

                    heapq.heappush(
                        frontier,
                        (
                            f_new,
                            g_new,
                            counter,
                            neighbor,
                            new_path
                        )
                    )

        # No path found
        return []

    # ==========================================================
    # FIND CLOSEST FOOD
    # ==========================================================

    def find_closest_food(
        self,
        start,
        food_positions,
        grid_size,
        walls
    ):

        closest_food = None
        shortest_path = None

        for food in food_positions:

            # Already standing on food
            if start == food:
                return food

            # Use BFS to check actual reachable distance
            path = self.bfs_search(
                start,
                food,
                grid_size,
                walls
            )

            # Ignore unreachable food
            if not path:
                continue

            # Find shortest path
            if (
                shortest_path is None
                or len(path) < len(shortest_path)
            ):

                shortest_path = path
                closest_food = food

        return closest_food

    # ==========================================================
    # SELECT SEARCH ALGORITHM
    # ==========================================================

    def search(self, start, goal, grid_size, walls):

        if self.active_algo == "BFS":

            return self.bfs_search(
                start,
                goal,
                grid_size,
                walls
            )

        elif self.active_algo == "DFS":

            return self.dfs_search(
                start,
                goal,
                grid_size,
                walls
            )

        elif self.active_algo == "UCS":

            return self.ucs_search(
                start,
                goal,
                grid_size,
                walls
            )

        elif self.active_algo == "AStar":

            return self.astar_search(
                start,
                goal,
                walls,
                grid_size,
                heuristic_type="manhattan"
            )

        else:

            print(
                "Invalid algorithm:",
                self.active_algo
            )

            return []

    # ==========================================================
    # SENSE AND ACT
    # ==========================================================

    def sense_and_act(self, percept):

        # Create a new plan if there is no plan
        if not self.plan:

            # Current position
            current_position = tuple(
                percept["position"]
            )

            # Grid information
            grid_size = tuple(
                percept["grid_size"]
            )

            # Walls
            walls = set(
                tuple(wall)
                for wall in percept["walls"]
            )

            # All remaining food
            all_food = [
                tuple(food)
                for food in percept["all_food"]
            ]

            # If no food remains
            if not all_food:
                return "Stay"

            # Find closest food
            closest_food = self.find_closest_food(
                current_position,
                all_food,
                grid_size,
                walls
            )

            # Find path using selected algorithm
            if closest_food is not None:

                self.plan = self.search(
                    current_position,
                    closest_food,
                    grid_size,
                    walls
                )

        # Execute first action
        if self.plan:

            return self.plan.pop(0)

        # No path found
        return "Stay"


# ==========================================================
# HEURISTIC TEST
# ==========================================================

if __name__ == "__main__":

    agent = SearchAgent()

    start = (0, 0)
    goal = (3, 4)

    print(
        "Manhattan Distance:",
        agent.manhattan_distance(start, goal)
    )

    print(
        "Euclidean Distance:",
        agent.euclidean_distance(start, goal)
    )