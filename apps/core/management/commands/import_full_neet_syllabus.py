# apps/core/management/commands/import_full_neet_syllabus.py

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.core.models import Subject, Chapter, Topic


class Command(BaseCommand):
    help = 'Import complete NEET syllabus for all 3 subjects'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Starting Full NEET Syllabus Import'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # ============================================================
        # BIOLOGY SYLLABUS
        # ============================================================
        
        biology, created = Subject.objects.get_or_create(
            name='Biology',
            defaults={
                'description': 'Biology syllabus for NEET preparation',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS(f'\n📘 Biology: {"Created" if created else "Exists"}'))

        biology_chapters = [
            # Class 11
            {'unit': 1, 'name': 'Diversity in the Living World', 'topics': [
                'The Living World', 'Biological Classification', 'Plant Kingdom', 'Animal Kingdom'
            ]},
            {'unit': 2, 'name': 'Structural Organisation in Animals and Plants', 'topics': [
                'Morphology of Flowering Plants', 'Anatomy of Flowering Plants', 
                'Structural Organisation in Animals'
            ]},
            {'unit': 3, 'name': 'Cell Structure and Function', 'topics': [
                'Cell: The Unit of Life', 'Biomolecules', 'Cell Cycle and Cell Division'
            ]},
            {'unit': 4, 'name': 'Plant Physiology', 'topics': [
                'Photosynthesis in Higher Plants', 'Respiration in Plants', 
                'Plant Growth and Development'
            ]},
            {'unit': 5, 'name': 'Human Physiology', 'topics': [
                'Breathing and Exchange of Gases', 'Body Fluids and Circulation',
                'Excretory Products and Their Elimination', 'Locomotion and Movement',
                'Neural Control and Coordination', 'Chemical Coordination and Integration'
            ]},
            # Class 12
            {'unit': 6, 'name': 'Reproduction', 'topics': [
                'Sexual Reproduction in Flowering Plants', 'Human Reproduction', 
                'Reproductive Health'
            ]},
            {'unit': 7, 'name': 'Genetics and Evolution', 'topics': [
                'Principles of Inheritance and Variation', 'Molecular Basis of Inheritance',
                'Evolution'
            ]},
            {'unit': 8, 'name': 'Biology and Human Welfare', 'topics': [
                'Human Health and Disease', 'Microbes in Human Welfare'
            ]},
            {'unit': 9, 'name': 'Biotechnology and Its Applications', 'topics': [
                'Biotechnology: Principles and Processes', 'Biotechnology and Its Applications'
            ]},
            {'unit': 10, 'name': 'Ecology and Environment', 'topics': [
                'Organisms and Populations', 'Ecosystem', 'Biodiversity and Conservation'
            ]},
        ]

        # ============================================================
        # CHEMISTRY SYLLABUS
        # ============================================================
        
        chemistry, created = Subject.objects.get_or_create(
            name='Chemistry',
            defaults={
                'description': 'Chemistry syllabus for NEET preparation',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS(f'\n🧪 Chemistry: {"Created" if created else "Exists"}'))

        chemistry_chapters = [
            # Physical Chemistry
            {'unit': 1, 'name': 'Some Basic Concepts of Chemistry', 'topics': [
                'Mole Concept', 'Stoichiometry', 'Laws of Chemical Combination',
                'Atomic and Molecular Masses', 'Percentage Composition', 'Empirical and Molecular Formula'
            ]},
            {'unit': 2, 'name': 'Atomic Structure', 'topics': [
                'Bohr\'s Model', 'Quantum Mechanical Model', 'Aufbau Principle',
                'Pauli Exclusion Principle', 'Hund\'s Rule', 'Electronic Configuration'
            ]},
            {'unit': 3, 'name': 'Chemical Bonding and Molecular Structure', 'topics': [
                'Ionic Bond', 'Covalent Bond', 'VSEPR Theory', 'VBT', 'Hybridisation',
                'Molecular Orbital Theory', 'Valence Bond Theory', 'Resonance'
            ]},
            {'unit': 4, 'name': 'Chemical Thermodynamics', 'topics': [
                'First Law of Thermodynamics', 'Enthalpy', 'Entropy', 'Gibbs Free Energy',
                'Spontaneity', 'Hess\'s Law', 'Bond Enthalpy'
            ]},
            {'unit': 5, 'name': 'Solutions', 'topics': [
                'Types of Solutions', 'Concentration Units', 'Colligative Properties',
                'Raoult\'s Law', 'Vapour Pressure', 'Boiling Point Elevation',
                'Freezing Point Depression', 'Osmotic Pressure'
            ]},
            {'unit': 6, 'name': 'Equilibrium', 'topics': [
                'Dynamic Equilibrium', 'Equilibrium Constant', 'Le Chatelier\'s Principle',
                'Ionic Equilibrium', 'pH and pOH', 'Buffer Solutions', 'Solubility Product'
            ]},
            {'unit': 7, 'name': 'Redox Reactions and Electrochemistry', 'topics': [
                'Oxidation and Reduction', 'Oxidation Number', 'Electrochemical Cells',
                'Nernst Equation', 'Electrolysis', 'Faraday\'s Laws'
            ]},
            {'unit': 8, 'name': 'Chemical Kinetics', 'topics': [
                'Rate of Reaction', 'Rate Laws', 'Order of Reaction', 'Molecularity',
                'Arrhenius Equation', 'Activation Energy', 'Catalysis'
            ]},
            # Inorganic Chemistry
            {'unit': 9, 'name': 'Classification of Elements and Periodicity in Properties', 'topics': [
                'Modern Periodic Table', 'Periodic Trends', 'Atomic Radius', 'Ionisation Enthalpy',
                'Electron Gain Enthalpy', 'Electronegativity'
            ]},
            {'unit': 10, 'name': 'p-Block Elements', 'topics': [
                'Group 13 Elements (Boron Family)', 'Group 14 Elements (Carbon Family)',
                'Group 15 Elements (Nitrogen Family)', 'Group 16 Elements (Oxygen Family)',
                'Group 17 Elements (Halogens)', 'Group 18 Elements (Noble Gases)'
            ]},
            {'unit': 11, 'name': 'd- and f-block Elements', 'topics': [
                'Transition Elements', 'Lanthanides', 'Actinides', 'Electronic Configuration',
                'Properties of d-block', 'Coordination Compounds'
            ]},
            {'unit': 12, 'name': 'Coordination Compounds', 'topics': [
                'Coordination Number', 'Werner\'s Theory', 'IUPAC Nomenclature',
                'Isomerism', 'VBT', 'CFT', 'Applications of Coordination Compounds'
            ]},
            # Organic Chemistry
            {'unit': 13, 'name': 'Purification and Characterisation of Organic Compounds', 'topics': [
                'Crystallisation', 'Distillation', 'Chromatography', 'Qualitative Analysis',
                'Quantitative Analysis', 'Empirical Formula'
            ]},
            {'unit': 14, 'name': 'Some Basic Principles of Organic Chemistry', 'topics': [
                'IUPAC Nomenclature', 'Structural Isomerism', 'Resonance', 'Hyperconjugation',
                'Inductive Effect', 'Electromeric Effect', 'Reaction Mechanisms'
            ]},
            {'unit': 15, 'name': 'Hydrocarbons', 'topics': [
                'Alkanes', 'Alkenes', 'Alkynes', 'Aromatic Hydrocarbons', 'Benzene',
                'Markovnikov\'s Rule', 'Anti-Markovnikov Addition', 'Aromaticity'
            ]},
            {'unit': 16, 'name': 'Organic Compounds Containing Halogens', 'topics': [
                'Haloalkanes', 'Haloarenes', 'Nucleophilic Substitution', 'Elimination Reactions',
                'Grignard Reagents', 'Environmental Effects'
            ]},
            {'unit': 17, 'name': 'Organic Compounds Containing Oxygen', 'topics': [
                'Alcohols', 'Phenols', 'Ethers', 'Aldehydes', 'Ketones', 'Carboxylic Acids',
                'Esters', 'Oxidation and Reduction Reactions'
            ]},
            {'unit': 18, 'name': 'Organic Compounds Containing Nitrogen', 'topics': [
                'Amines', 'Diazonium Salts', 'Cyanides', 'Isocyanides', 'Nitro Compounds',
                'Sandmeyer Reaction', 'Gattermann Reaction'
            ]},
            {'unit': 19, 'name': 'Biomolecules', 'topics': [
                'Carbohydrates', 'Proteins', 'Amino Acids', 'Enzymes', 'Vitamins',
                'Nucleic Acids', 'Lipids', 'Hormones'
            ]},
            {'unit': 20, 'name': 'Principles Related to Practical Chemistry', 'topics': [
                'Detection of Functional Groups', 'Test of Purity', 'Quantitative Analysis',
                'Volumetric Analysis', 'Gravimetric Analysis', 'Colorimetric Analysis'
            ]},
        ]

        # ============================================================
        # PHYSICS SYLLABUS
        # ============================================================
        
        physics, created = Subject.objects.get_or_create(
            name='Physics',
            defaults={
                'description': 'Physics syllabus for NEET preparation',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS(f'\n⚛️ Physics: {"Created" if created else "Exists"}'))

        physics_chapters = [
            # Class 11
            {'unit': 1, 'name': 'Units and Measurement', 'topics': [
                'Physical Quantities', 'Units', 'Dimensions', 'Dimensional Analysis',
                'Errors in Measurement', 'Significant Figures'
            ]},
            {'unit': 2, 'name': 'Motion in a Straight Line', 'topics': [
                'Kinematics', 'Position', 'Velocity', 'Acceleration', 'Equations of Motion',
                'Graphical Analysis', 'Relative Velocity'
            ]},
            {'unit': 3, 'name': 'Motion in a Plane', 'topics': [
                'Vectors', 'Scalars', 'Projectile Motion', 'Uniform Circular Motion',
                'Relative Motion in 2D', 'Centripetal Acceleration'
            ]},
            {'unit': 4, 'name': 'Laws of Motion', 'topics': [
                'Newton\'s Laws', 'Inertia', 'Impulse', 'Equilibrium', 'Friction',
                'Circular Motion Applications', 'Pseudo Forces'
            ]},
            {'unit': 5, 'name': 'Work, Energy and Power', 'topics': [
                'Work Done', 'Kinetic Energy', 'Potential Energy', 'Conservative Forces',
                'Work-Energy Theorem', 'Power', 'Collisions'
            ]},
            {'unit': 6, 'name': 'Rotational Motion', 'topics': [
                'Centre of Mass', 'Moment of Inertia', 'Torque', 'Angular Momentum',
                'Rolling Motion', 'Equilibrium of Rigid Bodies'
            ]},
            {'unit': 7, 'name': 'Gravitation', 'topics': [
                'Newton\'s Law of Gravitation', 'Gravitational Field', 'Gravitational Potential',
                'Satellite Motion', 'Escape Velocity', 'Kepler\'s Laws'
            ]},
            {'unit': 8, 'name': 'Properties of Solids and Liquids', 'topics': [
                'Elasticity', 'Hooke\'s Law', 'Young\'s Modulus', 'Bulk Modulus',
                'Shear Modulus', 'Fluid Mechanics', 'Bernoulli\'s Theorem', 'Viscosity'
            ]},
            {'unit': 9, 'name': 'Thermodynamics', 'topics': [
                'Thermal Equilibrium', 'Zeroth Law', 'First Law', 'Second Law',
                'Third Law', 'Heat Engines', 'Refrigerators', 'Carnot Cycle'
            ]},
            {'unit': 10, 'name': 'Kinetic Theory of Gases', 'topics': [
                'Gas Laws', 'Ideal Gas Equation', 'Kinetic Theory', 'Mean Free Path',
                'Avogadro\'s Law', 'Real Gases', 'Van der Waals Equation'
            ]},
            {'unit': 11, 'name': 'Oscillations and Waves', 'topics': [
                'Simple Harmonic Motion', 'Damped Oscillations', 'Forced Oscillations',
                'Resonance', 'Wave Motion', 'Standing Waves', 'Doppler Effect'
            ]},
            # Class 12
            {'unit': 12, 'name': 'Electrostatics', 'topics': [
                'Coulomb\'s Law', 'Electric Field', 'Electric Dipole', 'Gauss\'s Law',
                'Electric Potential', 'Capacitance', 'Dielectrics', 'Energy in Capacitors'
            ]},
            {'unit': 13, 'name': 'Current Electricity', 'topics': [
                'Ohm\'s Law', 'Resistivity', 'Conductivity', 'Kirchhoff\'s Laws',
                'Wheatstone Bridge', 'Potentiometer', 'Drift Velocity', 'Internal Resistance'
            ]},
            {'unit': 14, 'name': 'Magnetic Effects of Current and Magnetism', 'topics': [
                'Biot-Savart Law', 'Ampere\'s Law', 'Magnetic Force', 'Torque on a Loop',
                'Magnetic Properties', 'Earth\'s Magnetism', 'Moving Coil Galvanometer'
            ]},
            {'unit': 15, 'name': 'Electromagnetic Induction and Alternating Currents', 'topics': [
                'Faraday\'s Law', 'Lenz\'s Law', 'Self-Inductance', 'Mutual Inductance',
                'AC Circuits', 'Impedance', 'Power in AC', 'LC Oscillations', 'Transformers'
            ]},
            {'unit': 16, 'name': 'Electromagnetic Waves', 'topics': [
                'Maxwell\'s Equations', 'Electromagnetic Spectrum', 'Properties of EM Waves',
                'Displacement Current', 'Energy in EM Waves'
            ]},
            {'unit': 17, 'name': 'Optics', 'topics': [
                'Reflection', 'Refraction', 'Lenses', 'Mirrors', 'Optical Instruments',
                'Interference', 'Diffraction', 'Polarization', 'Huygens\' Principle'
            ]},
            {'unit': 18, 'name': 'Dual Nature of Matter and Radiation', 'topics': [
                'Photoelectric Effect', 'Wave-Particle Duality', 'de Broglie Wavelength',
                'Compton Effect', 'Davisson-Germer Experiment'
            ]},
            {'unit': 19, 'name': 'Atoms and Nuclei', 'topics': [
                'Rutherford\'s Model', 'Bohr\'s Model', 'Energy Levels', 'Radioactivity',
                'Nuclear Fission', 'Nuclear Fusion', 'Binding Energy'
            ]},
            {'unit': 20, 'name': 'Electronic Devices', 'topics': [
                'Semiconductors', 'Diodes', 'Transistors', 'Logic Gates', 'Amplifiers',
                'Oscillators', 'Rectifiers', 'Optoelectronic Devices'
            ]},
        ]

        # ============================================================
        # IMPORT DATA
        # ============================================================
        
        with transaction.atomic():
            self.stdout.write(self.style.SUCCESS('\n📚 Importing Biology chapters and topics...'))
            self._import_chapters(biology, biology_chapters)
            
            self.stdout.write(self.style.SUCCESS('\n📚 Importing Chemistry chapters and topics...'))
            self._import_chapters(chemistry, chemistry_chapters)
            
            self.stdout.write(self.style.SUCCESS('\n📚 Importing Physics chapters and topics...'))
            self._import_chapters(physics, physics_chapters)
        
        # ============================================================
        # SUMMARY
        # ============================================================
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ NEET Syllabus Import Completed!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'\n📊 Summary:'))
        self.stdout.write(self.style.SUCCESS(f'  Subjects: {Subject.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Chapters: {Chapter.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Topics: {Topic.objects.count()}'))
        
        for subject in Subject.objects.all():
            chapters = subject.chapters.count()
            topics = Topic.objects.filter(chapter__subject=subject).count()
            self.stdout.write(self.style.SUCCESS(f'  {subject.name}: {chapters} chapters, {topics} topics'))

    def _import_chapters(self, subject, chapters_data):
        """Helper method to import chapters and topics for a subject."""
        for chapter_data in chapters_data:
            unit = chapter_data['unit']
            name = chapter_data['name']
            topics = chapter_data['topics']
            
            chapter, created = Chapter.objects.get_or_create(
                subject=subject,
                name=name,
                defaults={
                    'unit_number': unit,
                    'description': f'Unit {unit} - {name}',
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✅ Created chapter: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⏳ Chapter exists: {name}'))
            
            for topic_name in topics:
                topic, created = Topic.objects.get_or_create(
                    chapter=chapter,
                    name=topic_name.strip(),
                    defaults={
                        'description': f'Topic from {name}',
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f'      📍 Created topic: {topic_name}')
                else:
                    self.stdout.write(f'      ⏳ Topic exists: {topic_name}')