"""
Recommendation & Health Insights Engine for NutriSmart.
Performs rule-based dietary pattern analysis, micronutrient deficiency detection,
and personalized meal recommendations with neutral non-medical health guidance.
"""

# Standard Recommended Dietary Allowances (RDA) for adults (informational benchmarks)
MICRONUTRIENT_RDA = {
    "vitamin_a": {"name": "Vitamin A", "unit": "mcg", "rda": 900.0, "sources": "Carrots, spinach, sweet potatoes, eggs, mangoes"},
    "vitamin_b12": {"name": "Vitamin B12", "unit": "mcg", "rda": 2.4, "sources": "Dairy products, eggs, fortified cereals, nutritional yeast, poultry"},
    "vitamin_c": {"name": "Vitamin C", "unit": "mg", "rda": 90.0, "sources": "Citrus fruits, oranges, amla, bell peppers, broccoli, tomatoes"},
    "vitamin_d": {"name": "Vitamin D", "unit": "mcg", "rda": 15.0, "sources": "Sunlight exposure, egg yolks, fortified milk, mushrooms, fatty fish"},
    "iron": {"name": "Iron", "unit": "mg", "rda": 18.0, "sources": "Spinach, lentils, beans, tofu, pumpkin seeds, lean meats"},
    "calcium": {"name": "Calcium", "unit": "mg", "rda": 1000.0, "sources": "Milk, yogurt, cheese, fortified plant milks, sesame seeds, almonds"},
    "zinc": {"name": "Zinc", "unit": "mg", "rda": 11.0, "sources": "Chickpeas, lentils, nuts, whole grains, eggs, seeds"}
}

def analyze_health_insights(today_totals, goals, past_logs=None):
    """
    Evaluates current day intake against configured goals and returns rule-based insights.
    All insights use neutral, non-diagnostic guidance language.
    """
    insights = []

    # 1. Calorie Balance
    cal_intake = today_totals.get('calories', 0)
    cal_goal = goals.calories if goals else 2000.0
    cal_diff = cal_intake - cal_goal

    if cal_intake == 0:
        insights.append({
            "type": "info",
            "title": "Start Logging Today's Meals",
            "message": "You haven't logged any food items yet today. Begin tracking your breakfast or snacks to monitor your daily energy levels.",
            "icon": "fa-utensils"
        })
    elif cal_diff > 350:
        insights.append({
            "type": "warning",
            "title": "Calorie Intake Higher Than Target",
            "message": f"Your recorded intake ({int(cal_intake)} kcal) exceeds your daily target ({int(cal_goal)} kcal) by {int(cal_diff)} kcal. Consider balancing with lighter vegetable or broth-based meals.",
            "icon": "fa-chart-line"
        })
    elif cal_diff < -500:
        insights.append({
            "type": "info",
            "title": "Caloric Deficit Detected",
            "message": f"You are currently {int(abs(cal_diff))} kcal below your daily energy target. Ensure you fuel your body adequately with nutrient-dense meals.",
            "icon": "fa-battery-half"
        })
    else:
        insights.append({
            "type": "success",
            "title": "Optimal Caloric Energy Balance",
            "message": f"Your caloric intake ({int(cal_intake)} kcal) is well-aligned with your daily energy maintenance target ({int(cal_goal)} kcal).",
            "icon": "fa-circle-check"
        })

    # 2. Protein Analysis
    protein_intake = today_totals.get('protein', 0)
    protein_goal = goals.protein if goals else 100.0
    if protein_goal > 0:
        protein_ratio = protein_intake / protein_goal
        if protein_ratio < 0.65:
            insights.append({
                "type": "warning",
                "title": "Protein Intake Below Target",
                "message": f"Your recorded protein ({round(protein_intake, 1)}g / {int(protein_goal)}g) is currently below your daily target. Adequate protein supports muscle recovery and satiety.",
                "icon": "fa-dumbbell"
            })
        elif protein_ratio >= 0.9:
            insights.append({
                "type": "success",
                "title": "Excellent Protein Intake",
                "message": f"You have met your daily protein target ({round(protein_intake, 1)}g / {int(protein_goal)}g), which supports cellular repair and satiety.",
                "icon": "fa-award"
            })

    # 3. Dietary Fiber
    fiber_intake = today_totals.get('fiber', 0)
    fiber_goal = goals.fiber if goals else 30.0
    if fiber_intake < (fiber_goal * 0.6):
        insights.append({
            "type": "warning",
            "title": "Low Fiber Intake",
            "message": f"Your recorded fiber is {round(fiber_intake, 1)}g against the recommended {int(fiber_goal)}g. Adding legumes, oats, flaxseeds, and leafy greens supports gut and cardiovascular health.",
            "icon": "fa-seedling"
        })
    else:
        insights.append({
            "type": "success",
            "title": "Good Fiber Intake",
            "message": f"Great job! Your recorded fiber ({round(fiber_intake, 1)}g) helps maintain smooth digestion and stable post-meal blood sugar levels.",
            "icon": "fa-apple-whole"
        })

    # 4. Sugar Intake
    sugar_intake = today_totals.get('sugar', 0)
    sugar_goal = goals.sugar if goals else 50.0
    if sugar_intake > sugar_goal:
        insights.append({
            "type": "warning",
            "title": "High Sugar Intake Recorded",
            "message": f"Recorded simple sugars ({round(sugar_intake, 1)}g) exceed the suggested upper threshold ({int(sugar_goal)}g). Consider swapping sweet treats for whole fruits or herbal teas.",
            "icon": "fa-cube"
        })

    # 5. Sodium Intake
    sodium_intake = today_totals.get('sodium', 0)
    sodium_goal = goals.sodium if goals else 2300.0
    if sodium_intake > sodium_goal:
        insights.append({
            "type": "warning",
            "title": "Elevated Sodium Intake",
            "message": f"Recorded sodium ({int(sodium_intake)} mg) is above the standard guideline of {int(sodium_goal)} mg. Moderate packaged seasonings and salted snacks.",
            "icon": "fa-droplet-slash"
        })

    # 6. Overall Balanced Nutrition Summary
    macros_met = sum([
        1 if protein_intake >= (protein_goal * 0.75) else 0,
        1 if fiber_intake >= (fiber_goal * 0.7) else 0,
        1 if abs(cal_diff) <= 400 else 0
    ])
    if macros_met >= 2 and cal_intake > 500:
        insights.append({
            "type": "success",
            "title": "Balanced Nutrition Profile",
            "message": "Your recorded macronutrients and micronutrients show a healthy, well-rounded distribution for the day.",
            "icon": "fa-scale-balanced"
        })

    return insights


def analyze_micronutrients(today_totals):
    """
    Computes percentage of RDA achieved for essential micronutrients.
    Returns status indicators and food source suggestions.
    """
    analysis = []
    for key, info in MICRONUTRIENT_RDA.items():
        val = today_totals.get(key, 0.0)
        rda = info["rda"]
        pct = min(round((val / rda) * 100, 1), 100.0)

        if pct < 50.0:
            status = "Low"
            status_class = "danger"
            guidance = f"Low intake ({round(val, 1)} {info['unit']} / {rda} {info['unit']}). Consider including more {key.replace('_', ' ')} rich foods such as {info['sources']}."
        elif pct < 85.0:
            status = "Moderate"
            status_class = "warning"
            guidance = f"Moderate intake ({round(val, 1)} {info['unit']} / {rda} {info['unit']}). On track towards daily requirement."
        else:
            status = "Optimal"
            status_class = "success"
            guidance = f"Well nourished ({round(val, 1)} {info['unit']} / {rda} {info['unit']}). Recommended daily allowance satisfied."

        analysis.append({
            "key": key,
            "name": info["name"],
            "current": round(val, 1),
            "rda": rda,
            "unit": info["unit"],
            "percentage": pct,
            "status": status,
            "status_class": status_class,
            "guidance": guidance,
            "sources": info["sources"]
        })
    return analysis


def get_diet_recommendations(user, today_totals, goals):
    """
    Generates personalized, meal-by-meal dietary suggestions based on
    user's dietary preference (Vegetarian, Non-Veg, Vegan, Eggetarian) and current nutritional gaps.
    """
    diet_pref = user.dietary_preference or "Vegetarian"
    protein_intake = today_totals.get('protein', 0)
    protein_goal = goals.protein if goals else 100.0
    fiber_intake = today_totals.get('fiber', 0)
    fiber_goal = goals.fiber if goals else 30.0
    cal_intake = today_totals.get('calories', 0)
    cal_goal = goals.calories if goals else 2000.0

    needs_protein = protein_intake < (protein_goal * 0.75)
    needs_fiber = fiber_intake < (fiber_goal * 0.70)
    high_calories = (cal_intake - cal_goal) > 250

    recommendations = {
        "status_summary": "",
        "focus_areas": [],
        "breakfast": [],
        "lunch": [],
        "dinner": [],
        "snacks": []
    }

    if needs_protein:
        recommendations["focus_areas"].append({
            "title": "Boost Protein Intake",
            "desc": f"Your current protein is {round(protein_intake, 1)}g vs goal of {int(protein_goal)}g. Include protein dense sources in your next meal.",
            "badge": "Protein Priority"
        })
    if needs_fiber:
        recommendations["focus_areas"].append({
            "title": "Increase Dietary Fiber",
            "desc": f"Fiber is at {round(fiber_intake, 1)}g (target {int(fiber_goal)}g). Incorporate more raw salads, steamed greens, and unpolished grains.",
            "badge": "Digestive Health"
        })
    if high_calories:
        recommendations["focus_areas"].append({
            "title": "Caloric Moderation",
            "desc": "Calorie intake is trending slightly high. Focus on high-volume, low-density foods such as clear soups and green vegetables.",
            "badge": "Portion Control"
        })
    if not needs_protein and not needs_fiber and not high_calories:
        recommendations["focus_areas"].append({
            "title": "Well Balanced Nutrition",
            "desc": "Your nutrient breakdown is closely tracking your daily goals. Maintain this balanced dietary diversity!",
            "badge": "Optimal Track"
        })

    # Meal ideas tailored to Dietary Preference
    if diet_pref == "Non-Vegetarian":
        recommendations["breakfast"] = [
            {"name": "2 Boiled Eggs & Whole Grain Toast", "macros": "280 kcal | 18g Protein", "tags": ["High Protein", "Quick"]},
            {"name": "Oatmeal with Almond Milk & Chia Seeds", "macros": "290 kcal | 12g Protein", "tags": ["High Fiber", "Heart Healthy"]}
        ]
        recommendations["lunch"] = [
            {"name": "Grilled Chicken Breast with Quinoa & Steamed Broccoli", "macros": "420 kcal | 42g Protein", "tags": ["Lean Muscle", "Low Carb"]},
            {"name": "Pan-Seared Salmon with Brown Rice & Mixed Green Salad", "macros": "480 kcal | 35g Protein", "tags": ["Omega-3 Rich", "Fiber Boost"]}
        ]
        recommendations["dinner"] = [
            {"name": "Chicken Curry with 2 Whole Wheat Chapatis & Cucumber Salad", "macros": "450 kcal | 32g Protein", "tags": ["Balanced Indian", "Satisfying"]},
            {"name": "Egg Bhurji (Scramble) with Stir-Fried Capsicum & Soup", "macros": "310 kcal | 22g Protein", "tags": ["Light Dinner", "High Protein"]}
        ]
        recommendations["snacks"] = [
            {"name": "Greek Yogurt with a Handful of Roasted Almonds", "macros": "190 kcal | 15g Protein", "tags": ["Satiety", "Calcium"]},
            {"name": "Sliced Apple with Natural Peanut Butter", "macros": "180 kcal | 5g Protein", "tags": ["Fiber", "Energy"]}
        ]

    elif diet_pref == "Eggetarian":
        recommendations["breakfast"] = [
            {"name": "Herb & Spinach 2-Egg Omelette with Chapati", "macros": "290 kcal | 18g Protein", "tags": ["High Protein", "Iron Rich"]},
            {"name": "Boiled Eggs & Seasonal Fruit Bowl", "macros": "220 kcal | 14g Protein", "tags": ["Low Sugar", "Energizing"]}
        ]
        recommendations["lunch"] = [
            {"name": "Egg Curry with Steamed Brown Rice & Dal Tadka", "macros": "460 kcal | 26g Protein", "tags": ["Wholesome", "Comfort Food"]},
            {"name": "Chickpea & Boiled Egg Salad with Lemon Herb Dressing", "macros": "380 kcal | 24g Protein", "tags": ["High Fiber", "Refreshing"]}
        ]
        recommendations["dinner"] = [
            {"name": "Paneer & Egg White Stir-Fry with Whole Wheat Phulkas", "macros": "410 kcal | 28g Protein", "tags": ["Muscle Repair", "Nutrient Dense"]},
            {"name": "Dal Palak (Spinach Lentils) with 2 Chapatis", "macros": "340 kcal | 16g Protein", "tags": ["Light", "Digestive"]}
        ]
        recommendations["snacks"] = [
            {"name": "Hard-Boiled Egg with Black Pepper & Green Tea", "macros": "80 kcal | 6.5g Protein", "tags": ["Zero Sugar", "Antioxidants"]},
            {"name": "Roasted Chana (Chickpeas) & Unsalted Walnuts", "macros": "160 kcal | 8g Protein", "tags": ["Crunchy", "High Fiber"]}
        ]

    elif diet_pref == "Vegan":
        recommendations["breakfast"] = [
            {"name": "Tofu Scramble with Turmeric, Tomatoes & Toast", "macros": "260 kcal | 18g Protein", "tags": ["100% Plant Based", "Iron Rich"]},
            {"name": "Vegetable Poha with Roasted Peanuts & Lemon Juice", "macros": "280 kcal | 8g Protein", "tags": ["Iron Rich", "Easy Digest"]}
        ]
        recommendations["lunch"] = [
            {"name": "Tofu & Vegetable Stir-Fry with Brown Rice", "macros": "410 kcal | 22g Protein", "tags": ["High Protein", "Micronutrients"]},
            {"name": "Chickpea Chole with Brown Rice & Fresh Salad", "macros": "440 kcal | 18g Protein", "tags": ["High Fiber", "Satiety"]}
        ]
        recommendations["dinner"] = [
            {"name": "Yellow Moong Dal with Sauteed Spinach & 2 Chapatis", "macros": "360 kcal | 17g Protein", "tags": ["Light", "High Iron"]},
            {"name": "Red Kidney Beans (Rajma) with Steamed Rice & Greens", "macros": "420 kcal | 16g Protein", "tags": ["Complete Protein", "Filling"]}
        ]
        recommendations["snacks"] = [
            {"name": "Roasted Soybeans or Almonds with Green Tea", "macros": "150 kcal | 10g Protein", "tags": ["Plant Protein", "Antioxidants"]},
            {"name": "Fresh Papaya Slices with Chia Seeds", "macros": "110 kcal | 3g Protein", "tags": ["Digestive Enzymes", "Vitamin C"]}
        ]

    else: # Default Vegetarian
        recommendations["breakfast"] = [
            {"name": "Steamed Idli with Vegetable Sambar & Mint Chutney", "macros": "260 kcal | 9g Protein", "tags": ["Fermented Gut Health", "Light"]},
            {"name": "Rolled Oats Cooked in Milk with Walnuts & Banana", "macros": "320 kcal | 14g Protein", "tags": ["Heart Healthy", "High Fiber"]}
        ]
        recommendations["lunch"] = [
            {"name": "Paneer Butter Masala with 2 Whole Wheat Chapatis & Salad", "macros": "490 kcal | 22g Protein", "tags": ["Calcium Rich", "High Protein"]},
            {"name": "Dal Tadka with Steamed Rice & Cucumber Mint Raita", "macros": "420 kcal | 16g Protein", "tags": ["Probiotic Curd", "Wholesome"]}
        ]
        recommendations["dinner"] = [
            {"name": "Palak Paneer (Spinach & Cottage Cheese) with Phulkas", "macros": "380 kcal | 20g Protein", "tags": ["Iron + Calcium", "Nourishing"]},
            {"name": "Chickpea Curry (Chole) with Steamed Brown Rice", "macros": "430 kcal | 16g Protein", "tags": ["Fiber Rich", "Comfort"]}
        ]
        recommendations["snacks"] = [
            {"name": "Plain Greek Yogurt (Curd) with Berries or Honey", "macros": "140 kcal | 15g Protein", "tags": ["Probiotic", "Bone Health"]},
            {"name": "Roasted Almonds & Pumpkin Seeds", "macros": "170 kcal | 7g Protein", "tags": ["Healthy Fats", "Magnesium"]}
        ]

    return recommendations
