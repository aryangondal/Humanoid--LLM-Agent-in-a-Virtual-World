from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


Position = Tuple[int, int]


@dataclass
class Item:
    """A simple object that can exist in the world and be observed by the agent."""

    name: str
    position: Position
    kind: str = "item"


@dataclass
class World:
    """A small text-based world for an LLM agent to navigate and act in."""
    width: int = 7
    height: int = 7
    agent_position: Position = (0, 0)
    inventory: List[str] = field(default_factory=list)
    items: Dict[str, Item] = field(default_factory=dict)
    goal: str = "red cube"
    steps_taken: int = 0

    def __post_init__(self) -> None:
        # Seed the world with a few simple interactive objects.
        self.items = {
            "red cube": Item("red cube", (4, 4), "collectible"),
            "key": Item("key", (2, 1), "key"),
            "door": Item("door", (5, 5), "door"),
        }

    def reset(self) -> None:
        self.agent_position = (0, 0)
        self.inventory = []
        self.steps_taken = 0

    def in_bounds(self, position: Position) -> bool:
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def is_blocked(self, position: Position) -> bool:
        x, y = position
        return (x == 2 and y == 2) or (x == 3 and y == 3)  # simple obstacles

    def nearby_cells(self) -> List[str]:
        x, y = self.agent_position
        cells = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if dx == 0 and dy == 0:
                    continue
                if not self.in_bounds((nx, ny)):
                    cells.append(f"({nx},{ny}) out-of-bounds")
                    continue
                if self.is_blocked((nx, ny)):
                    cells.append(f"({nx},{ny}) wall")
                    continue
                labels = []
                for name, item in self.items.items():
                    if item.position == (nx, ny):
                        labels.append(item.name)
                if labels:
                    cells.append(f"({nx},{ny}) {', '.join(labels)}")
                else:
                    cells.append(f"({nx},{ny}) empty")
        return cells

    def available_actions(self) -> List[str]:
        """Return the action vocabulary the agent can choose from."""
        return ["move_north", "move_south", "move_east", "move_west", "pickup_red cube", "pickup_key", "open_door", "look", "wait"]

    def observe(self) -> str:
        lines = [
            f"Position: ({self.agent_position[0]}, {self.agent_position[1]})",
            f"Inventory: {', '.join(self.inventory) if self.inventory else 'empty'}",
            f"Goal: find the {self.goal}",
            "Available actions: " + ", ".join(self.available_actions()),
            "Nearby:",
        ]
        lines.extend(f"  - {cell}" for cell in self.nearby_cells())
        return "\n".join(lines)

    def step(self, action: str) -> Tuple[bool, str]:
        # Normalize the action so the world can interpret both LLM and manual inputs.
        action = action.strip().lower()
        x, y = self.agent_position

        if action.startswith("move_"):
            direction = action.split("_", 1)[1]
            dx, dy = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}.get(direction, (0, 0))
            new_position = (x + dx, y + dy)
            if not self.in_bounds(new_position) or self.is_blocked(new_position):
                return False, "Blocked: cannot move there."
            self.agent_position = new_position
            self.steps_taken += 1
            return True, f"Moved {direction}."

        if action == "pickup_red cube":
            if self.agent_position == self.items["red cube"].position:
                self.inventory.append("red cube")
                return True, "Picked up the red cube."
            return False, "No red cube here."

        if action == "pickup_key":
            if self.agent_position == self.items["key"].position:
                self.inventory.append("key")
                return True, "Picked up the key."
            return False, "No key here."

        if action == "open_door":
            if self.agent_position == self.items["door"].position and "key" in self.inventory:
                return True, "Door opened with the key."
            return False, "Need the key to open the door."

        if action == "look":
            return True, self.observe()

        if action == "wait":
            self.steps_taken += 1
            return True, "Waited."

        return False, f"Unknown action: {action}"

    def goal_completed(self) -> bool:
        return self.agent_position == self.items[self.goal].position or "red cube" in self.inventory

    def render_map(self) -> str:
        """Render a simple ASCII map for a polished demo view."""
        rows = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if (x, y) == self.agent_position:
                    row.append('A')
                elif (x, y) == self.items['red cube'].position:
                    row.append('C')
                elif (x, y) == self.items['key'].position:
                    row.append('K')
                elif (x, y) == self.items['door'].position:
                    row.append('D')
                elif self.is_blocked((x, y)):
                    row.append('#')
                else:
                    row.append('.')
            rows.append(' '.join(row))
        return '\n'.join(rows)
