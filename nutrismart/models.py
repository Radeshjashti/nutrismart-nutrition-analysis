from datetime import datetime, date, time
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)  # 'Male', 'Female', 'Other'
    height = db.Column(db.Float, nullable=False)        # in cm
    weight = db.Column(db.Float, nullable=False)        # in kg
    activity_level = db.Column(db.String(50), nullable=False) # 'Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active'
    dietary_preference = db.Column(db.String(50), nullable=False) # 'Vegetarian', 'Non-Vegetarian', 'Vegan', 'Eggetarian'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    logs = db.relationship('FoodLog', backref='user', lazy=True, cascade='all, delete-orphan')
    water_logs = db.relationship('WaterLog', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('NutritionGoal', backref='user', uselist=False, lazy=True, cascade='all, delete-orphan')

    @property
    def target_water_ml(self):
        """Recommended daily water intake: ~35ml per kg of bodyweight, minimum 2000ml."""
        if self.weight and self.weight > 0:
            return max(2000, round(self.weight * 35))
        return 2500

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def bmi(self):
        """Calculate Body Mass Index (BMI)."""
        if self.height and self.weight and self.height > 0:
            h_meters = self.height / 100.0
            return round(self.weight / (h_meters ** 2), 1)
        return 0.0

    @property
    def bmi_category(self):
        """Return BMI classification."""
        val = self.bmi
        if val <= 0:
            return "Unknown"
        if val < 18.5:
            return "Underweight"
        elif val < 25.0:
            return "Normal weight"
        elif val < 30.0:
            return "Overweight"
        else:
            return "Obese"

    @property
    def bmr(self):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor formula."""
        if not (self.weight and self.height and self.age):
            return 2000
        if self.gender == 'Female':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        return max(round(bmr), 1200)

    @property
    def tdee(self):
        """Calculate Total Daily Energy Expenditure (estimated daily maintenance calories)."""
        multipliers = {
            'Sedentary': 1.2,
            'Lightly Active': 1.375,
            'Moderately Active': 1.55,
            'Very Active': 1.725
        }
        mult = multipliers.get(self.activity_level, 1.2)
        return round(self.bmr * mult)

    def calculate_recommended_goals(self):
        """Generate balanced macronutrient & micronutrient targets from TDEE."""
        cal = self.tdee
        # Standard balanced distribution: 20% protein, 50% carbs, 30% fat
        protein_g = round((cal * 0.22) / 4)
        carbs_g = round((cal * 0.50) / 4)
        fat_g = round((cal * 0.28) / 9)
        fiber_g = 30
        sugar_g = round((cal * 0.08) / 4) # Less than 8-10% of daily calories
        sodium_mg = 2300 # Standard recommendation
        return {
            'calories': float(cal),
            'protein': float(protein_g),
            'carbohydrates': float(carbs_g),
            'fat': float(fat_g),
            'fiber': float(fiber_g),
            'sugar': float(sugar_g),
            'sodium': float(sodium_mg)
        }


class Food(db.Model):
    __tablename__ = 'foods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=True) # e.g. 'Grain', 'Dairy', 'Fruit', 'Vegetable', 'Protein'
    serving_size = db.Column(db.String(50), nullable=False) # e.g. '1 bowl (150g)', '1 medium (120g)'
    serving_weight_grams = db.Column(db.Float, default=100.0) # Reference base grams
    
    # Macronutrients per serving
    calories = db.Column(db.Float, nullable=False)       # kcal
    protein = db.Column(db.Float, nullable=False)        # g
    carbohydrates = db.Column(db.Float, nullable=False)  # g
    fat = db.Column(db.Float, nullable=False)            # g
    fiber = db.Column(db.Float, default=0.0)             # g
    sugar = db.Column(db.Float, default=0.0)             # g
    sodium = db.Column(db.Float, default=0.0)            # mg

    # Micronutrients per serving
    vitamin_a = db.Column(db.Float, default=0.0)         # mcg
    vitamin_b12 = db.Column(db.Float, default=0.0)       # mcg
    vitamin_c = db.Column(db.Float, default=0.0)         # mg
    vitamin_d = db.Column(db.Float, default=0.0)         # mcg
    iron = db.Column(db.Float, default=0.0)              # mg
    calcium = db.Column(db.Float, default=0.0)           # mg
    zinc = db.Column(db.Float, default=0.0)              # mg

    dietary_type = db.Column(db.String(30), default='Vegetarian') # 'Vegetarian', 'Non-Vegetarian', 'Vegan', 'Eggetarian'
    image_url = db.Column(db.String(255), nullable=True)

    # Relationships
    logs = db.relationship('FoodLog', backref='food', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'serving_size': self.serving_size,
            'calories': round(self.calories, 1),
            'protein': round(self.protein, 1),
            'carbohydrates': round(self.carbohydrates, 1),
            'fat': round(self.fat, 1),
            'fiber': round(self.fiber, 1),
            'sugar': round(self.sugar, 1),
            'sodium': round(self.sodium, 1),
            'vitamin_a': round(self.vitamin_a, 1),
            'vitamin_b12': round(self.vitamin_b12, 1),
            'vitamin_c': round(self.vitamin_c, 1),
            'vitamin_d': round(self.vitamin_d, 1),
            'iron': round(self.iron, 1),
            'calcium': round(self.calcium, 1),
            'zinc': round(self.zinc, 1),
            'dietary_type': self.dietary_type
        }


class FoodLog(db.Model):
    __tablename__ = 'food_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=False)
    quantity = db.Column(db.Float, default=1.0) # Number of servings
    meal_type = db.Column(db.String(50), nullable=False) # 'Breakfast', 'Lunch', 'Dinner', 'Snack'

    # Calculated nutrition stored for fast historical aggregation and preservation of snapshot
    calories = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbohydrates = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    fiber = db.Column(db.Float, default=0.0)
    sugar = db.Column(db.Float, default=0.0)
    sodium = db.Column(db.Float, default=0.0)

    # Micronutrients stored
    vitamin_a = db.Column(db.Float, default=0.0)
    vitamin_b12 = db.Column(db.Float, default=0.0)
    vitamin_c = db.Column(db.Float, default=0.0)
    vitamin_d = db.Column(db.Float, default=0.0)
    iron = db.Column(db.Float, default=0.0)
    calcium = db.Column(db.Float, default=0.0)
    zinc = db.Column(db.Float, default=0.0)

    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    time = db.Column(db.String(20), nullable=False, default=lambda: datetime.now().strftime("%H:%M"))


class NutritionGoal(db.Model):
    __tablename__ = 'nutrition_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    calories = db.Column(db.Float, default=2000.0)
    protein = db.Column(db.Float, default=100.0)
    carbohydrates = db.Column(db.Float, default=250.0)
    fat = db.Column(db.Float, default=65.0)
    fiber = db.Column(db.Float, default=30.0)
    sugar = db.Column(db.Float, default=50.0)
    sodium = db.Column(db.Float, default=2300.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WaterLog(db.Model):
    __tablename__ = 'water_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount_ml = db.Column(db.Integer, nullable=False, default=250) # Standard glass is 250ml
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    time = db.Column(db.String(20), nullable=False, default=lambda: datetime.now().strftime("%H:%M"))
