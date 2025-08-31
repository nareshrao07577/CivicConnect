from flask import Flask, request, jsonify
import sys

app = Flask(__name__)


@app.post("/report")
def create_report():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    title = data.get("title")
    description = data.get("description")
    location = data.get("location")

    if not all(isinstance(x, str) for x in [title, description, location]):
        return jsonify({"error": "Fields 'title', 'description', 'location' must be strings"}), 400

    print(
        f"New report received: title={title!r}, description={description!r}, location={location!r}",
        file=sys.stdout,
        flush=True,
    )

    return jsonify({"status": "received"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

