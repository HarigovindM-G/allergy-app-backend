from app.core.constants import INGREDIENTS

def get_evidence(text: str, allergen: str) -> list[str] | None:
    # Skip evidence gathering for 'none' category or empty allergen
    if not allergen or allergen.lower() == 'none':
        return None
    
    # Verify allergen exists in INGREDIENTS
    if allergen not in INGREDIENTS:
        print(f"Warning: Unknown allergen category '{allergen}'")
        return None
    
    # Clean and normalize the text
    text = text.lower()
    
    # Parse text sections
    parts = parse_ingredient_text(text)
    
    # Look for allergen terms in all parts
    evidence = []
    allergen_terms = INGREDIENTS[allergen]
    
    # Check each section
    evidence.extend(check_ingredients(parts['ingredients'], allergen_terms))
    evidence.extend(check_contains_statements(parts['contains'], allergen_terms))
    evidence.extend(check_may_contain_statements(parts['may_contain'], allergen_terms))
    
    return evidence if evidence else None

def parse_ingredient_text(text: str) -> dict:
    parts = {
        'ingredients': [],
        'contains': [],
        'may_contain': []
    }
    
    # Parse sections
    if 'ingredients:' in text:
        ingredients_part = text.split('ingredients:')[1].split('contains')[0]
        parts['ingredients'] = [i.strip() for i in ingredients_part.split(',')]
    else:
        parts['ingredients'] = [i.strip() for i in text.split(',')]
    
    # Parse contains statements
    if 'contains' in text:
        try:
            contains_part = text.split('contains')[1].split('may contain')[0]
            parts['contains'] = [i.strip() for i in contains_part.split(',')]
        except IndexError:
            contains_part = text.split('contains')[1].split('.')[0]
            parts['contains'] = [i.strip() for i in contains_part.split(',')]
    
    # Parse may contain statements
    if 'may contain' in text:
        try:
            may_contain_part = text.split('may contain')[1].split('.')[0]
            parts['may_contain'] = [i.strip() for i in may_contain_part.split(',')]
        except IndexError:
            may_contain_part = text.split('may contain')[1]
            parts['may_contain'] = [i.strip() for i in may_contain_part.split(',')]
    
    return parts

def check_ingredients(ingredients: list[str], allergen_terms: list[str]) -> list[str]:
    return [
        ing for ing in ingredients
        if any(term.lower() in ing.lower() for term in allergen_terms)
    ]

def check_contains_statements(statements: list[str], allergen_terms: list[str]) -> list[str]:
    return [
        f"Contains statement: {stmt}" for stmt in statements
        if any(term.lower() in stmt.lower() for term in allergen_terms)
    ]

def check_may_contain_statements(statements: list[str], allergen_terms: list[str]) -> list[str]:
    return [
        f"May contain: {stmt}" for stmt in statements
        if any(term.lower() in stmt.lower() for term in allergen_terms)
    ] 