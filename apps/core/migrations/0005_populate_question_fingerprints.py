import hashlib
import re

from django.db import migrations


def normalize_question_text(text):
    text = text.strip().lower()
    return re.sub(r"\s+", " ", text)


def populate_question_fingerprints(apps, schema_editor):
    Question = apps.get_model("core", "Question")

    for question in Question.objects.filter(
        question_fingerprint__isnull=True,
    ):
        normalized = normalize_question_text(
            question.question
        )

        fingerprint = hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

        question.question_fingerprint = fingerprint
        question.save(
            update_fields=("question_fingerprint",)
        )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_question_question_fingerprint"),
    ]

    operations = [
        migrations.RunPython(
            populate_question_fingerprints,
            migrations.RunPython.noop,
        ),
    ]