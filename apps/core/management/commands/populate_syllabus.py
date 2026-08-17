from django.core.management.base import BaseCommand

from apps.core.models import Chapter, Subject


SYLLABUS = {
    "Physics": [
        (1, "Physics and Measurement"),
        (2, "Kinematics"),
        (3, "Laws of Motion"),
        (4, "Work, Energy and Power"),
        (5, "Rotational Motion"),
        (6, "Gravitation"),
        (7, "Properties of Solids and Liquids"),
        (8, "Thermodynamics"),
        (9, "Kinetic Theory of Gases"),
        (10, "Oscillations and Waves"),
        (11, "Electrostatics"),
        (12, "Current Electricity"),
        (13, "Magnetic Effects of Current and Magnetism"),
        (14, "Electromagnetic Induction and Alternating Currents"),
        (15, "Electromagnetic Waves"),
        (16, "Optics"),
        (17, "Dual Nature of Matter and Radiation"),
        (18, "Atoms and Nuclei"),
        (19, "Electronic Devices"),
        (20, "Experimental Skills"),
    ],
    "Chemistry": [
        (1, "Some Basic Concepts of Chemistry"),
        (2, "Atomic Structure"),
        (3, "Chemical Bonding and Molecular Structure"),
        (4, "Chemical Thermodynamics"),
        (5, "Solutions"),
        (6, "Equilibrium"),
        (7, "Redox Reactions and Electrochemistry"),
        (8, "Chemical Kinetics"),
        (9, "Classification of Elements and Periodicity in Properties"),
        (10, "P-Block Elements"),
        (11, "d- and f-Block Elements"),
        (12, "Coordination Compounds"),
        (13, "Purification and Characterisation of Organic Compounds"),
        (14, "Some Basic Principles of Organic Chemistry"),
        (15, "Hydrocarbons"),
        (16, "Organic Compounds Containing Halogens"),
        (17, "Organic Compounds Containing Oxygen"),
        (18, "Organic Compounds Containing Nitrogen"),
        (19, "Biomolecules"),
        (20, "Principles Related to Practical Chemistry"),
    ],
    "Biology": [
        (1, "Diversity in the Living World"),
        (2, "Structural Organisation in Animals and Plants"),
        (3, "Cell Structure and Function"),
        (4, "Plant Physiology"),
        (5, "Human Physiology"),
        (6, "Reproduction"),
        (7, "Genetics and Evolution"),
        (8, "Biology and Human Welfare"),
        (9, "Biotechnology and Its Applications"),
        (10, "Ecology and Environment"),
    ],
}


class Command(BaseCommand):
    help = "Populate the ConceptCode NEET UG 2026 syllabus."

    def handle(self, *args, **options):
        created_subjects = 0
        created_chapters = 0

        for subject_name, chapters in SYLLABUS.items():
            subject, subject_created = Subject.objects.get_or_create(
                name=subject_name,
                defaults={
                    "description": (
                        f"NEET (UG)-2026 {subject_name} syllabus."
                    ),
                    "is_active": True,
                },
            )

            if subject_created:
                created_subjects += 1

            for unit_number, chapter_name in chapters:
                _, chapter_created = Chapter.objects.update_or_create(
                    subject=subject,
                    name=chapter_name,
                    defaults={
                        "unit_number": unit_number,
                        "is_active": True,
                    },
                )

                if chapter_created:
                    created_chapters += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Syllabus population completed successfully."
            )
        )

        self.stdout.write(
            f"Subjects created: {created_subjects}"
        )

        self.stdout.write(
            f"Chapters created: {created_chapters}"
        )

        self.stdout.write(
            "Topics created: 0 "
            "(topic extraction will be handled separately)."
        )