"""Handlers for standings commands — thin wrappers over standings_service."""

import services.standings_service as standings


def handle_show_standings(params):
    league_name = params.get('league_identifier') or params.get('league_name')
    if not league_name:
        return "Формат: покажи класиране [лига]"

    table = standings.calculate_standings(league_name)
    if not table:
        return f"Няма намерена лига '{league_name}' или лигата няма отбори."

    has_matches = any(row['mp'] > 0 for row in table)

    lines = [
        f"{'#':>2} {'Отбор':<20} {'MP':>3} {'W':>2} {'D':>2} {'L':>2}  {'GF':>2}:{'GA':<2}  {'GD':>3}  {'PTS':>3}"
    ]
    for row in table:
        lines.append(
            f"{row['position']:>2}. {row['team']:<20} "
            f"{row['mp']:>3} {row['w']:>2} {row['d']:>2} {row['l']:>2}  "
            f"{row['gf']:>2}:{row['ga']:<2}  "
            f"{row['gd']:>+3}  {row['pts']:>3}"
        )

    if not has_matches:
        lines.append("")
        lines.append("Няма изиграни мачове.")

    return "\n".join(lines)
