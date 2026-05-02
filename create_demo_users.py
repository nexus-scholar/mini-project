"""Create demo users by calling the `users` module.

Run this script if you want to populate the DB from the command line without starting the Flask app.
"""
import users


def create_demo():
    demo = [
        {"first_name": "Alice", "last_name": "Smith", "birth_date": "1990-05-12", "birth_place": "Springfield", "phone": "+15550000001"},
        {"first_name": "Bob", "last_name": "Johnson", "birth_date": "1985-11-03", "birth_place": "Greenville", "phone": "+15550000002"},
        {"first_name": "Carol", "last_name": "Williams", "birth_date": "1992-07-22", "birth_place": "Rivertown", "phone": "+15550000003"},
    ]
    created = []
    skipped = []
    for d in demo:
        try:
            new_id = users.create_user(d)
            created.append({"id": new_id, "phone": d["phone"]})
        except Exception as e:
            skipped.append({"phone": d.get("phone"), "error": str(e)})
    print({"created": created, "skipped": skipped})


if __name__ == "__main__":
    create_demo()

