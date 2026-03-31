from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
import random, string, os, sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from mistralai.client import Mistral
from predict import process_xray

app = Flask(__name__)
app.secret_key = "Qazwsx@123"

# Configure upload settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
medlink=""" <a href="https://pharmeasy.in/"> Order Medicine Here </a>"""
doclink=""" <a href=" http://127.0.0.1:5000/doctors"> Doctors </a> """

# Database setup - SQLite
DB_PATH = 'healthbot.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT UNIQUE,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT
    )
    ''')
    
    # Create doctors table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT UNIQUE,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        specialization TEXT
    )
    ''')
    
    # Create appointments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date DATE NOT NULL,
        appointment_time TIME NOT NULL,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ SQLite database initialized")

# Initialize database on startup
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('enquiry'))

    if request.method == "GET":
        return render_template('login.html')
    else:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            email = request.form["email"]
            password = request.form["password"]
            cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user['id']
                session['user'] = user['email']
                session['username'] = user['name']
                return redirect(url_for('enquiry'))
            else:
                return render_template('login.html', error='Invalid email or password')

        except Exception as e:
            return render_template('login.html', error=str(e))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect(url_for('enquiry'))

    if request.method == "GET":
        return render_template('register.html')
    else:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            phone = request.form.get("phone", "").strip()
            
            # Validate inputs
            if not all([name, email, password, phone]):
                return render_template('register.html', error='All fields are required')
            
            uid = 'uid_'+''.join(random.choices(string.ascii_letters + string.digits, k=10))

            # Check if email exists
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user:
                conn.close()
                return render_template('register.html', exists='Email already exists')
            else:
                cursor.execute("INSERT INTO users (uid, name, email, password, phone) VALUES (?, ?, ?, ?, ?)",
                             (uid, name, email, password, phone))
                conn.commit()
                conn.close()
                print(f"✓ User registered successfully: {email}")
                return render_template('register.html', success='Registration successful')

        except Exception as e:
            error_str = str(e)
            print(f"✗ Registration error: {error_str}")
            return render_template('register.html', error=f'Registration failed: {error_str}')

@app.route('/doctor_register', methods=['GET', 'POST'])
def doctor_register():
    if 'doctor_user' in session:
        return redirect(url_for('doctor_appointments'))

    if request.method == "GET":
        return render_template('doctor_register.html')
    else:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            phone = request.form.get("phone", "").strip()
            specialization = request.form.get("specialization", "").strip()
            
            if not all([name, email, password, phone, specialization]):
                return render_template('doctor_register.html', error='All fields are required')
            
            uid = 'doc_uid_'+''.join(random.choices(string.ascii_letters + string.digits, k=10))

            cursor.execute("SELECT * FROM doctors WHERE email = ?", (email,))
            doctor = cursor.fetchone()

            if doctor:
                conn.close()
                return render_template('doctor_register.html', exists='Email already exists')
            else:
                cursor.execute("INSERT INTO doctors (uid, name, email, password, phone, specialization) VALUES (?, ?, ?, ?, ?, ?)",
                             (uid, name, email, password, phone, specialization))
                conn.commit()
                conn.close()
                return render_template('doctor_register.html', success='Registration successful')

        except Exception as e:
            return render_template('doctor_register.html', error=f'Registration failed: {str(e)}')

@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    if 'doctor_user' in session:
        return redirect(url_for('doctor_appointments'))

    if request.method == "GET":
        return render_template('doctor_login.html')
    else:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            email = request.form["email"]
            password = request.form["password"]
            cursor.execute("SELECT * FROM doctors WHERE email = ? AND password = ?", (email, password))
            doctor = cursor.fetchone()
            conn.close()
            
            if doctor:
                session['doctor_user_id'] = doctor['id']
                session['doctor_user'] = doctor['email']
                session['doctor_username'] = doctor['name']
                return redirect(url_for('doctor_appointments'))
            else:
                return render_template('doctor_login.html', error='Invalid email or password')

        except Exception as e:
            return render_template('doctor_login.html', error=str(e))

@app.route('/enquiry', methods=['GET', 'POST'])
def enquiry():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "GET":
        return render_template('enquiry.html')

    if 'file' not in request.files:
        return render_template('enquiry.html', error='No file uploaded')

    file = request.files['file']
    if file.filename == '':
        return render_template('enquiry.html', error='No file selected')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)

        try:
            processed_image, grayscale_image, thresholded_image, binary_image, result = process_xray(filepath)
            if processed_image:
                return render_template('enquiry.html',
                                     original_image=filepath,
                                     grayscale_image=grayscale_image,
                                     thresholded_image=thresholded_image,
                                     binary_image=binary_image,
                                     processed_image=processed_image,
                                     result=result)
            else:
                return render_template('enquiry.html', error='Error processing image')
        except Exception as e:
            return render_template('enquiry.html', error=str(e))

    return render_template('enquiry.html', error='Invalid file type')

@app.route('/doctors')
def doctors():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM doctors")
        doctors_list = [dict(row) for row in cursor.fetchall()]

        user_id = session['user_id']
        cursor.execute("""
            SELECT a.*, d.name
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.user_id = ?
        """, (user_id,))
        user_appointments = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return render_template('doctors.html', doctors=doctors_list, user_appointments=user_appointments)

    except Exception as e:
        return render_template('doctors.html', error=str(e), doctors=[], user_appointments=[])

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    if 'user' not in session:
        flash('Please login to book an appointment', 'danger')
        return redirect(url_for('login'))

    try:
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        user_id = session.get('user_id')

        if not all([doctor_id, appointment_date, appointment_time]):
            flash('All fields are required', 'danger')
            return redirect(url_for('doctors'))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for conflicts (appointments within 30 minutes)
        cursor.execute("""
            SELECT COUNT(*) as count FROM appointments
            WHERE doctor_id = ? AND appointment_date = ?
            AND datetime(appointment_time) BETWEEN 
                datetime(?) AND datetime(?, '+30 minutes')
        """, (doctor_id, appointment_date, appointment_time, appointment_time))
        
        result = cursor.fetchone()
        
        if result and result['count'] > 0:
            flash('Doctor has an appointment within 30 minutes of this time', 'danger')
            conn.close()
            return redirect(url_for('doctors'))

        # Insert appointment
        cursor.execute("""
            INSERT INTO appointments (user_id, doctor_id, appointment_date, appointment_time, status)
            VALUES (?, ?, ?, ?, 'pending')
        """, (user_id, doctor_id, appointment_date, appointment_time))
        
        conn.commit()
        conn.close()
        
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('doctors'))

    except Exception as e:
        flash(f'Error booking appointment: {str(e)}', 'danger')
        return redirect(url_for('doctors'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/doctor_logout')
def doctor_logout():
    session.pop('doctor_user', None)
    session.pop('doctor_username', None)
    session.pop('doctor_user_id', None)
    return redirect(url_for('index'))

@app.route('/chatbot', methods=['POST'])
def chatbot():
    if 'user' not in session and 'doctor_user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    appointment_keywords = ['appointment', 'doctor appointment', 'book doctor', 'see doctor', 'consult doctor', 'schedule appointment']
    if any(keyword in user_message.lower() for keyword in appointment_keywords):
        return jsonify({"response": "You can book a doctor appointment through our system. Book Doctor Here." + doclink})

    medicine_keywords = ['buy medicine', 'purchase medicine', 'order medicine', 'pharmacy', 'medication']
    if any(keyword in user_message.lower() for keyword in medicine_keywords):
        return jsonify({"response": "For purchasing medicines, I recommend using our partner pharmacy service. Book medicine here " + medlink})

    api_key = "WTuMOibXWmpTqjvscYHSaaCOjjXCakkJ"
    model = "mistral-large-latest"

    try:
        client = Mistral(api_key=api_key)
        messages = [
            {"role": "system", "content": "You are a medical chatbot. Provide information and answer questions related to human health and medical topics. Do not answer questions outside of this domain."},
            {"role": "user", "content": user_message}
        ]
        chat_response = client.chat.complete(model=model, messages=messages)
        bot_response = chat_response.choices[0].message.content
        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"error": f"Chatbot error: {str(e)}"}), 500

@app.route('/doctor_appointments')
def doctor_appointments():
    if 'doctor_user_id' not in session:
        return redirect(url_for('doctor_login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        doctor_id = session['doctor_user_id']
        
        cursor.execute("""
            SELECT a.*, u.name
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.doctor_id = ?
            ORDER BY a.appointment_date, a.appointment_time
        """, (doctor_id,))
        doctor_appointments_list = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return render_template('doctor_appointments.html', doctor_appointments=doctor_appointments_list)

    except Exception as e:
        return render_template('doctor_appointments.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
