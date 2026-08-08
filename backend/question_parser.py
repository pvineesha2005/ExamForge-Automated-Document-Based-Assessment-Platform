import re


QUESTION_PATTERN = re.compile(
    r"^\s*(?:Q(?:uestion)?\s*)?(\d+)[\.\):\-]\s*(.*)",
    re.IGNORECASE
)

OPTION_PATTERN = re.compile(
    r"^\s*\(?([A-Da-d])\)?[\.\):\-]\s*(.*)"
)


def parse_questions(pages):

    questions = []
    current_question = None

    for page in pages:

        for block in page["text_blocks"]:

            # A single PDF text block can contain multiple lines
            lines = block["text"].splitlines()

            for line in lines:

                text = line.strip()

                if not text:
                    continue

                # --------------------------------
                # Check for a new question
                # --------------------------------

                question_match = QUESTION_PATTERN.match(text)

                if question_match:

                    # Save previous question
                    if current_question:
                        questions.append(current_question)

                    current_question = {
                        "id": len(questions) + 1,
                        "source_number": question_match.group(1),
                        "question": question_match.group(2).strip(),
                        "options": [],
                        "image": None,
                        "page": page["page"]
                    }

                    continue

                # --------------------------------
                # Check for an option
                # --------------------------------

                if current_question:

                    option_match = OPTION_PATTERN.match(text)

                    if option_match:

                        option_label = option_match.group(1).upper()
                        option_text = option_match.group(2).strip()

                        current_question["options"].append({
                            "label": option_label,
                            "text": option_text
                        })

                    else:

                        # Continue question text
                        current_question["question"] += " " + text

        # --------------------------------
        # Attach images to current question
        # --------------------------------

        if current_question and page["images"]:

            if current_question["image"] is None:

                current_question["image"] = page["images"][0]["filename"]

    # Save final question
    if current_question:
        questions.append(current_question)

    return questions