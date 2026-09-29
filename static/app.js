let currentHighlightColor = "#fff0a8";
let lastHighlight = null;


/* =====================================
   GENERATE NOTES
===================================== */

document
    .getElementById("generate")
    .addEventListener("click", async () => {

        const topic =
            document
                .getElementById("topic")
                .value
                .trim();

        const sourcesRaw =
            document
                .getElementById("sources")
                .value
                .trim();


        if (!topic || !sourcesRaw) {

            alert(
                "Please provide a topic and source material."
            );

            return;
        }


        const sources =
            sourcesRaw
                .split(/\n\s*\n/)
                .map(source => source.trim())
                .filter(Boolean);


        document
            .getElementById("coverage-list")
            .innerHTML =
            `<div class="empty-state">
                Generating your Coverage Check...
            </div>`;


        document
            .getElementById("notes-area")
            .innerHTML =
            `<div class="empty-notes">
                <span>✦</span>
                <p>Organizing your study material...</p>
            </div>`;


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


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Something went wrong."
                );
            }


            renderNotes(data.notes);

            renderCoverage(data.coverage);


        } catch (error) {

            document
                .getElementById("coverage-list")
                .innerHTML =
                `<div class="empty-state">
                    ${error.message}
                </div>`;


            document
                .getElementById("notes-area")
                .innerHTML = "";
        }
    });


/* =====================================
   NOTES
===================================== */

function renderNotes(notes) {

    const area =
        document.getElementById(
            "notes-area"
        );


    area.innerHTML = "";


    createToolbar(area);


    (notes.sections || [])
        .forEach((section, index) => {

            const heading =
                document.createElement("div");

            heading.className =
                "section-heading";

            heading.innerText =
                section.heading ||
                `Section ${index + 1}`;


            const body =
                document.createElement("div");

            body.className =
                "section-body";

            body.innerText =
                section.body || "";


            const sources =
                document.createElement("div");

            sources.className =
                "source-reference";


            const sourceIds =
                section.source_ids || [];


            sources.innerText =
                sourceIds.length > 0
                    ? `Source${sourceIds.length > 1 ? "s" : ""}: ${sourceIds.join(", ")}`
                    : "Source: Not specified";


            area.appendChild(heading);

            area.appendChild(body);

            area.appendChild(sources);


            enableTextHighlighting(body);
        });
}


/* =====================================
   ANNOTATION TOOLBAR
===================================== */

function createToolbar(area) {

    const toolbar =
        document.createElement("div");


    toolbar.className =
        "annotation-toolbar";


    toolbar.innerHTML = `
        <button
            class="tool-button active"
            data-color="#fff0a8"
            title="Yellow highlighter">
            🟨
        </button>

        <button
            class="tool-button"
            data-color="#ffd6df"
            title="Pink highlighter">
            🩷
        </button>

        <button
            class="tool-button"
            data-color="#dcd5f2"
            title="Lavender highlighter">
            🟪
        </button>

        <button
            class="tool-button"
            data-color="#cfe8d5"
            title="Green highlighter">
            🟩
        </button>

        <button
            class="tool-button"
            data-color="#cfe3f2"
            title="Blue highlighter">
            🟦
        </button>

        <span class="toolbar-divider"></span>

        <button
            id="undo-highlight"
            class="tool-button"
            title="Undo last highlight">
            ↩
        </button>

        <button
            id="clear-highlights"
            class="tool-button"
            title="Clear all highlights">
            🧹
        </button>
    `;


    area.prepend(toolbar);


    toolbar
        .querySelectorAll("[data-color]")
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    currentHighlightColor =
                        button.dataset.color;


                    toolbar
                        .querySelectorAll(
                            "[data-color]"
                        )
                        .forEach(btn => {

                            btn.classList.remove(
                                "active"
                            );
                        });


                    button.classList.add(
                        "active"
                    );
                }
            );
        });


    document
        .getElementById("undo-highlight")
        .addEventListener(
            "click",
            undoHighlight
        );


    document
        .getElementById("clear-highlights")
        .addEventListener(
            "click",
            clearHighlights
        );
}


/* =====================================
   TEXT HIGHLIGHTING
===================================== */

function enableTextHighlighting(element) {

    element.addEventListener(
        "mouseup",
        () => {

            const selection =
                window.getSelection();


            const selectedText =
                selection
                    .toString()
                    .trim();


            if (!selectedText) {
                return;
            }


            const range =
                selection.getRangeAt(0);


            if (
                !element.contains(
                    range.commonAncestorContainer
                )
            ) {
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


                lastHighlight = span;


            } catch (error) {

                console.log(
                    "Please select text within one sentence."
                );
            }


            selection.removeAllRanges();
        }
    );
}


/* =====================================
   UNDO
===================================== */

function undoHighlight() {

    if (!lastHighlight) {
        return;
    }


    const parent =
        lastHighlight.parentNode;


    while (
        lastHighlight.firstChild
    ) {

        parent.insertBefore(
            lastHighlight.firstChild,
            lastHighlight
        );
    }


    parent.removeChild(
        lastHighlight
    );


    lastHighlight = null;
}


/* =====================================
   CLEAR HIGHLIGHTS
===================================== */

function clearHighlights() {

    const highlights =
        document.querySelectorAll(
            ".highlight"
        );


    highlights.forEach(
        highlight => {

            const parent =
                highlight.parentNode;


            while (
                highlight.firstChild
            ) {

                parent.insertBefore(
                    highlight.firstChild,
                    highlight
                );
            }


            parent.removeChild(
                highlight
            );
        }
    );


    lastHighlight = null;
}


/* =====================================
   COVERAGE CHECK
===================================== */

function renderCoverage(list) {

    const element =
        document.getElementById(
            "coverage-list"
        );


    element.innerHTML = "";


    if (!list || list.length === 0) {

        element.innerHTML =
            `<div class="empty-state">
                No concepts found.
            </div>`;

        return;
    }


    /* Summary */

    const covered =
        list.filter(
            item =>
                item.status === "Covered"
        ).length;


    const partial =
        list.filter(
            item =>
                item.status ===
                "Partially covered"
        ).length;


    const needsReview =
        list.filter(
            item =>
                item.status ===
                "Needs review"
        ).length;


    const summary =
        document.createElement("div");


    summary.className =
        "coverage-summary";


    summary.innerHTML = `
        <strong>
            ${covered} of ${list.length}
            concepts covered
        </strong>

        <div class="coverage-summary-counts">

            <span>
                🟢 ${covered}
            </span>

            <span>
                🟡 ${partial}
            </span>

            <span>
                🔴 ${needsReview}
            </span>

        </div>
    `;


    element.appendChild(
        summary
    );


    /* Individual concepts */

    list.forEach(item => {

        const row =
            document.createElement(
                "div"
            );


        const statusClass =
            item.status
                .toLowerCase()
                .replaceAll(
                    " ",
                    "-"
                );


        row.className =
            `coverage-${statusClass}`;


        const concept =
            document.createElement(
                "strong"
            );


        concept.innerText =
            item.concept;


        const status =
            document.createElement(
                "span"
            );


        status.innerText =
            item.status;


        const explanation =
            document.createElement(
                "small"
            );


        explanation.innerText =
            item.explanation || "";


        row.appendChild(
            concept
        );


        row.appendChild(
            document.createTextNode(
                " "
            )
        );


        row.appendChild(
            status
        );


        row.appendChild(
            explanation
        );


        element.appendChild(
            row
        );
    });
}