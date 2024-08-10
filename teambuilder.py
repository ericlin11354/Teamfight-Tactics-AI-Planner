"""
  Implements genetic algorithm to generate the optimal TFT team comp
  The idea is that we randomly generate multiple team comps, cross-over and mutate select units, and grade the team's value based on the number
  of trait breakpoints reached. "Good" teams are filtered to be modified in the next generation.
"""

import collections
import random
import time

from database import all_units, traits_breakpoints_units, unique_traits, Unit

"""
    Global Variables
"""
# e.g. "0.1" means 1 in 10 teams are mutated
MUTATION_RATE = 0.1
# factor by which the population is selected for the next generation
SELECTION_FACTOR = 2


def calculate_points(team: list[Unit], bonus_traits: dict[str, int]) -> int:
    """
    Determines and returns the value of a team
    bonus_traits is structured like {"Frost" : 3, ...}
    """
    trait_counter = collections.defaultdict(int)  # avoid KeyError

    # count traits in team
    for unit in team:
        for trait in unit.traits:
            if trait not in unique_traits:  # ignore unique traits
                trait_counter[trait] += 1

    # count bonus traits
    if bonus_traits:
        for trait, count in bonus_traits.items():
            if trait not in unique_traits:  # ignore unique traits
                trait_counter[trait] += 1

    # point scoring algorithm: add a point for every breakpoint reached in all traits
    points = 0
    for trait, count in trait_counter.items():
        if trait in traits_breakpoints_units:
            for bp in traits_breakpoints_units[trait][0]:
                if count >= bp:
                    points += 1
                else:
                    break

    return points


def generate_random_team(
    included_units: list[str], bd: bool, team_size: int
) -> list[Unit]:
    """
    Randomly generate and return a candidate team
    included_units is a list of unit names
    bd - True if "Built Different II" is selected as an augment. Otherwise False
    """
    # if Built Different, exclude units with unique traits (since they don't proc the buff)
    available_units = (
        all_units.copy()
        if not bd
        else {
            unit: all_units[unit]
            for unit in all_units
            if not any(
                trait in all_units[unit].traits for trait in unique_traits
            )  # iterate units and check that none of their traits match the dictionary of unique traits
        }
    )

    # generate team
    team = []

    # included units are part of the team
    if included_units:
        for unit in included_units:
            if unit in available_units:
                team.append(available_units[unit])
                del available_units[unit]  # avoid adding duplicate units

    # fill in the remaining team randomly
    while len(team) < team_size:
        new_unit = random.choice(list(available_units.keys()))
        team.append(available_units[new_unit])
        del available_units[new_unit]
    return team


def crossover(team1: list[Unit], team2: list[Unit]) -> list[Unit]:
    """
    Pick from two teams pseudo-randomly to return a "superior" team
    """
    # use bitwise operators to identify the common units
    set1, set2 = set(team1), set(team2)
    common = set1 & set2
    only1, only2 = list(set1 - common), list(set2 - common)  # we choose from these sets
    new_team = list(common)

    # add units
    while len(new_team) < len(
        team1
    ):  # we favour team1 for no particular reason (recall team1 was randomly selected)
        if len(only1) > 0 and (len(only2) == 0 or random.random() < 0.5):
            new_unit = only1.pop(random.randrange(len(only1)))
            new_team.append(new_unit)
        elif len(only2) > 0:
            new_unit = only2.pop(random.randrange(len(only2)))
            new_team.append(new_unit)
    return new_team


def mutate(team: list[Unit], included_units: list[str], bd: bool = False) -> list[Unit]:
    """
    Add genetic diversity to team comps by randomly replacing a unit
    """
    # remove included units before mutating randomly
    if included_units:
        for unit in team.copy():  # copy so we don't iterate while updating team
            if unit.name in included_units:
                team.remove(unit)

    if random.random() < MUTATION_RATE:
        # get units that are not already on the team and not included_units to avoid duplicates
        other_units = {
            unit: all_units[unit]
            for unit in all_units
            if all_units[unit] not in team
            and (not included_units or unit not in included_units)
        }
        # exclude units with unique traits
        if bd:
            other_units = {
                unit: other_units[unit]
                for unit in other_units
                if not any(trait in other_units[unit].traits for trait in unique_traits)
            }
        # randomly replace a unit
        team[random.randrange(len(team))] = random.choice(
            list(other_units.values())
        )  # randomly replace a unit with another one to encourage diversity

    # add included units back
    if included_units:
        for name in included_units:
            new_unit = all_units[name]
            if new_unit not in team:
                team.append(new_unit)

    return team


def find_team(
    generations: int = 1000,
    population_size: int = 500,
    bonus_traits: dict[str, int] = None,
    included_units: list[str] = None,
    bd: bool = False,
    team_size: int = 10,
) -> tuple[list[Unit], int]:
    """
    Generates the "best" team comp using genetic algorithm and scoring based on number of trait breakpoints
    """
    print("\n Generating... \n")
    start_time = time.time()
    # generate random teams
    try:
        population = [
            generate_random_team(included_units, bd, team_size)
            for _ in range(generations)
        ]
    except ValueError as e:
        print(f"Error occured during team generation: {e}")
        return
    for _ in range(generations):
        # get the "best" teams and send them to the subsequent generation
        # if Build Different, we want the least number of traits (and exlude unique traits)
        population.sort(
            key=lambda team: calculate_points(team, bonus_traits), reverse=not bd
        )
        population = population[
            : population_size // SELECTION_FACTOR
        ]  # filter population for the subsequent generation
        # fill up the new population by cross-over'ing and mutating the current "best" teams
        while len(population) < population_size:
            team1, team2 = random.sample(population, 2)
            new_team = crossover(team1, team2)
            population.append(mutate(new_team, included_units, bd))

    # return best team sorted by points
    best_team = sorted(population[0], key=lambda unit: unit.cost)
    best_points = calculate_points(best_team, bonus_traits)
    end_time = time.time()

    print(
        f"Best team: {[unit.name for unit in sorted(best_team, key=lambda unit : unit.cost)]}, points: {best_points}"
    )
    print(f"\n Runtime: {end_time - start_time} seconds\n")

    return best_team, best_points


# for testing
if __name__ == "__main__":
    # find_team()
    find_team(
        included_units=[
            "Kog'Maw",
            "Jinx",
            "Nunu",
            "Olaf",
            "Veigar",
            "Twitch",
            "Ziggs",
            "Blitzcrank",
        ],
        team_size=11,
    )
