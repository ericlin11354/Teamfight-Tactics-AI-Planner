"""
    File contains data for TFT set 12 units.
    Database uses hashmaps to map unit names, traits, costs, breakpoints, and unique traits
"""

"""
    Maps Trait to a tuple ([breakpoints, unit names])
    Used for calculating a team's "value" and fetching unit traits
"""
traits_breakpoints_units = {
    # Origins
    "Arcana": ([2, 3, 4, 5], ["Ahri", "Hecarim", "Tahm Kench", "Xerath"]),
    "Chrono": ([2, 4, 6], ["Jax", "Zilean", "Vex", "Karma", "Camille"]),
    "Dragon": ([2, 3], ["Nomsy", "Shyvana", "Smolder"]),
    "Eldritch": (
        [3, 5, 7, 10],
        ["Ashe", "Elise", "Nilah", "Syndra", "Mordekaiser", "Nami", "Briar"],
    ),
    "Faerie": (
        [2, 4, 6, 9],
        ["Lillia", "Seraphine", "Tristana", "Katarina", "Kalista", "Rakan", "Milio"],
    ),
    "Frost": (
        [3, 5, 7, 9],
        ["Twitch", "Warwick", "Zilean", "Hwei", "Swain", "Olaf", "Diana"],
    ),
    "Honeymancy": (
        [3, 5, 7],
        ["Blitzcrank", "Ziggs", "Kog'Maw", "Nunu", "Veigar"],
    ),
    "Portal": (
        [3, 6, 8, 10],
        [
            "Jayce",
            "Zoe",
            "Galio",
            "Kassadin",
            "Ezreal",
            "Ryze",
            "Taric",
            "Norra & Yuumi",
        ],
    ),
    "Pyro": ([2, 3, 4, 5], ["Akali", "Shen", "Nasus", "Varus"]),
    "Sugarcraft": ([2, 4, 6], ["Soraka", "Rumble", "Bard", "Jinx", "Gwen"]),
    "Witchcraft": (
        [2, 4, 6, 8],
        ["Poppy", "Zoe", "Cassiopeia", "Neeko", "Fiora", "Morgana"],
    ),
    # Classes
    "Bastion": (
        [2, 4, 6, 8],
        ["Lillia", "Poppy", "Nunu", "Hecarim", "Shen", "Taric", "Diana"],
    ),
    "Blaster": (
        [2, 4, 6],
        ["Rumble", "Tristana", "Ezreal", "Hwei", "Varus", "Smolder"],
    ),
    "Hunter": ([2, 4, 6], ["Nomsy", "Twitch", "Kog'Maw", "Jinx", "Olaf"]),
    "Incantor": ([2, 4], ["Ziggs", "Cassiopeia", "Syndra", "Karma"]),
    "Mage": (
        [3, 5, 7, 9],
        ["Seraphine", "Soraka", "Galio", "Veigar", "Vex", "Nami", "Norra & Yuumi"],
    ),
    "Multistriker": (
        [3, 5, 7, 9],
        ["Ashe", "Jax", "Akali", "Kassadin", "Hecarim", "Kalista", "Camille"],
    ),
    "Preserver": ([2, 3, 4, 5], ["Zilean", "Bard", "Rakan", "Morgana"]),
    "Scholar": ([2, 4, 6], ["Zoe", "Ahri", "Bard", "Ryze", "Milio"]),
    "Shapeshifter": (
        [2, 4, 6, 8],
        ["Elise", "Jayce", "Shyvana", "Neeko", "Swain", "Nasus", "Briar"],
    ),
    "Vanguard": (
        [2, 4, 6],
        ["Blitzcrank", "Warwick", "Galio", "Rumble", "Mordekaiser", "Tahm Kench"],
    ),
    "Warrior": ([2, 4, 6], ["Akali", "Nilah", "Katarina", "Fiora", "Gwen"]),
}

"""
    Maps costs to unit names
"""
costs_units = {
    1: [
        "Jayce",
        "Blitzcrank",
        "Ashe",
        "Elise",
        "Soraka",
        "Nomsy",
        "Lillia",
        "Warwick",
        "Poppy",
        "Seraphine",
        "Jax",
        "Zoe",
        "Twitch",
        "Ziggs",
    ],
    2: [
        "Tristana",
        "Syndra",
        "Nunu",
        "Rumble",
        "Cassiopeia",
        "Galio",
        "Ahri",
        "Shyvana",
        "Zilean",
        "Akali",
        "Kassadin",
        "Nilah",
        "Kog'Maw",
    ],
    3: [
        "Neeko",
        "Mordekaiser",
        "Vex",
        "Wukong",
        "Hecarim",
        "Jinx",
        "Shen",
        "Hwei",
        "Bard",
        "Swain",
        "Veigar",
        "Katarina",
        "Ezreal",
    ],
    4: [
        "Gwen",
        "Karma",
        "Ryze",
        "Nasus",
        "Rakan",
        "Nami",
        "Fiora",
        "Tahm Kench",
        "Varus",
        "Kalista",
        "Olaf",
        "Taric",
    ],
    5: [
        "Briar",
        "Diana",
        "Milio",
        "Camille",
        "Morgana",
        "Norra & Yuumi",
        "Xerath",
        "Smolder",
    ],
}

"""
    Maps unit names to costs
"""
units_costs = {unit: cost for cost, units in costs_units.items() for unit in units}

""" 
    Map unique traits to their respective unit name
    We exclude these traits when computing a team's value
"""
unique_traits = {
    "Druid": "Wukong",
    "Ravenous": "Briar",
    "Ascendant": "Xerath",
    "Bat Queen": "Morgana",
    "Explorer": "Norra & Yuumi",
}


"""
    Unit object holds a unit's name, traits, and cost
"""


class Unit:
    def __init__(self, name, traits, cost):
        self.name = name
        self.traits = traits
        self.cost = cost


"""
    Map unit names to Unit objects
    Dict datatype used to for O(1) search time
    Wukong does not exist in traits_breakpoints_units (i.e. he shares no traits), hence we initialize with him
"""
all_units = {"Wukong": Unit("Wukong", ["Druid"], 3)}

for trait, (breakpoints, units) in traits_breakpoints_units.items():
    for unit in units:
        if unit not in all_units:  # appends unique units
            all_units[unit] = Unit(unit, [trait], units_costs[unit])
        else:  # append remaining traits to existing unit
            all_units[unit].traits.append(trait)

# add unique traits to corresponding units (except Wukong since we already defined him)
for trait, unit in unique_traits.items():
    if unit != "Wukong":
        all_units[unit].traits.append(trait)
