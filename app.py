from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import os
import secrets
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
bcrypt = Bcrypt(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150), nullable=False)
    lastname = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    feedbacks = db.relationship('Feedback', backref='author', lazy=True)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def is_valid_password(password):
    return (
        len(password) >= 12 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'\d', password) and
        re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sorting')
def sorting_page():
    return render_template('sorting.html')

@app.route('/searching')
def searching_page():
    return render_template('searching.html')

# Configure Flask-Mail with Elastic Email SMTP settings
app.config.update(
    MAIL_SERVER='smtp.elasticemail.com',
    MAIL_PORT=2525,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='contactthessh@gmail.com',
    MAIL_PASSWORD='6EC602E55B61C26529531CEF3DBD6C50E855'
)

mail = Mail(app)

@app.route('/support', methods=['GET', 'POST'])
def support():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message_body = request.form['message']
        msg = Message(
            subject=f"New Enquiry from {name}",
            sender=app.config['MAIL_USERNAME'],
            recipients=["contactthessh@gmail.com"],
            reply_to=email
        )
        msg.html = f"""
            <h3>New Enquiry</h3>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone:</strong> {phone}</p>
            <p><strong>Message:</strong></p>
            <p>{message_body}</p>
        """
        try:
            mail.send(msg)
            flash("Message Sent Successfully", "success")
        except Exception as e:
            flash(f"Failed to send message: {str(e)}", "danger")
        
        return redirect(url_for('support'))
    
    return render_template('support.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        firstname = request.form.get('firstname').strip()
        lastname = request.form.get('lastname').strip()
        country = request.form.get('country').strip()
        gender = request.form.get('gender').strip()
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()
        confirm_password = request.form.get('confirm_password').strip()

        if not all([firstname, lastname, country, gender, username, email, password, confirm_password]):
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))

        if not is_valid_password(password):
            flash('Password must be at least 12 characters long and include uppercase, lowercase, number, and special character.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            firstname=firstname,
            lastname=lastname,
            country=country,
            gender=gender,
            username=username,
            email=email,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email').strip()
        password = request.form.get('password').strip()
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        if not user or not bcrypt.check_password_hash(user.password, password):
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        flash('Logged in successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        firstname = request.form.get('firstname').strip()
        lastname = request.form.get('lastname').strip()
        country = request.form.get('country').strip()
        gender = request.form.get('gender').strip()
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        old_password = request.form.get('old_password').strip()
        new_password = request.form.get('new_password').strip()
        confirm_new_password = request.form.get('confirm_new_password').strip()

        if not all([firstname, lastname, country, gender, username, email]):
            flash('First name, Last name, Country, Gender, Username, and Email cannot be empty.', 'danger')
            return redirect(url_for('profile'))

        if new_password or confirm_new_password:
            if not old_password:
                flash('Please enter your current password to update your password.', 'danger')
                return redirect(url_for('profile'))
            if not bcrypt.check_password_hash(current_user.password, old_password):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('profile'))
            if new_password != confirm_new_password:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('profile'))
            if not is_valid_password(new_password):
                flash('New password must be at least 12 characters long and include uppercase, lowercase, number, and special character.', 'danger')
                return redirect(url_for('profile'))
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        if User.query.filter(User.username == username, User.id != current_user.id).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('profile'))
        if User.query.filter(User.email == email, User.id != current_user.id).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('profile'))

        current_user.firstname = firstname
        current_user.lastname = lastname
        current_user.country = country
        current_user.gender = gender
        current_user.username = username
        current_user.email = email

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html')

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        content = request.form.get('content').strip()
        if not content:
            flash('Feedback cannot be empty.', 'danger')
            return redirect(url_for('feedback'))
        new_feedback = Feedback(content=content, author=current_user)
        db.session.add(new_feedback)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('feedback'))
    feedbacks = Feedback.query.filter_by(user_id=current_user.id).all()
    return render_template('feedback.html', feedbacks=feedbacks)

@app.route('/sort', methods=['POST'])
def sort_route():
    data = request.json
    array = data.get('array', [])
    algorithm = data.get('algorithm', '')
    ascending = data.get('ascending', True)

    if algorithm not in ['bubble', 'selection', 'insertion', 'quick', 'merge', 'heap', 'tim', 'shell']:
        return jsonify({'error': 'Invalid sorting algorithm'}), 400

    try:
        steps = []
        if algorithm == 'bubble':
            steps = bubble_sort(array, ascending)
        elif algorithm == 'selection':
            steps = selection_sort(array, ascending)
        elif algorithm == 'insertion':
            steps = insertion_sort(array, ascending)
        elif algorithm == 'quick':
            steps = quick_sort(array, ascending)
        elif algorithm == 'merge':
            steps = merge_sort(array, ascending)
        elif algorithm == 'heap':
            steps = heap_sort(array, ascending)
        elif algorithm == 'tim':
            steps = tim_sort(array, ascending)
        elif algorithm == 'shell':
            steps = shell_sort(array, ascending)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'steps': steps})

def bubble_sort(array, ascending=True):
    steps = []
    n = len(array)
    for i in range(n):
        for j in range(0, n-i-1):
            steps.append(([x for x in array], [j, j+1]))
            if (array[j] > array[j+1] and ascending) or (array[j] < array[j+1] and not ascending):
                array[j], array[j+1] = array[j+1], array[j]
                steps.append(([x for x in array], [j, j+1]))
    return steps

def selection_sort(array, ascending=True):
    steps = []
    n = len(array)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            steps.append(([x for x in array], [min_idx, j]))
            if (array[j] < array[min_idx] and ascending) or (array[j] > array[min_idx] and not ascending):
                min_idx = j
        if min_idx != i:
            array[i], array[min_idx] = array[min_idx], array[i]
            steps.append(([x for x in array], [i, min_idx]))
    return steps

def insertion_sort(array, ascending=True):
    steps = []
    for i in range(1, len(array)):
        key = array[i]
        j = i -1
        while j >=0 and ((array[j] > key and ascending) or (array[j] < key and not ascending)):
            steps.append(([x for x in array], [j, j+1]))
            array[j +1] = array[j]
            j -=1
        array[j +1] = key
        steps.append(([x for x in array], [j +1]))
    return steps

def quick_sort(array, ascending=True):
    steps = []
    def _quick_sort(arr, low, high):
        if low < high:
            pi = partition(arr, low, high)
            _quick_sort(arr, low, pi -1)
            _quick_sort(arr, pi +1, high)

    def partition(arr, low, high):
        pivot = arr[high]
        i = low -1
        for j in range(low, high):
            steps.append(([x for x in arr], [j, high]))
            if (arr[j] < pivot and ascending) or (arr[j] > pivot and not ascending):
                i +=1
                arr[i], arr[j] = arr[j], arr[i]
                steps.append(([x for x in arr], [i, j]))
        arr[i+1], arr[high] = arr[high], arr[i+1]
        steps.append(([x for x in arr], [i+1, high]))
        return i+1

    _quick_sort(array, 0, len(array)-1)
    return steps

def merge_sort(array, ascending=True):
    steps = []
    def _merge_sort(arr, l, r):
        if l < r:
            m = (l + r) //2
            _merge_sort(arr, l, m)
            _merge_sort(arr, m+1, r)
            merge(arr, l, m, r)

    def merge(arr, l, m, r):
        n1 = m -l +1
        n2 = r -m
        L = arr[l:m+1]
        R = arr[m+1:r+1]
        i = j =0
        k = l
        while i < n1 and j < n2:
            steps.append(([x for x in arr], [k]))
            if (L[i] <= R[j] and ascending) or (L[i] >= R[j] and not ascending):
                arr[k] = L[i]
                i +=1
            else:
                arr[k] = R[j]
                j +=1
            k +=1
            steps.append(([x for x in arr], [k-1]))
        while i < n1:
            arr[k] = L[i]
            steps.append(([x for x in arr], [k]))
            i +=1
            k +=1
            steps.append(([x for x in arr], [k-1]))
        while j < n2:
            arr[k] = R[j]
            steps.append(([x for x in arr], [k]))
            j +=1
            k +=1
            steps.append(([x for x in arr], [k-1]))
    
    _merge_sort(array, 0, len(array)-1)
    return steps

def heap_sort(array, ascending=True):
    steps = []
    n = len(array)

    def heapify(arr, n, i):
        largest_smallest = i
        l = 2 * i +1
        r = 2 * i +2
        if l < n:
            steps.append(([x for x in arr], [i, l]))
            if (arr[l] > arr[largest_smallest] and ascending) or (arr[l] < arr[largest_smallest] and not ascending):
                largest_smallest = l
        if r < n:
            steps.append(([x for x in arr], [largest_smallest, r]))
            if (arr[r] > arr[largest_smallest] and ascending) or (arr[r] < arr[largest_smallest] and not ascending):
                largest_smallest = r
        if largest_smallest != i:
            arr[i], arr[largest_smallest] = arr[largest_smallest], arr[i]
            steps.append(([x for x in arr], [i, largest_smallest]))
            heapify(arr, n, largest_smallest)

    for i in range(n//2 -1, -1, -1):
        heapify(array, n, i)
        
    for i in range(n-1, 0, -1):
        array[i], array[0] = array[0], array[i]
        steps.append(([x for x in array], [0, i]))
        heapify(array, i, 0)
    return steps

def tim_sort(array, ascending=True):
    steps = []
    min_run = 32
    def insertion_sort_tim(arr, left, right):
        for i in range(left + 1, right):
            key = arr[i]
            j = i - 1
            while j >= left and ((arr[j] > key and ascending) or (arr[j] < key and not ascending)):
                steps.append(([x for x in array], [j, j + 1]))
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
            steps.append(([x for x in array], [j + 1]))
    for start in range(0, len(array), min_run):
        end = min(start + min_run, len(array))
        insertion_sort_tim(array, start, end)
    size = min_run
    while size < len(array):
        for left in range(0, len(array), size * 2):
            mid = min(left + size, len(array))
            right = min((left + size * 2), len(array))
            if mid < right:
                merged = merge(array[left:mid], array[mid:right], ascending)
                array[left:right] = merged
                steps.append(([x for x in array], list(range(left, right))))
        size *= 2
    return steps

def merge(left, right, ascending=True):
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if (ascending and left[i] <= right[j]) or (not ascending and left[i] >= right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged

def shell_sort(array, ascending=True):
    steps = []
    n = len(array)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = array[i]
            j = i
            while j >= gap and ((ascending and array[j - gap] > temp) or (not ascending and array[j - gap] < temp)):
                steps.append(([x for x in array], [j - gap, j]))
                array[j] = array[j - gap]
                j -= gap
            array[j] = temp
            steps.append(([x for x in array], [j]))
        gap //= 2
    return steps

@app.route('/bubblesort')
def bubblesort():
    return render_template('bubblesort.html')

@app.route('/selectionsort')
def selectionsort():
    return render_template('selectionsort.html')

@app.route('/insertionsort')
def insertionsort():
    return render_template('insertionsort.html')

@app.route('/quicksort')
def quicksort():
    return render_template('quicksort.html')

@app.route('/mergesort')
def mergesort():
    return render_template('mergesort.html')

@app.route('/heapsort')
def heapsort():
    return render_template('heapsort.html')

@app.route('/timsort')
def timsort():
    return render_template('timsort.html')

@app.route('/shellsort')
def shellsort():
    return render_template('shellsort.html')

@app.route('/binarysearch')
def binarysearch():
    return render_template('binarysearch.html')

@app.route('/linearsearch')
def linearsearch():
    return render_template('linearsearch.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

if __name__ == '__main__':
    app.run(debug=True)