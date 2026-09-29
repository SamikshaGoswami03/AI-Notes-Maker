from flask import Flask, render_template, request, jsonify
from ai.processor import extract_concepts, generate_notes, compute_coverage

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    topic = data.get('topic', '').strip()
    sources = data.get('sources', [])

    if not topic or not sources:
        return jsonify({'error': 'Topic and at least one source are required.'}), 400

    concepts = extract_concepts(sources)
    notes = generate_notes(topic, sources)
    coverage = compute_coverage(concepts, notes)

    return jsonify({
        'topic': topic,
        'concepts': concepts,
        'notes': notes,
        'coverage': coverage
    })

if __name__ == '__main__':
    app.run(debug=True)
