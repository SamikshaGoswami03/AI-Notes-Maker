---

doc: prd
status: draft
-------------

# AI Notes Maker

## 1. Product Overview

AI Notes Maker is a student-focused study tool that turns selected study material into clear, organized, notebook-style notes.

The PoC focuses on a simple flow: the student provides a topic and study material, the system organizes the material into structured notes, and a Coverage Check identifies important concepts and shows whether they are covered in the generated notes.

## 2. Problem

Students often collect information from different places such as lectures, textbooks, PDFs, and web pages. Organizing all of that information into complete and understandable notes can take significant time.

A simple summarizer may produce shorter text while still leaving important concepts under-covered or difficult to identify.

AI Notes Maker addresses this by combining note generation with a Coverage Check.

## 3. Target Users

College and university students, particularly students preparing for exams or studying course topics.

The primary user is a student who wants to turn selected study material into a structured study reference without manually organizing every section.

## 4. User Journey

1. The student opens AI Notes Maker.
2. The student enters a topic, such as "Photosynthesis."
3. The student pastes at least two selected pieces of study material.
4. The student clicks "Generate Notes."
5. The system processes the supplied material.
6. The system generates structured notes with headings, explanations, definitions, examples where available, and source references.
7. The student reads the notes in the notebook-style interface.
8. The student opens the Coverage Check.
9. The Coverage Check displays important concepts identified from the supplied material and indicates whether each concept is covered, partially covered, or needs review.
10. The student can highlight useful parts of the generated notes.

## 5. Core Features

### 5.1 Topic Input

The student can enter the topic they are studying.

Example:

`Photosynthesis`

### 5.2 Study Material Input

The PoC allows the student to paste a small number of selected study materials.

Different sources are separated by a blank line.

For the PoC, the system does not need to fetch or crawl web pages automatically.

### 5.3 Structured Note Generation

The system converts the supplied material into organized study notes.

Notes should use:

* Clear section headings
* Definitions
* Explanations
* Important concepts
* Examples when available in the supplied material
* Source attribution

### 5.4 Coverage Check

The Coverage Check is the distinctive feature of the product.

It identifies important concepts from the supplied study material and compares them with the generated notes.

Each concept receives one of three statuses:

* Covered
* Partially covered
* Needs review

The feature helps students identify areas that may require another review instead of assuming that generated notes are automatically complete.

### 5.5 Source Attribution

Each generated section should identify the source material it came from where practical.

This allows the student to understand where information in the notes originated.

### 5.6 Notebook-Style Interface

Generated notes are displayed in a calm, readable digital notebook interface.

The interface uses:

* Paper-like background
* Notebook lines
* Clear typography
* Subtle visual accents
* Organized sections

### 5.7 Basic Highlighting

The student can select text in generated notes and apply a simple highlight.

The PoC includes a small set of highlight colors.

Advanced handwriting, drawing, pencil, and eraser functionality are outside the PoC.

## 6. Main Screens

### Screen 1: Home / Source Input

Contains:

* Topic input
* Study material input
* Generate Notes button
* Short guidance for providing multiple sources

### Screen 2: Notebook Viewer

Displays:

* Generated notes
* Section headings
* Explanations
* Source references
* Highlighting toolbar

### Screen 3: Coverage Check

Displays:

* Important concepts
* Coverage status
* Short explanation for each status
* Overall coverage summary

## 7. Functional Requirements

### FR1 — Topic

The system must accept a non-empty study topic.

### FR2 — Study Material

The system must accept student-provided study material.

### FR3 — Multiple Sources

The PoC should support at least two separate pieces of study material.

### FR4 — Note Generation

The system must generate structured notes from the supplied material.

### FR5 — Coverage Analysis

The system must identify important concepts and assign a coverage status.

### FR6 — Source References

The generated notes should provide identifiable source references.

### FR7 — Notebook Display

Generated notes must be displayed in the notebook-style interface.

### FR8 — Highlighting

The student must be able to highlight selected text.

### FR9 — End-to-End Flow

The complete flow from study material input to notes, source references, Coverage Check, and highlighting must work without manually editing generated results.

## 8. Non-Functional Requirements

### NFR1 — Simplicity

The PoC should remain small enough to build and demonstrate quickly.

### NFR2 — Readability

The generated notes and interface should be easy for students to read.

### NFR3 — Transparency

The system should clearly distinguish generated notes from the supplied source material and show source references.

### NFR4 — Honest Coverage

The Coverage Check should identify possible gaps but must not claim that it guarantees that no information has been missed.

### NFR5 — Beginner-Friendly Implementation

The implementation should use a simple architecture that is understandable and maintainable for a beginner.

## 9. Success Criteria

The PoC is successful when a student can:

1. Enter a topic.
2. Provide at least two pieces of study material.
3. Generate organized study notes.
4. See source references.
5. Open the Coverage Check.
6. Identify covered, partially covered, and review-needed concepts.
7. Highlight part of the generated notes.
8. Complete the entire flow in a short demonstration.

## 10. PoC Boundaries

The PoC does not require:

* Automatic crawling of every website
* Automatic collection of information from the entire internet
* PDF parsing
* Video-caption processing
* Browser extensions
* User accounts
* Collaboration
* Sharing
* Advanced handwriting
* Drawing tools
* Complex document editing
* Production-scale deployment
11. Future Possibilities

Future versions could allow AI Notes Maker to research a topic from selected online sources and automatically gather information before generating notes.

Other possible extensions include:

Automatic example generation
PDF support
Video-caption support
Browser extension
Pencil and eraser tools
Advanced annotations
User accounts
Collaboration
Shared study notebooks
