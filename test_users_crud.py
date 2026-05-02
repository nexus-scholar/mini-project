"""Quick script to test the `users` CRUD module.

This script will:
- list users (first 5)
- create a temporary test user
- read that user back
- update the user
- delete the user

It uses the MONGO_URI from .env if present. Keep it safe: the script cleans up the created test user.
"""
import time
import uuid

import users


def run_test():
    print("Listing up to 5 existing users:")
    try:
        all_users = users.list_users()
        for u in all_users[:5]:
            print(u)
    except Exception as e:
        print("Could not list users:", e)

    # Create a unique phone number for the test user
    unique_suffix = str(int(time.time()))
    phone = "+100000" + unique_suffix[-7:]

    test_user = {
        "first_name": "Test",
        "last_name": "User",
        "birth_date": "1990-01-01",
        "birth_place": "Testville",
        "phone": phone,
    }

    print("\nCreating test user with phone:", phone)
    try:
        user_id = users.create_user(test_user)
        print("Created user id:", user_id)
    except Exception as e:
        print("Create failed:", e)
        return

    try:
        fetched = users.get_user(user_id)
        print("Fetched user:", fetched)
    except Exception as e:
        print("Get failed:", e)

    # Update user
    updated_data = test_user.copy()
    updated_data["first_name"] = "UpdatedTest"
    print("\nUpdating user first_name to:", updated_data["first_name"])
    try:
        ok = users.update_user(user_id, updated_data)
        print("Update returned:", ok)
        print("Refetching:", users.get_user(user_id))
    except Exception as e:
        print("Update failed:", e)

    # Delete user
    print("\nDeleting test user")
    try:
        deleted = users.delete_user(user_id)
        print("Deleted:", deleted)
    except Exception as e:
        print("Delete failed:", e)


if __name__ == "__main__":
    run_test()

