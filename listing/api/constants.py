MONTHS_RO = {
    "January": "ianuarie",
    "February": "februarie",
    "March": "martie",
    "April": "aprilie",
    "May": "mai",
    "June": "iunie",
    "July": "iulie",
    "August": "august",
    "September": "septembrie",
    "October": "octombrie",
    "November": "noiembrie",
    "December": "decembrie",
}

CURRENCY_CHOICES = [
    (0, 'Lei'),
    (1, 'EUR'),
]

FLOOR_CHOICES = [
    (0, 'Demisol'),
    (1, 'Parter'),
    (2, 'Etaj 1'),
    (3, 'Etaj 2'),
    (4, 'Etaj 3'),
    (5, 'Etaj 4'),
    (6, 'Etaj 5'),
    (7, 'Etaj 6'),
    (8, 'Etaj 7'),
    (9, 'Etaj 8'),
    (10, 'Etaj 9'),
    (11, 'Etaj 10'),
    (12, 'Etaj 11'),
    (13, 'Etaj 12'),
    (14, 'Etaj 13'),
    (15, 'Etaj 14'),
    (16, 'Etaj 15'),
    (17, 'Etaj 16'),
    (18, 'Etaj 17'),
    (19, 'Etaj 18'),
    (20, 'Etaj 19'),
    (21, 'Etaj 20'),
    (22, 'Etaj 21+'),
    (23, 'Ultimul etaj'),
    (24, 'Mansardă'),
]

COMPARTIMENTARE_CHOICES = [
    (0, 'Decomandat'),
    (1, 'Semidecomandat'),
    (2, 'Nedecomandat'),
    (3, 'Circular'),
]

ZONARE_CHOICES = [
    (0, 'Intravilan'),
    (1, 'Extravilan'),
] 

NUMAR_CAMERE_CHOICES = [
    (1, '1 cameră'),
    (2, '2 camere'),
    (3, '3 camere'),
    (4, '4 camere'),
    (5, '5+ camere'),
]  

NUMBER_OF_BATHROOMS_CHOICES = [
    (0, 'Fără baie'),
    (1, '1 baie'),
    (2, '2 băi'),
    (3, '3 sau mai multe băi'),
]  

NUMBER_OF_BEDROOMS_CHOICES = [
    (1, '1 dormitor'),
    (2, '2 dormitoare'),
    (3, '3 dormitoare'),
    (4, '4 dormitoare'),
    (5, '5+ dormitoare'),
]  

NUMBER_OF_BALCONIES_CHOICES = [
    (0, "Fără balcon"),
    (1, "1 balcon"),
    (2, "2 balcoane"),
    (3, "3 balcoane"),
    (4, "4+ balcoane")
]

STRUCTURA_CHOICES = [
    (0, 'Cărămidă'),
    (1, 'Beton'),
    (2, 'BCA'),
    (3, 'Plăci'),
    (4, 'Lemn'),
    (5, 'Metal'),
    (6, 'Cărămidă + BCA'),
    (7, 'Beton + Metal'),
    (8, 'Lemn + Metal'),
    (9, 'Zidărie mixtă (Cărămidă + BCA + Beton)'),
    (10, 'Structură ușoară (Metal + Lemn + Plăci)'),
    (11, 'Combinată (Mai multe materiale)'),
]

FOUNDATION_TYPE_CHOICES = [
    (0, "Parter"),
    (1, "Subsol + Parter"),
    (2, "Demisol + Parter"),
]

CLASA_ENERGETICA_CHOICES = [
    (0, 'Necunoscută'),
    (1, 'A (Foarte bună)'),
    (2, 'B (Bună)'),
    (3, 'C (Medie)'),
    (4, 'D (Sub medie)'),
    (5, 'E (Scăzută)'),
    (6, 'F (Foarte scăzută)'),
    (7, 'G (Extrem de scăzută)'),
]

FIELD_LABELS = {
    'suprafata_utila': 'Suprafață utilă',  
    'suprafata_terenului': 'Suprafață teren',  
    'suprafata_constructie': 'Suprafață construită',   
    'suprafata_balcoane': 'Suprafață balcoane',              
    'year_of_construction': 'Anul construcției',
    'compartimentare': 'Tip compartimentare',
    'zonare': 'Tip zonare',
    'numar_camere': 'Număr de camere',
    'number_of_bedrooms': 'Număr de dormitoare',    
    'number_of_bathrooms': 'Număr de băi',    
    'number_of_balconies': 'Număr de balcoane',  
    'structura': 'Tip structură',
    'floor': 'Etaj',
    'foundation_type': 'Tip fundație',
    'number_of_floors': 'Număr de etaje',
    'has_attic': 'Are mansardă',
    'clasa_energetica': 'Clasa energetică',    
}
