import json
import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import matplotlib.image as img

import Visualisation.dataset as dataset

def create_event_slider() -> None:
    """
    Creates the widget to select a game event and visualise its location on the ice
    """

    def get_game_data(year: int, is_playoff: bool, game_num: int) -> dict:
        """
        Gives the game infos from the json file

        args:
            year (int): First year of the NHL season (e.g., 2023 for the 2023-2024 season).
            is_playoff (bool): If the game is a playoff game
            game_num (int): The number related to the nhl game

        returns:
            dict: containing all game infos
        """
        game_id = get_game_id(year, is_playoff, game_num)

        with open(f"../data/raw/{year}/play_by_play_{game_id}_data.json", "r", encoding = "utf-8") as f:
            data = json.load(f)

        return data

    # Year choice
    slider_year = widgets.IntSlider(
        value = 2023,
        min = 2016,
        max = 2023,
        step = 1,
        description = "Year:"
    )

    # Regular season vs playoffs
    checkbox_playoff = widgets.Checkbox(
        value = False,
        description = "Playoffs"
    )

    # Game choice
    slider_game = widgets.IntSlider(
        value = 1,
        min = 1,
        max = dataset.get_n_game(slider_year.value),
        step = 1,
        description = "Game:"
    )

    # Open game file
    game_data = get_game_data(slider_year.value, checkbox_playoff.value, slider_game.value)

    # General game infos
    game_info = widgets.HTML(
        value = get_game_info(game_data)
    )

    # Choice of game play
    slider_play = widgets.IntSlider(
        value = 1,
        min = 1,
        max = len(game_data["plays"]),
        step = 1,
        description = "Play:"
    )

    point, fig, plt, title = plot_play(game_data["plays"][slider_play.value], game_data)

    # Infos about the play
    play_info = widgets.HTML(
        value = get_play_info(game_data["plays"][slider_play.value])
    )

    def change_slider_game(change) -> None:
        """
        Change the max value of slider_game to reflect the number of game of the selected year
        """
        # TODO: Playoff
        slider_game.max = dataset.get_n_game(change['new'])

    def change_game(change) -> None:
        """
        Changes the game shown
        """
        nonlocal game_data
        game_data = get_game_data(slider_year.value, checkbox_playoff.value, change["new"])
        game_info.value = get_game_info(game_data)
        slider_play.max = len(game_data["plays"])

    def change_play(change) -> None:
        """
        Change the max value of slider_game to reflect the number of game of the selected year
        """
        play_data = game_data["plays"][change['new']]
        play_info.value = get_play_info(play_data)
        if get_coordinates(play_data) is not None:
            point.set_data(get_coordinates(play_data))
        else:
            point.set_data(200, 200)    # Out of bound
        title.set_text(get_plot_title(play_data, game_data["rosterSpots"]))
        fig.canvas.draw_idle()

    # Observe
    slider_year.observe(change_slider_game, names = "value")
    slider_game.observe(change_game, names = "value")
    slider_play.observe(change_play, names = "value")

    # Layout
    box_year = widgets.HBox([slider_year, checkbox_playoff])

    # Display
    display(box_year)
    display(slider_game)
    display(game_info)
    display(slider_play)
    plt.show()
    display(play_info)

    

def get_game_id(year: int, is_playoff: bool, game_num: int) -> str:
    """
    Gives the game id as NHL standart for a game

    args:
        year (int): First year of the NHL season (e.g., 2023 for the 2023-2024 season).
        is_playoff (bool): If the game is a playoff game
        game_num (int): The number related to the nhl game

    returns:
        str: the string of the formated game id
    """
    return f"{year}{"03" if is_playoff else "02"}{game_num:04d}"


def get_game_info(game_data: dict) -> str:
    """
    Returns the general game info of the game with game_id.

    args:
        game_data (dict): content of the json file of the game as dict

    returns:
        str : Information about the game to printed for visualisation (Teams, score, etc.)
    """

    # Get the general game description
    description = f"<pre>{game_data["gameDate"]} {game_data["gameType"]} {game_data["startTimeUTC"]} \n" +\
                  f"Game ID: {game_data["id"]}; {game_data["homeTeam"]["abbrev"]} (home) vs {game_data["awayTeam"]["abbrev"]} (away) \n" +\
                  f"    {game_data["gameOutcome"]["lastPeriodType"]} \n" +\
                  f"                    Home    Away \n" +\
                  f"    Teams:          {game_data["homeTeam"]["abbrev"]:<4}    {game_data["awayTeam"]["abbrev"]}\n" +\
                  f"    Goals:          {game_data["homeTeam"]["score"]:<4}    {game_data["awayTeam"]["score"]}\n" +\
                  f"    SoG:            {game_data["homeTeam"]["sog"]:<4}    {game_data["awayTeam"]["sog"]}</pre>"

    return description

def plot_play(play_data: dict, game_data: dict) -> (object, object, object):
    """
    Returns an image of a rink with a dot where the play was done

    args:
        play_data (dict): content of the json of the play
        game_data (dict): content of the json of the game

    returns:
        point : The point on the graph where the event was recorded
        fig : The graph that can be modified
        plt : The plot
    """
    clear_output(wait = True)

    # Show image
    rink = img.imread("../reports/figures/nhl_rink.png")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(rink, extent=[-100, 100, -42.5, 42.5], zorder = 0)
    plt.gca().invert_yaxis()
    ax.set_xlim(-100, 100)
    ax.set_ylim(-42.5, 42.5)
    
    
    # Show dot
    if get_coordinates(play_data) is not None:
        point, = ax.plot(get_coordinates(play_data)[0][0], get_coordinates(play_data)[1][0],
                         "ro", color = "red", markersize = 10, zorder = 1)
    else:
        point, = ax.plot(200, 200,
                         "ro", color = "red", markersize = 10, zorder = 1)

    # Set title
    title = ax.set_title(get_plot_title(play_data, game_data["rosterSpots"]))

    return point, fig, plt, title

def get_plot_title(play_data: dict, player_info: dict) -> str:
    """
    Gives the play description

    args:
        play_data (dict): content of the json of the play
        player_info (dict): dict of players on roster

    returns:
        str : Formated string representing the tile of the plot
    """


    play_type = play_data["typeDescKey"]

    match play_type:
        case "faceoff":
            player_1 = get_name(play_data["details"]["winningPlayerId"], player_info)
            player_2 = get_name(play_data["details"]["losingPlayerId"], player_info)
            return f"{player_1} wins face-off against {player_2}"
        case "hit":
            player_1 = get_name(play_data["details"]["hittingPlayerId"], player_info)
            player_2 = get_name(play_data["details"]["hitteePlayerId"], player_info)
            return f"{player_1} hit on {player_2}"
        case "shot-on-goal":
            player_1 = get_name(play_data["details"]["shootingPlayerId"], player_info)
            player_2 = get_name(play_data["details"]["goalieInNetId"], player_info)
            return f"{player_1} shot on {player_2}"
        case "blocked-shot":
            player_1 = get_name(play_data["details"]["shootingPlayerId"], player_info)
            player_2 = get_name(play_data["details"]["blockingPlayerId"], player_info)
            return f"{player_1} shot blocked by {player_2}"
        case "missed-shot":
            player_1 = get_name(play_data["details"]["shootingPlayerId"], player_info)
            if "goalieInNetId" in play_data["details"]:
                player_2 = get_name(play_data["details"]["goalieInNetId"], player_info)
            else:
                player_2 = empty_net
            return f"{player_1} shot misses on {player_2}"
        case "goal":
            player_1 = get_name(play_data["details"]["scoringPlayerId"], player_info)
            player_1t = play_data["details"]["scoringPlayerTotal"]
            if "goalieInNetId" in play_data["details"]:
                goalie = get_name(play_data["details"]["goalieInNetId"], player_info)
            else :
                goalie = "Empty net"
            if "assist1PlayerId" in play_data["details"]:
                player_2 = get_name(play_data["details"]["assist1PlayerId"], player_info)
                player_2t = play_data["details"]["assist1PlayerTotal"]
                if "assist2PlayerId" in play_data["details"]:
                    player_3 = get_name(play_data["details"]["assist2PlayerId"], player_info)
                    player_3t = play_data["details"]["assist2PlayerTotal"]
                    return f"{player_1} ({player_1t}) goal assisted by {player_2} ({player_2t}) and {player_3} ({player_3t}) on {goalie}"
                return f"{player_1} ({player_1t}) goal assisted by {player_2} ({player_2t}) on {goalie}"
            return f"{player_1} ({player_1t}) goal unassisted on {goalie}"
        case "takeaway":
            player = get_name(play_data["details"]["playerId"], player_info)
            return f"{player} takeaway"
        case "giveaway":
            player = get_name(play_data["details"]["playerId"], player_info)
            return f"{player} giveaway"
        case "penalty":
            player_1 = get_name(play_data["details"]["committedByPlayerId"], player_info)
            duration = play_data["details"]["duration"]
            pen_type = play_data["details"]["typeCode"]
            pen_desc = play_data["details"]["descKey"].replace("-", " ")
            if "drawnByPlayerId" in play_data["details"]:
                player_2 = get_name(play_data["details"]["drawnByPlayerId"], player_info)
                return f"Pendalty: {player_1} {duration} minute {pen_type} for {pen_desc} against {player_2}"
            return f"Pendalty: {player_1} {duration} minute {pen_type} for {pen_desc}"
        case "delayed-penalty":
            return f"Delayed penalty"
        case "stoppage":
            reason = play_data["details"]["reason"].replace("-", " ")
            return f"{reason}"
        case "period-end":
            return f"Period end"
        case "game-end":
            return f"Game end"

def get_coordinates(play_data: dict) -> (float, float):
    """
    Returns the information about a specific play

    args:
        play_data (dict): content of the json of the play

    returns:
        (x, y) : the coordinates of the play
    """
    
    if "details" in play_data.keys() and "xCoord" in play_data["details"].keys() and "yCoord" in play_data["details"].keys():
        return [play_data["details"]["xCoord"]], [play_data["details"]["yCoord"]]
    else:
        return None

def get_play_info(play_data: dict) -> str:
    """
    Returns the information about a specific play

    args:
        play_data (dict): content of the json of the play

    returns:
        str : Information about the game to printed for visualisation (Type of play, players invovlved, etc.)
    """
    
    return f"<pre>{json.dumps(play_data, indent = 4)}</pre>"

def get_name(player_id: int, roster_spots: list) -> str:
    """
    Find the name of a player with a certain id in the game roster

    args:
        player_id (int): NHL player id
        roster_spots (list): list of players in roster as in json from the NHL api
    
    returns:
        str: Full name of the player
    """

    for player in roster_spots:
        if player["playerId"] == player_id:
            return f"{player["firstName"]["default"]} {player["lastName"]["default"]}"
    
    return ""
