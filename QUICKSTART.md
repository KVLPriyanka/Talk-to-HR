# HR Portal - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd "c:\Users\udayk\Downloads\HR_Portal\HR\HR"
pip install -r requirements.txt
```

### Step 2: Configure MySQL (if needed)
Edit `app/config.py` line 10-14:
```python
MYSQL_HOST = 'localhost'      # Your MySQL host
MYSQL_USER = 'root'            # Your MySQL username
MYSQL_PASSWORD = 'root'        # Your MySQL password
MYSQL_DATABASE = 'hr_portal'
MYSQL_PORT = 3306
```

### Step 3: Run Application
```bash
python app.py
```

### Step 4: Open in Browser
Navigate to: **http://localhost:5000**

---

## 🔑 Default Login

**HR Account:**
- Username: `hr@portal.com`
- Password: `hrpass123`

**Test Applicant (Create via Sign Up):**
- Fill registration form with 10-digit mobile number

---

## 📁 Project Files

| File | Purpose |
|------|---------|
| `app.py` | Main application entry point |
| `app/__init__.py` | Flask app factory |
| `app/config.py` | Configuration settings |
| `app/models.py` | Database models |
| `app/routes.py` | API endpoints |
| `templates/index.html` | Login/Register page |
| `templates/dashboard.html` | Applicant dashboard |
| `templates/hr-dashboard.html` | HR dashboard |
| `static/css/style.css` | Styling |
| `static/js/app.js` | JavaScript utilities |

---

## ✨ Features Overview

### For Applicants
- Register with Email, Name, Mobile, Employee ID
- Submit Feedback, Complaints, or Suggestions
- Track submission status
- View HR responses

### For HR
- See all submitted tickets
- Update ticket status
- Add response notes
- Manage user access (activate/deactivate)

---

## 🔗 API Endpoints

```
POST   /api/auth/login              Login
POST   /api/auth/logout             Logout
POST   /api/auth/register           Register new user
POST   /api/auth/reset-password     Reset password
GET    /api/auth/current            Get logged-in user

GET    /api/tickets                 Get user tickets (Applicant)
POST   /api/tickets                 Create ticket (Applicant)
GET    /api/tickets/<id>            Get ticket details

GET    /api/tickets/all             Get all tickets (HR only)
PUT    /api/tickets/<id>            Update ticket (HR only)

GET    /api/users                   Get all users (HR only)
POST   /api/users/<username>/toggle Toggle user status (HR only)
```

---

## 🎯 Common Tasks

### Create New Applicant Account
1. Click "Sign Up" on login page
2. Enter: Name, Email, 10-digit Mobile, Employee ID, Password
3. Click "Create Account"
4. Login with credentials

### Submit Ticket (Applicant)
1. Login to account
2. Click "Submit Request"
3. Select Type: Feedback/Complaint/Suggestion
4. Enter Subject and Description
5. Click "Submit Request"

### Review & Update Ticket (HR)
1. Login as HR (hr@portal.com)
2. Click on ticket in list
3. Update Status
4. Add HR Response
5. Click "Update Ticket"

### Deactivate User (HR)
1. Go to "Manage Users"
2. Find user in list
3. Click "Deactivate" button
4. User cannot login until reactivated

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 5000 in use | Kill process or change port in app.py |
| MySQL connection error | Check DB credentials in app/config.py |
| Database doesn't exist | App creates it automatically on first run |
| Missing dependencies | Run: `pip install -r requirements.txt` |
| Login not working | Verify MySQL is running |
| Import errors | Update Python to 3.8+ and reinstall requirements |

---

## 📊 Database Location

After first run, the following are created automatically:
- Database: `hr_portal`
- Tables: `users`, `tickets`

---

## 🌐 Access Application

| Page | URL | Role |
|------|-----|------|
| Login/Register | http://localhost:5000 | Public |
| Applicant Dashboard | http://localhost:5000/dashboard | Applicant |
| HR Dashboard | http://localhost:5000/hr-dashboard | HR |

---

## ⚙️ System Requirements

- **Python**: 3.8+
- **MySQL**: 5.7+ or 8.0+
- **RAM**: 512 MB minimum
- **Disk**: 100 MB free space

---

## 🚀 Production Deployment

Before deploying to production:

1. **Change SECRET_KEY** in `app/config.py`
2. **Set FLASK_ENV** to 'production'
3. **Enable HTTPS** with SSL certificate
4. **Use production WSGI** (Gunicorn, uWSGI)
5. **Set strong MySQL password**
6. **Enable database backups**

---

## 📞 Support

For issues:
1. Check README.md for detailed documentation
2. Verify all dependencies installed
3. Check MySQL connection settings
4. Review application logs

---

**Ready to use! Happy coding! 🎉**
