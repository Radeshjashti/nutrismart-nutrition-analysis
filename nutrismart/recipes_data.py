"""
Healthy Recipes & Meal Preparation Database for NutriSmart
Includes complete macros, ingredients, steps, and database-matched food items.
"""

CURATED_RECIPES = [
    {
        "id": 1,
        "title": "Protein-Packed Spinach Egg Scramble",
        "category": "Breakfast",
        "dietary_type": "Eggetarian",
        "prep_time": "12 mins",
        "calories": 255.0,
        "protein": 17.8,
        "carbohydrates": 7.6,
        "fat": 17.5,
        "fiber": 4.0,
        "db_food_name": "Egg Omelette (with herbs)",
        "serving_multiplier": 1.3,
        "image_icon": "fa-egg",
        "description": "Fluffy eggs scrambled with baby spinach, cherry tomatoes, and a pinch of ground turmeric for cellular repair.",
        "ingredients": [
            "2 large farm eggs",
            "1 cup fresh baby spinach",
            "1/2 chopped tomato",
            "1 tsp olive oil",
            "Pinch of black pepper, turmeric, and sea salt"
        ],
        "instructions": [
            "Heat olive oil in a non-stick skillet over medium heat.",
            "Add chopped tomatoes and baby spinach; sauté for 1-2 minutes until spinach is wilted.",
            "Whisk eggs with a pinch of turmeric, salt, and black pepper.",
            "Pour whisked eggs into the pan and gently fold until soft curds form.",
            "Serve warm with whole wheat toast or as a light morning scramble."
        ]
    },
    {
        "id": 2,
        "title": "South Indian High-Fiber Idli & Sambar Bowl",
        "category": "Breakfast",
        "dietary_type": "Vegan",
        "prep_time": "20 mins",
        "calories": 246.0,
        "protein": 9.5,
        "carbohydrates": 43.0,
        "fat": 4.6,
        "fiber": 6.2,
        "db_food_name": "Steamed Idli",
        "serving_multiplier": 1.5,
        "image_icon": "fa-bowl-rice",
        "description": "Steamed fermented rice and urad dal cakes paired with vegetable and lentil sambar stew for optimal gut microbiome health.",
        "ingredients": [
            "3 steamed idlis",
            "1 bowl vegetable sambar (drumsticks, carrots, shallots)",
            "1 tsp fresh coriander leaves for garnish"
        ],
        "instructions": [
            "Steam the fermented idli batter in an idli cooker for 10-12 minutes.",
            "Warm the spiced toor dal and vegetable sambar.",
            "Place fresh hot idlis in a shallow bowl and ladle hot sambar generously over them.",
            "Garnish with coriander and enjoy a naturally probiotic, low-fat meal."
        ]
    },
    {
        "id": 3,
        "title": "Mediterranean Grilled Chicken & Quinoa Salad",
        "category": "Lunch",
        "dietary_type": "Non-Vegetarian",
        "prep_time": "25 mins",
        "calories": 420.0,
        "protein": 44.5,
        "carbohydrates": 26.0,
        "fat": 14.5,
        "fiber": 5.5,
        "db_food_name": "Grilled Chicken Breast",
        "serving_multiplier": 1.0,
        "image_icon": "fa-drumstick-bite",
        "description": "Juicy herb-marinated grilled chicken breast served over crisp cucumbers, kalamata olives, and light lemon vinaigrette.",
        "ingredients": [
            "150g boneless chicken breast",
            "1/2 cup cooked quinoa or brown rice",
            "1 cup mixed salad greens and cucumber cubes",
            "1 tbsp extra virgin olive oil and lemon juice",
            "Dried oregano and crushed garlic"
        ],
        "instructions": [
            "Marinate chicken breast with lemon juice, minced garlic, oregano, and olive oil for 15 minutes.",
            "Grill chicken on a ridged grill pan over medium heat for 6-7 minutes per side.",
            "In a bowl, toss fresh salad greens and cooked quinoa with lemon vinaigrette.",
            "Slice the grilled chicken and arrange over the salad bed."
        ]
    },
    {
        "id": 4,
        "title": "Homestyle Dal Tadka & Whole Wheat Phulka",
        "category": "Lunch",
        "dietary_type": "Vegetarian",
        "prep_time": "25 mins",
        "calories": 415.0,
        "protein": 16.2,
        "carbohydrates": 58.0,
        "fat": 11.5,
        "fiber": 11.0,
        "db_food_name": "Dal Tadka (Yellow Lentils)",
        "serving_multiplier": 1.2,
        "image_icon": "fa-spoon",
        "description": "Golden yellow lentils tempered with cumin seeds, garlic, and ghee, served with 2 freshly puffed whole wheat chapatis.",
        "ingredients": [
            "1 cup cooked yellow toor dal",
            "2 whole wheat chapatis",
            "1 tsp pure desi ghee or cumin temper",
            "1 green chili and ginger juliennes"
        ],
        "instructions": [
            "Boil washed toor dal with turmeric and water until tender.",
            "Prepare tempering by heating ghee, sputtering cumin seeds, garlic, and chilies.",
            "Pour aromatic tadka over the dal and simmer for 2 minutes.",
            "Serve hot with freshly baked dry phulkas and lemon wedge."
        ]
    },
    {
        "id": 5,
        "title": "Cottage Cheese (Paneer) & Bell Pepper Stir-Fry",
        "category": "Dinner",
        "dietary_type": "Vegetarian",
        "prep_time": "15 mins",
        "calories": 340.0,
        "protein": 22.0,
        "carbohydrates": 14.0,
        "fat": 22.0,
        "fiber": 4.5,
        "db_food_name": "Paneer Butter Masala",
        "serving_multiplier": 0.9,
        "image_icon": "fa-cheese",
        "description": "Cubed paneer pan-seared with tri-color bell peppers, onions, and dry Indian spices for a high-calcium, low-carb evening plate.",
        "ingredients": [
            "120g fresh low-fat paneer cubes",
            "1 cup diced red, yellow, and green capsicums",
            "1 small red onion",
            "1 tsp olive or mustard oil",
            "Coriander powder, garam masala, and chaat masala"
        ],
        "instructions": [
            "Sauté onions and bell peppers in a hot skillet for 3 minutes until crisp-tender.",
            "Add dry spices and paneer cubes; toss gently to coat.",
            "Cook on high heat for 3-4 minutes to sear the paneer edges.",
            "Squeeze fresh lime juice and serve immediately."
        ]
    },
    {
        "id": 6,
        "title": "Crispy Tofu & Green Veggie Sesame Bowl",
        "category": "Dinner",
        "dietary_type": "Vegan",
        "prep_time": "20 mins",
        "calories": 310.0,
        "protein": 21.0,
        "carbohydrates": 18.0,
        "fat": 16.0,
        "fiber": 7.5,
        "db_food_name": "Tofu Stir Fry with Veggies",
        "serving_multiplier": 1.1,
        "image_icon": "fa-seedling",
        "description": "Pan-browned organic firm tofu tossed with broccoli florets, snap peas, and toasted sesame seeds in a light ginger-soy glaze.",
        "ingredients": [
            "150g firm tofu, pressed and cubed",
            "1.5 cups broccoli florets and zucchini",
            "1 tsp sesame oil",
            "1 tbsp low-sodium soy sauce",
            "1 tsp toasted sesame seeds"
        ],
        "instructions": [
            "Pan-sear tofu cubes in sesame oil until golden brown on all sides.",
            "Add broccoli and zucchini; stir-fry over high heat with 2 tablespoons of water.",
            "Drizzle low-sodium soy sauce and toss for 1 minute.",
            "Top with sesame seeds and serve warm."
        ]
    },
    {
        "id": 7,
        "title": "Greek Yogurt Parfait with Honey & Walnuts",
        "category": "Snack",
        "dietary_type": "Vegetarian",
        "prep_time": "5 mins",
        "calories": 210.0,
        "protein": 18.5,
        "carbohydrates": 14.0,
        "fat": 8.0,
        "fiber": 2.0,
        "db_food_name": "Plain Greek Yogurt (Curd)",
        "serving_multiplier": 1.2,
        "image_icon": "fa-jar",
        "description": "Thick strained Greek yogurt layered with organic honey, crushed walnuts, and antioxidant-rich chia seeds.",
        "ingredients": [
            "1 cup unflavored Greek yogurt",
            "1 tsp pure raw honey",
            "1 tbsp crushed walnuts",
            "1/2 tsp chia seeds"
        ],
        "instructions": [
            "Spoon thick Greek yogurt into a glass.",
            "Drizzle honey over the top layer.",
            "Garnish with chopped walnuts and chia seeds for immediate crunch and omega-3s."
        ]
    },
    {
        "id": 8,
        "title": "Spiced Roasted Chickpeas (Chana Crunch)",
        "category": "Snack",
        "dietary_type": "Vegan",
        "prep_time": "15 mins",
        "calories": 180.0,
        "protein": 8.5,
        "carbohydrates": 26.0,
        "fat": 5.0,
        "fiber": 7.0,
        "db_food_name": "Chickpea Curry (Chole)",
        "serving_multiplier": 0.7,
        "image_icon": "fa-cookie",
        "description": "Oven-roasted white chickpeas seasoned with smoked paprika, cumin, and sea salt. A fiber-rich crunchy snack.",
        "ingredients": [
            "1 cup boiled chickpeas, completely pat-dried",
            "1 tsp olive oil",
            "1/2 tsp smoked paprika, cumin, and rock salt"
        ],
        "instructions": [
            "Toss pat-dried chickpeas with olive oil and spices.",
            "Roast in air fryer or oven at 200°C for 15-18 minutes until crisp.",
            "Cool to room temperature for maximum crispiness."
        ]
    }
]
