TOPIC_SECTIONS = {
    "Physics": {
        "Kinematics": {
            "Motion in a straight line": "3",
            "Position-time graph": "3.2",
            "Speed and velocity": "3.3",
            "Average speed and instantaneous velocity": "3.3",
            "Uniformly accelerated motion": "3.5",
            "Relative velocity": "3.7",
            "Scalars and vectors": "4.2",
            "Vector addition and subtraction": "4.4",
            "Resolution of a vector": "4.5",
            "Motion in a plane": "4.7",
            "Projectile motion": "4.10",
            "Uniform circular motion": "4.11",
        },
    },
}


TOPIC_SECTION_ENDS = {
    "Physics": {
        "Kinematics": {
            "Motion in a plane": "4.10",
            "Projectile motion": "4.11",
            "Uniform circular motion": None,
        },
    },
}


def get_topic_section(
    subject: str,
    chapter: str,
    topic: str,
) -> str:
    try:
        return TOPIC_SECTIONS[
            subject
        ][chapter][topic]
    except KeyError as exc:
        raise KeyError(
            f"No topic mapping found for "
            f"{subject} -> {chapter} -> {topic}"
        ) from exc


def get_topic_section_end(
    subject: str,
    chapter: str,
    topic: str,
):
    try:
        return TOPIC_SECTION_ENDS[
            subject
        ][chapter][topic]
    except KeyError as exc:
        raise KeyError(
            f"No topic section-end mapping found for "
            f"{subject} -> {chapter} -> {topic}"
        ) from exc