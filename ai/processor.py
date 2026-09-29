import re


STOPWORDS = {
    "the", "and", "is", "in", "to", "of", "a", "an", "for",
    "on", "with", "that", "this", "are", "as", "by", "be",
    "or", "from", "it", "you", "your", "we", "our", "they",
    "their", "at", "which", "these", "those", "has", "have",
    "was", "were", "but", "not", "can", "may", "mainly",
    "through", "while", "also", "into", "used", "use",
    "than", "then", "its", "them", "there", "about",
    "using", "such", "some", "more", "most"
}


def _split_sentences(text):
    return [
        sentence.strip()
        for sentence in re.split(
            r"(?<=[.!?])\s+",
            text
        )
        if sentence.strip()
    ]


def _words(text):
    return re.findall(
        r"[A-Za-z]{3,}",
        text.lower()
    )


def _important_words(text):
    return [
        word
        for word in _words(text)
        if word not in STOPWORDS
    ]


def extract_concepts(sources, top_n=8):
    """
    Extract important concepts from the
    supplied study material.
    """

    all_text = " ".join(sources)

    concepts = []

    phrase_patterns = [
        r"\bcarbon dioxide\b",
        r"\bgreen plants\b",
        r"\blight energy\b",
        r"\bphotosynthesis\b",
        r"\bchlorophyll\b",
        r"\bglucose\b",
        r"\boxygen\b",
        r"\bwater\b",
        r"\bstomata\b",
        r"\broots\b",
        r"\bleaves\b"
    ]

    for pattern in phrase_patterns:

        match = re.search(
            pattern,
            all_text,
            re.IGNORECASE
        )

        if match:

            concept = match.group(0).lower()

            if concept not in concepts:
                concepts.append(concept)


    educational_keywords = [
        "process",
        "called",
        "defined",
        "means",
        "occurs",
        "produces",
        "absorbs",
        "requires",
        "important",
        "function",
        "known",
        "involves",
        "enters",
        "transported",
        "needed",
        "necessary"
    ]

    for sentence in _split_sentences(all_text):

        lower = sentence.lower()

        if any(
            keyword in lower
            for keyword in educational_keywords
        ):

            words = _important_words(sentence)

            for i in range(len(words) - 1):

                phrase = (
                    f"{words[i]} {words[i + 1]}"
                )

                if (
                    phrase not in concepts
                    and len(phrase) > 7
                ):
                    concepts.append(phrase)


    for word in _important_words(all_text):

        if (
            word not in concepts
            and len(word) >= 5
        ):
            concepts.append(word)


    return concepts[:top_n]


def _find_sentence_for_concept(
    concept,
    sources
):
    """
    Find sentences containing a concept.
    """

    matches = []

    for source_id, source in enumerate(
        sources,
        1
    ):

        for sentence in _split_sentences(source):

            if concept.lower() in sentence.lower():

                matches.append(
                    (sentence, source_id)
                )

    return matches


def generate_notes(
    topic,
    sources,
    concepts=None
):
    """
    Convert supplied study material into
    organized study notes.
    """

    if concepts is None:

        concepts = extract_concepts(
            sources
        )


    sections = []


    # =====================================
    # OVERVIEW
    # =====================================

    overview_sentences = []

    topic_words = _important_words(topic)

    for source_id, source in enumerate(
        sources,
        1
    ):

        for sentence in _split_sentences(source):

            lower = sentence.lower()

            mentions_topic = any(
                word in lower
                for word in topic_words
            )

            educational_sentence = any(
                keyword in lower
                for keyword in [
                    "process",
                    "defined",
                    "means",
                    "refers to",
                    "is the",
                    "are the"
                ]
            )

            if (
                mentions_topic
                or educational_sentence
            ):

                overview_sentences.append(
                    (sentence, source_id)
                )


    # Remove duplicate sentences.
    unique_overview = []

    seen = set()

    for sentence, source_id in overview_sentences:

        if sentence not in seen:

            seen.add(sentence)

            unique_overview.append(
                (sentence, source_id)
            )


    if unique_overview:

        sections.append({
            "heading": "Overview",
            "body": " ".join(
                item[0]
                for item in unique_overview[:2]
            ),
            "source_ids": sorted(
                set(
                    item[1]
                    for item in unique_overview[:2]
                )
            )
        })


    # =====================================
    # KEY CONCEPTS
    # =====================================

    used_sentences = set()

    for concept in concepts:

        matches = _find_sentence_for_concept(
            concept,
            sources
        )

        if not matches:
            continue


        selected = matches[:2]

        sentences = [
            item[0]
            for item in selected
        ]

        source_ids = sorted(
            set(
                item[1]
                for item in selected
            )
        )


        unique_sentences = list(
            dict.fromkeys(
                sentences
            )
        )


        body = " ".join(
            unique_sentences
        )


        if body in used_sentences:
            continue


        used_sentences.add(body)


        sections.append({
            "heading": concept.title(),
            "body": body,
            "source_ids": source_ids
        })


    # =====================================
    # IMPORTANT POINTS
    # =====================================

    important_sentences = []

    for source in sources:

        for sentence in _split_sentences(source):

            lower = sentence.lower()

            if any(
                keyword in lower
                for keyword in [
                    "important",
                    "requires",
                    "produces",
                    "absorbs",
                    "enters",
                    "transported",
                    "needed",
                    "necessary"
                ]
            ):

                important_sentences.append(
                    sentence
                )


    important_sentences = list(
        dict.fromkeys(
            important_sentences
        )
    )


    if important_sentences:

        sections.append({
            "heading": "Important Points",
            "body": " ".join(
                important_sentences[:3]
            ),
            "source_ids": list(
                range(
                    1,
                    len(sources) + 1
                )
            )
        })


    # =====================================
    # FALLBACK
    # =====================================

    if not sections:

        sentences = []

        for source in sources:

            sentences.extend(
                _split_sentences(source)
            )


        sections.append({
            "heading": topic or "Notes",
            "body": " ".join(
                sentences[:5]
            ),
            "source_ids": list(
                range(
                    1,
                    len(sources) + 1
                )
            )
        })


    return {
        "sections": sections
    }


def compute_coverage(
    concepts,
    notes
):
    """
    Check how well each important concept
    is represented in the generated notes.

    Statuses:
    - Covered
    - Partially covered
    - Needs review
    """

    coverage = []

    sections = notes.get(
        "sections",
        []
    )


    for concept in concepts:

        matched_sections = []

        matching_text = []


        for section_number, section in enumerate(
            sections,
            1
        ):

            heading = section.get(
                "heading",
                ""
            )

            body = section.get(
                "body",
                ""
            )

            text = (
                heading
                + " "
                + body
            ).lower()


            if concept.lower() in text:

                matched_sections.append(
                    section_number
                )

                matching_text.append(
                    body
                )


        # No mention at all.
        if not matched_sections:

            status = "Needs review"

            explanation = (
                "This concept was identified "
                "in the source material but "
                "was not found in the notes."
            )


        # Mentioned in one short section.
        elif len(
            " ".join(matching_text)
        ) < 120:

            status = "Partially covered"

            explanation = (
                "This concept appears in the "
                "notes, but the supporting "
                "explanation is limited."
            )


        # Enough supporting material.
        else:

            status = "Covered"

            explanation = (
                "This concept appears with "
                "supporting information in "
                "the notes."
            )


        coverage.append({
            "concept": concept,
            "status": status,
            "explanation": explanation,
            "matched_sections":
                matched_sections
        })


    return coverage