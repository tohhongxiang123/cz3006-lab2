from World import World

if __name__ == "__main__":
    w = World(agent_original_position=(1, 1), agent_original_orientation='east', wumpus_positions=[], coin_positions=[(4, 1)], portal_positions=[], world_size=(7, 3))
    print("=== INITIAL WORLD ===")
    w.display_initial_world()

    print("=== RELATIVE WORLD ===")
    print(w.world[w.agent.position[1]][w.agent.position[0]].format_senses_to_print())
    w.display_relative_world()

    while True:
        next_moves = w.get_next_move()
        for next_move in next_moves:
            w.update_agent(next_move)
            print(next_move)
            print(w.world[w.agent.position[1]][w.agent.position[0]].format_senses_to_print())
            w.display_relative_world()
            input()