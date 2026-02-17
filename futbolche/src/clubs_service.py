from db import execute_query

def add_club(name):
    if not name or name.strip() == "":
        return "Името не може да бъде празно."

    # Проверка за дублиране
    existing = execute_query(
        "SELECT * FROM Clubs WHERE name = ?",
        (name,),
        fetch=True
    )

    if existing:
        return "Клуб с това име вече съществува."

    execute_query(
        "INSERT INTO Clubs (name, city, founded_year) VALUES (?, ?, ?)",
        (name, "Unknown", 1900)
    )

    return f"Клуб '{name}' беше добавен успешно."


def get_all_clubs():
    rows = execute_query("SELECT * FROM Clubs", fetch=True)
    if not rows:
        return "Няма добавени клубове."

    result = []
    for row in rows:
        result.append(f"{row['id']}. {row['name']}")
    return "\n".join(result)


def delete_club(name):
    existing = execute_query(
        "SELECT * FROM Clubs WHERE name = ?",
        (name,),
        fetch=True
    )

    if not existing:
        return "Няма такъв клуб."

    execute_query(
        "DELETE FROM Clubs WHERE name = ?",
        (name,)
    )

    return f"Клуб '{name}' беше изтрит."
