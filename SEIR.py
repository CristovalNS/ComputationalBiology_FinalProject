import math
import random
import pygame
import numpy as np
import imageio
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


# Helper functions
def find_distance(p1, p2):
    x_diff = p1[1] - p2[1]
    y_diff = p1[2] - p2[2]
    return ((x_diff ** 2) + (y_diff ** 2)) ** 0.5


def get_cell(x, y, cell_size):
    return x // cell_size, y // cell_size


def populate_grid(people, cell_size):
    grid = {}
    for p in people:
        cell = get_cell(p[1], p[2], cell_size)
        if cell not in grid:
            grid[cell] = []
        grid[cell].append(p)
    return grid


def step(people, infected, exposed, cell_size, infect_distance, infect_rate, recover_rate, progression_rate
         ):
    new_infected = []
    new_exposed = []
    recover = []
    grid = populate_grid(people, cell_size)

    for i in infected:
        cell = get_cell(i[1], i[2], cell_size)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                neighbor_cell = (cell[0] + dx, cell[1] + dy)
                if neighbor_cell in grid:
                    for p in grid[neighbor_cell]:
                        if p[0] == 'S' and find_distance(i, p) < infect_distance:
                            if random.random() < infect_rate:
                                p[0] = 'E'
                                new_exposed.append(p)

        # Determine if the infected person recovers or dies
        if random.random() < recover_rate:
            recover.append(i)
            i[0] = 'R'

    # Progress exposed individuals to infected
    for e in exposed:
        if random.random() < progression_rate:
            e[0] = 'I'
            new_infected.append(e)
        else:
            new_exposed.append(e)

    # Update lists
    for r in recover:
        infected.remove(r)

    return infected + new_infected, new_exposed, len(recover)


def move_all(people, max_move, width, height):
    for p in people:
        if p[0] != 'D':
            p[1] += random.randint(max_move * -1, max_move)
            if p[1] < 1:
                p[1] = 1
            if p[1] > width - 1:
                p[1] = width - 1
            p[2] += random.randint(max_move * -1, max_move)
            if p[2] < 1:
                p[2] = 1
            if p[2] > height - 1:
                p[2] = height - 1


# SEIR graph animation
def seir_model(y, t, beta, sigma, gamma, radius, dimensions):
    S, E, I, R = y
    N = S + E + I + R

    # probability any given person is within infection radius
    circle_probability = (math.pi * float(radius) * float(radius)) / float(dimensions[0] * dimensions[1])
    # recalculated beta based on the amount of infected people and probability
    accurate_beta = (1 - ((1 - beta) ** (circle_probability * I)))

    dS = -accurate_beta * S
    dE = accurate_beta * S - sigma * E
    dI = sigma * E - gamma * I
    dR = gamma * I

    return [dS, dE, dI, dR]


def create_SEIR_simulation(width=500, height=500, number_of_people=5000, num_infected=50, infect_rate=0.8,
                            recover_rate=0.1, progression_rate=0.2, infect_distance=10, max_move=5, max_days=100,
                            simulation_name="simulation1"):
    # Initialize people
    people = []
    infected = []
    exposed = []

    for _ in range(number_of_people):
        state = "I" if random.random() < num_infected / number_of_people else "S"
        person = [state, random.randint(0, width), random.randint(0, height)]
        if state == "I":
            infected.append(person)
        elif state == "E":
            exposed.append(person)
        people.append(person)

    # Initialize pygame for simulation
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    screen.fill((0, 0, 0))  # Black background

    # Simulation loop
    frames = []
    step_count = 1
    simulated_S, simulated_E, simulated_I, simulated_R = [number_of_people - num_infected], [0], [
        num_infected], [0]

    while (len(infected) > 0 or len(exposed) > 0) and step_count <= max_days:
        step_count += 1
        screen.fill((0, 0, 0))
        infected, exposed, recovered_amount = step(people, infected, exposed, infect_distance, infect_distance, infect_rate, recover_rate, progression_rate)
        move_all(people, max_move, width, height)
        for p in people:
            color = (
                (255, 0, 0) if p[0] == "I" else
                (0, 0, 255) if p[0] == "S" else
                (255, 20, 147) if p[0] == "E" else
                (0, 255, 0) if p[0] == "R" else
                (255, 255, 255)
            )
            pygame.draw.circle(screen, color, [p[1], p[2]], 1)

        pygame.display.flip()
        frame_array = pygame.surfarray.array3d(screen)
        frames.append(np.transpose(frame_array, (1, 0, 2)))

        pygame.image.save(screen, "frames/" + simulation_name + '_SEIR.png')

        simulated_R.append(simulated_R[-1] + recovered_amount)
        simulated_I.append(len(infected))
        simulated_E.append(len(exposed))
        simulated_S.append(number_of_people - simulated_I[-1] - simulated_E[-1] - simulated_R[-1])

    pygame.quit()

    days = step_count

    # Save simulation GIF
    simulation_gif_path = f"simulations/{simulation_name}_SEIR.gif"
    imageio.mimsave(simulation_gif_path, frames, fps=10)

    # Solve SEIR model
    t = np.linspace(0, days, days)
    initial_conditions = [simulated_S[0], simulated_E[0], simulated_I[0], simulated_R[0]]
    solution = odeint(seir_model, initial_conditions, t, args=(
        infect_rate, progression_rate, recover_rate, infect_distance, (width, height)))
    S_model, E_model, I_model, R_model = solution.T

    # Animate SEIR graph
    fig, ax = plt.subplots(figsize=(6, 4))
    lines = {
        'S': ax.plot([], [], label='Susceptible', color='blue', linestyle='--')[0],
        'E': ax.plot([], [], label='Exposed', color='purple', linestyle='--')[0],
        'I': ax.plot([], [], label='Infected', color='red', linestyle='--')[0],
        'R': ax.plot([], [], label='Recovered', color='green', linestyle='--')[0],
        'S_sim': ax.plot([], [], label='Susceptible (simulated)', color='blue')[0],
        'E_sim': ax.plot([], [], label='Exposed (simulated)', color='purple')[0],
        'I_sim': ax.plot([], [], label='Infected (simulated)', color='red')[0],
        'R_sim': ax.plot([], [], label='Recovered (simulated)', color='green')[0],
    }
    ax.set_xlim(0, days)
    ax.set_ylim(0, number_of_people)
    ax.set_title("SEIR Model Graph Animation")
    ax.set_xlabel("Days")
    ax.set_ylabel("Population")
    ax.legend()

    def update(frame):
        for key, data in zip(lines.keys(),
                             [S_model, E_model, I_model, R_model, simulated_S, simulated_E, simulated_I,
                              simulated_R]):
            lines[key].set_data(t[:frame], data[:frame])
        return lines.values()

    ani = FuncAnimation(fig, update, frames=len(t), blit=True)
    graph_gif_path = f"graphs/{simulation_name}_SEIR_graph.gif"
    ani.save(graph_gif_path, writer=PillowWriter(fps=10))

    print(f"Simulation saved as: {simulation_gif_path}")
    print(f"Graph animation saved as: {graph_gif_path}")


