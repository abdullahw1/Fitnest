import re
from collections import namedtuple

Flashcard = namedtuple('Flashcard', ['front', 'back'])

def _parse_header(data):
    """Group markdown by <# Heading1> and <# Heading2>
    while verifying that <# Heading 1> matches the string
    "Markdown Flashcards" and there's only one of it,
    to ensure that it's the correct file. Then, we categorizes
    the rest of the content by <# Heading 2>
    """
    header1_str = 'Markdown Flashcards'
    header1_match = False
    r_header = re.compile(r'# (?P<header1>(?:\S+(?: +\S+)*))|## (?P<header2>(?:\S+(?: +\S+)*))')
    section_idxs = []
    for match in r_header.finditer(data):
        d = match.groupdict()
        header1 = d.get('header1')
        header2 = d.get('header2')
        if not header1_match:
            if header1 and header1.lower() == header1_str.lower():
                header1_match = True
        else:
            if header1 != None:
                raise Exception("Invalid file, multiple header1 found")
            section_idxs.append((header2, match.start(), match.end()))
    sections = []
    for i in range(len(section_idxs)):
        cur = section_idxs[i]
        nex = section_idxs[i+1] if i+1 < len(section_idxs) else None
        if nex is not None:
            section_name, _, start = cur
            _, end, _ = nex
            section_content = data[start:end] 
        else:
            section_name, _, start = cur
            end = len(data)
            section_content = data[start:end] 
        sections.append((section_name, section_content)) 
    return sections


def _parse_individual_card_syntax(data):
    """Extract all markdown content that uses individual card syntax
    into a list of Flashcards
    """
    cards = []
    r_ind_cards = re.compile(r'\-{3}\n\n(?P<front>.*)\n\n\?\n\n(?P<back>.*)\n\n\-{3}')
    for match in r_ind_cards.finditer(data):
        d = match.groupdict()
        cards.append(Flashcard(front=d.get('front'), back=d.get('back')))
    return cards


def _parse_tabular_card_syntax(data):
    """Extract all markdown content that uses tabular card syntax
    into a list of Flashcards
    """
    cards = []
    r_tabular = re.compile(r'\|\s*[Ff][Rr][Oo][Nn][Tt]\s*\|\s*[Bb][Aa][Cc][Kk]\s*\|\n\|\s*\-{3,}\s*\|\s*\-{3,}\s*\|\n(?P<content>(?:\|[^\|]+\|[^\|]+\|\n*)+)')
    for match in r_tabular.finditer(data):
        d = match.groupdict()
        content = d.get('content')
        if content:
            # Decode multiple lines of "| front | back |"
            lines = content.splitlines()
            for line in lines:
                line = line[1:-1] # Discard first and last '|' character
                front, back = line.split('|')
                # Remove leading and trailing white spaces and add card
                cards.append(Flashcard(front=front.strip(), back=back.strip()))
    return cards


def md2flashcard(data):
    """Uses regular expressions to extract a list of flashcards from
    markdown text data.
    
    Arguments:
        data: Markdown text data
    
    Returns:
        dict: A dictionary with its key are the "section name" and their value
        would be their corresponding list of flashcard tuple (with front&back attributes).
    """
    sections = {}
    for section_name, section_content in _parse_header(data):
        cards = _parse_individual_card_syntax(section_content)\
                + _parse_tabular_card_syntax(section_content)
        sections[section_name] = cards
    return sections
