# Health Chatbot - Medical AI Assistant 🏥🤖

A comprehensive Flask-based healthcare application that provides medical consultation, doctor appointment booking, X-ray bone fracture detection, and AI-powered medical chatbot assistance.

---

## 🌟 Features

### 👥 User Authentication
- **User Registration** - Create new account with email, password, name, and phone
- **User Login** - Secure login with session management
- **Doctor Registration & Login** - Separate portal for healthcare professionals
- **Session Management** - Persistent sessions with 7-day expiration

### 👨‍⚕️ Doctor Management
- **Doctor Directory** - Browse all registered doctors with specializations
- **View Doctors List** - See doctor details (name, email, phone, specialization)
- **Book Appointments** - Schedule appointments with doctors
- **Appointment Conflict Detection** - Prevents double-bookings within 30-minute windows
- **View Appointments** - Track all booked appointments with status

### 🤖 AI Medical Chatbot
- **Mistral AI Integration** - Advanced medical chatbot for health queries
- **Smart Intent Detection** - Recognizes appointment and medicine queries
- **Medical Knowledge** - Provides information on health topics
- **Medicine Recommendations** - Suggests pharmacy links (PharMEasy integration)
- **Doctor Booking Suggestions** - Directs users to book appointments

### 📸 X-Ray Analysis
- **Bone Fracture Detection** - YOLOv8 model for detecting bone fractures
- **Image Processing** - Converts X-ray images to multiple formats:
  - Grayscale conversion
  - Thresholding analysis
  - Binary image processing
  - Fracture detection with bounding boxes
- **Multiple Fracture Types** - Detects:
  - Elbow fractures
  - Finger fractures
  - Forearm fractures
  - Humerus fractures
  - Shoulder fractures
  - Wrist fractures

### 📊 Dashboard
- **User Home** - Personalized user dashboard
- **Navigation** - Easy access to all features
- **Logout** - Secure session termination

---

## 🛠️ Technologies Used

### Backend
- **Flask** - Python web framework
- **SQLite** - Database (lightweight, no external server needed)
- **Flask-Session** - Session management

### AI & ML
- **Mistral AI API** - Medical chatbot and resume analysis
- **YOLOv8** - Object detection for X-ray analysis
- **OpenCV** - Image processing and manipulation
- **PyTorch** - Deep learning framework

### Frontend
- **HTML5** - Markup
- **Bootstrap 5** - Responsive UI framework
- **jQuery** - JavaScript library
- **DataTables** - Data table management

### APIs
- **Mistral AI** - Chatbot intelligence
- **YouTube Data API** - Tutorial recommendations
- **Adzuna Job API** - Job search (if configured)

---

## 📋 Project Structure

```
ChatBot/
├── app.py                          # Main Flask application
├── predict.py                      # YOLOv8 fracture detection model
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── healthbotdb.sql                # Database schema (MySQL alternative)
├── bonefracture_yolov8.pt         # Pre-trained YOLO model
│
├── templates/                      # HTML templates
│   ├── index.html                 # Home page
│   ├── login.html                 # User login
│   ├── register.html              # User registration
│   ├── doctor_login.html          # Doctor login
│   ├── doctor_register.html       # Doctor registration
│   ├── enquiry.html               # X-ray upload & analysis
│   ├── doctors.html               # Doctor directory & bookings
│   ├── doctor_appointments.html   # Doctor's appointment view
│   └── error.html                 # Error page
│
├── static/                         # Static assets
│   ├── css/
│   │   ├── bootstrap.css          # Bootstrap framework
│   │   └── custom.css             # Custom styles
│   ├── js/
│   │   ├── bootstrap.js           # Bootstrap JavaScript
│   │   └── jquery.js              # jQuery library
│   ├── images/                    # Image assets
│   ├── uploads/                   # User-uploaded X-ray images
│   └── processed/                 # Processed X-ray analysis images
│
└── venv/                           # Virtual environment (auto-created)
```

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.8+** installed
- **pip** package manager
- **Git** for cloning

### Step 1: Clone Repository
```bash
cd /Users/darshu/GitHub/HealthChatbot25/ChatBot
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Database
The application uses **SQLite by default** (no external database server needed).

**If using MySQL instead:**
1. Start MySQL server
2. Import schema: `mysql -u root -p healthbotdb < healthbotdb.sql`
3. Update database connection in `app.py`

### Step 5: Configure API Keys
Edit `app.py` and update:

```python
# Mistral AI API Key
mistral_api_key = "YOUR_MISTRAL_API_KEY"

# YouTube API Key (optional video recommendations)
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
```

Get API keys from:
- **Mistral AI**: https://console.mistral.ai/
- **YouTube**: https://console.cloud.google.com/

---

## 🏃 Running the Application

### Start Flask Server
```bash
source venv/bin/activate
python3 app.py
```

Server will start at: **http://127.0.0.1:5000**

### Debug Mode
Flask runs in **debug mode** by default with auto-reload on code changes.

---

## 📖 Usage Guide

### 1. User Registration
1. Navigate to **http://localhost:5000/register**
2. Fill in: Name, Email, Password, Phone
3. Click Register
4. Login with credentials

### 2. Doctor Registration
1. Navigate to **http://localhost:5000/doctor_register**
2. Fill in: Name, Email, Password, Phone, Specialization
3. Click Register
4. Login at **http://localhost:5000/doctor_login**

### 3. Upload X-Ray for Analysis
1. Login as user
2. Click **"Detect Fracture"** in navbar
3. Upload PNG/JPG X-ray image
4. View results with:
   - Grayscale version
   - Thresholded image
   - Binary image
   - Fracture detection with annotations

### 4. Book Doctor Appointment
1. Login as user
2. Click **"Doctors"** in navbar
3. View available doctors
4. Click **"Book Appointment"**
5. Select date and time
6. Confirm booking

### 5. Chat with Medical Bot
1. Login as user
2. Open any page with chatbot button (floating icon)
3. Ask health-related questions
4. Bot provides medical information
5. Special keywords trigger:
   - **"appointment"** → Shows doctor booking link
   - **"medicine"** → Shows pharmacy link

### 6. Doctor Dashboard
1. Login as doctor
2. View all patient appointments
3. Accept or reject appointments
4. Track appointment history

---

## 🔑 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET/POST | `/register` | User registration |
| GET/POST | `/login` | User login |
| GET/POST | `/doctor_register` | Doctor registration |
| GET/POST | `/doctor_login` | Doctor login |
| GET/POST | `/enquiry` | X-ray upload & analysis |
| GET | `/doctors` | List doctors & bookings |
| POST | `/book_appointment` | Book appointment |
| GET/POST | `/chatbot` | AI chatbot endpoint |
| GET | `/doctor_appointments` | Doctor's appointments |
| POST | `/update_appointment_status/<id>` | Accept/reject appointment |
| GET | `/logout` | User logout |
| GET | `/doctor_logout` | Doctor logout |

---

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  uid VARCHAR(255) UNIQUE,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  password VARCHAR(255),
  phone VARCHAR(20)
);
```

### Doctors Table
```sql
CREATE TABLE doctors (
  id INTEGER PRIMARY KEY,
  uid VARCHAR(255) UNIQUE,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  password VARCHAR(255),
  phone VARCHAR(20),
  specialization VARCHAR(255)
);
```

### Appointments Table
```sql
CREATE TABLE appointments (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  doctor_id INTEGER,
  appointment_date DATE,
  appointment_time TIME,
  status VARCHAR(50) DEFAULT 'pending',
  FOREIGN KEY(user_id) REFERENCES users(id),
  FOREIGN KEY(doctor_id) REFERENCES doctors(id)
);
```

---

## ⚙️ Configuration

### Database Connection
**SQLite (Default - No Setup Needed)**
```python
# Auto-creates database.db in project root
```

**MySQL (Alternative)**
```python
link = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='healthbotdb'
)
```

### Session Configuration
```python
app.secret_key = "Qazwsx@123"  # Change in production!
app.permanent_session_lifetime = timedelta(days=7)
```

### Upload Configuration
```python
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
```

---

## 🤖 AI Models

### YOLOv8 Fracture Detection
- **Model File**: `bonefracture_yolov8.pt`
- **Input**: X-ray images (PNG/JPG)
- **Output**: Annotated image with fracture locations and confidence scores
- **Classes**: 7 fracture types with color-coded bounding boxes

### Mistral AI Chatbot
- **Model**: `mistral-large-latest`
- **System Prompt**: Medical knowledge base specialized in bone health
- **Input**: User health questions
- **Output**: Medical information and recommendations

---

## 🐛 Troubleshooting

### Issue: Database Connection Error
**Solution**: 
- Ensure MySQL is running (if using MySQL)
- Check database credentials in `app.py`
- Or switch to SQLite (default)

```bash
# Kill existing MySQL
pkill mysqld

# Start MySQL
mysqld_safe --skip-grant-tables &
```

### Issue: Port 5000 Already in Use
**Solution**:
```bash
# Kill process using port 5000
lsof -i :5000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# Or run on different port
python3 app.py --port 5001
```

### Issue: Mistral API Errors
**Solution**:
- Verify API key is correct
- Check API quota at https://console.mistral.ai/
- Ensure internet connection is active

### Issue: X-Ray Model Not Found
**Solution**:
- Ensure `bonefracture_yolov8.pt` is in project root
- Re-download model if corrupted
- Check file permissions

---

## 🔒 Security Notes

⚠️ **Important for Production:**
1. Change `app.secret_key` to a strong random string
2. Never commit API keys to Git
3. Use environment variables for sensitive data:
   ```python
   import os
   mistral_api_key = os.getenv('MISTRAL_API_KEY')
   ```
4. Implement password hashing (use `werkzeug.security`)
5. Add HTTPS/SSL certificates
6. Implement rate limiting for APIs
7. Add input validation and sanitization

---

## 📦 Dependencies

See `requirements.txt` for complete list:
- Flask 3.1.3
- mysql-connector-python 9.6.0
- opencv-python (latest)
- torch (2.0+)
- torchvision (0.15+)
- ultralytics (8.0+)
- mistralai 2.2.0
- Werkzeug 3.1.7
- Pillow (7.1.2+)

---

## 📝 License

This project is for educational purposes.

---

## 👨‍💻 Author

**Darshu** - HealthChatbot25 Project

---

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review error messages in console
3. Verify all dependencies are installed
4. Ensure API keys are configured

---

## 🚀 Future Enhancements

- [ ] Electronic health records (EHR) integration
- [ ] Real-time video consultations
- [ ] Prescription management
- [ ] Medical report generation
- [ ] Mobile app (React Native/Flutter)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Insurance integration
- [ ] Payment gateway
- [ ] Telemedicine features

---

**Last Updated**: April 1, 2026

**Status**: ✅ Fully Functional
