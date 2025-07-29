from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from models import users, events
import os
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["UPLOAD_FOLDER"] = "static/uploads"

bcrypt = Bcrypt(app)

# ---- Home Page ----
@app.route('/')
def home():
    if 'username' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

# ---- Register ----
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        role = request.form['role']  # "admin" or "user"

        if users.find_one({"username": username}):
            flash("Username already exists!", "danger")
        else:
            users.insert_one({"username": username, "password": password, "role": role})
            flash("Registered successfully!", "success")
            return redirect(url_for('login'))

    return render_template('register.html')

# ---- Login ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.find_one({"username": username})

        if user and bcrypt.check_password_hash(user['password'], password):
            session['username'] = username
            session['role'] = user['role']
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials!", "danger")

    return render_template('login.html')

# ---- Logout ----
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out!", "success")
    return redirect(url_for('login'))

# ---- Admin Dashboard ----
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    all_events = list(events.find())
    return render_template('admin_dashboard.html', events=all_events)

# ---- Add Event ----
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date_time = request.form['date_time']
        location = request.form['location']
        image = request.files['image']

        if image:
            filename = secure_filename(image.filename)
            os.path.join(app.config["UPLOAD_FOLDER"], filename)
        else:
            filename = "default.jpg"

        event_data = {
            "title": title,
            "description": description,
            "date_time": date_time,
            "location": location,
            "image": filename
        }
        events.insert_one(event_data)
        flash("Event added successfully!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('event_form.html')

# ---- Edit Event ----
@app.route('/edit_event/<event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    event = events.find_one({"_id": ObjectId(event_id)}) # type: ignore

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date_time = request.form['date_time']
        location = request.form['location']
        image = request.files['image']

        filename = event.get('image', 'default.jpg')  # Safe fallback
        if image:
             filename = secure_filename(image.filename)
             image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

          
  
        else:
            filename = event['image_filename']

        events.update_one({"_id": ObjectId(event_id)}, {"$set": {
            "title": title,
            "description": description,
            "date_time": date_time,
            "location": location,
            "image": filename
        }})
        flash("Event updated!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('event_form.html', event=event)

# ---- Delete Event ----
@app.route('/delete_event/<event_id>', methods=['GET', 'POST'])
def delete_event(event_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    events.delete_one({"_id": ObjectId(event_id)}) # type: ignore
    flash("Event deleted!", "success")
    return redirect(url_for('admin_dashboard'))
    try:
       result = events.delete_one({"_id": ObjectId(event_id)})
       print("Deleted:", result.deleted_count)
    except Exception as e:
       print("Error while deleting event:", e)

# ---- User Dashboard ----
@app.route('/user_dashboard')
def user_dashboard():
    all_events = list(events.find())
    return render_template('user_dashboard.html', events=all_events)

if __name__ == '__main__':
    app.run(debug=True)
