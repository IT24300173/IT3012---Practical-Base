from collections import deque
import heapq


class SearchAgent:
    """
    Goal-Based / Planning Agent for Practical 03.

    Supports:
        BFS - Breadth-First Search
        DFS - Depth-First Search
        UCS - Uniform-Cost Search
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
        """
        Return valid neighbouring states.

        Each neighbour contains:
            action
            next_state
        """

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

            # Check grid boundaries
            if nx < 0 or nx >= width:
                continue

            if ny < 0 or ny >= height:
                continue

            # Check walls
            if next_state in walls:
                continue

            neighbors.append(
                (action, next_state)
            )

        return neighbors

    # ==========================================================
    # BFS
    # ==========================================================

    def bfs_search(self, start, goal, grid_size, walls):
        """
        Breadth-First Search.

        Frontier:
            FIFO queue using deque.popleft()

        BFS explores the shallowest nodes first.
        """

        frontier = deque()

        # Store:
        # (current_state, path)
        frontier.append(
            (start, [])
        )

        # Reached set
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

        # No path found
        return []

    # ==========================================================
    # DFS
    # ==========================================================

    def dfs_search(self, start, goal, grid_size, walls):
        """
        Depth-First Search.

        Frontier:
            LIFO stack using list.pop()

        DFS explores the deepest nodes first.
        """

        frontier = []

        # Store:
        # (current_state, path)
        frontier.append(
            (start, [])
        )

        # Reached set
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

        # No path found
        return []

    # ==========================================================
    # UCS
    # ==========================================================

    def ucs_search(self, start, goal, grid_size, walls):
        """
        Uniform-Cost Search.

        Frontier:
            Priority queue using heapq

        Priority:
            Total path cost g(n)

        Every movement currently has cost 1.
        """

        frontier = []

        counter = 0

        # Store:
        # (cost, counter, state, path)
        heapq.heappush(
            frontier,
            (0, counter, start, [])
        )

        # Reached dictionary stores the cheapest
        # known cost for each state.
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

            # Expand node
            for action, next_state in self.get_neighbors(
                current,
                grid_size,
                walls
            ):

                new_cost = cost + 1

                # If state has not been reached
                # OR this path is cheaper
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
        """
        Find the closest reachable food pellet.

        BFS is used here to determine which food has
        the shortest distance from the current position.
        """

        closest_food = None
        shortest_path = None

        for food in food_positions:

            # If already standing on food
            if start == food:
                return food

            path = self.bfs_search(
                start,
                food,
                grid_size,
                walls
            )

            # Ignore unreachable food
            if not path:
                continue

            # Check if this is the shortest path
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
        """
        Run the search algorithm selected by active_algo.
        """

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
        """
        If there is no current plan:
            1. Read the global environment information.
            2. Find the closest food.
            3. Run the selected search algorithm.
            4. Store the resulting action sequence.

        Then execute one action from the plan.
        """

        # ------------------------------------------------------
        # Create a new plan if current plan is empty
        # ------------------------------------------------------

        if not self.plan:

            # Current agent position
            current_position = tuple(
                percept["position"]
            )

            # Global environment information
            grid_size = tuple(
                percept["grid_size"]
            )

            walls = set(
                tuple(wall)
                for wall in percept["walls"]
            )

            all_food = [
                tuple(food)
                for food in percept["all_food"]
            ]

            # --------------------------------------------------
            # Find closest food
            # --------------------------------------------------

            closest_food = self.find_closest_food(
                current_position,
                all_food,
                grid_size,
                walls
            )

            # --------------------------------------------------
            # Search for path to food
            # --------------------------------------------------

            if closest_food is not None:

                self.plan = self.search(
                    current_position,
                    closest_food,
                    grid_size,
                    walls
                )

        # ------------------------------------------------------
        # Execute first action in plan
        # ------------------------------------------------------

        if self.plan:

            return self.plan.pop(0)

        # ------------------------------------------------------
        # No path available
        # ------------------------------------------------------

        return "Stay"