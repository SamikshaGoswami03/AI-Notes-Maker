let currentHighlightColor = "#fff0a8";
let lastHighlight = null;


// -----------------------------
// SOURCE MANAGEMENT
// -----------------------------

const addSourceButton =
    document.getElementById("add-source");

const sourcesContainer =
    document.getElementById("sources-container");


addSourceButton.addEventListener(
    "click",
    () => {

        const card =
            document.createElement("div");

        card.className =
            "source-card";

        const sourceNumber =
            sourcesContainer.querySelectorAll(
                ".source-card"
            ).length + 1;

        card.innerHTML = `
            <div class="source-card-header">

                <strong>
                    Source ${sourceNumber}
                </strong>

                <button
                    type="button"
                    class="remove-source"
                    title="Remove this source"
                >
                    ×
                </button>

            </div>

            <textarea
                class="source-input"
                placeholder="Paste your source here..."
            ></textarea>
        `;

        sourcesContainer.appendChild(
            card
        );

        const removeButton =
            card.querySelector(
                ".remove-source"
            );

        removeButton.addEventListener(
            "click",
            () => {

                card.remove();

                renumberSources();
            }
        );
    }
);


function renumberSources() {

    const cards =
        document.querySelectorAll(
            ".source-card"
        );

    cards.forEach(
        (card, index) => {

            const heading =
                card.querySelector(
                    ".source-card-header strong"
                );

            if (heading) {

                heading.textContent =
                    `Source ${index + 1}`;
            }
        }
    );
}


// -----------------------------
// GENERATE NOTES
// -----------------------------

const generateButton =
    document.getElementById(
        "generate"
    );


generateButton.addEventListener(
    "click",
    async () => {

        const topic =
            document
                .getElementById("topic")
                .value
                .trim();

        const sources =
            Array.from(
                document.querySelectorAll(
                    ".source-input"
                )
            )
                .map(
                    (input) =>
                        input.value.trim()
                )
                .filter(
                    (source) =>
                        source.length > 0
                );


        if (!topic) {

            alert(
                "Please enter a topic."
            );

            return;
        }


        if (sources.length < 2) {

            alert(
                "Please provide at least 2 sources."
            );

            return;
        }


        lastHighlight = null;


        generateButton.disabled =
            true;

        generateButton.textContent =
            "Generating...";


        try {

            const response =
                await fetch(
                    "/generate",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            topic: topic,
                            sources: sources
                        })
                    }
                );


            let data;

            try {

                data =
                    await response.json();

            }
            catch (jsonError) {

                throw new Error(
                    "The server returned an invalid response."
                );
            }


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Unable to generate notes."
                );
            }


            if (
                !data.notes ||
                !Array.isArray(
                    data.notes.sections
                )
            ) {

                throw new Error(
                    "The AI returned an invalid notes format."
                );
            }


            renderNotes(
                data.topic,
                data.notes
            );


            applyTopicTheme(
                data.topic
            );


            renderCoverage(
                data.concepts,
                data.coverage
            );


        }
        catch (error) {

            console.error(
                "Generation error:",
                error
            );

            alert(
                error.message ||
                "Something went wrong while generating your notes."
            );

        }
        finally {

            generateButton.disabled =
                false;

            generateButton.textContent =
                "Generate Notes";
        }
    }
);


// -----------------------------
// RENDER NOTES
// -----------------------------

function renderNotes(
    topic,
    notes
) {

    const area =
        document.getElementById(
            "notes-area"
        );


    /*
     * index.html already contains
     * the notebook header.
     */

    area.innerHTML = "";


    createToolbar(
        area
    );


    const sections =
        notes &&
        Array.isArray(
            notes.sections
        )
            ? notes.sections
            : [];


    if (
        sections.length === 0
    ) {

        const empty =
            document.createElement(
                "div"
            );

        empty.className =
            "empty-notes";

        empty.innerHTML = `
            <span>✎</span>

            <p>
                No notes were generated.
            </p>
        `;

        area.appendChild(
            empty
        );

        setupHighlighting();

        return;
    }


    sections.forEach(
        (
            section,
            index
        ) => {

            const heading =
                document.createElement(
                    "div"
                );

            heading.className =
                "section-heading";

            heading.textContent =
                section.heading ||
                `Section ${index + 1}`;


            /*
             * Every note heading receives a normalized
             * key so Coverage Check can find it later.
             */
            heading.dataset.noteKey =
                normalizeNoteKey(
                    section.heading ||
                    `Section ${index + 1}`
                );


            const body =
                document.createElement(
                    "div"
                );

            body.className =
                "section-body";

            body.textContent =
                section.body ||
                "";


            const sourceReference =
                document.createElement(
                    "div"
                );

            sourceReference.className =
                "source-reference";


            const sourceIds =
                Array.isArray(
                    section.source_ids
                )
                    ? section.source_ids
                    : [];


            if (
                sourceIds.length > 0
            ) {

                sourceReference.textContent =
                    `Source${
                        sourceIds.length > 1
                            ? "s"
                            : ""
                    }: ${sourceIds.join(", ")}`;

            }
            else {

                sourceReference.textContent =
                    "Source: Not specified";
            }


            area.appendChild(
                heading
            );

            area.appendChild(
                body
            );

            area.appendChild(
                sourceReference
            );


            enableTextHighlighting(
                body
            );
        }
    );


    setupHighlighting();
}


// -----------------------------
// COVERAGE CHECK
// -----------------------------

function renderCoverage(
    concepts,
    coverage
) {

    const list =
        document.getElementById(
            "coverage-list"
        );


    list.innerHTML = "";


    if (
        !Array.isArray(concepts) ||
        concepts.length === 0
    ) {

        list.innerHTML = `
            <div class="empty-state">
                No important concepts were identified.
            </div>
        `;

        return;
    }


    const results =
        Array.isArray(coverage)
            ? coverage
            : [];


    let coveredCount = 0;
    let partialCount = 0;
    let reviewCount = 0;


    // Count statuses
    concepts.forEach(
        (
            concept,
            index
        ) => {

            const result =
                results[index] || {};

            const status =
                String(
                    result.status ||
                    "Needs review"
                ).toLowerCase();


            if (
                status === "covered"
            ) {

                coveredCount++;

            }
            else if (
                status === "partially covered"
            ) {

                partialCount++;

            }
            else {

                reviewCount++;
            }
        }
    );


    // Summary
    const summary =
        document.createElement(
            "div"
        );

    summary.className =
        "coverage-summary";

    summary.innerHTML = `
        <strong>
            Coverage Summary
        </strong>

        <div class="coverage-summary-counts">

            <span>
                ✓ ${coveredCount} covered
            </span>

            <span>
                ◐ ${partialCount} partial
            </span>

            <span>
                ! ${reviewCount} review
            </span>

        </div>
    `;

    list.appendChild(
        summary
    );


    // Individual concepts
    concepts.forEach(
        (
            concept,
            index
        ) => {

            const result =
                results[index] || {};


            const status =
                result.status ||
                "Needs review";


            const normalizedStatus =
                status.toLowerCase();


            let className =
                "coverage-needs-review";


            if (
                normalizedStatus ===
                "covered"
            ) {

                className =
                    "coverage-covered";

            }
            else if (
                normalizedStatus ===
                "partially covered"
            ) {

                className =
                    "coverage-partially-covered";
            }


            const item =
                document.createElement(
                    "div"
                );

            item.className =
                className;


            /*
             * Coverage item is now connected to the
             * corresponding note section.
             */
            const noteKey =
                normalizeNoteKey(
                    concept
                );

            item.dataset.noteKey =
                noteKey;


            const title =
                document.createElement(
                    "strong"
                );

            title.textContent =
                concept;


            const badge =
                document.createElement(
                    "span"
                );

            badge.textContent =
                status;


            item.appendChild(
                title
            );

            item.appendChild(
                badge
            );


            if (
                result.explanation
            ) {

                const explanation =
                    document.createElement(
                        "small"
                    );

                explanation.textContent =
                    result.explanation;

                item.appendChild(
                    explanation
                );
            }


            /*
             * Clicking a Coverage concept jumps
             * directly to its note.
             */
            item.addEventListener(
                "click",
                () => {

                    jumpToNote(
                        noteKey
                    );
                }
            );


            /*
             * Give the user a visual hint that the
             * Coverage item is interactive.
             */
            item.style.cursor =
                "pointer";


            list.appendChild(
                item
            );
        }
    );
}


// -----------------------------
// COVERAGE → NOTE CONNECTION
// -----------------------------

function normalizeNoteKey(
    value
) {

    return String(
        value || ""
    )
        .toLowerCase()
        .replace(
            /[^a-z0-9]+/g,
            " "
        )
        .trim()
        .replace(
            /\s+/g,
            " "
        );
}


function jumpToNote(
    noteKey
) {

    if (!noteKey) {

        return;
    }


    const noteHeadings =
        document.querySelectorAll(
            "#notes-area .section-heading"
        );


    let matchingHeading = null;


    noteHeadings.forEach(
        (heading) => {

            const headingKey =
                normalizeNoteKey(
                    heading.dataset.noteKey ||
                    heading.textContent
                );


            if (
                headingKey === noteKey &&
                !matchingHeading
            ) {

                matchingHeading =
                    heading;
            }
        }
    );


    /*
     * No matching note exists.
     * This is normal for a "Needs review"
     * concept that the AI didn't put into notes.
     */
    if (!matchingHeading) {

        return;
    }


    matchingHeading.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });


    highlightNoteSection(
        matchingHeading
    );
}


function highlightNoteSection(
    heading
) {

    const body =
        heading.nextElementSibling;


    const sourceReference =
        body
            ? body.nextElementSibling
            : null;


    /*
     * Save original inline styles.
     */
    const originalHeadingBackground =
        heading.style.backgroundColor;

    const originalHeadingBoxShadow =
        heading.style.boxShadow;

    const originalBodyBackground =
        body
            ? body.style.backgroundColor
            : "";


    /*
     * Temporary visual focus.
     */
    heading.style.transition =
        "background-color 0.25s ease, box-shadow 0.25s ease";

    heading.style.backgroundColor =
        "#fff0a8";

    heading.style.boxShadow =
        "0 0 0 4px rgba(243, 217, 223, 0.7)";


    if (body) {

        body.style.transition =
            "background-color 0.25s ease";

        body.style.backgroundColor =
            "rgba(255, 240, 168, 0.22)";
    }


    setTimeout(
        () => {

            heading.style.backgroundColor =
                originalHeadingBackground;

            heading.style.boxShadow =
                originalHeadingBoxShadow;


            if (body) {

                body.style.backgroundColor =
                    originalBodyBackground;
            }

        },
        1400
    );
}


// -----------------------------
// ANNOTATION TOOLBAR
// -----------------------------

function createToolbar(
    area
) {

    const toolbar =
        document.createElement(
            "div"
        );

    toolbar.className =
        "annotation-toolbar";


    toolbar.innerHTML = `
        <button
            type="button"
            class="tool-button active"
            data-color="#fff0a8"
            title="Yellow highlighter"
        >
            🟨
        </button>

        <button
            type="button"
            class="tool-button"
            data-color="#ffd6df"
            title="Pink highlighter"
        >
            🩷
        </button>

        <button
            type="button"
            class="tool-button"
            data-color="#dcd5f2"
            title="Lavender highlighter"
        >
            🟪
        </button>

        <button
            type="button"
            class="tool-button"
            data-color="#cfe8d5"
            title="Green highlighter"
        >
            🟩
        </button>

        <button
            type="button"
            class="tool-button"
            data-color="#cfe3f2"
            title="Blue highlighter"
        >
            🟦
        </button>

        <span class="toolbar-divider"></span>

        <button
            type="button"
            id="undo-highlight"
            class="tool-button"
            title="Undo last highlight"
        >
            ↩
        </button>

        <button
            type="button"
            id="clear-highlights"
            class="tool-button"
            title="Clear all highlights"
        >
            🧹
        </button>
    `;


    area.appendChild(
        toolbar
    );
}


// -----------------------------
// TEXT HIGHLIGHTING
// -----------------------------

function enableTextHighlighting(
    element
) {

    element.addEventListener(
        "mouseup",
        () => {

            const selection =
                window.getSelection();


            if (
                !selection ||
                selection.isCollapsed
            ) {

                return;
            }


            const selectedText =
                selection
                    .toString()
                    .trim();


            if (!selectedText) {

                return;
            }


            const range =
                selection.getRangeAt(
                    0
                );


            if (
                !element.contains(
                    range.commonAncestorContainer
                )
            ) {

                selection.removeAllRanges();

                return;
            }


            const span =
                document.createElement(
                    "span"
                );

            span.className =
                "highlight";

            span.style.backgroundColor =
                currentHighlightColor;


            try {

                range.surroundContents(
                    span
                );

                lastHighlight =
                    span;

            }
            catch (error) {

                console.log(
                    "Highlight selection could not be applied. Try selecting text within one sentence or section."
                );
            }


            selection.removeAllRanges();
        }
    );
}


// -----------------------------
// HIGHLIGHTING CONTROLS
// -----------------------------

function setupHighlighting() {

    const colorButtons =
        document.querySelectorAll(
            ".tool-button[data-color]"
        );


    colorButtons.forEach(
        (button) => {

            button.onclick = () => {

                colorButtons.forEach(
                    (item) => {

                        item.classList.remove(
                            "active"
                        );
                    }
                );


                button.classList.add(
                    "active"
                );


                currentHighlightColor =
                    button.dataset.color;
            };
        }
    );


    const undoButton =
        document.getElementById(
            "undo-highlight"
        );


    if (undoButton) {

        undoButton.onclick = () => {

            if (!lastHighlight) {

                return;
            }


            const parent =
                lastHighlight.parentNode;


            if (!parent) {

                lastHighlight =
                    null;

                return;
            }


            while (
                lastHighlight.firstChild
            ) {

                parent.insertBefore(
                    lastHighlight.firstChild,
                    lastHighlight
                );
            }


            lastHighlight.remove();

            lastHighlight =
                null;
        };
    }


    const clearButton =
        document.getElementById(
            "clear-highlights"
        );


    if (clearButton) {

        clearButton.onclick = () => {

            document
                .querySelectorAll(
                    ".highlight"
                )
                .forEach(
                    (highlight) => {

                        const parent =
                            highlight.parentNode;


                        if (!parent) {

                            return;
                        }


                        while (
                            highlight.firstChild
                        ) {

                            parent.insertBefore(
                                highlight.firstChild,
                                highlight
                            );
                        }


                        highlight.remove();
                    }
                );


            lastHighlight =
                null;
        };
    }
}


// -----------------------------
// SECURITY / HTML ESCAPING
// -----------------------------

function escapeHtml(
    value
) {

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}


// -----------------------------
// TOPIC-AWARE NOTEBOOK THEME
// -----------------------------

function applyTopicTheme(
    topic
) {

    const notebook =
        document.querySelector(
            ".notebook"
        );


    if (!notebook) {

        return;
    }


    const text =
        String(topic)
            .toLowerCase();


    notebook.classList.remove(
        "theme-science",
        "theme-math",
        "theme-programming",
        "theme-history",
        "theme-business",
        "theme-general"
    );


    if (
        text.includes("biology") ||
        text.includes("photosynthesis") ||
        text.includes("cell") ||
        text.includes("plant") ||
        text.includes("chemistry") ||
        text.includes("physics") ||
        text.includes("science")
    ) {

        notebook.classList.add(
            "theme-science"
        );

    }
    else if (
        text.includes("math") ||
        text.includes("algebra") ||
        text.includes("geometry") ||
        text.includes("calculus") ||
        text.includes("statistics")
    ) {

        notebook.classList.add(
            "theme-math"
        );

    }
    else if (
        text.includes("programming") ||
        text.includes("python") ||
        text.includes("javascript") ||
        text.includes("coding") ||
        text.includes("computer") ||
        text.includes("software") ||
        text.includes("database") ||
        text.includes("dbms")
    ) {

        notebook.classList.add(
            "theme-programming"
        );

    }
    else if (
        text.includes("history") ||
        text.includes("ancient") ||
        text.includes("war") ||
        text.includes("civilization") ||
        text.includes("geography")
    ) {

        notebook.classList.add(
            "theme-history"
        );

    }
    else if (
        text.includes("business") ||
        text.includes("economics") ||
        text.includes("marketing") ||
        text.includes("finance")
    ) {

        notebook.classList.add(
            "theme-business"
        );

    }
    else {

        notebook.classList.add(
            "theme-general"
        );
    }
}