from ai import ai_service


def handle_predict_match(params):
    team1 = params.get('team1')
    team2 = params.get('team2')
    if not team1 or not team2:
        return "Формат: Prediction [отбор1] vs [отбор2]"

    try:
        result = ai_service.predict_match(team1, team2)
    except ValueError as e:
        return str(e)

    return (
        f"🏠 {team1} Win: {result['home']}%\n"
        f"🤝 Draw: {result['draw']}%\n"
        f"🛫 {team2} Win: {result['away']}%"
    )
