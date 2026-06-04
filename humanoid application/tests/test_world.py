from app.world import World


def test_move_and_pickup():
    # Basic movement and pickup behavior should work in the simulated world.
    world = World()
    world.reset()

    ok, message = world.step("move_east")
    assert ok is True
    assert world.agent_position == (1, 0)
    assert "Moved east" in message

    world.agent_position = world.items["red cube"].position
    ok, message = world.step("pickup_red cube")
    assert ok is True
    assert "red cube" in world.inventory


def test_goal_completed_after_pickup():
    # Reaching the target object should mark the goal as complete.
    world = World()
    world.reset()
    world.agent_position = world.items["red cube"].position
    world.inventory.append("red cube")
    assert world.goal_completed() is True
