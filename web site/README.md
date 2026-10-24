# NutriSmart: A Smart Nutrition Analysis System for Real-Time Food Health Monitoring and Diet Management

A responsive full-stack web application developed as a **College Minor Project**. NutriSmart provides intelligent nutritional monitoring, macronutrient and micronutrient tracking, Mifflin-St Jeor metabolic target calculations, rule-based dietary pattern analysis, and an image processing food-recognition prototype.

---

## 1. Technology Stack

- **Backend:** Python 3.10+ & Flask 3.0
- **Database & ORM:** SQLite with SQLAlchemy ORM (`database.db`)
- **Frontend:** HTML5, CSS3, JavaScript (ES6)
- **UI Framework:** Bootstrap 5.3 & Custom Modern Health/Nutrition CSS Theme
- **Data Visualization:** Chart.js 4.4
- **Icons:** Font Awesome 6
- **Image Processing & ML Prototype:** Pillow 10.x & Modular Machine Learning Classifier Hook (ready for TensorFlow/Keras or PyTorch)
- **Authentication & Security:** Flask session management, Werkzeug password hashing, secure file validation

---

## 2. Key Features

1. **Smart Food Analyzer (Dual Mode):**
   - **Manual Search:** Instant lookup from 35+ verified Indian & global food items with full breakdown of 13 macros & micros (Calories, Protein, Carbs, Fat, Fiber, Sugar, Sodium, Vitamin A, B12, C, D, Iron, Calcium, Zinc).
   - **Food Image Scanner (Prototype AI):** Drag-and-drop / upload food picture with real-time preview, visual feature inspection (Pillow), confidence scoring (e.g., `Detected Food: Dosa (91.4% confidence)`), and 1-click logging to daily diary.
2. **Interactive Real-Time Dashboard:**
   - Visual progress bars for Calories, Protein, Carbohydrates, Healthy Fats, Fiber, Sugar, and Sodium against personalized targets.
   - **Daily Calorie Chart:** 7-day trend line comparing consumed calories against user's daily target.
   - **Macronutrient Doughnut Chart:** Real-time ratio distribution of Protein, Carbs, and Fats.
   - **Weekly Nutrition Multi-Bar Chart:** Visual multi-bar comparison across the past 7 days.
3. **Mifflin-St Jeor Metabolic Engine & Daily Goals:**
   - Calculates Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE) based on age, gender, height, weight, and activity level.
   - Customizable targets with one-click **Strategic Goal Presets** (Fat Loss `-500 kcal`, Muscle Hypertrophy `+300 kcal`, Maintenance, Keto) and "Recalculate Base Goals".
4. **Real-Time Hydration Tracker (Water Monitor):**
   - Live daily water tracking with personal target calculation (~35 ml/kg bodyweight).
   - One-click logging buttons (`+250ml Glass`, `+500ml Bottle`, `Reset`) with asynchronous progress updates.
5. **Head-to-Head Nutritional Food Comparison Tool (`/compare`):**
   - Side-by-side comparison of any two foods from the database.
   - Detailed metric table, visual deltas, and advantage badges (e.g. "🏆 Plain Dosa: +12g Protein", "⚡ Lower Calorie", "🥗 +4.2g Fiber").
6. **Healthy Recipes & Meal Planner (`/recipes`):**
   - Chef-crafted balanced recipes categorized by meal (Breakfast, Lunch, Dinner, Snack) and dietary preferences (Veg, Non-Veg, Vegan, Eggetarian).
   - Ingredients, preparation methods, prep time, and **"1-Click Log to Diary"** button.
7. **Comprehensive Printable Health Report (`/report`):**
   - 7-day adherence score (% compliance), weekly average calorie & macro breakdown, daily log progression table, and micronutrient sufficiency summary formatted for `window.print()` / PDF export.
8. **Nutrition History & Logging Streak:**
   - Interactive table with live search by food name, date filter, meal filter (Breakfast, Lunch, Dinner, Snack), full micronutrient modal popup, print/export, and consecutive active logging streak counter.
9. **Rule-Based Health Insights & Micronutrient Analysis:**
   - Evaluates sugar spikes, fiber deficit, protein sufficiency, and caloric surplus/deficit with neutral, non-medical guidance.
   - Progress tracking against adult Recommended Dietary Allowances (RDA) for essential vitamins and minerals.
10. **Smart Diet Recommendations:**
   - Generates personalized breakfast, lunch, dinner, and snack suggestions tailored to dietary preferences (Vegetarian, Non-Vegetarian, Vegan, Eggetarian) and active nutritional gaps.
11. **Profile & Anthropometrics:**
   - Live Body Mass Index (BMI) computation with category classification and password security.
12. **Pre-Seeded Demo Account:**
   - Pre-loaded with 7 full days of realistic meals and water logs so all charts and insights are ready for immediate evaluation presentation.

---

## 3. Quick Start & Setup Instructions

### Prerequisites
- Python 3.9, 3.10, 3.11, 3.12, or 3.13 installed.
- `pip` package manager.

### Step 1: Open Terminal / PowerShell
Navigate to the project directory:
```bash
cd "C:\Users\jasht\.gemini\antigravity\scratch\nutrismart"
```

### Step 2: Install Dependencies
Run:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
Start the Flask development server:
```bash
python app.py
```

### Step 4: Access in Web Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 4. Demo Account Credentials (For Project Presentation)

To present the project without manually typing 7 days of historical logs, click the **"Quick Demo Login"** button on the landing page or login page, or use:

- **Email:** `demo@nutrismart.com`
- **Password:** `Demo@123`

The database seeds automatically on first run with:
- 35+ verified food items (Dosa, Idli, Chapati, Chicken Curry, Paneer, Rice, Dal, Fruits, Salads, etc.).
- 7 continuous days of realistic Breakfast, Lunch, Dinner, and Snack entries.
- Active calculated goals and health insights.

---

## 5. Project Directory Structure

```text
nutrismart/
├── app.py                     # Main Flask application & route controller
├── models.py                  # SQLAlchemy models (User, Food, FoodLog, NutritionGoal, WaterLog)
├── seed_database.py           # Database seeder with 35+ foods, 7-day meal logs & water tracking
├── food_recognizer.py         # Pillow image feature inspector & modular ML classifier hook
├── recommendation_engine.py   # Rule-based health insights & personalized diet recommendations
├── recipes_data.py            # Chef-crafted healthy recipes database with full macros
├── requirements.txt           # Python package dependencies
├── README.md                  # Project documentation & execution guide
├── database.db                # SQLite database (auto-generated on startup)
│
├── templates/                 # Jinja2 HTML5 Templates
│   ├── base.html              # Master layout with responsive sidebar & public navbar
│   ├── index.html             # Landing page with hero, features, workflow, limitations
│   ├── login.html             # Login form with one-click demo access
│   ├── register.html          # Registration with anthropometric metrics input
│   ├── dashboard.html         # User dashboard with progress cards, hydration bar & 3 Chart.js charts
│   ├── food_analyzer.html     # Dual-mode food analyzer, file upload & WebRTC live camera scanner
│   ├── add_food.html          # Food logger with live nutrient computation
│   ├── history.html           # Filterable meal history table & micronutrient modal
│   ├── goals.html             # Daily goals editor, goal presets & Mifflin-St Jeor recalculator
│   ├── compare.html           # Side-by-side food comparison & nutritional advantage analyzer
│   ├── recipes.html           # Healthy recipes catalog with 1-click meal logging
│   ├── insights.html          # Rule-based dietary insights & RDA micronutrients
│   ├── recommendations.html   # Diet suggestions by meal type & dietary preference
│   ├── report.html            # Weekly printable / PDF-ready analytical health report
│   └── profile.html           # User metrics, BMI calculation & password change
│
├── static/                    # Frontend Static Assets
│   ├── css/
│   │   └── style.css          # Healthcare & nutrition design system
│   └── js/
│       ├── main.js            # Responsive sidebar toggle & UI alert handling
│       ├── dashboard.js       # Chart.js rendering & real-time AJAX water tracker
│       └── analyzer.js        # Drag-and-drop file upload, live image preview & WebRTC camera
│
└── uploads/                   # Upload directory for scanned food images
```

---

## 6. Major Modules Explanation

| Module | Description |
|---|---|
| **`models.py`** | Defines 5 relational tables: `users`, `foods`, `food_logs`, `nutrition_goals`, and `water_logs`. Includes ORM helper properties for BMI calculation, Mifflin-St Jeor BMR, and TDEE estimation. |
| **`seed_database.py`** | Automatically initializes the SQLite database with 35+ foods spanning grains, legumes, dairy, poultry, fruits, vegetables, and snacks, alongside 7 days of realistic logs and water tracking for presentation. |
| **`food_recognizer.py`** | Modular image recognition pipeline. Uses Pillow to inspect pixel dimensions and dominant RGB color distributions. Maps image features to 12 food classes (Apple, Banana, Rice, Chapati, Idli, Dosa, Sambar, Salad, Chicken, Egg, Pizza, Burger). Includes a direct hook for loading TensorFlow/Keras `.h5` or `.keras` models. |
| **`recipes_data.py`** | Complete catalog of balanced recipes categorized by meal and diet, with ingredients, preparation steps, and direct logging hooks. |
| **`recommendation_engine.py`** | Implements rule-based health heuristics comparing current intake against targets. Generates non-medical guidance for protein gaps, sugar thresholds, fiber intake, and RDA micronutrient benchmarks. |
| **`app.py`** | Central Flask controller managing session authentication, route protection (`@login_required`), image upload handling, date calculations, and REST API endpoints. |
| **`recommendation_engine.py`** | Implements rule-based health heuristics comparing current intake against targets. Generates non-medical guidance for protein gaps, sugar thresholds, fiber intake, and RDA micronutrient benchmarks. |
| **`app.py`** | Central Flask controller managing session authentication, route protection (`@login_required`), image upload handling, date calculations, and REST API endpoints. |

---

## 7. Project Limitations & Non-Medical Disclaimer

- **Prototype Scope:** The food recognition module is an educational prototype demonstrating image ingestion, feature extraction, and database matching. Real-world accuracy depends on a deep learning model trained on larger datasets (e.g., Food-101).
- **Approximate Reference Values:** Nutrition values represent standard averages from the USDA FoodData Central and ICMR Indian Food Composition Tables; actual prepared food dishes vary based on recipes and cooking oils.
- **Portion Estimation:** Portion estimation from 2D images is approximate; users are encouraged to specify exact gram weights or servings.
- **Informational Guidance:** NutriSmart provides informational guidance and is strictly **not a medical diagnosis or treatment system**. It does not replace advice from certified physicians or registered dietitians.

---

## 8. Viva Presentation Tips

1. **How does the system calculate daily calorie targets?**
   - It implements the Mifflin-St Jeor formula:
     $$\text{BMR (Men)} = 10 \times \text{weight (kg)} + 6.25 \times \text{height (cm)} - 5 \times \text{age} + 5$$
     $$\text{BMR (Women)} = 10 \times \text{weight (kg)} + 6.25 \times \text{height (cm)} - 5 \times \text{age} - 161$$
     Then multiplies BMR by the physical activity coefficient (1.2 to 1.725) to derive TDEE.
2. **How does the food recognition module work?**
   - It accepts image uploads, validates formats with Werkzeug, resizes and inspects dominant color histograms using Pillow, and evaluates class associations. Code is modularly structured so `tf.keras.models.load_model()` can be dropped in without changing any route logic.
3. **How are charts updated?**
   - Chart data is dynamically computed in `app.py` from the user's actual database records in `food_logs` across the last 7 calendar days, converted to JSON, and rendered using Chart.js.
