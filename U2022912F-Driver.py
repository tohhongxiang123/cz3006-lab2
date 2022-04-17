from World import World
from time import sleep

if __name__ == "__main__":
    w = World(agent_original_position=(1, 1), agent_original_orientation='north', wumpus_positions=[(1, 4)], coin_positions=[], portal_positions=[(5,1)])
    # w = World(agent_original_position=(3, 4), agent_original_orientation='east', wumpus_positions=[(6,4)], coin_positions=[(8,8), (3,2)], portal_positions=[(5, 3), (1, 7)], wall_positions=[(7,7), (8,7), (4, 4), (2, 2), (2, 3), (3, 3), (4, 3), (4, 2), (7, 4), (3, 5)], world_size=(10,10))
    # w = World(agent_original_position=(2, 2), agent_original_orientation='east', wumpus_positions=[(5, 5)], coin_positions=[(5, 6), (5, 8), (1, 2)], portal_positions=[(4, 8), (4, 1), (2, 4)], wall_positions=[(4, 4), (4, 5), (4, 6), (4, 7), (5, 7), (6, 7), (6, 6), (6, 5), (6, 4), (8, 7), (7, 5)], world_size=(10,10))
    
    print("=== INITIAL WORLD ===")
    w.display_initial_world()

    print("=== RELATIVE WORLD ===")
    w.display_relative_world()

    # input()

    while True:
        next_moves = w.get_next_move()
        for next_move in next_moves:
            w.update_agent(next_move)
            print(next_move)
            w.display_relative_world()
            sleep(0.1)
            # input()