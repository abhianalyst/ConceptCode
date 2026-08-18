from dataclasses import dataclass


@dataclass(frozen=True)
class SourceChapter:
    subject: str
    syllabus_chapter: str
    source_chapters: tuple[str, ...]


SOURCE_CHAPTERS = (
    SourceChapter(
        subject="Physics",
        syllabus_chapter="Physics and Measurement",
        source_chapters=(
            "PHYSICAL WORLD",
            "UNITS AND MEASUREMENTS",
        ),
    ),
    SourceChapter(
        subject="Physics",
        syllabus_chapter="Kinematics",
        source_chapters=(
            "MOTION IN A STRAIGHT LINE",
            "MOTION IN A PLANE",
        ),
    ),
    SourceChapter(
        subject="Physics",
        syllabus_chapter="Laws of Motion",
        source_chapters=(
            "LAWS OF MOTION",
        ),
    ),
)

def get_source_chapters(
    subject: str,
    syllabus_chapter: str,
) -> tuple[str, ...]:
    for mapping in SOURCE_CHAPTERS:
        if (
            mapping.subject == subject
            and mapping.syllabus_chapter == syllabus_chapter
        ):
            return mapping.source_chapters

    raise KeyError(
        f"No source mapping found for "
        f"{subject} -> {syllabus_chapter}"
    )

TOPIC_SOURCE_CHAPTERS = {
    "Physics": {
        "Kinematics": {
            "Motion in a plane": "MOTION IN A PLANE",
            "Projectile motion": "MOTION IN A PLANE",
            "Uniform circular motion": "MOTION IN A PLANE",
        },
    },
}

def get_topic_source_chapter(
    subject: str,
    chapter: str,
    topic: str,
) -> str:
    try:
        return TOPIC_SOURCE_CHAPTERS[
            subject
        ][chapter][topic]
    except KeyError as exc:
        raise KeyError(
            f"No topic source-chapter mapping found for "
            f"{subject} -> {chapter} -> {topic}"
        ) from exc