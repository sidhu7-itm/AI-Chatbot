import re


def normalize_spaces(text):
    """Normalize whitespace."""

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def clean_course_name(course):
    """Clean extracted course name."""

    course = normalize_spaces(course)

    return course.strip(" -:")


def parse_fee_structure(text, source, page):
    """
    Convert the fee-structure PDF into
    course-level records.

    Each detected course becomes a
    separate retrieval document.
    """

    text = normalize_spaces(text)

    records = []

    # ==================================================
    # COURSE START PATTERNS
    # ==================================================

    course_patterns = [

        # Engineering
        r"Civil Engineering",

        r"Mechanical Engineering\(Mecatronics\)",

        r"Electronics & Communication Engineering",

        r"Electrical Engineering"
        r"\(Solar & Alternative Energy/"
        r"Electrical Vehicle/AI\)",

        r"B\.Tech Computer Science\s*&\s*Engineering"
        r"\s*\(Specialization in Data Science\)",

        r"B\.Tech Computer Science\s*&\s*Engineering"
        r"\s*\(AI and Machine Learning\)",

        r"B\.Tech Computer Science\s*&\s*Engineering"
        r"\s*\(Cyber Security\)",

        r"B\.Tech Computer Science\s*&\s*Engineering",

        # Management
        r"MBA",

        r"BBA",

        r"MCA",

        # Computer / Science
        r"BCA",

        r"BSc/BSc\(Hon/Research\) \(CS\)/PCM",

        r"BSc/BSc\(Hon/Research\) Biotechnology",

        r"BSc/BSc\(Hon/Research\) Microbiology",

        r"BSc/BSc\(Hon/Research\) Food Technology",

        r"BSc/BSc\(Hon/Research\) \(Forensic Science\)",

        r"M\.Sc\. \(Food Technology\)",

        r"M\.Sc\. \(Microbiology\)",

        r"M\.Sc\. \(Biotechnology\)",

        # Agriculture
        r"B\.Sc\. \(Honours\) Agriculture",

        r"B\.Sc\. \(Honours\) Horticulture",

        r"M\.Sc\. \(Ag\.\)",

        # Nursing
        r"Post Basic B\.Sc\. Nursing",

        r"B\.Sc\. Nursing",

        r"GNM"
    ]

    # Remove duplicates while preserving order
    course_patterns = list(
        dict.fromkeys(course_patterns)
    )



    matches = []

    for pattern in course_patterns:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE
        ):

            matches.append({
                "start": match.start(),
                "end": match.end(),
                "text": match.group(0)
            })

    # Sort by location in document
    matches.sort(
        key=lambda x: x["start"]
    )


    filtered_matches = []

    last_end = -1

    for match in matches:

        if match["start"] >= last_end:

            filtered_matches.append(
                match
            )

            last_end = match["end"]



    for i, match in enumerate(
        filtered_matches
    ):

        start = match["start"]

        # End at next course
        if i + 1 < len(
            filtered_matches
        ):

            end = filtered_matches[
                i + 1
            ]["start"]

        else:

            end = len(text)

        record_text = text[
            start:end
        ]

        record_text = normalize_spaces(
            record_text
        )

        # Avoid extremely large accidental records
        if len(record_text) > 1000:

            record_text = record_text[
                :1000
            ]

        course_name = clean_course_name(
            match["text"]
        )

        # Determine broad category
        lower_course = (
            course_name.lower()
        )

        if "b.tech" in lower_course:

            category = "B.Tech"

        elif "mba" in lower_course:

            category = "MBA"

        elif "bba" in lower_course:

            category = "BBA"

        elif "mca" in lower_course:

            category = "MCA"

        elif "bca" in lower_course:

            category = "BCA"

        elif (
            "nursing" in lower_course
            or "gnm" in lower_course
        ):

            category = "Nursing"

        elif (
            "agriculture" in lower_course
            or "horticulture" in lower_course
            or "m.sc. (ag.)" in lower_course
        ):

            category = "Agriculture"

        elif (
            "bsc" in lower_course
            or "m.sc" in lower_course
        ):

            category = "Science"

        else:

            category = "Other"

        records.append({

            "text": record_text,

            "course_name": course_name,

            "category": category,

            "source": source,

            "page": page,

            "type": "fee_structure"

        })

    return records