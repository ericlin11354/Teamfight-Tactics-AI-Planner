import collections
import customtkinter
from database import all_units, traits_breakpoints_units, unique_traits
from PIL import Image
from teambuilder import find_team
import sys
import os

# themeing
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

""" 
    Global variables
"""
DEFAULT_TEAM_SIZE = 10
team_list = []  # current TFT comp (Unit instances)
bonus_traits = collections.defaultdict(int)  # emblems, augments, etc.
included_units = []  # core units
team_size = DEFAULT_TEAM_SIZE  # default team comp max size
bd_flag = False  # True if Built Different II. Otherwise False
# used for mapping unit cost to unit color
cost_to_hex = {1: "#7f817e", 2: "#13c412", 3: "#4180c8", 4: "#bd10c8", 5: "#b79b1e"}
CHAMPION_COL_LIMIT = 7  # number of champions in a UI row
"""
    Functions
"""


def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def show_trait_count(trait: str, count: int) -> str:
    """
    Displays the next largest breakpoint if it exists.
    e.g. Frost "2/3" or Frost "4/5"
    """
    if trait in unique_traits:
        return f"{count}"  # format unique traits
    else:
        # get next largest breakpoint. Otherwise, get the largest breakpoint
        return f"{count} / {next((bp for bp in traits_breakpoints_units[trait][0] if count // bp == 0), traits_breakpoints_units[trait][0][-1])}"


def generate_team():
    """
    Define team_list by calling find_team
    """
    global team_list
    new_team, _ = find_team(
        bonus_traits=bonus_traits,
        included_units=included_units,
        team_size=team_size,
        bd=bd_flag,
    )
    team_list = new_team
    # update team and traits display
    draw_team()
    draw_traits()


def add_bonus_trait(trait: str):
    bonus_traits[trait] += 1
    draw_traits()


def remove_bonus_trait(trait: str):
    bonus_traits[trait] -= 1
    draw_traits()


def add_unit(new_unit: str):
    # Add a unique unit whenever possible
    if len(team_list) == team_size or new_unit in team_list:
        return
    team_list.append(new_unit)
    draw_team()
    draw_traits()


def remove_unit(index: int):
    # avoid index error
    if index >= len(team_list):
        return
    del team_list[index]
    draw_team()
    draw_traits()


def add_core(new_unit: str):
    # add a core unit whenever possible
    if len(included_units) == team_size or new_unit in included_units:
        return
    included_units.append(new_unit)
    draw_core()


def remove_core(index: int):
    if index >= len(included_units):
        return
    del included_units[index]
    draw_core()


def increment_team_size():
    global team_size
    team_size += 1
    draw_team_size()


def decrement_team_size():
    global team_size
    team_size -= 1
    draw_team_size()


def toggle_bd():
    global bd_flag
    bd_flag = not bd_flag


"""
    UI components
"""


"""
    The App root
"""
root = customtkinter.CTk()
root.title("TFT Set 12 AI Planner")
root.geometry("1300x870")

frame = customtkinter.CTkFrame(master=root)
frame.pack(side="top", pady=20, fill="both", expand=True)

"""
    Frame holds traits, current team comp, core units, etc.
    Champions window will be on the bottom of the app
"""
top = customtkinter.CTkFrame(master=frame)
top.pack(fill="both", expand=True)

"""
    Displays all champion icons + names
"""
champions = customtkinter.CTkScrollableFrame(master=frame)
champions.pack(fill="both", padx=10, pady=10, expand=True)

"""
    Displays team traits
"""
traits = customtkinter.CTkScrollableFrame(master=top)
traits.pack(side="left", fill="y")

"""
    Contains current team comp and core unit frames
"""
team_core_frame = customtkinter.CTkFrame(master=top)
team_core_frame.pack(fill="both", expand=True)

"""
    Contains current team comp, generate button, BD checkbox, and team size selector
"""
team_misc_frame = customtkinter.CTkFrame(master=team_core_frame)
team_misc_frame.pack(fill="both", side="left", expand=True)

"""
    Displays current team comp
"""
team = customtkinter.CTkFrame(master=team_misc_frame)
team.pack(fill="both")

"""
    Displays "Generate team comp" button
"""
generate = customtkinter.CTkButton(
    master=team_misc_frame,
    text="Generate",
    command=lambda: generate_team(),
)
generate.pack(side="left", pady=10, padx=10)

"""
    Displays "Build Different II" checkbox
"""
bd_box = customtkinter.CTkCheckBox(
    master=team_misc_frame,
    text='Toggle if you have "Built Different II"',
    command=toggle_bd,
)
bd_box.pack(side="left", padx=10)

"""
    Displays team size selector
"""
size = customtkinter.CTkFrame(master=team_misc_frame)
size.pack(side="right", pady=10, padx=10)

"""
    Displays core units
"""
core = customtkinter.CTkScrollableFrame(master=team_core_frame)
core.pack(side="right", fill="y")


# draw champion buttons
row = 0
col = 0
for unit in sorted(all_units):
    img = customtkinter.CTkImage(
        # Image.open(f"assets/champions/{unit}.png"), size=(60, 60)
        Image.open(resource_path(f"assets/champions/{unit}.png")),
        size=(60, 60),
    )
    button = customtkinter.CTkButton(
        master=champions,
        image=img,
        text=unit,
        fg_color="transparent",
        command=lambda unit=unit: add_unit(all_units[unit]),
    )
    button.grid(row=row, column=col, padx=10, pady=10)
    col += 1
    if col == CHAMPION_COL_LIMIT:
        row += 1
        col = 0


def draw_traits():
    """
    Draw current team traits
    """
    # update frame by deleting beforehand
    for widget in traits.winfo_children():
        widget.destroy()

    traits_label = customtkinter.CTkLabel(
        master=traits, text="Traits", font=("Roboto", 24)
    )
    traits_label.grid(row=0, column=1, pady=10)

    # trait counter works similiarly to calculate_points()
    trait_counter = collections.defaultdict(int)  # avoid KeyError

    for unit in team_list:
        unit_traits = all_units[unit.name].traits
        for trait in unit_traits:
            trait_counter[trait] += 1

    for trait, count in bonus_traits.items():
        trait_counter[trait] += count

    # sort traits in descending order
    sort_traits = {
        trait: count
        for trait, count in sorted(
            trait_counter.items(), key=lambda item: item[1], reverse=True
        )
    }
    row = 1  # recall traits_label is row 0
    # draw team traits
    for trait, count in sort_traits.items():
        if count > 0:
            img = customtkinter.CTkImage(
                # Image.open(f"assets/traits/{trait}.png"), size=(32, 32)
                Image.open(resource_path(f"assets/traits/{trait}.png")),
                size=(32, 32),
            )
            button = customtkinter.CTkButton(
                master=traits,
                image=img,
                text=show_trait_count(trait, count),  #
                fg_color="transparent",
            )
            button.grid(row=row, column=1, pady=10)
            add_button = customtkinter.CTkButton(
                master=traits,
                text="+",
                width=5,
                command=lambda trait=trait: add_bonus_trait(trait),
            )
            add_button.grid(row=row, column=2, padx=5)
            if trait in bonus_traits and bonus_traits[trait] > 0:
                remove_button = customtkinter.CTkButton(
                    master=traits,
                    text="-",
                    width=5,
                    command=lambda trait=trait: remove_bonus_trait(trait),
                )
                remove_button.grid(row=row, column=0, padx=5)
            row += 1


def draw_team():
    """
    Draw current team comp
    """
    for widget in team.winfo_children():
        widget.destroy()

    row = 0
    col = 0
    for i in range(team_size):
        img = customtkinter.CTkImage(
            # Image.open(
            #     f"assets/champions/{'default' if i >= len(team_list) else team_list[i].name}.png"
            # ),
            Image.open(
                resource_path(
                    f"assets/champions/{'default' if i >= len(team_list) else team_list[i].name}.png"
                )
            ),
            size=(125, 150),
        )
        button_frame = customtkinter.CTkFrame(master=team)
        button_frame.grid(row=row, column=col, padx=10, pady=10)
        button = customtkinter.CTkButton(
            master=button_frame,
            image=img,
            text="",
            fg_color="transparent",
            command=lambda i=i: remove_unit(i),
            border_color=(
                None if i >= len(team_list) else cost_to_hex[team_list[i].cost]
            ),
            border_width=0 if i >= len(team_list) else 5,
        )
        button.pack(fill="both")
        if i < len(team_list):
            favourite = customtkinter.CTkButton(
                master=button_frame,
                text="Make core",
                fg_color="red",
                text_color="black",
                command=lambda i=i: add_core(team_list[i].name),
            )
            favourite.pack(side="bottom")
        col += 1
        if col == 5:  # 5 units per row
            row += 1
            col = 0


def draw_team_size():
    """
    Draw team size selector
    """
    for widget in size.winfo_children():
        widget.destroy()

    label = customtkinter.CTkLabel(master=size, text=f"Team Size: {team_size}")
    label.grid(row=0, column=1, padx=10)

    add_button = customtkinter.CTkButton(
        master=size, text="+", width=5, command=increment_team_size
    )
    add_button.grid(row=0, column=2)
    if team_size > DEFAULT_TEAM_SIZE:
        remove_button = customtkinter.CTkButton(
            master=size, text="-", width=5, command=decrement_team_size
        )
        remove_button.grid(row=0, column=0, padx=5)


def draw_core():
    """
    Draw core unit list
    """
    for widget in core.winfo_children():
        widget.destroy()

    label = customtkinter.CTkLabel(master=core, text="Core Units", font=("Roboto", 24))
    label.pack(side="top", fill="x")
    for i in range(len(included_units)):
        img = customtkinter.CTkImage(
            # Image.open(f"assets/champions/{included_units[i]}.png"), size=(60, 60)
            Image.open(resource_path(f"assets/champions/{included_units[i]}.png")),
            size=(60, 60),
        )
        button = customtkinter.CTkButton(
            master=core,
            image=img,
            text="",
            fg_color="transparent",
            command=lambda i=i: remove_core(i),
        )
        button.pack(pady=10)


draw_traits()
draw_core()
draw_team()
draw_team_size()

# keep GUI running
root.mainloop()
