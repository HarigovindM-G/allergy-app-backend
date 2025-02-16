from app.core.constants import INGREDIENTS, INDIRECT_ALLERGEN_SOURCES

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
    
    # Check direct ingredients
    for ingredient in parts['ingredients']:
        # Direct match
        if any(term.lower() in ingredient.lower() for term in allergen_terms):
            evidence.append(ingredient)
        # Check indirect sources
        indirect_evidence = check_indirect_allergens(ingredient)
        for ind_allergen, ind_evidence in indirect_evidence:
            if ind_allergen == allergen:
                evidence.append(ind_evidence)
    
    # Check contains statements
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

def check_indirect_allergens(ingredient: str) -> list[tuple[str, str]]:
    evidence = []
    
    # Check emulsifiers
    if 'INS' in ingredient:
        code = ingredient.split('INS')[1].strip().split(')')[0].strip()
        if code in INDIRECT_ALLERGEN_SOURCES['emulsifiers']:
            for allergen in INDIRECT_ALLERGEN_SOURCES['emulsifiers'][code]:
                evidence.append((allergen, f"May contain {allergen} (from emulsifier {code})"))
    
    # Check flavorings
    for flavor_type, allergens in INDIRECT_ALLERGEN_SOURCES['flavoring'].items():
        if flavor_type.lower() in ingredient.lower():
            for allergen in allergens:
                evidence.append((allergen, f"May contain {allergen} (from {flavor_type})"))
    
    # Check starches
    for starch, allergens in INDIRECT_ALLERGEN_SOURCES['starches'].items():
        if starch.lower() in ingredient.lower():
            for allergen in allergens:
                evidence.append((allergen, f"May contain {allergen} (from {starch})"))
                
    return evidence 