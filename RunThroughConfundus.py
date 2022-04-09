from U2022912F_Driver import World

"""
This file shows that the agent loses memory after walking through the portal
"""

if __name__ == "__main__":
    w = World(portal_positions=[(4, 1)], agent_original_position=(1,1), agent_original_orientation="east")
    w.display_initial_world()

    for i in range(3):
        w.update_agent("moveforward")
        w.display_relative_world()

        safe_positions = set([(a['X'], a['Y']) for a in list(w.db.query("safe(X,Y)"))])
        print("Safe positions", safe_positions)

        relative_position = list(w.db.query("position(X,Y,Z)"))[0]
        relative_position = (relative_position["X"], relative_position["Y"], relative_position["Z"])

        actual_position = (*w.agent.position, w.agent.orientation)
        print("Relative position:", relative_position, "Actual position:", actual_position)
        # input()