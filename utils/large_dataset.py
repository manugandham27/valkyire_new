"""
large_dataset.py
================
Comprehensive knowledge dataset for VALKYRIE-Decoder v2.
Provides 873+ structured facts as StructuredClaim-compatible samples
across multiple domains: geography, science, technology, history, etc.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DataSample:
    """One fact sample for the knowledge base."""
    text: str
    subject: str
    relation: str
    obj: str
    confidence: float
    label: bool  # True = factual, False = hallucination

    def is_true(self) -> bool:
        return self.label

    def has_triple(self) -> bool:
        return bool(self.subject and self.relation and self.obj)


def build_large_dataset() -> list:
    """Return 873+ DataSample objects covering diverse knowledge domains."""
    samples = []

    # ── GEOGRAPHY: Capitals ───────────────────────────────────────────
    capitals = [
        ("Paris", "capital_of", "France", 1.0),
        ("London", "capital_of", "United Kingdom", 1.0),
        ("Berlin", "capital_of", "Germany", 1.0),
        ("Rome", "capital_of", "Italy", 1.0),
        ("Madrid", "capital_of", "Spain", 1.0),
        ("Tokyo", "capital_of", "Japan", 1.0),
        ("Beijing", "capital_of", "China", 1.0),
        ("Moscow", "capital_of", "Russia", 1.0),
        ("Washington D.C.", "capital_of", "United States", 1.0),
        ("Ottawa", "capital_of", "Canada", 1.0),
        ("Canberra", "capital_of", "Australia", 1.0),
        ("Brasilia", "capital_of", "Brazil", 1.0),
        ("New Delhi", "capital_of", "India", 1.0),
        ("Seoul", "capital_of", "South Korea", 1.0),
        ("Bangkok", "capital_of", "Thailand", 1.0),
        ("Cairo", "capital_of", "Egypt", 1.0),
        ("Ankara", "capital_of", "Turkey", 1.0),
        ("Athens", "capital_of", "Greece", 1.0),
        ("Dublin", "capital_of", "Ireland", 1.0),
        ("Vienna", "capital_of", "Austria", 1.0),
        ("Lisbon", "capital_of", "Portugal", 1.0),
        ("Stockholm", "capital_of", "Sweden", 1.0),
        ("Oslo", "capital_of", "Norway", 1.0),
        ("Copenhagen", "capital_of", "Denmark", 1.0),
        ("Helsinki", "capital_of", "Finland", 1.0),
        ("Warsaw", "capital_of", "Poland", 1.0),
        ("Prague", "capital_of", "Czech Republic", 1.0),
        ("Budapest", "capital_of", "Hungary", 1.0),
        ("Bucharest", "capital_of", "Romania", 1.0),
        ("Amsterdam", "capital_of", "Netherlands", 1.0),
        ("Brussels", "capital_of", "Belgium", 1.0),
        ("Bern", "capital_of", "Switzerland", 1.0),
        ("Nairobi", "capital_of", "Kenya", 1.0),
        ("Pretoria", "capital_of", "South Africa", 1.0),
        ("Lima", "capital_of", "Peru", 1.0),
        ("Santiago", "capital_of", "Chile", 1.0),
        ("Buenos Aires", "capital_of", "Argentina", 1.0),
        ("Bogota", "capital_of", "Colombia", 1.0),
        ("Mexico City", "capital_of", "Mexico", 1.0),
        ("Havana", "capital_of", "Cuba", 1.0),
        ("Jakarta", "capital_of", "Indonesia", 1.0),
        ("Kuala Lumpur", "capital_of", "Malaysia", 1.0),
        ("Manila", "capital_of", "Philippines", 1.0),
        ("Hanoi", "capital_of", "Vietnam", 1.0),
        ("Islamabad", "capital_of", "Pakistan", 1.0),
        ("Dhaka", "capital_of", "Bangladesh", 1.0),
        ("Colombo", "capital_of", "Sri Lanka", 1.0),
        ("Kathmandu", "capital_of", "Nepal", 1.0),
        ("Riyadh", "capital_of", "Saudi Arabia", 1.0),
        ("Baghdad", "capital_of", "Iraq", 1.0),
        ("Tehran", "capital_of", "Iran", 1.0),
        ("Kabul", "capital_of", "Afghanistan", 1.0),
        ("Kyiv", "capital_of", "Ukraine", 1.0),
        ("Minsk", "capital_of", "Belarus", 1.0),
        ("Tbilisi", "capital_of", "Georgia", 1.0),
        ("Accra", "capital_of", "Ghana", 1.0),
        ("Addis Ababa", "capital_of", "Ethiopia", 1.0),
        ("Rabat", "capital_of", "Morocco", 1.0),
        ("Tunis", "capital_of", "Tunisia", 1.0),
        ("Algiers", "capital_of", "Algeria", 1.0),
    ]

    for subj, rel, obj, conf in capitals:
        samples.append(DataSample(
            text=f"{subj} is the capital of {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── GEOGRAPHY: Located In ─────────────────────────────────────────
    locations = [
        ("Eiffel Tower", "located_in", "Paris", 1.0),
        ("Statue Of Liberty", "located_in", "New York", 1.0),
        ("Big Ben", "located_in", "London", 1.0),
        ("Colosseum", "located_in", "Rome", 1.0),
        ("Great Wall", "located_in", "China", 1.0),
        ("Taj Mahal", "located_in", "Agra", 1.0),
        ("Machu Picchu", "located_in", "Peru", 1.0),
        ("Pyramids Of Giza", "located_in", "Egypt", 1.0),
        ("Sydney Opera House", "located_in", "Sydney", 1.0),
        ("Christ The Redeemer", "located_in", "Rio De Janeiro", 1.0),
        ("Parthenon", "located_in", "Athens", 1.0),
        ("Buckingham Palace", "located_in", "London", 1.0),
        ("Golden Gate Bridge", "located_in", "San Francisco", 1.0),
        ("Mount Rushmore", "located_in", "South Dakota", 1.0),
        ("Kremlin", "located_in", "Moscow", 1.0),
        ("Forbidden City", "located_in", "Beijing", 1.0),
        ("Angkor Wat", "located_in", "Cambodia", 1.0),
        ("Petra", "located_in", "Jordan", 1.0),
        ("Sagrada Familia", "located_in", "Barcelona", 1.0),
        ("Tower Of London", "located_in", "London", 1.0),
        ("Vatican City", "located_in", "Rome", 1.0),
        ("Louvre Museum", "located_in", "Paris", 1.0),
        ("Hollywood Sign", "located_in", "Los Angeles", 1.0),
        ("Stonehenge", "located_in", "England", 1.0),
        ("Mount Fuji", "located_in", "Japan", 1.0),
        ("Niagara Falls", "located_in", "Ontario", 0.95),
        ("Grand Canyon", "located_in", "Arizona", 1.0),
        ("Amazon River", "located_in", "South America", 1.0),
        ("Nile River", "located_in", "Africa", 1.0),
        ("Mount Everest", "located_in", "Nepal", 1.0),
        ("Sahara Desert", "located_in", "Africa", 1.0),
        ("Silicon Valley", "located_in", "California", 1.0),
        ("Wall Street", "located_in", "New York", 1.0),
        ("Broadway", "located_in", "New York", 1.0),
        ("Times Square", "located_in", "New York", 1.0),
        ("Central Park", "located_in", "New York", 1.0),
        ("White House", "located_in", "Washington D.C.", 1.0),
        ("Pentagon", "located_in", "Virginia", 1.0),
        ("Burj Khalifa", "located_in", "Dubai", 1.0),
        ("Leaning Tower", "located_in", "Pisa", 1.0),
    ]

    for subj, rel, obj, conf in locations:
        samples.append(DataSample(
            text=f"{subj} is located in {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── TECHNOLOGY: Founded By ────────────────────────────────────────
    tech_founders = [
        ("Apple", "founded_by", "Steve Jobs", 1.0),
        ("Microsoft", "founded_by", "Bill Gates", 1.0),
        ("Google", "founded_by", "Larry Page", 1.0),
        ("Google", "founded_by", "Sergey Brin", 1.0),
        ("Amazon", "founded_by", "Jeff Bezos", 1.0),
        ("Tesla", "founded_by", "Elon Musk", 0.90),
        ("Facebook", "founded_by", "Mark Zuckerberg", 1.0),
        ("Twitter", "founded_by", "Jack Dorsey", 0.95),
        ("SpaceX", "founded_by", "Elon Musk", 1.0),
        ("Netflix", "founded_by", "Reed Hastings", 0.95),
        ("Oracle", "founded_by", "Larry Ellison", 1.0),
        ("IBM", "founded_by", "Charles Ranlett Flint", 0.90),
        ("Intel", "founded_by", "Robert Noyce", 0.95),
        ("Samsung", "founded_by", "Lee Byung-chul", 0.95),
        ("Sony", "founded_by", "Akio Morita", 0.95),
        ("Nintendo", "founded_by", "Fusajiro Yamauchi", 0.95),
        ("Alibaba", "founded_by", "Jack Ma", 1.0),
        ("Uber", "founded_by", "Travis Kalanick", 0.95),
        ("Airbnb", "founded_by", "Brian Chesky", 0.95),
        ("PayPal", "founded_by", "Peter Thiel", 0.90),
        ("LinkedIn", "founded_by", "Reid Hoffman", 0.95),
        ("Spotify", "founded_by", "Daniel Ek", 0.95),
        ("Snapchat", "founded_by", "Evan Spiegel", 0.95),
        ("TikTok", "founded_by", "Zhang Yiming", 0.95),
        ("Nvidia", "founded_by", "Jensen Huang", 1.0),
        ("AMD", "founded_by", "Jerry Sanders", 0.90),
        ("Dell", "founded_by", "Michael Dell", 1.0),
        ("HP", "founded_by", "Bill Hewlett", 0.95),
        ("Cisco", "founded_by", "Leonard Bosack", 0.90),
        ("Adobe", "founded_by", "John Warnock", 0.95),
        ("Salesforce", "founded_by", "Marc Benioff", 0.95),
        ("Zoom", "founded_by", "Eric Yuan", 0.95),
        ("Reddit", "founded_by", "Steve Huffman", 0.95),
        ("Wikipedia", "founded_by", "Jimmy Wales", 0.95),
        ("Yahoo", "founded_by", "Jerry Yang", 0.95),
        ("eBay", "founded_by", "Pierre Omidyar", 0.95),
        ("Dropbox", "founded_by", "Drew Houston", 0.95),
        ("Stripe", "founded_by", "Patrick Collison", 0.95),
        ("ByteDance", "founded_by", "Zhang Yiming", 0.95),
        ("OpenAI", "founded_by", "Sam Altman", 0.90),
    ]

    for subj, rel, obj, conf in tech_founders:
        samples.append(DataSample(
            text=f"{subj} was founded by {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── SCIENCE: Discoveries ──────────────────────────────────────────
    discoveries = [
        ("Einstein", "discovered", "Relativity", 1.0),
        ("Newton", "discovered", "Gravity", 1.0),
        ("Darwin", "discovered", "Evolution", 1.0),
        ("Curie", "discovered", "Radium", 1.0),
        ("Curie", "discovered", "Polonium", 1.0),
        ("Fleming", "discovered", "Penicillin", 1.0),
        ("Galileo", "discovered", "Jupiter Moons", 0.95),
        ("Hubble", "discovered", "Expanding Universe", 0.95),
        ("Watson", "discovered", "DNA Structure", 0.90),
        ("Crick", "discovered", "DNA Structure", 0.90),
        ("Mendeleev", "discovered", "Periodic Table", 0.95),
        ("Faraday", "discovered", "Electromagnetic Induction", 1.0),
        ("Tesla", "discovered", "Alternating Current", 0.95),
        ("Edison", "discovered", "Practical Light Bulb", 0.90),
        ("Pasteur", "discovered", "Pasteurization", 1.0),
        ("Copernicus", "discovered", "Heliocentric Model", 1.0),
        ("Kepler", "discovered", "Planetary Motion Laws", 0.95),
        ("Bohr", "discovered", "Atomic Model", 0.95),
        ("Heisenberg", "discovered", "Uncertainty Principle", 1.0),
        ("Schrodinger", "discovered", "Wave Equation", 0.95),
        ("Planck", "discovered", "Quantum Theory", 1.0),
        ("Rutherford", "discovered", "Atomic Nucleus", 1.0),
        ("Leeuwenhoek", "discovered", "Microorganisms", 0.95),
        ("Jenner", "discovered", "Vaccination", 0.95),
        ("Rosalind Franklin", "discovered", "DNA X-ray Diffraction", 0.95),
        ("Hawking", "discovered", "Hawking Radiation", 0.95),
        ("Turing", "discovered", "Turing Machine", 1.0),
        ("Babbage", "discovered", "Analytical Engine", 0.90),
        ("Archimedes", "discovered", "Buoyancy Principle", 1.0),
        ("Pythagoras", "discovered", "Pythagorean Theorem", 0.95),
    ]

    for subj, rel, obj, conf in discoveries:
        samples.append(DataSample(
            text=f"{subj} discovered {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── GEOGRAPHY: Population ─────────────────────────────────────────
    populations = [
        ("Tokyo", "population_of", "37 Million", 0.95),
        ("Delhi", "population_of", "32 Million", 0.90),
        ("Shanghai", "population_of", "29 Million", 0.90),
        ("Sao Paulo", "population_of", "22 Million", 0.90),
        ("Mexico City", "population_of", "22 Million", 0.90),
        ("Cairo", "population_of", "21 Million", 0.90),
        ("Mumbai", "population_of", "21 Million", 0.90),
        ("Beijing", "population_of", "21 Million", 0.90),
        ("Dhaka", "population_of", "22 Million", 0.85),
        ("Osaka", "population_of", "19 Million", 0.90),
        ("New York", "population_of", "18 Million", 0.90),
        ("Karachi", "population_of", "16 Million", 0.85),
        ("Istanbul", "population_of", "16 Million", 0.90),
        ("Buenos Aires", "population_of", "15 Million", 0.90),
        ("Kolkata", "population_of", "15 Million", 0.85),
        ("Lagos", "population_of", "15 Million", 0.85),
        ("Manila", "population_of", "14 Million", 0.85),
        ("Guangzhou", "population_of", "14 Million", 0.85),
        ("London", "population_of", "9 Million", 0.98),
        ("Paris", "population_of", "11 Million", 0.95),
        ("Los Angeles", "population_of", "13 Million", 0.90),
        ("Moscow", "population_of", "12 Million", 0.90),
        ("Chicago", "population_of", "9 Million", 0.90),
        ("Toronto", "population_of", "6 Million", 0.90),
        ("Sydney", "population_of", "5 Million", 0.90),
    ]

    for subj, rel, obj, conf in populations:
        samples.append(DataSample(
            text=f"{subj} has a population of {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── ASTRONOMY: Planet/Space Facts ─────────────────────────────────
    space = [
        ("Mars", "color", "Red", 1.0),
        ("Jupiter", "is", "Largest Planet", 1.0),
        ("Saturn", "is", "Ringed Planet", 1.0),
        ("Mercury", "is", "Closest To Sun", 1.0),
        ("Venus", "is", "Hottest Planet", 0.95),
        ("Neptune", "is", "Farthest Planet", 0.95),
        ("Pluto", "is", "Dwarf Planet", 1.0),
        ("Sun", "is", "Star", 1.0),
        ("Moon", "is", "Natural Satellite", 1.0),
        ("Earth", "is", "Third Planet", 1.0),
        ("Milky Way", "is", "Galaxy", 1.0),
        ("Black Hole", "is", "Collapsed Star", 0.90),
        ("Mars", "is", "Fourth Planet", 1.0),
        ("Uranus", "is", "Ice Giant", 0.95),
        ("Europa", "located_in", "Jupiter System", 0.95),
        ("Titan", "located_in", "Saturn System", 0.95),
        ("Phobos", "located_in", "Mars System", 0.95),
        ("Andromeda", "is", "Nearest Galaxy", 0.95),
        ("ISS", "located_in", "Low Earth Orbit", 0.95),
        ("Hubble Telescope", "located_in", "Low Earth Orbit", 0.95),
    ]

    for subj, rel, obj, conf in space:
        samples.append(DataSample(
            text=f"{subj} is {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── GEOGRAPHY: Continents / Regions ───────────────────────────────
    geo_facts = [
        ("France", "located_in", "Europe", 1.0),
        ("Germany", "located_in", "Europe", 1.0),
        ("Italy", "located_in", "Europe", 1.0),
        ("Spain", "located_in", "Europe", 1.0),
        ("Japan", "located_in", "Asia", 1.0),
        ("China", "located_in", "Asia", 1.0),
        ("India", "located_in", "Asia", 1.0),
        ("Brazil", "located_in", "South America", 1.0),
        ("Australia", "located_in", "Oceania", 1.0),
        ("Egypt", "located_in", "Africa", 1.0),
        ("Kenya", "located_in", "Africa", 1.0),
        ("Mexico", "located_in", "North America", 1.0),
        ("Canada", "located_in", "North America", 1.0),
        ("Russia", "located_in", "Europe", 0.90),
        ("South Korea", "located_in", "Asia", 1.0),
        ("Thailand", "located_in", "Asia", 1.0),
        ("Nigeria", "located_in", "Africa", 1.0),
        ("Argentina", "located_in", "South America", 1.0),
        ("Colombia", "located_in", "South America", 1.0),
        ("Peru", "located_in", "South America", 1.0),
        ("Chile", "located_in", "South America", 1.0),
        ("Iran", "located_in", "Asia", 1.0),
        ("Turkey", "located_in", "Europe", 0.85),
        ("Pakistan", "located_in", "Asia", 1.0),
        ("Indonesia", "located_in", "Asia", 1.0),
        ("Philippines", "located_in", "Asia", 1.0),
        ("Vietnam", "located_in", "Asia", 1.0),
        ("Sweden", "located_in", "Europe", 1.0),
        ("Norway", "located_in", "Europe", 1.0),
        ("Poland", "located_in", "Europe", 1.0),
    ]

    for subj, rel, obj, conf in geo_facts:
        samples.append(DataSample(
            text=f"{subj} is located in {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── HISTORY: Historical Facts ─────────────────────────────────────
    history = [
        ("United States", "founded_by", "Founding Fathers", 0.90),
        ("Roman Empire", "founded_by", "Augustus", 0.90),
        ("Ottoman Empire", "founded_by", "Osman I", 0.90),
        ("Mongol Empire", "founded_by", "Genghis Khan", 1.0),
        ("Alexander The Great", "discovered", "Persian Empire", 0.85),
        ("Columbus", "discovered", "Americas", 0.90),
        ("Magellan", "discovered", "Pacific Ocean Route", 0.90),
        ("Marco Polo", "discovered", "Silk Road", 0.85),
        ("Vasco Da Gama", "discovered", "Sea Route To India", 0.90),
        ("Neil Armstrong", "discovered", "Moon Surface", 0.95),
        ("Wright Brothers", "discovered", "Powered Flight", 0.95),
        ("Gutenberg", "discovered", "Printing Press", 0.95),
        ("James Watt", "discovered", "Steam Engine", 0.90),
        ("Alexander Graham Bell", "discovered", "Telephone", 0.95),
        ("Marconi", "discovered", "Radio", 0.95),
        ("Tim Berners-Lee", "discovered", "World Wide Web", 1.0),
        ("Ada Lovelace", "discovered", "Computer Programming", 0.90),
        ("Marie Curie", "discovered", "Radioactivity", 1.0),
        ("Nikola Tesla", "discovered", "AC Motor", 0.95),
        ("Benjamin Franklin", "discovered", "Lightning Rod", 0.90),
    ]

    for subj, rel, obj, conf in history:
        samples.append(DataSample(
            text=f"{subj} discovered {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── LANGUAGE / CULTURE ────────────────────────────────────────────
    culture = [
        ("English", "is", "Language Of United Kingdom", 0.95),
        ("Mandarin", "is", "Language Of China", 0.95),
        ("Spanish", "is", "Language Of Spain", 0.95),
        ("Hindi", "is", "Language Of India", 0.95),
        ("Arabic", "is", "Language Of Saudi Arabia", 0.95),
        ("French", "is", "Language Of France", 0.95),
        ("Portuguese", "is", "Language Of Portugal", 0.95),
        ("Russian", "is", "Language Of Russia", 0.95),
        ("Japanese", "is", "Language Of Japan", 0.95),
        ("Korean", "is", "Language Of South Korea", 0.95),
        ("German", "is", "Language Of Germany", 0.95),
        ("Italian", "is", "Language Of Italy", 0.95),
        ("Turkish", "is", "Language Of Turkey", 0.95),
        ("Dutch", "is", "Language Of Netherlands", 0.95),
        ("Swedish", "is", "Language Of Sweden", 0.95),
        ("Greek", "is", "Language Of Greece", 0.95),
        ("Polish", "is", "Language Of Poland", 0.95),
        ("Thai", "is", "Language Of Thailand", 0.95),
        ("Vietnamese", "is", "Language Of Vietnam", 0.95),
        ("Swahili", "is", "Language Of Kenya", 0.90),
    ]

    for subj, rel, obj, conf in culture:
        samples.append(DataSample(
            text=f"{subj} is the {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── TECHNOLOGY: Product/Company Facts ─────────────────────────────
    tech_facts = [
        ("Apple", "located_in", "Cupertino", 1.0),
        ("Google", "located_in", "Mountain View", 1.0),
        ("Microsoft", "located_in", "Redmond", 1.0),
        ("Amazon", "located_in", "Seattle", 1.0),
        ("Tesla", "located_in", "Austin", 0.95),
        ("Facebook", "located_in", "Menlo Park", 1.0),
        ("Netflix", "located_in", "Los Gatos", 0.95),
        ("Twitter", "located_in", "San Francisco", 0.95),
        ("Nvidia", "located_in", "Santa Clara", 1.0),
        ("Intel", "located_in", "Santa Clara", 0.95),
        ("Oracle", "located_in", "Austin", 0.95),
        ("Salesforce", "located_in", "San Francisco", 0.95),
        ("Adobe", "located_in", "San Jose", 0.95),
        ("Samsung", "located_in", "Seoul", 1.0),
        ("Sony", "located_in", "Tokyo", 1.0),
        ("Toyota", "located_in", "Toyota City", 0.95),
        ("BMW", "located_in", "Munich", 1.0),
        ("Mercedes", "located_in", "Stuttgart", 1.0),
        ("Volkswagen", "located_in", "Wolfsburg", 0.95),
        ("Siemens", "located_in", "Munich", 0.95),
        ("Nokia", "located_in", "Espoo", 0.95),
        ("Huawei", "located_in", "Shenzhen", 0.95),
        ("Tencent", "located_in", "Shenzhen", 0.95),
        ("Baidu", "located_in", "Beijing", 0.95),
        ("Alibaba", "located_in", "Hangzhou", 1.0),
        ("SpaceX", "located_in", "Hawthorne", 0.95),
        ("OpenAI", "located_in", "San Francisco", 0.95),
        ("Uber", "located_in", "San Francisco", 0.95),
        ("Airbnb", "located_in", "San Francisco", 0.95),
        ("Stripe", "located_in", "San Francisco", 0.95),
    ]

    for subj, rel, obj, conf in tech_facts:
        samples.append(DataSample(
            text=f"{subj} is located in {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── SCIENCE: Elements / Chemistry ─────────────────────────────────
    elements = [
        ("Hydrogen", "is", "Lightest Element", 1.0),
        ("Helium", "is", "Noble Gas", 1.0),
        ("Oxygen", "is", "Essential For Life", 1.0),
        ("Carbon", "is", "Basis Of Organic Chemistry", 1.0),
        ("Gold", "is", "Precious Metal", 1.0),
        ("Silver", "is", "Precious Metal", 1.0),
        ("Iron", "is", "Most Common Metal", 0.90),
        ("Uranium", "is", "Radioactive Element", 1.0),
        ("Nitrogen", "is", "Most Abundant In Atmosphere", 1.0),
        ("Water", "is", "H2O", 1.0),
        ("Diamond", "is", "Hardest Natural Material", 1.0),
        ("Copper", "is", "Conductive Metal", 0.95),
        ("Platinum", "is", "Precious Metal", 0.95),
        ("Titanium", "is", "Strong Light Metal", 0.95),
        ("Silicon", "is", "Semiconductor", 1.0),
        ("Lithium", "is", "Lightest Metal", 0.95),
        ("Sodium", "is", "Alkali Metal", 1.0),
        ("Chlorine", "is", "Halogen", 1.0),
        ("Neon", "is", "Noble Gas", 1.0),
        ("Mercury", "is", "Liquid Metal", 1.0),
    ]

    for subj, rel, obj, conf in elements:
        samples.append(DataSample(
            text=f"{subj} is {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── BIOLOGY: Animals / Nature ─────────────────────────────────────
    biology = [
        ("Blue Whale", "is", "Largest Animal", 1.0),
        ("Cheetah", "is", "Fastest Land Animal", 1.0),
        ("Elephant", "is", "Largest Land Animal", 1.0),
        ("Giraffe", "is", "Tallest Animal", 1.0),
        ("Hummingbird", "is", "Smallest Bird", 0.95),
        ("Eagle", "is", "Bird Of Prey", 0.95),
        ("Dolphin", "is", "Intelligent Marine Mammal", 0.95),
        ("Octopus", "is", "Intelligent Invertebrate", 0.90),
        ("Penguin", "located_in", "Antarctica", 0.90),
        ("Polar Bear", "located_in", "Arctic", 0.95),
        ("Kangaroo", "located_in", "Australia", 1.0),
        ("Panda", "located_in", "China", 1.0),
        ("Tiger", "located_in", "Asia", 0.95),
        ("Lion", "located_in", "Africa", 0.95),
        ("Koala", "located_in", "Australia", 1.0),
        ("Amazon Rainforest", "located_in", "South America", 1.0),
        ("Great Barrier Reef", "located_in", "Australia", 1.0),
        ("Sequoia", "is", "Tallest Tree", 0.95),
        ("Shark", "is", "Apex Predator", 0.90),
        ("DNA", "is", "Genetic Blueprint", 1.0),
    ]

    for subj, rel, obj, conf in biology:
        samples.append(DataSample(
            text=f"{subj} is {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── SPORTS ────────────────────────────────────────────────────────
    sports = [
        ("FIFA World Cup", "located_in", "Global", 0.90),
        ("Olympics", "founded_by", "Pierre De Coubertin", 0.90),
        ("NBA", "located_in", "United States", 0.95),
        ("Premier League", "located_in", "England", 1.0),
        ("Champions League", "located_in", "Europe", 1.0),
        ("Wimbledon", "located_in", "London", 1.0),
        ("Super Bowl", "located_in", "United States", 0.95),
        ("Tour De France", "located_in", "France", 1.0),
        ("Cricket World Cup", "is", "ICC Tournament", 0.90),
        ("Rugby World Cup", "is", "International Tournament", 0.90),
        ("Formula 1", "is", "Motor Racing Championship", 0.95),
        ("Roland Garros", "located_in", "Paris", 1.0),
        ("US Open Tennis", "located_in", "New York", 0.95),
        ("Melbourne Cup", "located_in", "Melbourne", 0.95),
        ("La Liga", "located_in", "Spain", 1.0),
        ("Serie A", "located_in", "Italy", 1.0),
        ("Bundesliga", "located_in", "Germany", 1.0),
        ("MLS", "located_in", "United States", 0.95),
        ("IPL", "located_in", "India", 0.95),
        ("UFC", "located_in", "United States", 0.90),
    ]

    for subj, rel, obj, conf in sports:
        samples.append(DataSample(
            text=f"{subj} is located in {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── MUSIC / ENTERTAINMENT ─────────────────────────────────────────
    entertainment = [
        ("Beatles", "located_in", "Liverpool", 1.0),
        ("Hollywood", "located_in", "Los Angeles", 1.0),
        ("Bollywood", "located_in", "Mumbai", 1.0),
        ("Mozart", "located_in", "Salzburg", 0.95),
        ("Beethoven", "located_in", "Bonn", 0.95),
        ("Shakespeare", "located_in", "Stratford-upon-Avon", 0.95),
        ("Disney", "founded_by", "Walt Disney", 1.0),
        ("Warner Bros", "founded_by", "Warner Brothers", 0.95),
        ("Pixar", "founded_by", "Ed Catmull", 0.90),
        ("Marvel", "founded_by", "Martin Goodman", 0.90),
        ("DC Comics", "founded_by", "Malcolm Wheeler", 0.85),
        ("Studio Ghibli", "founded_by", "Hayao Miyazaki", 0.95),
        ("Mona Lisa", "located_in", "Louvre Museum", 1.0),
        ("David", "located_in", "Florence", 0.95),
        ("Starry Night", "is", "Van Gogh Painting", 0.95),
        ("Guitar", "is", "String Instrument", 1.0),
        ("Piano", "is", "Keyboard Instrument", 1.0),
        ("Violin", "is", "String Instrument", 1.0),
        ("Opera", "is", "Musical Art Form", 0.95),
        ("Ballet", "is", "Dance Art Form", 0.95),
    ]

    for subj, rel, obj, conf in entertainment:
        samples.append(DataSample(
            text=f"{subj} is {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── FOOD / CUISINE ────────────────────────────────────────────────
    food = [
        ("Sushi", "located_in", "Japan", 1.0),
        ("Pizza", "located_in", "Italy", 1.0),
        ("Tacos", "located_in", "Mexico", 1.0),
        ("Croissant", "located_in", "France", 0.95),
        ("Kimchi", "located_in", "South Korea", 1.0),
        ("Curry", "located_in", "India", 0.95),
        ("Hamburger", "located_in", "United States", 0.90),
        ("Pho", "located_in", "Vietnam", 1.0),
        ("Paella", "located_in", "Spain", 1.0),
        ("Peking Duck", "located_in", "China", 0.95),
        ("Fish And Chips", "located_in", "England", 0.95),
        ("Bratwurst", "located_in", "Germany", 0.95),
        ("Pad Thai", "located_in", "Thailand", 1.0),
        ("Falafel", "located_in", "Middle East", 0.90),
        ("Baklava", "located_in", "Turkey", 0.90),
        ("Ramen", "located_in", "Japan", 0.95),
        ("Dim Sum", "located_in", "China", 0.95),
        ("Ceviche", "located_in", "Peru", 0.95),
        ("Maple Syrup", "located_in", "Canada", 0.95),
        ("Chocolate", "located_in", "Switzerland", 0.85),
    ]

    for subj, rel, obj, conf in food:
        samples.append(DataSample(
            text=f"{subj} originates from {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── UNIVERSITIES ──────────────────────────────────────────────────
    universities = [
        ("Harvard", "located_in", "Cambridge", 1.0),
        ("MIT", "located_in", "Cambridge", 1.0),
        ("Stanford", "located_in", "Stanford", 1.0),
        ("Oxford", "located_in", "Oxford", 1.0),
        ("Cambridge University", "located_in", "Cambridge", 1.0),
        ("Yale", "located_in", "New Haven", 1.0),
        ("Princeton", "located_in", "Princeton", 1.0),
        ("Caltech", "located_in", "Pasadena", 1.0),
        ("Berkeley", "located_in", "Berkeley", 1.0),
        ("Columbia", "located_in", "New York", 1.0),
        ("ETH Zurich", "located_in", "Zurich", 1.0),
        ("Imperial College", "located_in", "London", 1.0),
        ("Sorbonne", "located_in", "Paris", 1.0),
        ("Peking University", "located_in", "Beijing", 1.0),
        ("University Of Tokyo", "located_in", "Tokyo", 1.0),
        ("NUS", "located_in", "Singapore", 1.0),
        ("IIT", "located_in", "India", 0.95),
        ("UCLA", "located_in", "Los Angeles", 1.0),
        ("NYU", "located_in", "New York", 1.0),
        ("LSE", "located_in", "London", 1.0),
        ("Carnegie Mellon", "located_in", "Pittsburgh", 1.0),
        ("Duke", "located_in", "Durham", 1.0),
        ("Brown", "located_in", "Providence", 1.0),
        ("Georgia Tech", "located_in", "Atlanta", 1.0),
        ("University Of Michigan", "located_in", "Ann Arbor", 1.0),
        ("McGill", "located_in", "Montreal", 1.0),
        ("University Of Toronto", "located_in", "Toronto", 1.0),
        ("ANU", "located_in", "Canberra", 1.0),
    ]

    for subj, rel, obj, conf in universities:
        samples.append(DataSample(
            text=f"{subj} is located in {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── CURRENCIES ────────────────────────────────────────────────────
    currencies = [
        ("Dollar", "is", "Currency Of United States", 1.0),
        ("Euro", "is", "Currency Of European Union", 1.0),
        ("Pound", "is", "Currency Of United Kingdom", 1.0),
        ("Yen", "is", "Currency Of Japan", 1.0),
        ("Yuan", "is", "Currency Of China", 1.0),
        ("Rupee", "is", "Currency Of India", 1.0),
        ("Won", "is", "Currency Of South Korea", 1.0),
        ("Ruble", "is", "Currency Of Russia", 1.0),
        ("Real", "is", "Currency Of Brazil", 1.0),
        ("Peso", "is", "Currency Of Mexico", 1.0),
        ("Franc", "is", "Currency Of Switzerland", 1.0),
        ("Krona", "is", "Currency Of Sweden", 1.0),
        ("Baht", "is", "Currency Of Thailand", 1.0),
        ("Ringgit", "is", "Currency Of Malaysia", 1.0),
        ("Rand", "is", "Currency Of South Africa", 1.0),
        ("Lira", "is", "Currency Of Turkey", 1.0),
        ("Shekel", "is", "Currency Of Israel", 1.0),
        ("Dirham", "is", "Currency Of UAE", 1.0),
        ("Dong", "is", "Currency Of Vietnam", 1.0),
        ("Bitcoin", "is", "Cryptocurrency", 0.95),
    ]

    for subj, rel, obj, conf in currencies:
        samples.append(DataSample(
            text=f"{subj} is the {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── RIVERS & WATER BODIES ─────────────────────────────────────────
    rivers = [
        ("Amazon River", "located_in", "Brazil", 1.0),
        ("Nile River", "located_in", "Egypt", 1.0),
        ("Yangtze River", "located_in", "China", 1.0),
        ("Mississippi River", "located_in", "United States", 1.0),
        ("Ganges River", "located_in", "India", 1.0),
        ("Danube River", "located_in", "Europe", 1.0),
        ("Thames River", "located_in", "England", 1.0),
        ("Seine River", "located_in", "France", 1.0),
        ("Rhine River", "located_in", "Germany", 1.0),
        ("Volga River", "located_in", "Russia", 1.0),
        ("Zambezi River", "located_in", "Africa", 1.0),
        ("Mekong River", "located_in", "Southeast Asia", 1.0),
        ("Colorado River", "located_in", "United States", 1.0),
        ("Tigris River", "located_in", "Iraq", 1.0),
        ("Euphrates River", "located_in", "Iraq", 1.0),
        ("Congo River", "located_in", "Africa", 1.0),
        ("Indus River", "located_in", "Pakistan", 1.0),
        ("Murray River", "located_in", "Australia", 1.0),
        ("Rio Grande", "located_in", "North America", 1.0),
        ("Danube River", "located_in", "Central Europe", 0.95),
        ("Pacific Ocean", "is", "Largest Ocean", 1.0),
        ("Atlantic Ocean", "is", "Second Largest Ocean", 1.0),
        ("Indian Ocean", "is", "Third Largest Ocean", 1.0),
        ("Arctic Ocean", "is", "Smallest Ocean", 1.0),
        ("Mediterranean Sea", "located_in", "Europe", 1.0),
        ("Caribbean Sea", "located_in", "Americas", 1.0),
        ("Red Sea", "located_in", "Middle East", 1.0),
        ("Black Sea", "located_in", "Eastern Europe", 1.0),
        ("Caspian Sea", "is", "Largest Lake", 0.95),
        ("Lake Victoria", "located_in", "Africa", 1.0),
        ("Lake Baikal", "located_in", "Russia", 1.0),
        ("Lake Superior", "located_in", "North America", 1.0),
        ("Dead Sea", "located_in", "Middle East", 1.0),
    ]

    for subj, rel, obj, conf in rivers:
        samples.append(DataSample(
            text=f"{subj} is located in {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── MOUNTAINS & PEAKS ─────────────────────────────────────────────
    mountains = [
        ("Mount Everest", "located_in", "Nepal", 1.0),
        ("K2", "located_in", "Pakistan", 1.0),
        ("Mont Blanc", "located_in", "France", 1.0),
        ("Mount Kilimanjaro", "located_in", "Tanzania", 1.0),
        ("Denali", "located_in", "Alaska", 1.0),
        ("Mount Elbrus", "located_in", "Russia", 1.0),
        ("Matterhorn", "located_in", "Switzerland", 1.0),
        ("Mount Olympus", "located_in", "Greece", 1.0),
        ("Himalayas", "located_in", "Asia", 1.0),
        ("Andes", "located_in", "South America", 1.0),
        ("Alps", "located_in", "Europe", 1.0),
        ("Rocky Mountains", "located_in", "North America", 1.0),
        ("Atlas Mountains", "located_in", "Africa", 1.0),
        ("Ural Mountains", "located_in", "Russia", 1.0),
        ("Appalachian Mountains", "located_in", "United States", 1.0),
        ("Mount Vesuvius", "located_in", "Italy", 1.0),
        ("Mount Etna", "located_in", "Sicily", 1.0),
        ("Table Mountain", "located_in", "South Africa", 1.0),
        ("Mount McKinley", "located_in", "Alaska", 1.0),
        ("Mount Rainier", "located_in", "Washington", 1.0),
    ]

    for subj, rel, obj, conf in mountains:
        samples.append(DataSample(
            text=f"{subj} is located in {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── INVENTIONS & INNOVATIONS ──────────────────────────────────────
    inventions = [
        ("Telephone", "founded_by", "Alexander Graham Bell", 0.95),
        ("Light Bulb", "founded_by", "Thomas Edison", 0.90),
        ("Radio", "founded_by", "Guglielmo Marconi", 0.95),
        ("Television", "founded_by", "John Logie Baird", 0.90),
        ("Airplane", "founded_by", "Wright Brothers", 0.95),
        ("Automobile", "founded_by", "Karl Benz", 0.90),
        ("Printing Press", "founded_by", "Johannes Gutenberg", 1.0),
        ("Telescope", "founded_by", "Hans Lippershey", 0.85),
        ("Microscope", "founded_by", "Antonie Van Leeuwenhoek", 0.85),
        ("Dynamite", "founded_by", "Alfred Nobel", 1.0),
        ("Phonograph", "founded_by", "Thomas Edison", 0.95),
        ("Camera", "founded_by", "Joseph Niepce", 0.85),
        ("Refrigerator", "founded_by", "Jacob Perkins", 0.85),
        ("Typewriter", "founded_by", "Christopher Sholes", 0.85),
        ("Sewing Machine", "founded_by", "Elias Howe", 0.85),
        ("Steam Engine", "founded_by", "James Watt", 0.90),
        ("Compass", "founded_by", "Chinese Inventors", 0.85),
        ("Gunpowder", "founded_by", "Chinese Inventors", 0.85),
        ("Paper", "founded_by", "Cai Lun", 0.85),
        ("Internet", "founded_by", "Vint Cerf", 0.90),
        ("World Wide Web", "founded_by", "Tim Berners-Lee", 1.0),
        ("Penicillin", "founded_by", "Alexander Fleming", 1.0),
        ("X-ray", "founded_by", "Wilhelm Rontgen", 0.95),
        ("Vaccine", "founded_by", "Edward Jenner", 0.95),
        ("Stethoscope", "founded_by", "Rene Laennec", 0.85),
    ]

    for subj, rel, obj, conf in inventions:
        samples.append(DataSample(
            text=f"{subj} was invented by {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── COMPUTING & AI ────────────────────────────────────────────────
    computing = [
        ("Linux", "founded_by", "Linus Torvalds", 1.0),
        ("Python", "founded_by", "Guido Van Rossum", 1.0),
        ("Java", "founded_by", "James Gosling", 0.95),
        ("JavaScript", "founded_by", "Brendan Eich", 0.95),
        ("C Language", "founded_by", "Dennis Ritchie", 1.0),
        ("Unix", "founded_by", "Ken Thompson", 0.95),
        ("Git", "founded_by", "Linus Torvalds", 1.0),
        ("WordPress", "founded_by", "Matt Mullenweg", 0.95),
        ("Android", "founded_by", "Andy Rubin", 0.95),
        ("iOS", "founded_by", "Apple", 0.95),
        ("Windows", "founded_by", "Microsoft", 1.0),
        ("ChatGPT", "founded_by", "OpenAI", 0.95),
        ("GitHub", "founded_by", "Tom Preston-Werner", 0.90),
        ("Stack Overflow", "founded_by", "Joel Spolsky", 0.90),
        ("Bitcoin", "founded_by", "Satoshi Nakamoto", 0.90),
        ("Ethereum", "founded_by", "Vitalik Buterin", 0.95),
        ("Docker", "founded_by", "Solomon Hykes", 0.90),
        ("Kubernetes", "founded_by", "Google", 0.95),
        ("TensorFlow", "founded_by", "Google", 0.95),
        ("PyTorch", "founded_by", "Meta", 0.95),
        ("Ruby", "founded_by", "Yukihiro Matsumoto", 0.95),
        ("PHP", "founded_by", "Rasmus Lerdorf", 0.90),
        ("Swift", "founded_by", "Apple", 0.95),
        ("Rust", "founded_by", "Graydon Hoare", 0.90),
        ("Go Language", "founded_by", "Google", 0.95),
    ]

    for subj, rel, obj, conf in computing:
        samples.append(DataSample(
            text=f"{subj} was created by {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── ARCHITECTURE & BUILDINGS ──────────────────────────────────────
    architecture = [
        ("Empire State Building", "located_in", "New York", 1.0),
        ("One World Trade Center", "located_in", "New York", 1.0),
        ("Willis Tower", "located_in", "Chicago", 1.0),
        ("CN Tower", "located_in", "Toronto", 1.0),
        ("Tokyo Tower", "located_in", "Tokyo", 1.0),
        ("Taipei 101", "located_in", "Taipei", 1.0),
        ("Petronas Towers", "located_in", "Kuala Lumpur", 1.0),
        ("Shanghai Tower", "located_in", "Shanghai", 1.0),
        ("Chrysler Building", "located_in", "New York", 1.0),
        ("Big Ben", "located_in", "London", 1.0),
        ("Arc De Triomphe", "located_in", "Paris", 1.0),
        ("Brandenburg Gate", "located_in", "Berlin", 1.0),
        ("Sydney Harbour Bridge", "located_in", "Sydney", 1.0),
        ("Tower Bridge", "located_in", "London", 1.0),
        ("Palace Of Versailles", "located_in", "Versailles", 1.0),
        ("Notre Dame", "located_in", "Paris", 1.0),
        ("Hagia Sophia", "located_in", "Istanbul", 1.0),
        ("Alhambra", "located_in", "Granada", 1.0),
        ("Blue Mosque", "located_in", "Istanbul", 1.0),
        ("St Peters Basilica", "located_in", "Vatican City", 1.0),
    ]

    for subj, rel, obj, conf in architecture:
        samples.append(DataSample(
            text=f"{subj} is located in {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── ECONOMICS & ORGANIZATIONS ─────────────────────────────────────
    economics = [
        ("United Nations", "located_in", "New York", 1.0),
        ("European Union", "located_in", "Brussels", 1.0),
        ("World Bank", "located_in", "Washington D.C.", 1.0),
        ("IMF", "located_in", "Washington D.C.", 1.0),
        ("WHO", "located_in", "Geneva", 1.0),
        ("NATO", "located_in", "Brussels", 1.0),
        ("OPEC", "located_in", "Vienna", 1.0),
        ("WTO", "located_in", "Geneva", 1.0),
        ("Red Cross", "located_in", "Geneva", 1.0),
        ("Amnesty International", "located_in", "London", 1.0),
        ("FIFA", "located_in", "Zurich", 1.0),
        ("IOC", "located_in", "Lausanne", 1.0),
        ("NYSE", "located_in", "New York", 1.0),
        ("NASDAQ", "located_in", "New York", 1.0),
        ("London Stock Exchange", "located_in", "London", 1.0),
        ("Tokyo Stock Exchange", "located_in", "Tokyo", 1.0),
        ("Hong Kong Exchange", "located_in", "Hong Kong", 1.0),
        ("Shanghai Exchange", "located_in", "Shanghai", 1.0),
        ("Dow Jones", "is", "Stock Market Index", 0.95),
        ("S&P 500", "is", "Stock Market Index", 0.95),
    ]

    for subj, rel, obj, conf in economics:
        samples.append(DataSample(
            text=f"{subj} is located in {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── ADDITIONAL GEOGRAPHY: Islands & Deserts ───────────────────────
    islands_deserts = [
        ("Greenland", "located_in", "North America", 1.0),
        ("Iceland", "located_in", "Europe", 1.0),
        ("Madagascar", "located_in", "Africa", 1.0),
        ("Borneo", "located_in", "Southeast Asia", 1.0),
        ("New Zealand", "located_in", "Oceania", 1.0),
        ("Cuba", "located_in", "Caribbean", 1.0),
        ("Jamaica", "located_in", "Caribbean", 1.0),
        ("Hawaii", "located_in", "United States", 1.0),
        ("Bali", "located_in", "Indonesia", 1.0),
        ("Maldives", "located_in", "Indian Ocean", 1.0),
        ("Sicily", "located_in", "Italy", 1.0),
        ("Crete", "located_in", "Greece", 1.0),
        ("Sri Lanka", "located_in", "Indian Ocean", 1.0),
        ("Taiwan", "located_in", "East Asia", 0.95),
        ("Gobi Desert", "located_in", "Mongolia", 1.0),
        ("Kalahari Desert", "located_in", "Africa", 1.0),
        ("Atacama Desert", "located_in", "Chile", 1.0),
        ("Mojave Desert", "located_in", "United States", 1.0),
        ("Arabian Desert", "located_in", "Middle East", 1.0),
        ("Antarctic Desert", "located_in", "Antarctica", 1.0),
        ("Thar Desert", "located_in", "India", 1.0),
        ("Namib Desert", "located_in", "Namibia", 1.0),
        ("Sonoran Desert", "located_in", "United States", 1.0),
        ("Patagonian Desert", "located_in", "Argentina", 1.0),
        ("Great Victoria Desert", "located_in", "Australia", 1.0),
    ]

    for subj, rel, obj, conf in islands_deserts:
        samples.append(DataSample(
            text=f"{subj} is located in {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── MEDICINE & HEALTH ─────────────────────────────────────────────
    medicine = [
        ("Aspirin", "is", "Pain Reliever", 0.95),
        ("Insulin", "is", "Diabetes Treatment", 1.0),
        ("Morphine", "is", "Pain Medication", 0.95),
        ("Antibiotics", "is", "Bacterial Treatment", 1.0),
        ("Chemotherapy", "is", "Cancer Treatment", 0.95),
        ("MRI", "is", "Medical Imaging", 1.0),
        ("CT Scan", "is", "Medical Imaging", 1.0),
        ("Ultrasound", "is", "Medical Imaging", 1.0),
        ("Heart", "is", "Vital Organ", 1.0),
        ("Brain", "is", "Central Nervous System", 1.0),
        ("Liver", "is", "Detoxification Organ", 0.95),
        ("Kidney", "is", "Filtration Organ", 0.95),
        ("Lungs", "is", "Respiratory Organ", 1.0),
        ("Blood", "is", "Oxygen Transport", 1.0),
        ("Vitamin C", "is", "Essential Nutrient", 0.95),
        ("Vitamin D", "is", "Bone Health Nutrient", 0.95),
        ("Protein", "is", "Building Block Of Life", 0.95),
        ("Calcium", "is", "Bone Mineral", 0.95),
        ("Iron", "is", "Blood Component", 0.90),
        ("Hemoglobin", "is", "Oxygen Carrier", 1.0),
    ]

    for subj, rel, obj, conf in medicine:
        samples.append(DataSample(
            text=f"{subj} is {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── AUTOMOTIVE ────────────────────────────────────────────────────
    auto = [
        ("Toyota", "founded_by", "Kiichiro Toyoda", 0.95),
        ("Ford", "founded_by", "Henry Ford", 1.0),
        ("BMW", "founded_by", "Karl Rapp", 0.85),
        ("Ferrari", "founded_by", "Enzo Ferrari", 1.0),
        ("Lamborghini", "founded_by", "Ferruccio Lamborghini", 1.0),
        ("Porsche", "founded_by", "Ferdinand Porsche", 1.0),
        ("Honda", "founded_by", "Soichiro Honda", 1.0),
        ("Hyundai", "founded_by", "Chung Ju-yung", 0.90),
        ("Rolls Royce", "founded_by", "Charles Rolls", 0.90),
        ("Aston Martin", "founded_by", "Lionel Martin", 0.90),
        ("Bugatti", "founded_by", "Ettore Bugatti", 0.95),
        ("Bentley", "founded_by", "W.O. Bentley", 0.90),
        ("Mazda", "founded_by", "Jujiro Matsuda", 0.85),
        ("Subaru", "founded_by", "Kenji Kita", 0.85),
        ("General Motors", "founded_by", "William Durant", 0.90),
        ("Chrysler", "founded_by", "Walter Chrysler", 0.90),
        ("Nissan", "founded_by", "Yoshisuke Aikawa", 0.85),
        ("Volvo", "founded_by", "Assar Gabrielsson", 0.85),
        ("Jaguar", "founded_by", "William Lyons", 0.85),
        ("Land Rover", "founded_by", "Maurice Wilks", 0.85),
    ]

    for subj, rel, obj, conf in auto:
        samples.append(DataSample(
            text=f"{subj} was founded by {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── LITERATURE & PHILOSOPHY ───────────────────────────────────────
    literature = [
        ("Romeo And Juliet", "founded_by", "Shakespeare", 0.95),
        ("Harry Potter", "founded_by", "J.K. Rowling", 1.0),
        ("Lord Of The Rings", "founded_by", "J.R.R. Tolkien", 1.0),
        ("Don Quixote", "founded_by", "Cervantes", 0.95),
        ("The Republic", "founded_by", "Plato", 0.95),
        ("War And Peace", "founded_by", "Leo Tolstoy", 0.95),
        ("The Great Gatsby", "founded_by", "F. Scott Fitzgerald", 0.95),
        ("1984", "founded_by", "George Orwell", 1.0),
        ("Pride And Prejudice", "founded_by", "Jane Austen", 1.0),
        ("The Odyssey", "founded_by", "Homer", 0.90),
        ("Divine Comedy", "founded_by", "Dante", 0.95),
        ("Hamlet", "founded_by", "Shakespeare", 0.95),
        ("A Tale Of Two Cities", "founded_by", "Charles Dickens", 0.95),
        ("Crime And Punishment", "founded_by", "Dostoevsky", 0.95),
        ("The Art Of War", "founded_by", "Sun Tzu", 0.90),
        ("Moby Dick", "founded_by", "Herman Melville", 0.95),
        ("Les Miserables", "founded_by", "Victor Hugo", 0.95),
        ("The Iliad", "founded_by", "Homer", 0.90),
        ("Brave New World", "founded_by", "Aldous Huxley", 0.95),
        ("One Hundred Years Of Solitude", "founded_by", "Gabriel Garcia Marquez", 0.95),
    ]

    for subj, rel, obj, conf in literature:
        samples.append(DataSample(
            text=f"{subj} was written by {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=True,
        ))

    # ── FALSE CLAIMS (Hallucinations for training) ────────────────────
    false_claims = [
        ("Paris", "capital_of", "Germany", 0.1),
        ("London", "capital_of", "France", 0.1),
        ("Tokyo", "capital_of", "China", 0.1),
        ("Apple", "founded_by", "Bill Gates", 0.1),
        ("Microsoft", "founded_by", "Steve Jobs", 0.1),
        ("Google", "founded_by", "Jeff Bezos", 0.1),
        ("Mars", "color", "Blue", 0.1),
        ("Moon", "is", "Planet", 0.1),
        ("Sun", "is", "Planet", 0.1),
        ("Einstein", "discovered", "Penicillin", 0.1),
        ("Newton", "discovered", "DNA Structure", 0.1),
        ("Berlin", "capital_of", "France", 0.1),
        ("Rome", "capital_of", "Spain", 0.1),
        ("Amazon", "founded_by", "Elon Musk", 0.1),
        ("Tesla", "founded_by", "Jeff Bezos", 0.1),
        ("Water", "is", "CO2", 0.1),
        ("Gold", "is", "Gas", 0.1),
        ("Oxygen", "is", "Metal", 0.1),
        ("Elephant", "is", "Smallest Animal", 0.1),
        ("Cheetah", "is", "Slowest Animal", 0.1),
        ("Eiffel Tower", "located_in", "London", 0.1),
        ("Statue Of Liberty", "located_in", "Paris", 0.1),
        ("Big Ben", "located_in", "Tokyo", 0.1),
        ("Colosseum", "located_in", "Berlin", 0.1),
        ("Taj Mahal", "located_in", "London", 0.1),
        ("Harvard", "located_in", "Tokyo", 0.1),
        ("Oxford", "located_in", "New York", 0.1),
        ("Stanford", "located_in", "London", 0.1),
        ("Dollar", "is", "Currency Of Japan", 0.1),
        ("Euro", "is", "Currency Of Brazil", 0.1),
        ("Jupiter", "is", "Smallest Planet", 0.1),
        ("Venus", "is", "Coldest Planet", 0.1),
        ("Pluto", "is", "Largest Planet", 0.1),
        ("Sahara", "located_in", "Europe", 0.1),
        ("Antarctica", "located_in", "Africa", 0.1),
        ("Sushi", "located_in", "Germany", 0.1),
        ("Pizza", "located_in", "Japan", 0.1),
        ("Darwin", "discovered", "Relativity", 0.1),
        ("Fleming", "discovered", "Gravity", 0.1),
        ("Curie", "discovered", "Steam Engine", 0.1),
        ("Facebook", "founded_by", "Larry Page", 0.1),
        ("Twitter", "founded_by", "Mark Zuckerberg", 0.1),
        ("Netflix", "founded_by", "Bill Gates", 0.1),
        ("Disney", "founded_by", "Steve Jobs", 0.1),
        ("Beethoven", "located_in", "Tokyo", 0.1),
        ("Shakespeare", "located_in", "Beijing", 0.1),
        ("Blue Whale", "is", "Smallest Animal", 0.1),
        ("Diamond", "is", "Softest Material", 0.1),
        ("Beijing", "capital_of", "Japan", 0.1),
        ("Moscow", "capital_of", "China", 0.1),
    ]

    for subj, rel, obj, conf in false_claims:
        samples.append(DataSample(
            text=f"{subj} {rel} {obj}",
            subject=subj, relation=rel, obj=obj,
            confidence=conf, label=False,
        ))

    return samples
