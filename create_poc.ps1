mkdir -Force ai
mkdir -Force templates
mkdir -Force static
mkdir -Force devpost

@'
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
'@ | Out-File -Encoding utf8 app.py

@'
def extract_concepts(sources):
    return [
        "Main concept",
        "Key idea",
        "Important definition"
    ]

def generate_notes(topic, sources):
    return {
        'sections': [
            {
                'heading': topic,
                'body': 'Your AI-generated notes will appear here.',
                'source_ids': list(range(1, len(sources) + 1))
            }
        ]
    }

def compute_coverage(concepts, notes):
    coverage = []

    for concept in concepts:
        coverage.append({
            'concept': concept,
            'status': 'Covered',
            'matched_sections': [1]
        })

    return coverage
'@ | Out-File -Encoding utf8 ai\processor.py

@'
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>AI Notes Maker</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>

<body>

<main class="container">

    <h1>AI Notes Maker</h1>

    <section id="input">

        <label>Topic</label>

        <input
            id="topic"
            placeholder="Enter study topic"
        >

        <label>Sources</label>

        <textarea
            id="sources"
            placeholder="Paste your source material here. Separate different sources with a blank line."
        ></textarea>

        <button id="generate">
            Generate Notes
        </button>

    </section>

    <section id="results">

        <aside id="coverage" class="panel">

            <h2>Coverage Check</h2>

            <div id="coverage-list">
                No results yet.
            </div>

        </aside>

        <article id="notebook" class="notebook">

            <h2>Notebook</h2>

            <div id="notes-area">
                No notes yet.
            </div>

        </article>

    </section>

</main>

<script src="/static/app.js"></script>

</body>
</html>
'@ | Out-File -Encoding utf8 templates\index.html

@'
body {
    font-family: system-ui, sans-serif;
    background: #fbfaf7;
    color: #222;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 980px;
    margin: 0 auto;
}

label {
    display: block;
    margin-top: 12px;
    font-weight: 600;
}

#topic {
    width: 100%;
    padding: 8px;
    font-size: 16px;
    box-sizing: border-box;
}

#sources {
    width: 100%;
    height: 180px;
    padding: 8px;
    font-size: 14px;
    box-sizing: border-box;
}

#generate {
    margin-top: 10px;
    padding: 10px 16px;
    font-size: 16px;
}

#results {
    display: flex;
    gap: 20px;
    margin-top: 20px;
}

.panel {
    width: 280px;
    background: white;
    padding: 12px;
    border-radius: 8px;
}

.notebook {
    flex: 1;
    background: white;
    padding: 20px;
    border-radius: 8px;
}

.section-heading {
    font-size: 20px;
    margin-top: 16px;
}

.section-body {
    margin-top: 8px;
    line-height: 1.5;
}

.highlight {
    background: yellow;
}
'@ | Out-File -Encoding utf8 static\styles.css

@'
document.getElementById("generate").addEventListener("click", async () => {

    const topic = document.getElementById("topic").value.trim();

    const sourcesRaw =
        document.getElementById("sources").value.trim();

    if (!topic || !sourcesRaw) {
        alert("Please provide a topic and source material.");
        return;
    }

    const sources = sourcesRaw
        .split(/\n\s*\n/)
        .map(s => s.trim())
        .filter(Boolean);

    document.getElementById("coverage-list").innerText =
        "Generating...";

    document.getElementById("notes-area").innerText =
        "Generating...";

    const resp = await fetch("/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            topic: topic,
            sources: sources
        })
    });

    const data = await resp.json();

    if (!resp.ok) {
        document.getElementById("coverage-list").innerText =
            data.error || "Error";
        return;
    }

    renderNotes(data.notes);
    renderCoverage(data.coverage);
});


function renderNotes(notes) {

    const area = document.getElementById("notes-area");

    area.innerHTML = "";

    (notes.sections || []).forEach((section, index) => {

        const heading = document.createElement("div");

        heading.className = "section-heading";

        heading.innerText =
            section.heading || `Section ${index + 1}`;

        const body = document.createElement("div");

        body.className = "section-body";

        body.innerText = section.body || "";

        body.addEventListener("mouseup", () => {

            const selection =
                window.getSelection().toString();

            if (selection) {
                body.innerHTML =
                    body.innerHTML.replace(
                        selection,
                        `<span class="highlight">${selection}</span>`
                    );
            }

        });

        area.appendChild(heading);
        area.appendChild(body);

    });
}


function renderCoverage(list) {

    const element =
        document.getElementById("coverage-list");

    element.innerHTML = "";

    list.forEach(item => {

        const row = document.createElement("div");

        row.innerText =
            `${item.concept} — ${item.status}`;

        element.appendChild(row);

    });
}
'@ | Out-File -Encoding utf8 static\app.js

@'
Flask
'@ | Out-File -Encoding utf8 requirements.txt

@'
# AI Notes Maker

Minimal Flask proof-of-concept.

Features:
- Topic input
- Pasted source material
- Notes display
- Coverage Check
- Basic highlighting
'@ | Out-File -Encoding utf8 README.md

Write-Host ""
Write-Host "PoC files created successfully!"
Write-Host ""