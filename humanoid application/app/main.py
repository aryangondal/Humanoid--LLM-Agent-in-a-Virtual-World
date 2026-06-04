from __future__ import annotations

import argparse

from app.llm import choose_action
from app.world import World


def run_episode(max_steps: int = 20, goal: str = "red cube", verbose: bool = True) -> str:
    """Run one episode and produce a polished trace for the demo.

    This is the main loop used to show how the agent observes, reasons, and acts.
    """
    world = World(goal=goal)
    world.reset()
    goal = world.goal
    log_lines = ["=== LLM Agent in a Virtual World ===", f"Goal: find the {goal}"]

    for step_idx in range(max_steps):
        # Observe the current state of the world before choosing the next action.
        observation = world.observe()
        action, thought = choose_action(observation, goal)
        log_lines.append(f"\nStep {step_idx + 1}")
        log_lines.append(f"Observation:\n{observation}")
        log_lines.append("ASCII map:")
        log_lines.append(world.render_map())
        log_lines.append(f"LLM thought: {thought}")
        log_lines.append(f"Chosen action: {action}")

        # Execute the action and record the result for the trace.
        success, message = world.step(action)
        log_lines.append(f"Result: {message} (success={success})")

        if world.goal_completed():
            log_lines.append("✅ Goal completed.")
            log_lines.append("Mission summary: the agent reached its objective in the virtual world.")
            break

    if not world.goal_completed():
        log_lines.append("⚠️ Goal not reached within the step limit.")

    log_lines.append(f"Final position: {world.agent_position}")
    log_lines.append(f"Inventory: {world.inventory}")
    log_lines.append(f"Steps taken: {world.steps_taken}")
    return "\n".join(log_lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the virtual-world LLM agent challenge")
    parser.add_argument("--steps", type=int, default=20, help="Maximum number of simulation steps")
    parser.add_argument("--goal", type=str, default="red cube", help="Goal to chase in the world")
    parser.add_argument("--quiet", action="store_true", help="Hide the verbose trace and print only a compact summary")
    args = parser.parse_args()

    trace = run_episode(max_steps=args.steps, goal=args.goal)
    if args.quiet:
        compact = [line for line in trace.splitlines() if "Step " in line or "✅" in line or "⚠️" in line or "Final position" in line or "Inventory" in line or "Steps taken" in line]
        print("\n".join(compact))
    else:
        print(trace)


if __name__ == "__main__":
    main()
