import math
from collections import namedtuple
from enum import Enum
from ..routes.utils import save_to_file

class Role(Enum):
    Top = 0
    Jungle = 1
    Middle = 2
    Bottom = 3
    Support = 4

# Assuming Dataset, Role, and other necessary models are defined elsewhere in your Flask application
# from your_app.models import Dataset, Role

# Mock definitions for Dataset and Role, replace with your actual implementations
Dataset = namedtuple('Dataset', ['champion_data'])
Role = namedtuple('Role', ['name'])  # Example Role definition

# Constants
RiskLevel = ('very-low', 'low', 'medium', 'high', 'very-high')
displayNameByRiskLevel = {
    "very-low": "Very Low",
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "very-high": "Very High",
}
priorGamesByRiskLevel = {
    "very-low": 3000,
    "low": 2000,
    "medium": 1000,
    "high": 500,
    "very-high": 250,
}
buildPriorGamesByRiskLevel = {
    "very-low": 3000,
    "low": 2000,
    "medium": 1000,
    "high": 750,
    "very-high": 500,
}

# Helper functions (ratingToWinrate, winrateToRating, etc.) translated to Python
def rating_to_winrate(d):
    return 1 / (1 + math.pow(10, -d / 400))

def winrate_to_rating(w):
    return -400 * math.log10(1 / w - 1)

# Add your translation of analyzeChampions, analyzeChampion, analyzeDuos, analyzeMatchups here
# These functions will need to be adapted to Python, following the structure of analyzeDraft below

def analyze_draft(dataset, full_dataset, team, enemy, config):
    prior_games = priorGamesByRiskLevel[config['riskLevel']]

    # Example structure, adapt based on your actual data models and logic
    ally_champion_rating = analyze_champions(dataset, full_dataset, team, prior_games) if not config['ignoreChampionWinrates'] else {'totalRating': 0, 'winrate': 0, 'championResults': []}
    enemy_champion_rating = analyze_champions(dataset, full_dataset, enemy, prior_games) if not config['ignoreChampionWinrates'] else {'totalRating': 0, 'winrate': 0, 'championResults': []}

    ally_duo_rating = analyze_duos(full_dataset, team, prior_games)
    enemy_duo_rating = analyze_duos(full_dataset, enemy, prior_games)
    matchup_rating = analyze_matchups(full_dataset, team, enemy, prior_games)

    total_rating = ally_champion_rating['totalRating'] + ally_duo_rating['totalRating'] + matchup_rating['totalRating'] - enemy_champion_rating['totalRating'] - enemy_duo_rating['totalRating']
    winrate = rating_to_winrate(total_rating)

    return {
        'allyChampionRating': ally_champion_rating,
        'enemyChampionRating': enemy_champion_rating,
        'allyDuoRating': ally_duo_rating,
        'enemyDuoRating': enemy_duo_rating,
        'matchupRating': matchup_rating,
        'totalRating': total_rating,
        'winrate': winrate,
    }

def analyze_champions(dataset, synergy_matchup_dataset, team, prior_games):
    champion_results = []
    total_rating = 0

    for role, champion_key in team.items():  # Assuming team is a dict {Role: champion_key}
        champion_result = analyze_champion(dataset, synergy_matchup_dataset, role, champion_key, prior_games)
        champion_results.append(champion_result)
        total_rating += champion_result['rating']

    return {
        'championResults': champion_results,
        'totalRating': total_rating,
    }


def analyze_champion(dataset, full_dataset, role, champion_key, prior_games):
    # Fetching champion data from the current and full datasets
    champion_data = dataset['championData'].get(champion_key, {})
    full_champion_data = full_dataset['championData'].get(champion_key, {})
    
    role_data = champion_data.get('statsByRole', {}).get(role.name, {})
    full_role_data = full_champion_data.get('statsByRole', {}).get(role.name, {})
    
    # Calculating win rates
    if role_data and full_role_data:
        current_winrate = role_data['wins'] / role_data['games'] if role_data['games'] > 0 else 0
        full_winrate = full_role_data['wins'] / full_role_data['games'] if full_role_data['games'] > 0 else 0
        
        # Adjusting stats based on prior games
        adjusted_wins = role_data['wins'] + (prior_games * full_winrate)
        adjusted_games = role_data['games'] + prior_games
        adjusted_winrate = adjusted_wins / adjusted_games
        
        rating = winrate_to_rating(adjusted_winrate)
    else:
        rating = 0  # Default rating if data is missing
    
    return {
        'role': role,
        'championKey': champion_key,
        'rating': rating,
        'wins': role_data.get('wins', 0),
        'games': role_data.get('games', 0),
    }

def analyze_duos(dataset, team, prior_games):
    # Assuming team is a dict {Role: champion_key}
    team_entries = sorted(team.items(), key=lambda x: x[0])

    duo_results = []
    total_rating = 0

    for i in range(len(team_entries)):
        for j in range(i + 1, len(team_entries)):
            roleA, championKeyA = team_entries[i]
            roleB, championKeyB = team_entries[j]

            role_stats = get_stats(dataset, championKeyA, roleA)
            champion2_role_stats = get_stats(dataset, championKeyB, roleB)

            expected_rating = winrate_to_rating(role_stats['wins'] / role_stats['games']) + winrate_to_rating(champion2_role_stats['wins'] / champion2_role_stats['games'])
            expected_winrate = rating_to_winrate(expected_rating)

            duo_stats = get_stats(dataset, championKeyA, roleA, "duo", roleB, championKeyB)
            champion2_duo_stats = get_stats(dataset, championKeyB, roleB, "duo", roleA, championKeyA)
            combined_stats = average_stats(duo_stats, champion2_duo_stats)

            adjusted_stats = add_stats(combined_stats, multiply_stats({'wins': expected_winrate, 'games': 1}, prior_games))
            winrate = adjusted_stats['wins'] / adjusted_stats['games']

            actual_rating = winrate_to_rating(winrate)
            rating_difference = actual_rating - expected_rating

            duo_results.append({
                'roleA': roleA,
                'championKeyA': championKeyA,
                'roleB': roleB,
                'championKeyB': championKeyB,
                'rating': rating_difference,
                'wins': adjusted_stats['wins'],
                'games': adjusted_stats['games'],
            })
            total_rating += rating_difference

    return {
        'duoResults': duo_results,
        'totalRating': total_rating,
    }

def get_stats(dataset, champion_key, role, stat_type=None, role2=None, champion_key2=None):
    """
    Fetches stats for a champion, duo, or matchup based on the provided parameters.

    :param dataset: Dataset instance containing champion data.
    :param champion_key: The key of the champion.
    :param role: The role of the champion (expected to be an instance of Role or similar).
    :param stat_type: Optional; specifies the type of stats to fetch ('duo' or 'matchup').
    :param role2: Optional; the role of the second champion (for duo or matchup stats).
    :param champion_key2: Optional; the key of the second champion (for duo or matchup stats).
    :return: A dictionary containing 'wins' and 'games'.
    """
    # Accessing champion data
    champion_data = dataset['championData'].get(champion_key, {})
    # Adjust based on your Role structure
    role_str = str(role.name) if hasattr(role, 'name') else str(role)

    # Accessing stats by role
    stats_by_role = champion_data.get('statsByRole', {}).get(role_str, {})

    if stat_type == "matchup":
        # Logic for 'matchup'
        if role2 is not None and champion_key2 is not None:
            role2_str = str(role2.name) if hasattr(role2, 'name') else str(role2)
            matchup_stats = stats_by_role.get('matchup', {}).get(role2_str, {}).get(champion_key2, {'wins': 0, 'games': 0})
            return matchup_stats
    elif stat_type == "duo":
        # Logic for 'duo'
        if role2 is not None and champion_key2 is not None:
            role2_str = str(role2.name) if hasattr(role2, 'name') else str(role2)
            synergy_stats = stats_by_role.get('synergy', {}).get(role2_str, {}).get(champion_key2, {'wins': 0, 'games': 0})
            return synergy_stats
    else:
        # Logic for individual champion stats or any other case not covered above
        return stats_by_role

    # Fallback for unexpected conditions or missing parameters
    return {'wins': 0, 'games': 0}


def add_stats(*stats):
    total_wins = sum(stat['wins'] for stat in stats)
    total_games = sum(stat['games'] for stat in stats)
    return {'wins': total_wins, 'games': total_games}

def multiply_stats(stats, number):
    return {'wins': stats['wins'] * number, 'games': stats['games'] * number}

def divide_stats(stats, number):
    return {'wins': stats['wins'] / number, 'games': stats['games'] / number}

def average_stats(*stats):
    total = add_stats(*stats)
    return divide_stats(total, len(stats))

def analyze_matchups(dataset, team, enemy, prior_games):
    matchup_results = []
    total_rating = 0

    # Assuming team and enemy are dictionaries {Role: champion_key}
    for ally_role, ally_champion_key in team.items():
        for enemy_role, enemy_champion_key in enemy.items():
            role_stats = get_stats(dataset, ally_champion_key, ally_role)
            enemy_role_stats = get_stats(dataset, enemy_champion_key, enemy_role)

            expected_rating = winrate_to_rating(role_stats['wins'] / role_stats['games']) - winrate_to_rating(enemy_role_stats['wins'] / enemy_role_stats['games'])
            expected_winrate = rating_to_winrate(expected_rating)

            matchup_stats = get_stats(dataset, ally_champion_key, ally_role, "matchup", enemy_role, enemy_champion_key)
            enemy_matchup_stats = get_stats(dataset, enemy_champion_key, enemy_role, "matchup", ally_role, ally_champion_key)
            enemy_losses = enemy_matchup_stats['games'] - enemy_matchup_stats['wins']

            wins = (matchup_stats['wins'] + enemy_losses) / 2
            games = (matchup_stats['games'] + enemy_matchup_stats['games']) / 2

            adjusted_stats = add_stats({'wins': wins, 'games': games}, multiply_stats({'wins': expected_winrate, 'games': 1}, prior_games))
            winrate = adjusted_stats['wins'] / adjusted_stats['games']

            actual_rating = winrate_to_rating(winrate)
            rating = actual_rating - expected_rating

            matchup_results.append({
                'roleA': ally_role,
                'championKeyA': ally_champion_key,
                'roleB': enemy_role,
                'championKeyB': enemy_champion_key,
                'rating': rating,
                'wins': rating_to_winrate(winrate_to_rating(wins / games) - expected_rating) * games,
                'games': games,
            })
            total_rating += rating

    return {
        'matchupResults': matchup_results,
        'totalRating': total_rating,
    }
