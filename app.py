from flask import Flask, render_template, request, jsonify

from ai.processor import (
    generate_study_package,
    compute_coverage
)


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():

    data = request.get_json(
        silent=True
    ) or {}

    topic = data.get(
        "topic",
        ""
    ).strip()

    sources = data.get(
        "sources",
        []
    )

    sources = [
        source.strip()
        for source in sources
        if isinstance(source, str)
        and source.strip()
    ]

    if not topic:
        return jsonify({
            "error": "Please enter a topic."
        }), 400

    if len(sources) < 2:
        return jsonify({
            "error": "Please provide at least 2 sources."
        }), 400

    package = generate_study_package(
        topic,
        sources
    )

    concepts = package.get(
        "concepts",
        []
    )

    notes = package.get(
        "notes",
        {"sections": []}
    )

    coverage = compute_coverage(
        concepts,
        notes
    )

    return jsonify({
        "topic": topic,
        "concepts": concepts,
        "notes": notes,
        "coverage": coverage
    })


if __name__ == "__main__":
    app.run(
        debug=True
    )