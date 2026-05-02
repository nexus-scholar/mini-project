from flask import Flask, render_template, request, jsonify
from pymongo import errors as pymongo_errors
import users

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/users", methods=["GET"])
def api_list_users():
    q = request.args.get("q", "")
    try:
        result = users.list_users(q)
        return jsonify(result)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/users", methods=["POST"])
def api_create_user():
    data = request.get_json()
    try:
        new_id = users.create_user(data)
        return jsonify({"success": "User added successfully.", "id": new_id}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except pymongo_errors.DuplicateKeyError:
        return jsonify({"error": "Phone number already exists."}), 409
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/users/<user_id>", methods=["GET"])
def api_get_user(user_id):
    try:
        u = users.get_user(user_id)
        if not u:
            return jsonify({"error": "User not found."}), 404
        return jsonify(u)
    except ValueError:
        return jsonify({"error": "Invalid user id."}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/users/<user_id>", methods=["PUT"])
def api_update_user(user_id):
    data = request.get_json()
    try:
        ok = users.update_user(user_id, data)
        if not ok:
            return jsonify({"error": "User not found."}), 404
        return jsonify({"success": "User updated successfully."})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except pymongo_errors.DuplicateKeyError:
        return jsonify({"error": "Phone number already exists."}), 409
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/users/<user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    try:
        ok = users.delete_user(user_id)
        if not ok:
            return jsonify({"error": "User not found."}), 404
        return jsonify({"success": "User deleted."})
    except ValueError:
        return jsonify({"error": "Invalid user id."}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/demo/create", methods=["POST", "GET"])
def create_demo_users():
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
            # skip duplicates or validation errors
            skipped.append({"phone": d.get("phone"), "error": str(e)})
    return jsonify({"created": created, "skipped": skipped})


if __name__ == "__main__":
    app.run(debug=True)