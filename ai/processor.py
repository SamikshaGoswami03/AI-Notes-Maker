import json
import re
import urllib.error
import urllib.request

from difflib import SequenceMatcher


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"


# ============================================================
# Generic language filters
# ============================================================

STOPWORDS = {
    "the", "and", "is", "in", "to", "of", "a", "an", "for",
    "on", "with", "that", "this", "are", "as", "by", "be",
    "or", "from", "it", "you", "your", "we", "our", "they",
    "their", "at", "which", "these", "those", "has", "have",
    "was", "were", "but", "not", "can", "may", "mainly",
    "through", "while", "also", "into", "used", "use",
    "than", "then", "its", "them", "there", "about",
    "using", "such", "some", "more", "most", "very",
    "been", "being", "when", "where", "what", "who",
    "how", "why", "because", "during", "between", "each",
    "other", "one", "two", "three", "first", "second",
    "many", "much", "often", "usually"
}


GENERIC_WORDS = {
    "thing", "things",
    "example", "examples",
    "information",
    "content",
    "material", "materials",
    "source", "sources",
    "topic", "topics",
    "part", "parts",
    "aspect", "aspects",
    "way", "ways",
    "type", "types",
    "kind", "kinds",
    "result", "results",
    "fact", "facts",
    "idea", "ideas",
    "point", "points",
    "detail", "details",
    "section", "sections"
}


GENERIC_ACTION_WORDS = {
    "store", "stores", "stored", "storing",
    "organize", "organizes", "organized", "organizing",
    "organise", "organises", "organised", "organising",
    "retrieve", "retrieves", "retrieved", "retrieving",
    "manage", "manages", "managed", "managing",
    "allow", "allows", "allowed", "allowing",
    "create", "creates", "created", "creating",
    "provide", "provides", "provided", "providing",
    "include", "includes", "included", "including",
    "contain", "contains", "contained", "containing",
    "make", "makes", "made", "making",
    "support", "supports", "supported", "supporting",
    "refer", "refers", "referred", "referring",
    "query", "queries", "querying",
    "manipulate", "manipulates", "manipulated",
    "manipulating"
}


# These are ordinary words that may appear in uppercase
# in source material, but are NOT acronyms by themselves.
COMMON_UPPERCASE_WORDS = {
    "A", "AN", "THE",
    "AND", "OR", "NOT",
    "PRIMARY", "FOREIGN", "KEY", "KEYS",
    "UNIQUE", "NULL", "CHECK",
    "TABLE", "TABLES", "ROW", "ROWS",
    "COLUMN", "COLUMNS",
    "RECORD", "RECORDS",
    "ATTRIBUTE", "ATTRIBUTES",
    "CREATE", "INSERT", "UPDATE", "DELETE",
    "SELECT", "FROM", "WHERE",
    "COMMON", "IMPORTANT",
    "FIRST", "SECOND",
    "SOURCE", "SOURCES",
    "USER", "USERS",
    "SYSTEM", "SYSTEMS",
    "SOFTWARE",
    "APPLICATION", "APPLICATIONS"
}


# Words that make a concept look like a sentence.
GRAMMAR_WORDS = {
    "is", "are", "was", "were",
    "means", "refers",
    "consists", "called", "known",
    "used", "commonly",
    "typically", "usually", "often",
    "includes", "contains",
    "provides", "allows", "enables"
}


# Verbs / predicate words that must never be part of a
# concept heading.
PREDICATE_WORDS = {
    "uniquely",
    "identifies",
    "identify",
    "identifying",
    "represents",
    "represent",
    "representing",
    "describes",
    "describe",
    "describing",
    "measures",
    "measure",
    "measuring",
    "connects",
    "connect",
    "connecting",
    "controls",
    "control",
    "controlling",
    "contains",
    "contain",
    "containing",
    "prevents",
    "prevent",
    "preventing",
    "maintains",
    "maintain",
    "maintaining",
    "supports",
    "support",
    "supporting",
    "helps",
    "help",
    "helping",
    "provides",
    "provide",
    "providing",
    "enables",
    "enable",
    "enabling"
}


# Words that usually indicate a sentence subject rather
# than a study concept.
BAD_CONCEPT_STARTS = {
    "a", "an", "the",
    "this", "that", "these", "those",
    "some", "many", "each", "every",
    "all", "any", "either", "neither",
    "common", "important", "different", "main"
}


# Weak standalone words that should not become concepts.
GENERIC_SINGLE_WORDS = {
    "key", "keys",
    "thing", "things",
    "information",
    "content",
    "material",
    "topic",
    "part",
    "aspect",
    "way",
    "type",
    "kind",
    "result",
    "fact",
    "idea",
    "point",
    "detail",
    "details",
    "section",
    "sections",
    "example",
    "examples",
    "user",
    "users",
    "system",
    "systems"
}


# ============================================================
# Basic text helpers
# ============================================================

def _split_sentences(text):
    return [
        sentence.strip()
        for sentence in re.split(
            r"(?<=[.!?])\s+",
            str(text)
        )
        if sentence.strip()
    ]


def _normalize_text(text):
    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9\s-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def _normalize_concept(concept):
    return _normalize_text(concept)


def _phrase_in_text(phrase, text):
    """
    Whole-word / whole-phrase matching.

    Examples:
        row does NOT match rows
        se does NOT match these
    """

    phrase = _normalize_concept(phrase)
    text = _normalize_text(text)

    if not phrase:
        return False

    return bool(
        re.search(
            rf"(?<![a-z0-9])"
            rf"{re.escape(phrase)}"
            rf"(?![a-z0-9])",
            text
        )
    )


def _title_case_concept(concept, sources=None):
    """
    Format headings:

        database management system
        -> Database Management System

        primary key
        -> Primary Key

        DBMS
        -> DBMS

        SQL
        -> SQL
    """

    if not concept:
        return ""

    if sources is None:
        sources = []

    acronym_map = {}

    for source in sources:
        matches = re.findall(
            r"\b[A-Z][A-Z0-9-]{1,8}\b",
            source
        )

        for word in matches:
            if word not in COMMON_UPPERCASE_WORDS:
                acronym_map[word.lower()] = word

    result = []

    for word in str(concept).strip().split():
        lower_word = word.lower()

        if lower_word in acronym_map:
            result.append(
                acronym_map[lower_word]
            )

        elif re.fullmatch(
            r"[A-Z0-9-]{2,9}",
            word
        ):
            result.append(word)

        else:
            result.append(
                word[:1].upper()
                + word[1:].lower()
            )

    return " ".join(result)


# ============================================================
# Ollama
# ============================================================

def _call_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(
            payload
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=180
        ) as response:

            raw = response.read().decode(
                "utf-8"
            )

        result = json.loads(raw)

        return result.get(
            "response",
            ""
        )

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError
    ):
        return None


# ============================================================
# Source relationships
# ============================================================

def _source_alias_pairs(sources):
    """
    Detect generic full-form / acronym relationships.

    Example:
        database management system (DBMS)

    becomes:
        database management system <-> dbms
    """

    pairs = []

    pattern = (
        r"\b([A-Za-z][A-Za-z0-9-]*"
        r"(?:\s+[A-Za-z][A-Za-z0-9-]*){1,7})"
        r"\s*\(([A-Z][A-Z0-9-]{1,8})\)"
    )

    for source in sources:

        for match in re.finditer(
            pattern,
            source
        ):

            full_form = re.sub(
                r"^(?:a|an|the)\s+",
                "",
                match.group(1).strip(),
                flags=re.IGNORECASE
            ).strip()

            acronym = match.group(2).strip()

            if len(full_form.split()) >= 2:
                pairs.append(
                    (
                        _normalize_concept(full_form),
                        _normalize_concept(acronym)
                    )
                )

    return pairs


def _is_real_acronym(word, sources):
    if not isinstance(
        word,
        str
    ):
        return False

    word = word.strip()

    if not re.fullmatch(
        r"[A-Z][A-Z0-9-]{1,8}",
        word
    ):
        return False

    if word in COMMON_UPPERCASE_WORDS:
        return False

    normalized_word = word.lower()

    for _, acronym in _source_alias_pairs(
        sources
    ):
        if normalized_word == acronym:
            return True

    return len(word) <= 6


# ============================================================
# Definition detection
# ============================================================

def _explicit_definition_candidates(sources):
    """
    Find phrases that are genuinely introduced as concepts.

    Good:
        Photosynthesis is...
        A primary key uniquely identifies...
        Database constraints help...

    Bad:
        Each row represents...
        Every student receives...
    """

    candidates = set()

    patterns = [

        # X is / means / refers to ...
        r"^(?!each\b|every\b|all\b|these\b|those\b)"
        r"(?:a|an|the)?\s*"
        r"([A-Za-z][A-Za-z0-9-]*"
        r"(?:\s+[A-Za-z][A-Za-z0-9-]*){0,5}?)"
        r"\s+"
        r"(?:is|are|was|were|means|refers to|"
        r"is called|is known as)\b",

        # A primary key uniquely identifies...
        r"^(?:a|an|the)\s+"
        r"([A-Za-z][A-Za-z0-9-]*"
        r"(?:\s+[A-Za-z][A-Za-z0-9-]*){0,5}?)"
        r"\s+"
        r"(?:uniquely identifies|identifies|"
        r"represents|describes|measures|"
        r"connects|controls|contains|includes|"
        r"provides|enables|helps|help|"
        r"prevents|prevent|maintains|maintain|"
        r"supports|support)\b",

        # Database constraints help...
        r"^(?!each\b|every\b|all\b|these\b|those\b|"
        r"this\b|that\b)"
        r"([A-Za-z][A-Za-z0-9-]*"
        r"(?:\s+[A-Za-z][A-Za-z0-9-]*){0,5}?)"
        r"\s+"
        r"(?:helps|help|prevents|prevent|"
        r"maintains|maintain|supports|support|"
        r"provides|provide|enables|enable)\b"
    ]

    for source in sources:

        for sentence in _split_sentences(
            source
        ):

            for pattern in patterns:

                match = re.search(
                    pattern,
                    sentence.strip(),
                    flags=re.IGNORECASE
                )

                if not match:
                    continue

                candidate = match.group(
                    1
                ).strip()

                candidate = candidate.strip(
                    " ,:;-"
                )

                words = _normalize_concept(
                    candidate
                ).split()

                if not words:
                    continue

                if words[0] in BAD_CONCEPT_STARTS:
                    continue

                candidates.add(
                    _normalize_concept(
                        candidate
                    )
                )

                break

    return candidates


# ============================================================
# Concept cleaning / validation
# ============================================================

def _clean_concept_text(
    concept,
    sources
):
    if not isinstance(
        concept,
        str
    ):
        return ""

    concept = concept.strip()

    # Remove surrounding quotes/backticks.
    concept = concept.strip(
        "\"'` "
    )

    # Remove:
    # Database Management System (DBMS)
    concept = re.sub(
        r"\s*\([A-Z][A-Z0-9-]{1,8}\)\s*$",
        "",
        concept
    ).strip()

    concept = concept.strip(
        ".,;:!?- "
    )

    normalized = _normalize_concept(
        concept
    )

    # Remove:
    # database management system DBMS
    for full_form, acronym in _source_alias_pairs(
        sources
    ):

        if normalized == (
            f"{full_form} {acronym}"
        ):

            words = concept.split()

            if len(words) > 1:
                concept = " ".join(
                    words[:-1]
                )

            break

    return concept.strip()


def _is_good_concept(
    concept,
    sources
):
    if not isinstance(
        concept,
        str
    ):
        return False

    concept = _clean_concept_text(
        concept,
        sources
    )

    if not concept:
        return False

    normalized = _normalize_concept(
        concept
    )

    words = normalized.split()

    if not words:
        return False

    # Concepts should be concise.
    if len(words) > 6:
        return False

    # Must appear as an actual whole phrase in sources.
    if not _phrase_in_text(
        concept,
        " ".join(sources)
    ):
        return False

    # Reject sentence-like phrases.
    if any(
        word in GRAMMAR_WORDS
        for word in words
    ):
        return False

    # Reject action/predicate words.
    if any(
        word in PREDICATE_WORDS
        for word in words
    ):
        return False

    # Reject weak sentence openings.
    if words[0] in BAD_CONCEPT_STARTS:
        return False

    # Don't end in ordinary stopwords.
    if words[-1] in STOPWORDS:
        return False

    # --------------------------------------------------------
    # Single-word concepts
    # --------------------------------------------------------

    if len(words) == 1:

        word = words[0]

        if word in STOPWORDS:
            return False

        if word in GENERIC_WORDS:
            return False

        if word in GENERIC_ACTION_WORDS:
            return False

        if word in GENERIC_SINGLE_WORDS:
            return False

        if len(word) < 3:
            return False

        # Uppercase one-word concept = acronym.
        if concept.isupper():
            return _is_real_acronym(
                concept,
                sources
            )

        # A normal one-word concept must be explicitly
        # introduced as a concept/definition.
        if word not in _explicit_definition_candidates(
            sources
        ):
            return False

    return True


def _deduplicate_concepts(
    concepts
):
    final = []
    seen = set()

    for concept in concepts:

        if not isinstance(
            concept,
            str
        ):
            continue

        normalized = _normalize_concept(
            concept
        )

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)

        final.append(
            concept.strip()
        )

    return final


# ============================================================
# Generic fallback concept extraction
# ============================================================

def _extract_definition_concepts(
    sources
):
    """
    Conservative source-grounded concept extraction.

    It can find:
        Primary Key
        Foreign Key
        Database Management System
        Database Constraints

    without hard-coding DBMS as a subject.
    """

    concepts = []

    patterns = [

        # A primary key uniquely identifies...
        r"^(?:a|an|the)\s+"
        r"([A-Za-z][A-Za-z0-9-]*"
        r"(?:\s+[A-Za-z][A-Za-z0-9-]*){0,5}?)"
        r"\s+"
        r"(?:uniquely identifies|identifies|"
        r"represents|describes|measures|"
        r"connects|controls|contains|includes|"
        r"provides|enables|helps|help|"
        r"prevents|prevent|maintains|maintain|"
        r"supports|support)\b",

        # X is...
        r"^(?!each\b|every\b|all\b|these\b|those\b)"
        r"(?:a|an|the)?\s*"
        r"([A-Za-z][A-Za-z0-9-]*"
        r"(?:\s+[A-Za-z][A-Za-z0-9-]*){0,5}?)"
        r"\s+"
        r"(?:is|are|was|were|means|refers to|"
        r"is called|is known as)\b",

        # Database constraints help...
        r"^(?!each\b|every\b|all\b|these\b|those\b|"
        r"this\b|that\b)"
        r"([A-Za-z][A-Za-z0-9-]*"
        r"(?:\s+[A-Za-z][A-Za-z0-9-]*){0,5}?)"
        r"\s+"
        r"(?:helps|help|prevents|prevent|"
        r"maintains|maintain|supports|support|"
        r"provides|provide|enables|enable)\b"
    ]

    for source in sources:

        for sentence in _split_sentences(
            source
        ):

            for pattern in patterns:

                match = re.search(
                    pattern,
                    sentence.strip(),
                    flags=re.IGNORECASE
                )

                if not match:
                    continue

                candidate = match.group(
                    1
                ).strip()

                candidate = candidate.strip(
                    " ,:;-"
                )

                if _is_good_concept(
                    candidate,
                    sources
                ):
                    concepts.append(
                        candidate
                    )

                break

    return concepts


def _extract_parenthetical_acronyms(
    sources
):
    concepts = []

    for source in sources:

        matches = re.findall(
            r"\(([A-Z][A-Z0-9-]{1,8})\)",
            source
        )

        for match in matches:

            if _is_real_acronym(
                match,
                sources
            ):
                concepts.append(
                    match
                )

    return concepts


def _extract_standalone_acronyms(
    sources
):
    concepts = []

    for source in sources:

        matches = re.findall(
            r"\b[A-Z][A-Z0-9-]{1,8}\b",
            source
        )

        for match in matches:

            if not _is_real_acronym(
                match,
                sources
            ):
                continue

            if _is_good_concept(
                match,
                sources
            ):
                concepts.append(
                    match
                )

    return concepts


def _extract_source_concepts(
    sources
):
    concepts = []

    concepts.extend(
        _extract_definition_concepts(
            sources
        )
    )

    concepts.extend(
        _extract_parenthetical_acronyms(
            sources
        )
    )

    concepts.extend(
        _extract_standalone_acronyms(
            sources
        )
    )

    concepts = _deduplicate_concepts(
        concepts
    )

    concepts = concepts[:8]

    return [
        _title_case_concept(
            concept,
            sources
        )
        for concept in concepts
    ]


# ============================================================
# Duplicate information removal
# ============================================================

def _sentence_similarity(
    first,
    second
):
    first_normalized = _normalize_text(
        first
    )

    second_normalized = _normalize_text(
        second
    )

    if first_normalized == second_normalized:
        return 1.0

    first_words = [
        word
        for word in first_normalized.split()
        if word not in STOPWORDS
    ]

    second_words = [
        word
        for word in second_normalized.split()
        if word not in STOPWORDS
    ]

    if not first_words or not second_words:
        return 0.0

    first_set = set(first_words)
    second_set = set(second_words)

    union = first_set | second_set

    jaccard = (
        len(first_set & second_set) / len(union)
        if union
        else 0.0
    )

    sequence = SequenceMatcher(
        None,
        " ".join(first_words),
        " ".join(second_words)
    ).ratio()

    # Compare the beginnings too. This catches cases like:
    #
    # A database management system (DBMS) is software used...
    # A database management system (DBMS) is software that...
    #
    # where the wording differs slightly after the shared
    # definition.
    prefix_length = min(
        8,
        len(first_words),
        len(second_words)
    )

    if prefix_length >= 5:

        shared_prefix = sum(
            1
            for index in range(prefix_length)
            if first_words[index] == second_words[index]
        )

        prefix_ratio = (
            shared_prefix / prefix_length
        )

    else:
        prefix_ratio = 0.0

    return max(
        jaccard,
        sequence,
        prefix_ratio
    )


def _remove_duplicate_sentences(
    text
):
    sentences = _split_sentences(
        text
    )

    kept = []

    for sentence in sentences:

        duplicate_index = None

        for index, previous in enumerate(
            kept
        ):

            if _sentence_similarity(
                previous,
                sentence
            ) >= 0.82:

                duplicate_index = index
                break

        if duplicate_index is None:

            kept.append(
                sentence
            )

        else:

            # Keep the longer/more informative version.
            if len(sentence) > len(
                kept[duplicate_index]
            ):
                kept[duplicate_index] = sentence

    return " ".join(
        kept
    )


# ============================================================
# Heading cleanup
# ============================================================

def _clean_heading(
    heading,
    sources
):
    """
    Prevent accidental AI headings such as:

        Primary Key Uniquely

    from reaching the UI.
    """

    heading = _clean_concept_text(
        heading,
        sources
    )

    words = heading.split()

    # Remove trailing predicate words.
    while (
        len(words) > 1
        and words[-1].lower()
        in PREDICATE_WORDS
    ):
        words.pop()

    heading = " ".join(
        words
    )

    return _title_case_concept(
        heading,
        sources
    )


# ============================================================
# Section validation
# ============================================================

def _validate_sections(
    sections,
    source_count,
    sources
):
    if not isinstance(
        sections,
        list
    ):
        return []

    cleaned = []
    seen_headings = set()

    for section in sections:

        if not isinstance(
            section,
            dict
        ):
            continue

        raw_heading = str(
            section.get(
                "heading",
                ""
            )
        ).strip()

        raw_body = str(
            section.get(
                "body",
                ""
            )
        ).strip()

        if not raw_heading or not raw_body:
            continue

        heading = _clean_heading(
            raw_heading,
            sources
        )

        if not heading:
            continue

        body = _remove_duplicate_sentences(
            raw_body
        )

        if not body:
            continue

        heading_key = _normalize_concept(
            heading
        )

        if heading_key in seen_headings:
            continue

        seen_headings.add(
            heading_key
        )

        source_ids = section.get(
            "source_ids",
            []
        )

        if not isinstance(
            source_ids,
            list
        ):
            source_ids = []

        valid_source_ids = []

        for source_id in source_ids:

            try:
                source_id = int(
                    source_id
                )
            except (
                ValueError,
                TypeError
            ):
                continue

            if (
                1 <= source_id <= source_count
                and source_id not in valid_source_ids
            ):
                valid_source_ids.append(
                    source_id
                )

        cleaned.append({
            "heading": heading,
            "body": body,
            "source_ids": valid_source_ids
        })

    return cleaned[:7]


# ============================================================
# AI generation
# ============================================================

def _ai_generate_study_package(
    topic,
    sources
):
    source_text = "\n\n".join(
        f"SOURCE {index}:\n{source}"
        for index, source in enumerate(
            sources,
            1
        )
    )

    prompt = f"""
You are an expert educational notes assistant.

The student is studying:

{topic}

The student supplied these sources:

{source_text}

Use ONLY the information in the supplied sources.

CONCEPT RULES:

Identify 5 to 8 genuinely useful study concepts.

A concept must be a meaningful noun phrase that a
student would actually write in exam notes.

Good concept types include:
- technical terms
- definitions
- principles
- processes
- structures
- mechanisms
- laws
- theorems
- relationships
- named events
- named objects
- subject-specific ideas

Every concept MUST literally occur in the supplied sources.

CRITICAL RULES:

1. Concepts should normally be noun phrases.

2. Keep meaningful multi-word concepts together.

3. "primary key" = ONE concept.

4. "foreign key" = ONE concept.

5. "database management system" = ONE concept.

6. "database constraints" = ONE concept.

7. "DBMS" may be a separate acronym concept.

8. NEVER split a multi-word concept into separate words.

9. NEVER output ordinary sentence subjects such as:
   "each row"
   "every student"
   "all users"
   "these constraints"

10. NEVER create sentence fragments.

11. NEVER append a verb or action to a concept.

    WRONG:
    "primary key uniquely"
    "foreign key refers"
    "database constraints prevent"

    RIGHT:
    "primary key"
    "foreign key"
    "database constraints"

12. Do not output concepts containing:
    is
    are
    was
    were
    used
    commonly
    typically
    usually
    uniquely
    identifies
    represents
    describes
    measures
    connects
    contains
    prevents
    maintains
    helps

13. Do NOT create concepts by joining nearby words.

14. Do NOT invent concepts.

15. If a source contains:
    "database management system (DBMS)"

    acceptable:
    "database management system"
    "DBMS"

    NOT acceptable:
    "database management system DBMS"

NOTES RULES:

Create 4 to 7 useful sections.

Each section must:
- have a meaningful noun-phrase heading
- explain one distinct idea
- use only supplied sources
- use simple student-friendly language
- preserve important terminology
- combine overlapping information
- avoid repeating the same sentence
- include supporting source numbers

Return ONLY valid JSON:

{{
  "concepts": [
    "important concept 1",
    "important concept 2",
    "important concept 3",
    "important concept 4",
    "important concept 5"
  ],
  "sections": [
    {{
      "heading": "Meaningful heading",
      "body": "Explanation based only on supplied sources.",
      "source_ids": [1]
    }},
    {{
      "heading": "Another heading",
      "body": "Explanation based only on supplied sources.",
      "source_ids": [1, 2]
    }}
  ]
}}
"""

    response = _call_ollama(
        prompt
    )

    if not response:
        return None

    try:
        data = json.loads(
            response
        )
    except (
        json.JSONDecodeError,
        TypeError
    ):
        return None

    # --------------------------------------------------------
    # AI concepts
    # --------------------------------------------------------

    ai_concepts = []

    raw_concepts = data.get(
        "concepts",
        []
    )

    if isinstance(
        raw_concepts,
        list
    ):

        for concept in raw_concepts:

            cleaned = _clean_concept_text(
                concept,
                sources
            )

            if _is_good_concept(
                cleaned,
                sources
            ):
                ai_concepts.append(
                    cleaned
                )

    ai_concepts = _deduplicate_concepts(
        ai_concepts
    )

    # --------------------------------------------------------
    # Reliable source-grounded fallback
    # --------------------------------------------------------

    fallback_concepts = _extract_source_concepts(
        sources
    )

    concepts = _deduplicate_concepts(
        ai_concepts + fallback_concepts
    )

    concepts = concepts[:8]

    concepts = [
        _title_case_concept(
            concept,
            sources
        )
        for concept in concepts
    ]

    # --------------------------------------------------------
    # Notes sections
    # --------------------------------------------------------

    sections = _validate_sections(
        data.get(
            "sections",
            []
        ),
        len(sources),
        sources
    )

    if not sections:
        return None

    return {
        "concepts": concepts,
        "notes": {
            "sections": sections
        }
    }


# ============================================================
# Fallback notes if Ollama fails
# ============================================================

def _fallback_notes(
    topic,
    sources,
    concepts
):
    sentences = []

    for source_id, source in enumerate(
        sources,
        1
    ):

        for sentence in _split_sentences(
            source
        ):

            sentences.append(
                (
                    sentence,
                    source_id
                )
            )

    sections = []
    used_bodies = []

    for concept in concepts:

        matches = []

        for sentence, source_id in sentences:

            if _phrase_in_text(
                concept,
                sentence
            ):
                matches.append(
                    (
                        sentence,
                        source_id
                    )
                )

        if not matches:
            continue

        body = _remove_duplicate_sentences(
            " ".join(
                item[0]
                for item in matches[:3]
            )
        )

        duplicate = False

        for previous_body in used_bodies:

            if _sentence_similarity(
                previous_body,
                body
            ) >= 0.82:

                duplicate = True
                break

        if duplicate:
            continue

        used_bodies.append(
            body
        )

        sections.append({
            "heading": _title_case_concept(
                concept,
                sources
            ),
            "body": body,
            "source_ids": sorted(
                set(
                    item[1]
                    for item in matches[:3]
                )
            )
        })

    if not sections:

        all_sentences = [
            item[0]
            for item in sentences[:5]
        ]

        sections.append({
            "heading": _title_case_concept(
                topic,
                sources
            ),
            "body": _remove_duplicate_sentences(
                " ".join(
                    all_sentences
                )
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


# ============================================================
# Main generation pipeline
# ============================================================

def generate_study_package(
    topic,
    sources
):
    package = _ai_generate_study_package(
        topic,
        sources
    )

    if package:
        return package

    concepts = _extract_source_concepts(
        sources
    )

    return {
        "concepts": concepts,
        "notes": _fallback_notes(
            topic,
            sources,
            concepts
        )
    }


# ============================================================
# Coverage Check
# ============================================================

def _concept_match_score(
    concept,
    text
):
    normalized_concept = _normalize_concept(
        concept
    )

    normalized_text = _normalize_text(
        text
    )

    if not normalized_concept:
        return 0.0

    # Exact whole phrase.
    if _phrase_in_text(
        normalized_concept,
        normalized_text
    ):
        return 1.0

    concept_words = [
        word
        for word in normalized_concept.split()
        if word not in STOPWORDS
    ]

    if not concept_words:
        return 0.0

    matched = 0

    for word in concept_words:

        if re.search(
            rf"(?<![a-z0-9])"
            rf"{re.escape(word)}"
            rf"(?![a-z0-9])",
            normalized_text
        ):
            matched += 1

    return (
        matched /
        len(concept_words)
    )


def compute_coverage(
    concepts,
    notes
):
    """
    Coverage is based on the actual explanatory BODY.

    A heading by itself can never make a concept Covered.
    """

    coverage = []

    if not isinstance(
        concepts,
        list
    ):
        concepts = []

    if not isinstance(
        notes,
        dict
    ):
        notes = {
            "sections": []
        }

    sections = notes.get(
        "sections",
        []
    )

    if not isinstance(
        sections,
        list
    ):
        sections = []

    for concept in concepts:

        display_concept = _title_case_concept(
            concept
        )

        best_score = 0.0
        matched_sections = []
        supporting_bodies = []

        for section_number, section in enumerate(
            sections,
            1
        ):

            if not isinstance(
                section,
                dict
            ):
                continue

            body = str(
                section.get(
                    "body",
                    ""
                )
            ).strip()

            # ONLY body is checked.
            # Heading alone cannot produce Covered.
            score = _concept_match_score(
                concept,
                body
            )

            best_score = max(
                best_score,
                score
            )

            if score >= 1.0:

                matched_sections.append(
                    section_number
                )

                supporting_bodies.append(
                    body
                )

        supporting_text = " ".join(
            supporting_bodies
        ).strip()

        if best_score == 0:

            status = "Needs review"

            explanation = (
                "This important concept was "
                "identified in the source material "
                "but was not represented in the "
                "generated notes."
            )

        elif (
            best_score < 1.0
            or len(supporting_text) < 45
        ):

            status = "Partially covered"

            explanation = (
                "This concept appears in the "
                "notes, but the explanation "
                "could be more complete."
            )

        else:

            status = "Covered"

            explanation = (
                "This concept appears in the "
                "notes with supporting "
                "information."
            )

        coverage.append({
            "concept": display_concept,
            "status": status,
            "explanation": explanation,
            "matched_sections": matched_sections
        })

    return coverage