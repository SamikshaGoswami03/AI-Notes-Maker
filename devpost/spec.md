---

doc: spec
status: draft
-------------

# AI Notes Maker

## 1. Technical Overview

AI Notes Maker is a small web application designed to demonstrate an end-to-end study-note generation workflow.

For the PoC, the application uses a simple Flask backend and a browser-based HTML, CSS, and JavaScript frontend.

The PoC accepts a topic and student-provided study material, processes the material locally, generates structured notes, performs a Coverage Check, and displays the result in a notebook-style interface.

## 2. Technology Stack

### Frontend

* HTML
* CSS
* JavaScript

Responsibilities:

* Display the topic and study-material inputs
* Send the student's input to the backend
* Display generated notes
* Display Coverage Check results
* Provide basic text highlighting

### Backend

* Python
* Flask

Responsibilities:

* Receive the topic and study material
* Process the supplied material
* Extract important concepts
* Generate structured notes
* Calculate coverage
* Return results to the frontend

### Processing

The PoC uses a local processing module:

`ai/processor.py`

This keeps the application simple and avoids requiring a paid external AI API for the demonstration.

## 3. Project Structure

```text
AI-Notes-Maker/
│
├── ai/
│   └── processor.py
│
├── devpost/
│   ├── scope.md
│   ├── prd.md
│   └── spec.md
│
├── static/
│   ├── app.js
│   └── styles.css
│
├── templates/
│   └── index.html
│
├── app.py
├── requirements.txt
└── .gitignore
```

The learner profile is kept out of the public repository because it contains personal learning context.

## 4. Application Flow

```text
Student
   ↓
Enter Topic
   ↓
Paste Study Material
   ↓
Frontend JavaScript
   ↓
POST /generate
   ↓
Flask Backend
   ↓
Extract Concepts
   ↓
Generate Structured Notes
   ↓
Compute Coverage
   ↓
JSON Response
   ↓
Frontend Rendering
   ↓
Notebook + Coverage Check
   ↓
Student Highlights Notes
```

## 5. API Specification

### POST `/generate`

The frontend sends a JSON request.

Example:

```json
{
  "topic": "Photosynthesis",
  "sources": [
    "First study material...",
    "Second study material..."
  ]
}
```

### Successful Response

The backend returns JSON containing:

```json
{
  "topic": "Photosynthesis",
  "concepts": [],
  "notes": {
    "sections": []
  },
  "coverage": []
}
```

### Error Response

If the topic or study material is missing, the backend returns an HTTP 400 response with an error message.

## 6. Processing Pipeline

### Step 1 — Receive Input

The backend receives:

* Topic
* One or more pieces of student-provided study material

### Step 2 — Extract Concepts

`extract_concepts()` identifies important concepts from the supplied material.

The extracted concepts form the basis of the Coverage Check.

### Step 3 — Generate Notes

`generate_notes()` organizes the supplied information into structured sections.

Each section may contain:

* Heading
* Explanation
* Source identifiers

### Step 4 — Compute Coverage

`compute_coverage()` compares the extracted concepts with the generated notes.

Each concept receives a status:

* `Covered`
* `Partially covered`
* `Needs review`

### Step 5 — Return Results

The backend returns the topic, concepts, notes, and coverage data as JSON.

## 7. Frontend Behaviour

### Topic Input

The topic is read from:

`#topic`

The frontend trims whitespace and checks that the field is not empty.

### Source Input

Study material is read from:

`#sources`

Separate pieces of material are divided using blank lines.

### Generate Button

The Generate Notes button sends a POST request to:

`/generate`

While processing, the interface displays a temporary loading message.

### Notes Rendering

The JavaScript function:

`renderNotes()`

creates the notebook sections dynamically.

Each section displays:

* Heading
* Body
* Source reference

### Coverage Rendering

The JavaScript function:

`renderCoverage()`

displays:

* Overall coverage summary
* Individual concepts
* Coverage status
* Short explanations

### Highlighting

The user can select text in a generated note.

JavaScript wraps the selected text in a highlight element and applies the currently selected highlight color.

The toolbar also provides:

* Yellow highlight
* Pink highlight
* Lavender highlight
* Green highlight
* Blue highlight
* Undo last highlight
* Clear all highlights

## 8. Data Model

The application does not require a database for the PoC.

The main data is held temporarily during the request.

### Source

Conceptually:

```text
Source
- id
- text
```

### Note Section

```text
NoteSection
- heading
- body
- source_ids
```

### Coverage Item

```text
CoverageItem
- concept
- status
- explanation
```

## 9. Validation

The backend validates that:

* Topic is present
* Study material is present

The frontend also prevents generation when the required input fields are empty.

The PoC should encourage the student to provide at least two separate sources so that the Coverage Check can be demonstrated meaningfully.

## 10. Error Handling

If required input is missing, the backend returns an error response.

If generation fails, the frontend displays the error instead of showing incomplete results.

The application should not silently present fabricated source information.

## 11. Security and Privacy Considerations

The PoC does not require user accounts or permanent storage of student material.

Student-provided study material is processed for the current generation flow.

No passwords, authentication systems, or payment information are required.

## 12. Scope Constraints

The implementation intentionally does not include:

* Web crawling
* Server-side URL fetching
* PDF parsing
* Video processing
* User authentication
* Collaboration
* Cloud database
* Advanced document editing
* Handwriting recognition
* Complex drawing tools

These can be considered future extensions.

13. Local Development

Create and activate a Python virtual environment:

python -m venv .venv

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py

The Flask development server runs locally and can be opened in a browser.

14. Proof-of-Concept Demonstration

The demonstration should show the complete working flow:

Enter a topic.
Paste at least two study materials.
Click Generate Notes.
Show the generated notebook-style notes.
Show source references.
Open or display the Coverage Check.
Show covered, partially covered, and review-needed concepts where applicable.
Select a section of text.
Apply a highlight.
Show the final result.

15. Implementation Principle

The PoC prioritizes:

A complete end-to-end workflow
Simple architecture
Clear student experience
Transparent source attribution
A useful Coverage Check
A polished but lightweight interface