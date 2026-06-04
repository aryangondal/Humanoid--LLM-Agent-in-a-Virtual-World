from __future__ import annotations

import json
import os
from collections import deque
from typing import Dict, Generator, List, Tuple

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - dependency may be unavailable in some envs
    OpenAI = None


def fallback_plan(observation: str, goal: str) -> str:
    # Lightweight planner used when the API key is not set or a call fails.
    """Deterministic fallback planner that navigates toward the target cube.

    This keeps the project runnable even when no API key is available.
    """
    import re

    # Read the agent's current position from the observation text.
    match = re.search(r"Position:\s*\((\d+),\s*(\d+)\)", observation)
    if not match:
        return "look"

    x = int(match.group(1))
    y = int(match.group(2))
    target = (4, 4)
    obstacles = {(2, 2), (3, 3)}

    def neighbors(position: Tuple[int, int]) -> Generator[Tuple[int, int], None, None]:
        cx, cy = position
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < 7 and 0 <= ny < 7 and (nx, ny) not in obstacles:
                yield (nx, ny)

    queue = deque([(x, y)])
    parents = {(x, y): None}
    while queue:
        current = queue.popleft()
        if current == target:
            break
        for next_pos in neighbors(current):
            if next_pos not in parents:
                parents[next_pos] = current
                queue.append(next_pos)

    if target not in parents:
        return "look"

    path = []
    cursor = target
    while parents[cursor] is not None:
        path.append(cursor)
        cursor = parents[cursor]
    path.reverse()

    if not path:
        return "pickup_red cube" if (x, y) == target else "look"

    next_step = path[0]
    dx = next_step[0] - x
    dy = next_step[1] - y

    if dx == 1 and dy == 0:
        return "move_east"
    if dx == -1 and dy == 0:
        return "move_west"
    if dx == 0 and dy == 1:
        return "move_south"
    if dx == 0 and dy == -1:
        return "move_north"

    return "look"


def choose_action(observation: str, goal: str) -> Tuple[str, str]:
    """Ask an LLM for the next action; fall back to the planner when needed.

    The returned tuple contains the chosen action and a short reasoning label.
    """
    # Use the real LLM path when an API key is available; otherwise fall back safely.
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return fallback_plan(observation, goal), "fallback"

    client = OpenAI(api_key=api_key)
    prompt = f"""
You are an agent in a text-based world.
Observation:
{observation}
Goal: {goal}
Choose exactly one action from this action space:
- move_north, move_south, move_east, move_west
- pickup_red cube
- pickup_key
- open_door
- look
- wait
Return JSON with keys 'thought' and 'action'.
"""
    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            temperature=0.2,
        )
        text = response.output_text.strip()
        data = json.loads(text)
        action = str(data.get("action", "look")).strip().lower()
        thought = str(data.get("thought", "used llm reasoning")).strip()
        return action, thought
    except Exception:
        return fallback_plan(observation, goal), "fallback"
