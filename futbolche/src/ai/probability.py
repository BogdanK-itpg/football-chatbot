HOME_ADVANTAGE = 0.15

FORM_WEIGHT = 0.35
ATTACK_WEIGHT = 0.30
DEFENSE_WEIGHT = 0.20
RANKING_WEIGHT = 0.15


def calculate_team_index(features):
    return (
        features['form'] * FORM_WEIGHT
        + features['attack'] * ATTACK_WEIGHT
        + features['defense'] * DEFENSE_WEIGHT
        + features['ranking'] * RANKING_WEIGHT
    )


def calculate_draw_probability(home_index, away_index):
    diff = abs(home_index - away_index)
    return max(0.15, 0.35 - diff)


def calculate_probabilities(home_features, away_features):
    home_index = calculate_team_index(home_features) + HOME_ADVANTAGE
    away_index = calculate_team_index(away_features)

    draw_probability = calculate_draw_probability(home_index, away_index)
    remaining = 1 - draw_probability

    total_index = home_index + away_index
    if total_index == 0:
        home_probability = 0.5
        away_probability = 0.5
    else:
        home_probability = remaining * (home_index / total_index)
        away_probability = remaining * (away_index / total_index)

    home_pct = round(home_probability * 100)
    draw_pct = round(draw_probability * 100)
    away_pct = 100 - home_pct - draw_pct

    return {
        'home': home_pct,
        'draw': draw_pct,
        'away': away_pct
    }
