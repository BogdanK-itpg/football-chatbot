from repositories import clubs_repo


def add_club(name):
    if not name or not name.strip():
        return "Името не може да бъде празно."
    name = name.strip()
    existing = clubs_repo.get_by_name(name)
    if existing:
        return "Клуб с това име вече съществува."
    res = clubs_repo.create(name)
    if res is None:
        return "Грешка при добавяне на клуба."
    return f"Клуб '{name}' беше добавен успешно."


def get_all_clubs():
    rows = clubs_repo.get_all()
    if not rows:
        return "Няма добавени клубове."
    lines = []
    for idx, r in enumerate(rows, start=1):
        lines.append(f"{idx}. {r['name']}")
    return "\n".join(lines)


def delete_club(identifier):
    club = None
    if str(identifier).isdigit():
        club = clubs_repo.get_by_id(int(identifier))
    else:
        club = clubs_repo.get_by_name(identifier)
    if not club:
        return "Няма такъв клуб."
    res = clubs_repo.delete(club['id'])
    if res is None:
        return "Грешка при изтриване на клуба."
    return f"Клуб '{club['name']}' беше изтрит."


def update_club(identifier, new_name=None, new_city=None, new_founded_year=None):
    club = None
    if str(identifier).isdigit():
        club = clubs_repo.get_by_id(int(identifier))
    else:
        club = clubs_repo.get_by_name(identifier)
    if not club:
        return "Клубът не беше намерен."
    kwargs = {}
    if new_name:
        kwargs['name'] = new_name.strip()
    if new_city:
        kwargs['city'] = new_city.strip()
    if new_founded_year:
        try:
            kwargs['founded_year'] = int(new_founded_year)
        except (ValueError, TypeError):
            return "Невалидна година на основаване."
    if not kwargs:
        return "Няма зададени промени."
    res = clubs_repo.update(club['id'], **kwargs)
    if res is None:
        return "Грешка при обновяване на клуба."
    return "Клубът беше успешно обновен."
