# Constants used across the application

INGREDIENTS = {
    'dairy': [
        'milk', 'cream', 'butter', 'cheese', 'whey', 'casein', 'yogurt', 'lactose',
        'milk solids', 'milk powder', 'buttermilk', 'curd', 'ghee', 'paneer',
        'milk protein', 'dairy cream', 'milk fat', 'skimmed milk powder',
        'milk protein isolate', 'sodium caseinate'
    ],
    'egg': [
        'egg', 'egg white', 'egg yolk', 'albumin', 'egg powder', 'dried egg',
        'egg lecithin', 'lysozyme', 'globulin', 'egg protein', 'mayonnaise',
        'meringue', 'egg wash', 'pasteurized egg', 'dried albumin'
    ],
    'peanut': [
        'peanut', 'peanut butter', 'peanut oil', 'peanut flour', 'peanut protein',
        'ground peanuts', 'beer nuts', 'monkey nuts', 'peanut paste', 'goober peas',
        'arachis oil', 'ground nut oil', 'peanut sauce'
    ],
    'tree_nuts': [
        'almond', 'walnut', 'cashew', 'pecan', 'pistachio', 'hazelnut', 'macadamia',
        'brazil nut', 'pine nut', 'chestnut', 'almond milk', 'cashew butter',
        'almond flour', 'walnut oil', 'almond paste', 'marzipan'
    ],
    'soy': [
        'soy', 'soya', 'soybean', 'tofu', 'tempeh', 'miso', 'edamame', 'natto',
        'soy lecithin', 'soy protein', 'soy flour', 'soy sauce', 'tamari',
        'textured vegetable protein', 'hydrolyzed soy protein'
    ],
    'wheat': [
        'wheat', 'flour', 'bread crumbs', 'bran', 'semolina', 'couscous', 'pasta',
        'seitan', 'wheat germ', 'wheat starch', 'modified wheat starch', 'wheat protein',
        'wheat gluten', 'durum wheat', 'whole wheat flour', 'wheat bran'
    ],
    'fish': [
        'fish', 'salmon', 'tuna', 'cod', 'anchovy', 'sardine', 'mackerel', 'fish sauce',
        'fish stock', 'fish extract', 'fish protein', 'fish powder', 'fish oil',
        'fish paste', 'surimi'
    ],
    'shellfish': [
        'shrimp', 'crab', 'lobster', 'prawn', 'crayfish', 'langoustine', 'shellfish',
        'shellfish extract', 'seafood', 'krill', 'crawfish', 'shrimp paste'
    ],
    'sesame': [
        'sesame', 'sesame oil', 'sesame seed', 'tahini', 'sesame paste', 'sesame flour',
        'gingelly oil', 'til', 'sesame protein', 'black sesame', 'white sesame'
    ],
    'mustard': [
        'mustard', 'mustard seed', 'mustard powder', 'mustard oil', 'mustard paste',
        'mustard flour', 'mustard extract', 'dijon mustard', 'yellow mustard'
    ],
    'lupin': [
        'lupin', 'lupini beans', 'lupin flour', 'lupin protein', 'lupine', 
        'lupin seeds', 'lupin bean powder', 'sweet lupin', 'lupini', 'lupin concentrate'
    ],
    'sulphites': [
        'sulfites', 'sulphites', 'sulfur dioxide', 'sodium sulfite', 'sodium bisulfite',
        'potassium bisulfite', 'potassium metabisulfite', 'sodium metabisulfite',
        'preserved with sulfites', 'contains sulfites', 'wine preservative (sulfites)',
        'dried fruits with sulfites', 'treated with sulfites'
    ],
    'celery': [
        'celery', 'celery root', 'celery seeds', 'celery salt', 'celery powder',
        'celery extract', 'celery juice', 'celery leaves', 'celery stalk', 'celeriac',
        'celery spice', 'celery seasoning'
    ],
    'molluscs': [
        'oyster', 'mussel', 'clam', 'scallop', 'octopus', 'squid', 'calamari',
        'abalone', 'snail', 'whelk', 'periwinkle', 'mollusc extract', 'oyster sauce',
        'clam juice', 'mollusc powder'
    ]
}

# Add common product types that might contain these allergens
PRODUCT_TYPES = [
    ('lupin_product', ['lupin flour', 'lupin protein'], ['preservatives', 'stabilizers']),
    ('preserved_food', ['sulfites', 'sodium sulfite'], ['preservatives', 'antioxidants']),
    ('celery_product', ['celery', 'celery salt'], ['seasonings', 'spices']),
    ('seafood_product', ['oyster sauce', 'clam juice'], ['seasonings', 'preservatives'])
] 