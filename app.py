# <<<< app.py >>>>
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory storage for simplicity. In a real app, use a database.
questions_board = []
food_data = {
    "Meats": [
        {"name": "Chicken Breast (100g, cooked)", "calories": 165},
        {"name": "Beef Steak (100g, lean, cooked)", "calories": 250},
        {"name": "Salmon (100g, cooked)", "calories": 208},
        {"name": "Pork Chop (100g, cooked)", "calories": 231},
    ],
    "Dairy": [
        {"name": "Milk (1 cup, 2%)", "calories": 122},
        {"name": "Cheddar Cheese (1 oz)", "calories": 115},
        {"name": "Yogurt (1 cup, plain, non-fat)", "calories": 137},
        {"name": "Butter (1 tbsp)", "calories": 102},
    ],
    "Vegetables": [
        {"name": "Broccoli (1 cup, chopped)", "calories": 55},
        {"name": "Spinach (1 cup, raw)", "calories": 7},
        {"name": "Carrot (1 medium)", "calories": 25},
        {"name": "Potato (1 medium, baked)", "calories": 160},
        {"name": "Bell Pepper (1 medium, red)", "calories": 37},
    ],
    "Fruits": [
        {"name": "Apple (1 medium)", "calories": 95},
        {"name": "Banana (1 medium)", "calories": 105},
        {"name": "Orange (1 medium)", "calories": 62},
        {"name": "Strawberries (1 cup, whole)", "calories": 49},
    ],
    "Grains": [
        {"name": "White Rice (1 cup, cooked)", "calories": 205},
        {"name": "Whole Wheat Bread (1 slice)", "calories": 81},
        {"name": "Oats (1/2 cup, dry)", "calories": 150},
        {"name": "Pasta (1 cup, cooked)", "calories": 220},
    ]
} 

premium_plans_data = [
    {"id": "silver", "name": "Silver Plan", "price": 9.99, "interval": "month", 
     "features": ["Access to standard calorie data", "Basic community Q&A", "Email support"]},
    {"id": "gold", "name": "Gold Plan", "price": 19.99, "interval": "month", 
     "features": ["All Silver features", "Expanded food database", "Ad-free experience", "Priority Q&A"]},
    {"id": "platinum", "name": "Platinum Plan", "price": 39.99, "interval": "month", 
     "features": ["All Gold features", "Personalized meal planning (simulated)", "Direct expert support (simulated)", "Early access to new features"]},
]

# --- Authentication ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'John Doe' and password == 'Test1':
            session['logged_in'] = True
            session['username'] = username
            session['user_plan'] = 'free' 
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('user_plan', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- Protected Routes Decorator ---
def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first", "warning")
            return redirect(url_for('login'))
    wrap.__name__ = f.__name__
    return wrap

# --- Main Pages ---
@app.route('/')
@app.route('/home')
@login_required
def home():
    current_plan_id = session.get('user_plan', 'free')
    current_plan_name = "Free"
    if current_plan_id != 'free':
        plan_details = next((plan for plan in premium_plans_data if plan['id'] == current_plan_id), None)
        if plan_details:
            current_plan_name = plan_details['name']
    return render_template('home.html', username=session.get('username'), current_plan_name=current_plan_name)

@app.route('/questions', methods=['GET', 'POST'])
@login_required
def questions():
    if request.method == 'POST':
        question_text = request.form.get('question_text')
        if question_text:
            questions_board.append({"text": question_text, "user": session.get('username', 'Anonymous')})
            flash('Your question has been posted!', 'success')
            return redirect(url_for('questions'))
        else:
            flash('Question cannot be empty.', 'warning')
    return render_template('questions.html', questions=questions_board)

@app.route('/foods')
@login_required
def foods():
    return render_template('foods.html', food_categories=food_data)

@app.route('/upgrade', methods=['GET', 'POST']) # MODIFIED: Added POST method
@login_required
def upgrade():
    if request.method == 'POST': # ADDED: Logic to handle POST request from upgrade form
        chosen_plan_id = request.form.get('plan_id')
        chosen_plan = next((plan for plan in premium_plans_data if plan['id'] == chosen_plan_id), None)
        
        if chosen_plan:
            # Redirect to checkout for the chosen plan
            return redirect(url_for('checkout', plan_id=chosen_plan_id))
        else:
            flash("Invalid plan selected.", 'danger')
            # Fallback to GET request for the upgrade page
            return render_template('upgrade.html', plans=premium_plans_data, current_plan_id=session.get('user_plan'))
            
    # This is for GET request: displays the plans
    return render_template('upgrade.html', plans=premium_plans_data, current_plan_id=session.get('user_plan'))

# --- Checkout and Payment Simulation ---
@app.route('/checkout/<plan_id>')
@login_required
def checkout(plan_id):
    selected_plan = next((plan for plan in premium_plans_data if plan['id'] == plan_id), None)
    if not selected_plan:
        flash("Invalid plan for checkout.", 'danger')
        return redirect(url_for('upgrade'))
    
    user_email_placeholder = f"{session.get('username', '').replace(' ', '').lower()}@example.com"
    return render_template('checkout.html', plan=selected_plan, user_email_placeholder=user_email_placeholder)

@app.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    plan_id = request.form.get('plan_id')
    email = request.form.get('email')
    card_number = request.form.get('card_number') 

    if not all([plan_id, email, card_number]): 
        flash("Please fill in all required payment details.", 'warning')
        return redirect(url_for('checkout', plan_id=plan_id if plan_id else premium_plans_data[0]['id']))

    selected_plan = next((p for p in premium_plans_data if p['id'] == plan_id), None)
    if not selected_plan:
        flash("Invalid plan during payment processing.", 'danger')
        return redirect(url_for('upgrade'))

    session['user_plan'] = plan_id
    flash(f"Thank you for subscribing to the {selected_plan['name']}! Your payment was successful (simulation).", 'success')
    return redirect(url_for('home'))

# --- Subscription Management ---
@app.route('/manage_subscription')
@login_required
def manage_subscription():
    current_plan_id = session.get('user_plan', 'free')
    if current_plan_id == 'free':
        flash("You are not currently subscribed to a premium plan.", 'info')
        return redirect(url_for('upgrade')) 

    current_plan_details = next((plan for plan in premium_plans_data if plan['id'] == current_plan_id), None)
    if not current_plan_details: 
        flash("Could not find your current plan details. Please contact support.", 'danger')
        session['user_plan'] = 'free' 
        return redirect(url_for('home'))
        
    return render_template('manage_subscription.html', plan=current_plan_details)

@app.route('/cancel_subscription', methods=['POST'])
@login_required
def cancel_subscription():
    current_plan_id = session.get('user_plan', 'free')
    if current_plan_id == 'free':
        flash("You do not have an active premium subscription to cancel.", 'warning')
        return redirect(url_for('home'))

    plan_being_cancelled = next((plan for plan in premium_plans_data if plan['id'] == current_plan_id), None)
    plan_name = plan_being_cancelled['name'] if plan_being_cancelled else "your premium plan"

    session['user_plan'] = 'free'
    flash(f"Your subscription to the {plan_name} has been cancelled. You are now on the Free plan.", 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
