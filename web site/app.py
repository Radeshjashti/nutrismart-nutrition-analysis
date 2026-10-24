"""
NutriSmart - A Smart Nutrition Analysis System for Real-Time Food Health Monitoring and Diet Management
College Minor Project Prototype
"""

import os
from datetime import date, datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, session,
    flash, jsonify, abort, send_from_directory, send_file
)
from werkzeug.utils import secure_filename
from sqlalchemy import func

from models import db, User, Food, FoodLog, NutritionGoal, WaterLog
from seed_database import seed_database
from food_recognizer import recognizer
from recipes_data import CURATED_RECIPES
from recommendation_engine import (
    analyze_health_insights, analyze_micronutrients, get_diet_recommendations
)

# Application Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'nutrismart-secret-key-project-2026-secure-session'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Expose standard math and built-in functions to Jinja2 templates
app.jinja_env.globals.update(
    round=round,
    min=min,
    max=max,
    int=int,
    abs=abs
)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB file
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

db.init_app(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    if 'user_id' in session:
        return db.session.get(User, session['user_id'])
    return None


@app.context_processor
def inject_global_data():
    """Injects current_user and current_year into all Jinja templates."""
    return {
        'current_user': get_current_user(),
        'current_year': datetime.now().year,
        'today_date': date.today().strftime('%A, %B %d, %Y')
    }


def calculate_day_totals(user_id, target_date=None):
    """Calculates total macros and micros for a given user and date."""
    if target_date is None:
        target_date = date.today()

    logs = FoodLog.query.filter_by(user_id=user_id, date=target_date).all()
    totals = {
        'calories': 0.0,
        'protein': 0.0,
        'carbohydrates': 0.0,
        'fat': 0.0,
        'fiber': 0.0,
        'sugar': 0.0,
        'sodium': 0.0,
        'vitamin_a': 0.0,
        'vitamin_b12': 0.0,
        'vitamin_c': 0.0,
        'vitamin_d': 0.0,
        'iron': 0.0,
        'calcium': 0.0,
        'zinc': 0.0,
        'meal_counts': {'Breakfast': 0, 'Lunch': 0, 'Dinner': 0, 'Snack': 0}
    }

    for log in logs:
        totals['calories'] += log.calories or 0.0
        totals['protein'] += log.protein or 0.0
        totals['carbohydrates'] += log.carbohydrates or 0.0
        totals['fat'] += log.fat or 0.0
        totals['fiber'] += log.fiber or 0.0
        totals['sugar'] += log.sugar or 0.0
        totals['sodium'] += log.sodium or 0.0
        totals['vitamin_a'] += log.vitamin_a or 0.0
        totals['vitamin_b12'] += log.vitamin_b12 or 0.0
        totals['vitamin_c'] += log.vitamin_c or 0.0
        totals['vitamin_d'] += log.vitamin_d or 0.0
        totals['iron'] += log.iron or 0.0
        totals['calcium'] += log.calcium or 0.0
        totals['zinc'] += log.zinc or 0.0
        if log.meal_type in totals['meal_counts']:
            totals['meal_counts'][log.meal_type] += 1

    # Round all values
    for k in totals:
        if isinstance(totals[k], float):
            totals[k] = round(totals[k], 1)

    return totals, logs


def calculate_user_streak(user_id):
    """Calculates consecutive days with active logged food records."""
    streak = 0
    check_date = date.today()
    # Check if user logged today or yesterday
    has_today = FoodLog.query.filter_by(user_id=user_id, date=check_date).first()
    if not has_today:
        check_date = check_date - timedelta(days=1)
        if not FoodLog.query.filter_by(user_id=user_id, date=check_date).first():
            return 0

    while True:
        if FoodLog.query.filter_by(user_id=user_id, date=check_date).first():
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak


# -------------------------------------------------------------------------
# AUTHENTICATION & LANDING ROUTES
# -------------------------------------------------------------------------

@app.route('/')
def index():
    """Landing Page showcasing NutriSmart features, how it works, and limitations."""
    return render_template('index.html')


@app.route('/download-project')
def download_project():
    """Direct one-click browser download of the complete project folder as a ZIP file."""
    import zipfile
    project_dir = os.path.dirname(os.path.abspath(__file__))
    zip_dest = os.path.join(project_dir, 'nutrismart_download.zip')

    with zipfile.ZipFile(zip_dest, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            if '__pycache__' in root or 'uploads' in root or '.git' in root:
                continue
            for file in files:
                if file.endswith('.pyc') or file.startswith('nutrismart_download'):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, project_dir)
                try:
                    zipf.write(full_path, rel_path)
                except Exception:
                    pass

    return send_file(zip_dest, as_attachment=True, download_name='nutrismart_full_project.zip')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        age = request.form.get('age', type=int)
        gender = request.form.get('gender', 'Male')
        height = request.form.get('height', type=float)
        weight = request.form.get('weight', type=float)
        activity_level = request.form.get('activity_level', 'Moderately Active')
        dietary_preference = request.form.get('dietary_preference', 'Vegetarian')

        # Validation
        if not name or not email or not password:
            flash('Please complete all required fields.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match. Please verify.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        if not age or age < 12 or age > 110:
            flash('Please enter a valid age between 12 and 110.', 'danger')
            return render_template('register.html')

        if not height or height < 50 or height > 260:
            flash('Please enter a valid height in centimeters (50 - 260 cm).', 'danger')
            return render_template('register.html')

        if not weight or weight < 25 or weight > 300:
            flash('Please enter a valid weight in kilograms (25 - 300 kg).', 'danger')
            return render_template('register.html')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

        # Create user
        user = User(
            name=name,
            email=email,
            age=age,
            gender=gender,
            height=height,
            weight=weight,
            activity_level=activity_level,
            dietary_preference=dietary_preference
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Initialize recommended nutrition goals based on profile
        rec_goals = user.calculate_recommended_goals()
        goals = NutritionGoal(user_id=user.id, **rec_goals)
        db.session.add(goals)
        db.session.commit()

        session['user_id'] = user.id
        session['user_name'] = user.name
        flash(f'Account created successfully! Welcome to NutriSmart, {user.name}.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash(f'Welcome back, {user.name}!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('dashboard'))
        else:
            flash('Invalid email or password. Please check your credentials.', 'danger')

    return render_template('login.html')


@app.route('/demo-login')
def demo_login():
    """Quick one-click login for evaluator / professor project presentation."""
    demo_user = User.query.filter_by(email='demo@nutrismart.com').first()
    if demo_user:
        session['user_id'] = demo_user.id
        session['user_name'] = demo_user.name
        flash('Logged in as Demo User with 7 days of realistic preloaded nutrition logs!', 'success')
        return redirect(url_for('dashboard'))
    else:
        seed_database()
        demo_user = User.query.filter_by(email='demo@nutrismart.com').first()
        if demo_user:
            session['user_id'] = demo_user.id
            session['user_name'] = demo_user.name
            flash('Demo database seeded and logged in!', 'success')
            return redirect(url_for('dashboard'))
    flash('Demo user setup failed.', 'danger')
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('login'))


# -------------------------------------------------------------------------
# DASHBOARD & DATA CHARTS
# -------------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    today_totals, today_logs = calculate_day_totals(user.id, date.today())
    goals = user.goals
    if not goals:
        rec_goals = user.calculate_recommended_goals()
        goals = NutritionGoal(user_id=user.id, **rec_goals)
        db.session.add(goals)
        db.session.commit()

    # Progress percentages
    cal_pct = min(round((today_totals['calories'] / (goals.calories or 2000.0)) * 100, 1), 100.0)
    pro_pct = min(round((today_totals['protein'] / (goals.protein or 100.0)) * 100, 1), 100.0)
    carb_pct = min(round((today_totals['carbohydrates'] / (goals.carbohydrates or 250.0)) * 100, 1), 100.0)
    fat_pct = min(round((today_totals['fat'] / (goals.fat or 70.0)) * 100, 1), 100.0)
    fib_pct = min(round((today_totals['fiber'] / (goals.fiber or 30.0)) * 100, 1), 100.0)

    # 7-day historical trend for Chart.js
    seven_days = []
    daily_calories = []
    daily_protein = []
    daily_carbs = []
    daily_fat = []

    today = date.today()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime('%b %d')
        seven_days.append(day_str)

        day_logs = FoodLog.query.filter_by(user_id=user.id, date=day).all()
        cals = sum(l.calories or 0 for l in day_logs)
        pros = sum(l.protein or 0 for l in day_logs)
        carbs = sum(l.carbohydrates or 0 for l in day_logs)
        fats = sum(l.fat or 0 for l in day_logs)

        daily_calories.append(round(cals, 1))
        daily_protein.append(round(pros, 1))
        daily_carbs.append(round(carbs, 1))
        daily_fat.append(round(fats, 1))

    chart_data = {
        'labels': seven_days,
        'calories': daily_calories,
        'calorie_goal': [goals.calories] * 7,
        'protein': daily_protein,
        'carbs': daily_carbs,
        'fat': daily_fat,
        'today_macros': {
            'protein': today_totals['protein'],
            'carbs': today_totals['carbohydrates'],
            'fat': today_totals['fat']
        }
    }

    # Generate quick high-level insights for dashboard widgets
    insights = analyze_health_insights(today_totals, goals)[:3]

    # Hydration tracking for today
    today_water_logs = WaterLog.query.filter_by(user_id=user.id, date=today).all()
    today_water_ml = sum(w.amount_ml for w in today_water_logs)
    target_water_ml = user.target_water_ml
    water_pct = min(round((today_water_ml / target_water_ml) * 100, 1), 100.0)

    # Active streak calculation
    streak_days = calculate_user_streak(user.id)

    return render_template(
        'dashboard.html',
        user=user,
        today_totals=today_totals,
        goals=goals,
        today_logs=today_logs,
        cal_pct=cal_pct,
        pro_pct=pro_pct,
        carb_pct=carb_pct,
        fat_pct=fat_pct,
        fib_pct=fib_pct,
        chart_data=chart_data,
        insights=insights,
        today_water_ml=today_water_ml,
        target_water_ml=target_water_ml,
        water_pct=water_pct,
        streak_days=streak_days
    )


# -------------------------------------------------------------------------
# FOOD ANALYZER (MANUAL SEARCH & IMAGE RECOGNITION PROTOTYPE)
# -------------------------------------------------------------------------

@app.route('/food-analyzer', methods=['GET', 'POST'])
@login_required
def food_analyzer():
    user = get_current_user()
    all_foods = Food.query.order_by(Food.name.asc()).all()

    selected_food = None
    recognition_result = None
    uploaded_image_url = None

    # Handle manual food selection via query params or POST
    food_id = request.args.get('food_id', type=int)
    if food_id:
        selected_food = db.session.get(Food, food_id)

    search_arg = request.args.get('food_search', '').strip()
    if search_arg and not selected_food:
        matched = Food.query.filter(Food.name.ilike(f'%{search_arg}%')).first()
        if not matched:
            # Try fuzzy word match
            words = search_arg.split()
            for w in words:
                if len(w) > 3:
                    matched = Food.query.filter(Food.name.ilike(f'%{w}%')).first()
                    if matched:
                        break
        if matched:
            selected_food = matched

    # Handle direct manual search form
    if request.method == 'POST' and 'manual_search' in request.form:
        search_query = request.form.get('food_search', '').strip()
        matched = Food.query.filter(Food.name.ilike(f'%{search_query}%')).first()
        if matched:
            selected_food = matched
        else:
            flash(f'No matching food found for "{search_query}". Try selecting from the dropdown list.', 'info')

    # Handle image upload form
    if request.method == 'POST' and ('upload_image' in request.form or 'food_image' in request.files or 'image' in request.files):
        file = request.files.get('food_image') or request.files.get('image')
        if not file or file.filename == '':
            flash('Please choose or capture a food image to analyze.', 'warning')
        elif allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp_prefix = datetime.now().strftime('%Y%m%d_%H%M%S_')
            saved_filename = timestamp_prefix + filename
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
            file.save(save_path)

            # Execute modular recognition prototype
            result = recognizer.analyze_image(save_path, original_filename=filename)
            if result:
                recognition_result = result
                uploaded_image_url = url_for('uploaded_file', filename=saved_filename)
                # Find corresponding food in database
                db_food = Food.query.filter_by(name=result['db_food_name']).first()
                if not db_food:
                    db_food = Food.query.filter(Food.name.ilike(f"%{result['detected_food']}%")).first()
                if db_food:
                    selected_food = db_food
                flash(f"Analyzed! Prototype detected: {result['detected_food']} ({result['confidence']}% confidence)", 'success')
        else:
            flash('Unsupported image format. Allowed: JPG, PNG, WEBP.', 'danger')

    return render_template(
        'food_analyzer.html',
        user=user,
        all_foods=all_foods,
        selected_food=selected_food,
        recognition_result=recognition_result,
        uploaded_image_url=uploaded_image_url
    )


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Securely serve uploaded food pictures."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/analyze-image', methods=['POST'])
@login_required
def api_analyze_image():
    """AJAX endpoint for instant interactive food image recognition."""
    file = request.files.get('image') or request.files.get('food_image')
    if not file or file.filename == '':
        return jsonify({'error': 'No image file uploaded'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid image format. Please upload JPG, PNG or WEBP.'}), 400

    filename = secure_filename(file.filename)
    timestamp_prefix = datetime.now().strftime('%Y%m%d_%H%M%S_')
    saved_filename = timestamp_prefix + filename
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
    file.save(save_path)

    result = recognizer.analyze_image(save_path, original_filename=filename)
    if not result:
        return jsonify({'error': 'Image analysis failed.'}), 500

    db_food = Food.query.filter_by(name=result['db_food_name']).first()
    if not db_food:
        db_food = Food.query.filter(Food.name.ilike(f"%{result['detected_food']}%")).first()
    food_data = db_food.to_dict() if db_food else None

    return jsonify({
        'success': True,
        'result': result,
        'image_url': url_for('uploaded_file', filename=saved_filename),
        'food': food_data
    })


@app.route('/api/food-search')
def api_food_search():
    """Returns JSON list of matching foods for autocomplete."""
    q = request.args.get('q', '').strip()
    if not q:
        foods = Food.query.limit(10).all()
    else:
        foods = Food.query.filter(Food.name.ilike(f'%{q}%')).limit(15).all()
    return jsonify([f.to_dict() for f in foods])


# -------------------------------------------------------------------------
# ADD FOOD & NUTRITION LOGGING
# -------------------------------------------------------------------------

@app.route('/add-food', methods=['GET', 'POST'])
@login_required
def add_food():
    user = get_current_user()
    all_foods = Food.query.order_by(Food.name.asc()).all()

    prefill_food_id = request.args.get('food_id', type=int)
    prefill_meal = request.args.get('meal_type', 'Lunch')

    if request.method == 'POST':
        food_id = request.form.get('food_id', type=int)
        quantity = request.form.get('quantity', type=float)
        meal_type = request.form.get('meal_type', 'Lunch')
        log_date_str = request.form.get('date', '')
        log_time_str = request.form.get('time', '')

        if not food_id or not quantity or quantity <= 0:
            flash('Please select a valid food and enter a quantity greater than 0.', 'warning')
            return redirect(url_for('add_food'))

        food_item = db.session.get(Food, food_id)
        if not food_item:
            flash('Selected food not found in database.', 'danger')
            return redirect(url_for('add_food'))

        try:
            log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date() if log_date_str else date.today()
        except ValueError:
            log_date = date.today()

        if not log_time_str:
            log_time_str = datetime.now().strftime('%H:%M')

        # Compute proportional nutrition based on quantity of standard servings
        new_log = FoodLog(
            user_id=user.id,
            food_id=food_item.id,
            quantity=round(quantity, 2),
            meal_type=meal_type,
            calories=round(food_item.calories * quantity, 1),
            protein=round(food_item.protein * quantity, 1),
            carbohydrates=round(food_item.carbohydrates * quantity, 1),
            fat=round(food_item.fat * quantity, 1),
            fiber=round(food_item.fiber * quantity, 1),
            sugar=round(food_item.sugar * quantity, 1),
            sodium=round(food_item.sodium * quantity, 1),
            vitamin_a=round(food_item.vitamin_a * quantity, 1),
            vitamin_b12=round(food_item.vitamin_b12 * quantity, 1),
            vitamin_c=round(food_item.vitamin_c * quantity, 1),
            vitamin_d=round(food_item.vitamin_d * quantity, 1),
            iron=round(food_item.iron * quantity, 1),
            calcium=round(food_item.calcium * quantity, 1),
            zinc=round(food_item.zinc * quantity, 1),
            date=log_date,
            time=log_time_str
        )

        db.session.add(new_log)
        db.session.commit()

        flash(f'Logged {quantity}x {food_item.name} ({round(food_item.calories * quantity, 1)} kcal) under {meal_type}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template(
        'add_food.html',
        user=user,
        all_foods=all_foods,
        prefill_food_id=prefill_food_id,
        prefill_meal=prefill_meal,
        today_date=date.today().strftime('%Y-%m-%d'),
        current_time=datetime.now().strftime('%H:%M')
    )


# -------------------------------------------------------------------------
# NUTRITION HISTORY & LOG MANAGEMENT
# -------------------------------------------------------------------------

@app.route('/history')
@login_required
def history():
    user = get_current_user()

    # Filters
    search_query = request.args.get('search', '').strip()
    filter_meal = request.args.get('meal', '').strip()
    filter_date = request.args.get('date', '').strip()

    query = FoodLog.query.filter_by(user_id=user.id).join(Food)

    if search_query:
        query = query.filter(Food.name.ilike(f'%{search_query}%'))

    if filter_meal and filter_meal in ['Breakfast', 'Lunch', 'Dinner', 'Snack']:
        query = query.filter(FoodLog.meal_type == filter_meal)

    if filter_date:
        try:
            parsed_date = datetime.strptime(filter_date, '%Y-%m-%d').date()
            query = query.filter(FoodLog.date == parsed_date)
        except ValueError:
            pass

    logs = query.order_by(FoodLog.date.desc(), FoodLog.time.desc()).all()

    # Aggregate metrics for the filtered view
    total_cals = round(sum(l.calories or 0 for l in logs), 1)
    total_prot = round(sum(l.protein or 0 for l in logs), 1)
    total_carb = round(sum(l.carbohydrates or 0 for l in logs), 1)
    total_fat = round(sum(l.fat or 0 for l in logs), 1)
    total_fib = round(sum(l.fiber or 0 for l in logs), 1)

    return render_template(
        'history.html',
        user=user,
        logs=logs,
        search_query=search_query,
        filter_meal=filter_meal,
        filter_date=filter_date,
        total_cals=total_cals,
        total_prot=total_prot,
        total_carb=total_carb,
        total_fat=total_fat,
        total_fib=total_fib
    )


@app.route('/history/delete/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    user = get_current_user()
    log = FoodLog.query.filter_by(id=log_id, user_id=user.id).first_or_404()
    food_name = log.food.name if log.food else "Food entry"
    db.session.delete(log)
    db.session.commit()
    flash(f'Removed "{food_name}" from your food history.', 'info')
    return redirect(url_for('history'))


# -------------------------------------------------------------------------
# DAILY GOALS MANAGEMENT
# -------------------------------------------------------------------------

@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    user = get_current_user()
    goal = user.goals
    if not goal:
        rec_goals = user.calculate_recommended_goals()
        goal = NutritionGoal(user_id=user.id, **rec_goals)
        db.session.add(goal)
        db.session.commit()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'recalculate':
            # Recalculate based on Mifflin-St Jeor formula
            recs = user.calculate_recommended_goals()
            goal.calories = recs['calories']
            goal.protein = recs['protein']
            goal.carbohydrates = recs['carbohydrates']
            goal.fat = recs['fat']
            goal.fiber = recs['fiber']
            goal.sugar = recs['sugar']
            goal.sodium = recs['sodium']
            db.session.commit()
            flash('Nutrition goals automatically recalculated based on your updated age, weight, and activity level!', 'success')
            return redirect(url_for('goals'))

        # Manual goal update
        try:
            goal.calories = float(request.form.get('calories', goal.calories))
            goal.protein = float(request.form.get('protein', goal.protein))
            goal.carbohydrates = float(request.form.get('carbohydrates', goal.carbohydrates))
            goal.fat = float(request.form.get('fat', goal.fat))
            goal.fiber = float(request.form.get('fiber', goal.fiber))
            goal.sugar = float(request.form.get('sugar', goal.sugar))
            goal.sodium = float(request.form.get('sodium', goal.sodium))
            db.session.commit()
            flash('Your daily nutrition goals have been updated successfully!', 'success')
        except ValueError:
            flash('Please enter valid numeric values for all targets.', 'danger')

        return redirect(url_for('goals'))

    # Calculate today's progress vs goals
    today_totals, _ = calculate_day_totals(user.id, date.today())
    progress = {
        'calories': min(round((today_totals['calories'] / (goal.calories or 1)) * 100, 1), 100),
        'protein': min(round((today_totals['protein'] / (goal.protein or 1)) * 100, 1), 100),
        'carbohydrates': min(round((today_totals['carbohydrates'] / (goal.carbohydrates or 1)) * 100, 1), 100),
        'fat': min(round((today_totals['fat'] / (goal.fat or 1)) * 100, 1), 100),
        'fiber': min(round((today_totals['fiber'] / (goal.fiber or 1)) * 100, 1), 100),
        'sugar': min(round((today_totals['sugar'] / (goal.sugar or 1)) * 100, 1), 100),
        'sodium': min(round((today_totals['sodium'] / (goal.sodium or 1)) * 100, 1), 100)
    }

    return render_template(
        'goals.html',
        user=user,
        goal=goal,
        today_totals=today_totals,
        progress=progress
    )


# -------------------------------------------------------------------------
# HEALTH INSIGHTS & MICRONUTRIENTS
# -------------------------------------------------------------------------

@app.route('/insights')
@login_required
def insights():
    user = get_current_user()
    today_totals, _ = calculate_day_totals(user.id, date.today())
    goals = user.goals

    rule_insights = analyze_health_insights(today_totals, goals)
    micronutrient_analysis = analyze_micronutrients(today_totals)

    return render_template(
        'insights.html',
        user=user,
        today_totals=today_totals,
        goals=goals,
        insights=rule_insights,
        micronutrients=micronutrient_analysis
    )


# -------------------------------------------------------------------------
# DIET RECOMMENDATIONS
# -------------------------------------------------------------------------

@app.route('/recommendations')
@login_required
def recommendations():
    user = get_current_user()
    today_totals, _ = calculate_day_totals(user.id, date.today())
    goals = user.goals

    recs = get_diet_recommendations(user, today_totals, goals)

    return render_template(
        'recommendations.html',
        user=user,
        today_totals=today_totals,
        goals=goals,
        recommendations=recs
    )


# -------------------------------------------------------------------------
# PROFILE & SETTINGS
# -------------------------------------------------------------------------

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_current_user()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            name = request.form.get('name', '').strip()
            age_raw = request.form.get('age', '').strip()
            gender = request.form.get('gender', 'Male').strip()
            height_raw = request.form.get('height', '').strip()
            weight_raw = request.form.get('weight', '').strip()
            activity_level = request.form.get('activity_level', 'Moderately Active').strip()
            dietary_preference = request.form.get('dietary_preference', 'Vegetarian').strip()

            # Clean and parse numeric inputs
            try:
                age = int(age_raw) if age_raw else None
            except (ValueError, TypeError):
                age = None

            try:
                clean_h = height_raw.lower().replace('cm', '').replace(',', '.').strip()
                height = float(clean_h) if clean_h else None
            except (ValueError, TypeError):
                height = None

            try:
                clean_w = weight_raw.lower().replace('kg', '').replace(',', '.').strip()
                weight = float(clean_w) if clean_w else None
            except (ValueError, TypeError):
                weight = None

            if not name:
                flash('Please enter your full name.', 'danger')
            elif age is None or age < 10 or age > 120:
                flash('Please enter a valid age between 10 and 120 years.', 'danger')
            elif height is None or height < 50 or height > 260:
                flash('Please enter a valid height between 50 and 260 cm.', 'danger')
            elif weight is None or weight < 20 or weight > 350:
                flash('Please enter a valid weight between 20 and 350 kg.', 'danger')
            else:
                user.name = name
                user.age = age
                user.gender = gender
                user.height = round(height, 1)
                user.weight = round(weight, 1)
                user.activity_level = activity_level
                user.dietary_preference = dietary_preference
                session['user_name'] = user.name

                # Synchronize and update user's daily nutrition goals with new metrics
                rec_goals = user.calculate_recommended_goals()
                if user.goals:
                    user.goals.calories = rec_goals['calories']
                    user.goals.protein = rec_goals['protein']
                    user.goals.carbohydrates = rec_goals['carbohydrates']
                    user.goals.fat = rec_goals['fat']
                    user.goals.fiber = rec_goals['fiber']
                    user.goals.sugar = rec_goals['sugar']
                    user.goals.sodium = rec_goals['sodium']

                db.session.commit()
                flash('Profile details and metabolic targets updated successfully!', 'success')

        elif action == 'change_password':
            current_pw = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')

            if not user.check_password(current_pw):
                flash('Current password is incorrect.', 'danger')
            elif new_pw != confirm_pw:
                flash('New passwords do not match.', 'danger')
            elif len(new_pw) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
            else:
                user.set_password(new_pw)
                db.session.commit()
                flash('Password updated successfully!', 'success')

        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


# -------------------------------------------------------------------------
# HYDRATION TRACKING API
# -------------------------------------------------------------------------

@app.route('/api/water/log', methods=['POST'])
@login_required
def api_log_water():
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    amount_ml = int(data.get('amount_ml', request.form.get('amount_ml', 250)))

    entry = WaterLog(
        user_id=user.id,
        amount_ml=amount_ml,
        date=date.today(),
        time=datetime.now().strftime("%H:%M")
    )
    db.session.add(entry)
    db.session.commit()

    today_logs = WaterLog.query.filter_by(user_id=user.id, date=date.today()).all()
    today_water_ml = sum(w.amount_ml for w in today_logs)
    target_water_ml = user.target_water_ml
    pct = min(round((today_water_ml / target_water_ml) * 100, 1), 100.0)

    return jsonify({
        'success': True,
        'today_water_ml': today_water_ml,
        'target_water_ml': target_water_ml,
        'percentage': pct,
        'message': f'Logged +{amount_ml}ml of water!'
    })


@app.route('/api/water/reset', methods=['POST'])
@login_required
def api_reset_water():
    user = get_current_user()
    WaterLog.query.filter_by(user_id=user.id, date=date.today()).delete()
    db.session.commit()
    target_water_ml = user.target_water_ml
    return jsonify({
        'success': True,
        'today_water_ml': 0,
        'target_water_ml': target_water_ml,
        'percentage': 0.0,
        'message': "Today's water intake reset."
    })


# -------------------------------------------------------------------------
# FOOD COMPARISON TOOL
# -------------------------------------------------------------------------

@app.route('/compare')
@login_required
def compare():
    user = get_current_user()
    all_foods = Food.query.order_by(Food.name.asc()).all()

    food_a_id = request.args.get('food_a', type=int)
    food_b_id = request.args.get('food_b', type=int)

    # Defaults: Dosa vs Idli or first two items
    if not food_a_id and len(all_foods) > 3:
        food_a_id = all_foods[3].id # Plain Dosa
    elif not food_a_id and all_foods:
        food_a_id = all_foods[0].id

    if not food_b_id and len(all_foods) > 2:
        food_b_id = all_foods[2].id # Steamed Idli
    elif not food_b_id and len(all_foods) > 1:
        food_b_id = all_foods[1].id

    food_a = db.session.get(Food, food_a_id) if food_a_id else None
    food_b = db.session.get(Food, food_b_id) if food_b_id else None

    comparison = None
    if food_a and food_b:
        def diff(val_a, val_b, lower_is_better=False):
            val_a = val_a or 0.0
            val_b = val_b or 0.0
            delta = round(val_a - val_b, 1)
            if lower_is_better:
                winner = 'a' if val_a < val_b else ('b' if val_b < val_a else 'equal')
            else:
                winner = 'a' if val_a > val_b else ('b' if val_b > val_a else 'equal')
            return {'val_a': val_a, 'val_b': val_b, 'delta': abs(delta), 'winner': winner, 'diff': delta}

        comparison = {
            'calories': diff(food_a.calories, food_b.calories, lower_is_better=True),
            'protein': diff(food_a.protein, food_b.protein),
            'carbohydrates': diff(food_a.carbohydrates, food_b.carbohydrates),
            'fat': diff(food_a.fat, food_b.fat, lower_is_better=True),
            'fiber': diff(food_a.fiber, food_b.fiber),
            'sugar': diff(food_a.sugar, food_b.sugar, lower_is_better=True),
            'sodium': diff(food_a.sodium, food_b.sodium, lower_is_better=True),
            'iron': diff(food_a.iron, food_b.iron),
            'calcium': diff(food_a.calcium, food_b.calcium),
            'vitamin_c': diff(food_a.vitamin_c, food_b.vitamin_c)
        }

    return render_template(
        'compare.html',
        user=user,
        all_foods=all_foods,
        food_a=food_a,
        food_b=food_b,
        comparison=comparison
    )


# -------------------------------------------------------------------------
# HEALTHY RECIPES & MEAL PLANNER
# -------------------------------------------------------------------------

@app.route('/recipes')
@login_required
def recipes():
    user = get_current_user()
    category = request.args.get('category', '').strip()
    diet = request.args.get('diet', '').strip()

    filtered = CURATED_RECIPES
    if category and category != 'All':
        filtered = [r for r in filtered if r['category'].lower() == category.lower()]
    if diet and diet != 'All':
        filtered = [r for r in filtered if r['dietary_type'].lower() == diet.lower()]

    return render_template(
        'recipes.html',
        user=user,
        recipes=filtered,
        selected_category=category or 'All',
        selected_diet=diet or 'All'
    )


@app.route('/recipes/log/<int:recipe_id>', methods=['POST'])
@login_required
def log_recipe(recipe_id):
    user = get_current_user()
    recipe = next((r for r in CURATED_RECIPES if r['id'] == recipe_id), None)
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('recipes'))

    meal_type = request.form.get('meal_type', recipe['category'])
    db_food = Food.query.filter_by(name=recipe['db_food_name']).first()
    if not db_food:
        db_food = Food.query.first()

    mult = recipe.get('serving_multiplier', 1.0)

    new_log = FoodLog(
        user_id=user.id,
        food_id=db_food.id,
        quantity=mult,
        meal_type=meal_type,
        calories=recipe['calories'],
        protein=recipe['protein'],
        carbohydrates=recipe['carbohydrates'],
        fat=recipe['fat'],
        fiber=recipe['fiber'],
        sugar=round(db_food.sugar * mult, 1),
        sodium=round(db_food.sodium * mult, 1),
        vitamin_a=round(db_food.vitamin_a * mult, 1),
        vitamin_b12=round(db_food.vitamin_b12 * mult, 1),
        vitamin_c=round(db_food.vitamin_c * mult, 1),
        vitamin_d=round(db_food.vitamin_d * mult, 1),
        iron=round(db_food.iron * mult, 1),
        calcium=round(db_food.calcium * mult, 1),
        zinc=round(db_food.zinc * mult, 1),
        date=date.today(),
        time=datetime.now().strftime("%H:%M")
    )
    db.session.add(new_log)
    db.session.commit()

    flash(f"Successfully logged recipe '{recipe['title']}' ({recipe['calories']} kcal) as {meal_type}!", 'success')
    return redirect(url_for('dashboard'))


# -------------------------------------------------------------------------
# ANALYTICAL HEALTH & PROGRESS REPORT (PRINTABLE)
# -------------------------------------------------------------------------

@app.route('/report')
@login_required
def report():
    user = get_current_user()
    today = date.today()
    days_data = []

    total_cals_week = 0
    total_prot_week = 0
    total_carb_week = 0
    total_fat_week = 0
    total_fib_week = 0
    total_water_week = 0

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_totals, _ = calculate_day_totals(user.id, day)
        day_water = sum(w.amount_ml for w in WaterLog.query.filter_by(user_id=user.id, date=day).all())

        days_data.append({
            'date': day,
            'day_name': day.strftime('%a, %b %d'),
            'calories': day_totals['calories'],
            'protein': day_totals['protein'],
            'carbs': day_totals['carbohydrates'],
            'fat': day_totals['fat'],
            'fiber': day_totals['fiber'],
            'water_ml': day_water
        })

        total_cals_week += day_totals['calories']
        total_prot_week += day_totals['protein']
        total_carb_week += day_totals['carbohydrates']
        total_fat_week += day_totals['fat']
        total_fib_week += day_totals['fiber']
        total_water_week += day_water

    avg_cals = round(total_cals_week / 7, 1)
    avg_prot = round(total_prot_week / 7, 1)
    avg_carb = round(total_carb_week / 7, 1)
    avg_fat = round(total_fat_week / 7, 1)
    avg_fib = round(total_fib_week / 7, 1)
    avg_water = round(total_water_week / 7)

    goal_cals = user.goals.calories if user.goals else 2000.0
    adherent_days = sum(1 for d in days_data if abs(d['calories'] - goal_cals) <= (goal_cals * 0.20))
    adherence_pct = round((adherent_days / 7) * 100)

    today_totals, _ = calculate_day_totals(user.id, today)
    micros = analyze_micronutrients(today_totals)

    return render_template(
        'report.html',
        user=user,
        today=today,
        days_data=days_data,
        avg_cals=avg_cals,
        avg_prot=avg_prot,
        avg_carb=avg_carb,
        avg_fat=avg_fat,
        avg_fib=avg_fib,
        avg_water=avg_water,
        adherence_pct=adherence_pct,
        micros=micros
    )


# -------------------------------------------------------------------------
# ERROR HANDLERS
# -------------------------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', custom_error='404 - Page Not Found'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html', custom_error='500 - An unexpected internal error occurred. Please try again.'), 500


# -------------------------------------------------------------------------
# INITIALIZATION & ENTRY POINT
# -------------------------------------------------------------------------

with app.app_context():
    db.create_all()
    seed_database()

if __name__ == '__main__':
    print("\n========================================================")
    print(" NutriSmart - Smart Nutrition Analysis System Prototype")
    print(" Running locally at: http://127.0.0.1:5000")
    print(" Demo Account: demo@nutrismart.com  |  Password: Demo@123")
    print("========================================================\n")
    app.run(host='127.0.0.1', port=5000, debug=True)
