# Humanoid Internship Challenge: LLM Agent in a Virtual World

This project is a compact, submission-ready LLM-agent harness that places a reasoning agent into a small virtual world and lets it observe, choose actions, and pursue a goal.

## Why this stands out
- A real agent loop: observation → reasoning → action → result
- A clean, minimal interface between the LLM and the environment
- A deterministic fallback planner, so the project still runs without an API key
- A live ASCII map and compact summary mode for impressive demo output
- A simple, testable world model that is easy to extend

## What is included
- A 7x7 text-based grid world with a red cube, a key, a door, and obstacles
- A compact observation format with position, inventory, goal, nearby cells, and available actions
- A small action space for movement, exploration, pickup, and door interaction
- OpenAI integration when `OPENAI_API_KEY` is available, plus a reliable fallback planner
- A polished trace output and a `--quiet` mode for quick demos

## How to run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the main demo:
   ```bash
   python -m app.main
   ```
3. Try a custom goal or a shorter run:
   ```bash
   python -m app.main --goal "red cube" --steps 8
   ```
4. Use the compact summary mode for a short showcase:
   ```bash
   python -m app.main --steps 5 --quiet
   ```

## Design choices
- The world is intentionally simple so the LLM can reason over a compact observation string without extra complexity.
- The action vocabulary is small and explicit, which keeps the harness reliable and easy to debug.
- The fallback planner ensures the system remains runnable in fresh environments.

## Example output
A typical run prints:
- the current observation,
- the ASCII world map,
- the chosen action,
- the action result,
- and a final success/failure summary.

## Verification
Verified locally with:
```bash
C:\Program Files\Python313\python.exe -m pytest -q
C:\Program Files\Python313\python.exe -m app.main --steps 5
```

## Submission note
This project is ready to submit as the challenge solution: it includes a working harness, runnable instructions, and a verified demo path.
