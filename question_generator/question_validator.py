from question_generator.question_schema import Question


def validate_question(question: Question) -> list[str]:
    errors: list[str] = []

    if not question.question.strip():
        errors.append("Question text cannot be empty.")

    if len(question.options) != 4:
        errors.append("Question must have exactly four options.")

    cleaned_options = [
        option.strip()
        for option in question.options
    ]

    if any(not option for option in cleaned_options):
        errors.append("Options cannot be empty.")

    if len(set(cleaned_options)) != len(cleaned_options):
        errors.append("Options must be unique.")

    if question.correct_answer.strip() not in cleaned_options:
        errors.append(
            "Correct answer must exactly match one of the options."
        )

    if not question.explanation.strip():
        errors.append("Explanation cannot be empty.")

    if not question.subject.strip():
        errors.append("Subject cannot be empty.")

    if not question.chapter.strip():
        errors.append("Chapter cannot be empty.")

    if not question.topic.strip():
        errors.append("Topic cannot be empty.")

    if not question.source.strip():
        errors.append("Source cannot be empty.")

    return errors