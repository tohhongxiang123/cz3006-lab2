from World import World

"""
Agent in a full world, able to pickup multiple coins
"""

if __name__ == "__main__":
    w = World(agent_original_position=(3, 4), agent_original_orientation='east', wumpus_positions=[(6,4)], coin_positions=[(8,8), (3,2)], portal_positions=[(5, 3), (1, 7)], wall_positions=[(7,7), (8,7), (4, 4), (2, 2), (2, 3), (3, 3), (4, 3), (4, 2), (7, 4)], world_size=(10,10))
    
    print("=== INITIAL WORLD ===")
    w.display_initial_world()

    print("=== RELATIVE WORLD ===")
    w.display_relative_world()

    while True:
        next_move = w.get_next_move()[0]
        w.update_agent(next_move)
        print(next_move)
        w.display_relative_world()