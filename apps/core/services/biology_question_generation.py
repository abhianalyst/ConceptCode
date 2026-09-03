from pathlib import Path

from apps.core.services.biology_source import (
    get_chapter_pages,
    load_book,
)
from question_generator.generation import (
    QuestionGenerationService,
    build_generation_context,
    generate_questions_for_topic,
)
from question_generator.output import export_topic_questions_json
from question_generator.schemas import Section
from question_generator.sections import extract_sections


BIOLOGY_CHAPTER_TITLES = {
    "class_11": {
        1: "The Living World",
        2: "Biological Classification",
        3: "Plant Kingdom",
        4: "Animal Kingdom",
        5: "Morphology of Flowering Plants",
        6: "Anatomy of Flowering Plants",
        7: "Structural Organisation in Animals",
        8: "Cell: The Unit of Life",
        9: "Biomolecules",
        10: "Cell Cycle and Cell Division",
        11: "Transport in Plants",
        12: "Mineral Nutrition",
        13: "Photosynthesis in Higher Plants",
        14: "Respiration in Plants",
        15: "Plant Growth and Development",
        16: "Digestion and Absorption",
        17: "Breathing and Exchange of Gases",
        18: "Body Fluids and Circulation",
        19: "Excretory Products and their Elimination",
        20: "Locomotion and Movement",
        21: "Neural Control and Coordination",
        22: "Chemical Coordination and Integration",
    },
    "class_12": {
        1: "Reproduction in Organisms",
        2: "Sexual Reproduction in Flowering Plants",
        3: "Human Reproduction",
        4: "Reproductive Health",
        5: "Principles of Inheritance and Variation",
        6: "Molecular Basis of Inheritance",
        7: "Evolution",
        8: "Human Health and Disease",
        9: "Strategies for Enhancement in Food Production",
        10: "Microbes in Human Welfare",
        11: "Biotechnology: Principles and Processes",
        12: "Biotechnology and its Applications",
        13: "Organisms and Populations",
        14: "Ecosystem",
        15: "Biodiversity and Conservation",
        16: "Environmental Issues",
    },
}


def generate_questions_from_biology_json(
    class_name: str,
    chapter_number: int,
    output_path: str | Path,
    *,
    service: QuestionGenerationService,
) -> Path:
    """
    Generate Biology questions chapter-by-chapter and topic-by-topic.

    Pipeline:

        Biology JSON
        -> chapter pages
        -> sections/topics
        -> generation per topic
        -> 20 Easy + 20 Medium + 20 Hard
        -> validation
        -> deduplication
        -> JSON export
    """

    if not isinstance(class_name, str) or not class_name.strip():
        raise ValueError(
            "class_name must be a non-empty string"
        )

    if not isinstance(chapter_number, int):
        raise ValueError(
            "chapter_number must be an integer"
        )

    if not isinstance(
        service,
        QuestionGenerationService,
    ):
        raise TypeError(
            "service must be a QuestionGenerationService"
        )

    if class_name not in BIOLOGY_CHAPTER_TITLES:
        raise ValueError(
            f"Unknown Biology book: {class_name}"
        )

    chapter_titles = BIOLOGY_CHAPTER_TITLES[class_name]

    if chapter_number not in chapter_titles:
        raise ValueError(
            f"Chapter {chapter_number} does not exist "
            f"in {class_name}"
        )

    chapter = chapter_titles[chapter_number]

    data = load_book(class_name)

    source = data["document"]["filename"]

    pages = get_chapter_pages(
        class_name,
        chapter_number,
    )

    sections = extract_sections(
        pages,
        source=source,
        chapter=chapter,
        subject="Biology",
    )

    if not sections:
        raise ValueError(
            f"No sections found for "
            f"{class_name} chapter {chapter_number}"
        )

    all_questions = []

    for section in sections:
        if not isinstance(section, Section):
            raise TypeError(
                "extract_sections must return Section objects"
            )

        context = build_generation_context(
            section,
            subject="Biology",
            source=source,
        )

        topic_questions = generate_questions_for_topic(
            context,
            service,
        )

        if len(topic_questions) != 60:
            raise ValueError(
                f"Topic {section.title!r} generated "
                f"{len(topic_questions)} questions instead of 60"
            )

        all_questions.extend(topic_questions)

    return export_topic_questions_json(
        all_questions,
        output_path,
        source_file=source,
    )