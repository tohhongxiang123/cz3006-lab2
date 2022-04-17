from World import World

if __name__ == "__main__":
    w = World(agent_original_position=(3, 4), agent_original_orientation='east', wumpus_positions=[(6,4)], coin_positions=[(8,8)], portal_positions=[(5, 3), (1, 7), (6, 8)], world_size=(10,10))
    w.display_initial_world()
    w.display_relative_world()
    for i in range(6):
        w.update_agent("moveforward")
        print("moveforward")
        w.display_relative_world()
        # input()