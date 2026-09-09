# apps/core/management/commands/import_biology_syllabus.py

import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.core.models import Subject, Chapter, Topic


class Command(BaseCommand):
    help = 'Import Biology syllabus from CSV data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Biology syllabus import...'))
        
        # Get or create Biology subject
        biology, created = Subject.objects.get_or_create(
            name='Biology',
            defaults={
                'description': 'Biology syllabus for NEET preparation',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Biology subject'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Found existing Biology subject'))
        
        # Define the syllabus data
        syllabus_data = [
            # Class 11 Chapters
            {
                'class': '11',
                'chapter': 'The Living World',
                'topics': [
                    'What is living', 'Characteristics of living organisms', 'Biodiversity',
                    'Need for classification', 'Taxonomy', 'Systematics', 'Taxonomic categories',
                    'Taxonomic hierarchy', 'Species', 'Binomial nomenclature', 'Taxonomical aids'
                ]
            },
            {
                'class': '11',
                'chapter': 'Biological Classification',
                'topics': [
                    'Five-kingdom classification', 'Monera', 'Archaebacteria', 'Eubacteria',
                    'Cyanobacteria', 'Mycoplasma', 'Protista', 'Chrysophytes', 'Dinoflagellates',
                    'Euglenoids', 'Slime moulds', 'Protozoans', 'Fungi', 'Phycomycetes',
                    'Ascomycetes', 'Basidiomycetes', 'Deuteromycetes', 'Lichens', 'Viruses',
                    'Viroids'
                ]
            },
            {
                'class': '11',
                'chapter': 'Plant Kingdom',
                'topics': [
                    'Classification of plants', 'Algae', 'Chlorophyceae', 'Phaeophyceae',
                    'Rhodophyceae', 'Bryophytes', 'Pteridophytes', 'Gymnosperms',
                    'Salient features', 'Classification', 'Life cycles', 'Alternation of generations'
                ]
            },
            {
                'class': '11',
                'chapter': 'Animal Kingdom',
                'topics': [
                    'Basis of classification', 'Levels of organisation', 'Symmetry',
                    'Diploblastic and triploblastic organisation', 'Coelom', 'Segmentation',
                    'Notochord', 'Porifera', 'Cnidaria', 'Ctenophora', 'Platyhelminthes',
                    'Aschelminthes', 'Annelida', 'Arthropoda', 'Mollusca', 'Echinodermata',
                    'Hemichordata', 'Chordata', 'Pisces', 'Amphibia', 'Reptilia', 'Aves',
                    'Mammalia'
                ]
            },
            {
                'class': '11',
                'chapter': 'Morphology of Flowering Plants',
                'topics': [
                    'Root', 'Types of roots', 'Root modifications', 'Stem', 'Stem modifications',
                    'Leaf', 'Venation', 'Phyllotaxy', 'Leaf modifications', 'Inflorescence',
                    'Racemose', 'Cymose', 'Flower', 'Floral parts', 'Symmetry', 'Sexuality',
                    'Ovary position', 'Placentation', 'Fruit', 'Seed', 'Malvaceae', 'Cruciferae',
                    'Leguminosae', 'Compositae', 'Gramineae'
                ]
            },
            {
                'class': '11',
                'chapter': 'Anatomy of Flowering Plants',
                'topics': [
                    'Plant tissues', 'Meristematic tissues', 'Permanent tissues', 'Parenchyma',
                    'Collenchyma', 'Sclerenchyma', 'Xylem', 'Phloem', 'Tissue systems',
                    'Root anatomy', 'Stem anatomy', 'Leaf anatomy', 'Dicot anatomy',
                    'Monocot anatomy', 'Secondary growth'
                ]
            },
            {
                'class': '11',
                'chapter': 'Structural Organisation in Animals',
                'topics': [
                    'Animal tissues', 'Epithelial tissue', 'Connective tissue', 'Muscular tissue',
                    'Neural tissue', 'Animal morphology', 'Animal anatomy', 'Digestive system',
                    'Circulatory system', 'Respiratory system', 'Nervous system',
                    'Reproductive system'
                ]
            },
            {
                'class': '11',
                'chapter': 'Cell: The Unit of Life',
                'topics': [
                    'Cell theory', 'Prokaryotic cells', 'Eukaryotic cells', 'Plasma membrane',
                    'Cell wall', 'Endoplasmic reticulum', 'Golgi apparatus', 'Lysosomes',
                    'Mitochondria', 'Ribosomes', 'Plastids', 'Vacuoles', 'Peroxisomes',
                    'Cytoskeleton', 'Cilia', 'Flagella', 'Centrioles', 'Nucleus', 'Chromatin',
                    'Chromosomes', 'Plant cell', 'Animal cell'
                ]
            },
            {
                'class': '11',
                'chapter': 'Biomolecules',
                'topics': [
                    'Carbohydrates', 'Monosaccharides', 'Disaccharides', 'Polysaccharides',
                    'Proteins', 'Amino acids', 'Protein structure', 'Lipids', 'Fatty acids',
                    'Nucleic acids', 'DNA', 'RNA', 'Primary metabolites', 'Secondary metabolites',
                    'Enzymes', 'Properties of enzymes', 'Mechanism of enzyme action',
                    'Factors affecting enzyme activity', 'Cofactors', 'Enzyme inhibitors'
                ]
            },
            {
                'class': '11',
                'chapter': 'Cell Cycle and Cell Division',
                'topics': [
                    'Cell cycle', 'Interphase', 'G1 phase', 'S phase', 'G2 phase', 'M phase',
                    'Mitosis', 'Prophase', 'Metaphase', 'Anaphase', 'Telophase', 'Cytokinesis',
                    'Meiosis', 'Meiosis I', 'Meiosis II', 'Crossing over',
                    'Significance of mitosis', 'Significance of meiosis'
                ]
            },
            {
                'class': '11',
                'chapter': 'Photosynthesis in Higher Plants',
                'topics': [
                    'Photosynthesis', 'Site of photosynthesis', 'Photosynthetic pigments',
                    'Light reaction', 'Photophosphorylation', 'Cyclic photophosphorylation',
                    'Non-cyclic photophosphorylation', 'Chemiosmotic hypothesis',
                    'Dark reaction', 'Calvin cycle', 'C3 pathway', 'C4 pathway',
                    'Photorespiration', 'Factors affecting photosynthesis'
                ]
            },
            {
                'class': '11',
                'chapter': 'Respiration in Plants',
                'topics': [
                    'Exchange of gases', 'Cellular respiration', 'Glycolysis', 'Fermentation',
                    'Anaerobic respiration', 'Aerobic respiration', 'TCA cycle', 'Krebs cycle',
                    'Electron transport system', 'Oxidative phosphorylation', 'ATP production',
                    'Amphibolic pathways', 'Respiratory quotient'
                ]
            },
            {
                'class': '11',
                'chapter': 'Plant Growth and Development',
                'topics': [
                    'Seed germination', 'Phases of plant growth', 'Growth rate',
                    'Conditions required for growth', 'Differentiation', 'Dedifferentiation',
                    'Redifferentiation', 'Developmental sequence', 'Auxin', 'Gibberellins',
                    'Cytokinins', 'Ethylene', 'Abscisic acid'
                ]
            },
            {
                'class': '11',
                'chapter': 'Breathing and Exchange of Gases',
                'topics': [
                    'Respiratory organs', 'Human respiratory system', 'Mechanism of breathing',
                    'Inspiration', 'Expiration', 'Exchange of gases', 'Transport of oxygen',
                    'Transport of carbon dioxide', 'Regulation of respiration',
                    'Respiratory volumes', 'Respiratory capacities', 'Asthma', 'Emphysema',
                    'Occupational respiratory disorders'
                ]
            },
            {
                'class': '11',
                'chapter': 'Body Fluids and Circulation',
                'topics': [
                    'Blood', 'Plasma', 'RBC', 'WBC', 'Platelets', 'Blood groups',
                    'Blood coagulation', 'Lymph', 'Human circulatory system', 'Heart',
                    'Blood vessels', 'Cardiac cycle', 'Cardiac output', 'ECG',
                    'Double circulation', 'Regulation of cardiac activity', 'Hypertension',
                    'Coronary artery disease', 'Angina pectoris', 'Heart failure'
                ]
            },
            {
                'class': '11',
                'chapter': 'Excretory Products and Their Elimination',
                'topics': [
                    'Modes of excretion', 'Ammonotelism', 'Ureotelism', 'Uricotelism',
                    'Human excretory system', 'Kidney', 'Nephron', 'Urine formation',
                    'Glomerular filtration', 'Reabsorption', 'Tubular secretion',
                    'Osmoregulation', 'Regulation of kidney function', 'ADH',
                    'Renin-angiotensin system', 'Atrial natriuretic factor',
                    'Diabetes insipidus', 'Uraemia', 'Renal failure', 'Renal calculi',
                    'Nephritis', 'Dialysis', 'Artificial kidney'
                ]
            },
            {
                'class': '11',
                'chapter': 'Locomotion and Movement',
                'topics': [
                    'Types of movement', 'Ciliary movement', 'Flagellar movement',
                    'Muscular movement', 'Skeletal muscles', 'Contractile proteins',
                    'Actin', 'Myosin', 'Muscle contraction', 'Sliding filament theory',
                    'Skeletal system', 'Functions of skeleton', 'Joints',
                    'Myasthenia gravis', 'Tetany', 'Muscular dystrophy', 'Arthritis',
                    'Osteoporosis', 'Gout'
                ]
            },
            {
                'class': '11',
                'chapter': 'Neural Control and Coordination',
                'topics': [
                    'Nervous system', 'Neuron', 'Structure of neuron', 'Types of neurons',
                    'Nerve impulse', 'Resting potential', 'Action potential', 'Synapse',
                    'CNS', 'PNS', 'Autonomic nervous system', 'Brain', 'Spinal cord',
                    'Reflex action', 'Sensory receptors', 'Eye', 'Ear', 'Neural coordination'
                ]
            },
            {
                'class': '11',
                'chapter': 'Chemical Coordination and Integration',
                'topics': [
                    'Endocrine glands', 'Hormones', 'Hypothalamus', 'Pituitary gland',
                    'Pineal gland', 'Thyroid gland', 'Parathyroid gland', 'Thymus',
                    'Adrenal gland', 'Pancreas', 'Testes', 'Ovaries', 'Hormonal regulation',
                    'Mechanism of hormone action', 'Hormonal disorders'
                ]
            },
            # Class 12 Chapters
            {
                'class': '12',
                'chapter': 'Sexual Reproduction in Flowering Plants',
                'topics': [
                    'Flower structure', 'Androecium', 'Gynoecium', 'Male gametophyte',
                    'Female gametophyte', 'Microsporogenesis', 'Megasporogenesis',
                    'Pollination', 'Self-pollination', 'Cross-pollination',
                    'Agents of pollination', 'Outbreeding devices', 'Pollen-pistil interaction',
                    'Fertilisation', 'Double fertilisation', 'Triple fusion', 'Endosperm',
                    'Embryo development', 'Seed formation', 'Fruit formation', 'Apomixis',
                    'Parthenocarpy', 'Polyembryony'
                ]
            },
            {
                'class': '12',
                'chapter': 'Human Reproduction',
                'topics': [
                    'Male reproductive system', 'Female reproductive system', 'Testis',
                    'Ovary', 'Gametogenesis', 'Spermatogenesis', 'Oogenesis',
                    'Menstrual cycle', 'Fertilisation', 'Embryonic development',
                    'Blastocyst formation', 'Implantation', 'Pregnancy', 'Placenta',
                    'Parturition', 'Lactation'
                ]
            },
            {
                'class': '12',
                'chapter': 'Reproductive Health',
                'topics': [
                    'Reproductive health', 'Sexually transmitted diseases', 'Prevention of STDs',
                    'Birth control', 'Natural contraceptive methods', 'Barrier methods',
                    'IUDs', 'Hormonal contraception', 'Surgical contraception', 'MTP',
                    'Amniocentesis', 'Infertility', 'IVF', 'ZIFT', 'GIFT',
                    'Assisted reproductive technologies'
                ]
            },
            {
                'class': '12',
                'chapter': 'Principles of Inheritance and Variation',
                'topics': [
                    'Heredity', 'Variation', "Mendel's experiments", 'Mendelian inheritance',
                    'Law of dominance', 'Law of segregation', 'Law of independent assortment',
                    'Monohybrid cross', 'Dihybrid cross', 'Test cross', 'Back cross',
                    'Incomplete dominance', 'Codominance', 'Multiple alleles', 'ABO blood groups',
                    'Polygenic inheritance', 'Pleiotropy', 'Chromosomal theory of inheritance',
                    'Linkage', 'Crossing over', 'Sex determination', 'Sex-linked inheritance',
                    'Haemophilia', 'Colour blindness', 'Thalassemia', 'Sickle-cell anaemia',
                    'Down syndrome', 'Klinefelter syndrome', 'Turner syndrome'
                ]
            },
            {
                'class': '12',
                'chapter': 'Molecular Basis of Inheritance',
                'topics': [
                    'Genetic material', 'DNA', 'RNA', 'Structure of DNA', 'Structure of RNA',
                    'DNA packaging', 'DNA replication', 'Semiconservative replication',
                    'Central dogma', 'Transcription', 'Genetic code', 'Translation',
                    'Protein synthesis', 'Gene expression', 'Gene regulation', 'Lac operon',
                    'Human Genome Project', 'Genome', 'DNA fingerprinting'
                ]
            },
            {
                'class': '12',
                'chapter': 'Evolution',
                'topics': [
                    'Origin of life', 'Biological evolution', 'Evidence for evolution',
                    'Paleontology', 'Comparative anatomy', 'Embryology', 'Molecular evidence',
                    'Darwinism', 'Natural selection', 'Modern synthetic theory', 'Variation',
                    'Mutation', 'Recombination', 'Types of natural selection', 'Gene flow',
                    'Genetic drift', 'Hardy-Weinberg principle', 'Adaptive radiation',
                    'Human evolution'
                ]
            },
            {
                'class': '12',
                'chapter': 'Human Health and Disease',
                'topics': [
                    'Health', 'Disease', 'Pathogens', 'Parasites', 'Malaria', 'Filariasis',
                    'Ascariasis', 'Typhoid', 'Pneumonia', 'Common cold', 'Amoebiasis',
                    'Ringworm', 'Dengue', 'Chikungunya', 'Immunity', 'Innate immunity',
                    'Acquired immunity', 'Vaccines', 'Cancer', 'HIV', 'AIDS', 'Drug abuse',
                    'Alcohol abuse', 'Tobacco abuse'
                ]
            },
            {
                'class': '12',
                'chapter': 'Microbes in Human Welfare',
                'topics': [
                    'Microbes in household products', 'Curd', 'Bread', 'Fermented foods',
                    'Industrial production', 'Antibiotics', 'Organic acids', 'Alcohol',
                    'Enzymes', 'Sewage treatment', 'Biogas', 'Biocontrol agents',
                    'Biofertilisers'
                ]
            },
            {
                'class': '12',
                'chapter': 'Biotechnology: Principles and Processes',
                'topics': [
                    'Biotechnology', 'Genetic engineering', 'Recombinant DNA technology',
                    'Restriction enzymes', 'DNA ligase', 'DNA polymerase', 'Vectors',
                    'Plasmids', 'Host organisms', 'Recombinant DNA', 'Gene cloning',
                    'Transformation', 'Selection of transformed cells', 'PCR',
                    'Biotechnology processes'
                ]
            },
            {
                'class': '12',
                'chapter': 'Biotechnology and Its Applications',
                'topics': [
                    'Applications of biotechnology', 'Human insulin', 'Vaccines',
                    'Gene therapy', 'Biotechnology in agriculture',
                    'Genetically modified organisms', 'Bt crops', 'Transgenic animals',
                    'Biosafety', 'Biopiracy', 'Patents'
                ]
            },
            {
                'class': '12',
                'chapter': 'Organisms and Populations',
                'topics': [
                    'Organisms and environment', 'Environmental factors', 'Population',
                    'Population attributes', 'Population density', 'Natality', 'Mortality',
                    'Age distribution', 'Population growth', 'Mutualism', 'Competition',
                    'Predation', 'Parasitism', 'Adaptations'
                ]
            },
            {
                'class': '12',
                'chapter': 'Ecosystem',
                'topics': [
                    'Ecosystem', 'Abiotic components', 'Biotic components', 'Productivity',
                    'Primary productivity', 'Secondary productivity', 'Decomposition',
                    'Energy flow', 'Food chain', 'Food web', 'Ecological pyramids',
                    'Pyramid of number', 'Pyramid of biomass', 'Pyramid of energy',
                    'Nutrient cycling'
                ]
            },
            {
                'class': '12',
                'chapter': 'Biodiversity and Conservation',
                'topics': [
                    'Biodiversity', 'Genetic diversity', 'Species diversity',
                    'Ecosystem diversity', 'Patterns of biodiversity',
                    'Importance of biodiversity', 'Loss of biodiversity',
                    'Biodiversity conservation', 'Biodiversity hotspots',
                    'Endangered organisms', 'Extinction', 'Red Data Book',
                    'Biosphere reserves', 'National parks', 'Wildlife sanctuaries',
                    'Sacred groves'
                ]
            }
        ]
        
        # Import the data
        with transaction.atomic():
            for item in syllabus_data:
                class_num = item['class']
                chapter_name = item['chapter']
                topics = item['topics']
                
                # Create chapter (using class as unit number)
                chapter, created = Chapter.objects.get_or_create(
                    subject=biology,
                    name=chapter_name,
                    defaults={
                        'unit_number': int(class_num),
                        'description': f'Class {class_num} - {chapter_name}',
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  Created chapter: {chapter_name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  Chapter exists: {chapter_name}'))
                
                # Create topics for this chapter
                for topic_name in topics:
                    topic, created = Topic.objects.get_or_create(
                        chapter=chapter,
                        name=topic_name.strip(),
                        defaults={
                            'description': f'Topic from {chapter_name}',
                            'is_active': True
                        }
                    )
                    if created:
                        self.stdout.write(f'    Created topic: {topic_name}')
                    else:
                        self.stdout.write(f'    Topic exists: {topic_name}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Biology syllabus import completed!'))
        self.stdout.write(self.style.SUCCESS(f'Total chapters: {Chapter.objects.filter(subject=biology).count()}'))
        self.stdout.write(self.style.SUCCESS(f'Total topics: {Topic.objects.filter(chapter__subject=biology).count()}'))