import random


def get_random_questions(questions, number_of_questions):

    if not questions:
        return []

    # Do not request more questions than available
    number_of_questions = min(
        number_of_questions,
        len(questions)
    )

    # Randomly select complete question objects
    selected_questions = random.sample(
        questions,
        number_of_questions
    )

    return selected_questions