# EduManage - Class Management System

A Django web application for managing students, teachers, classes, and enrollments using Microsoft SQL Server.

---

## Quick Start

### Prerequisites

- **Python 3.12+**
- **SQL Server** with ODBC Driver 17
- **Git**

### Installation

```bash
# Clone & enter directory
git clone https://github.com/dqvuong2111/ClassManagementProject.git
cd ClassManagementWebsite

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Database Setup

1. **Create a SQL Server database** named `ClassManagementWebsite`

2. **Update `ClassManagementWebsite/settings.py`** with your credentials:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'mssql',
           'NAME': 'ClassManagementWebsite',
           'USER': 'your_username',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '1433',
           'OPTIONS': {
               'driver': 'ODBC Driver 17 for SQL Server',
           },
       }
   }
   ```

3. **Run migrations and constraints:**
   ```bash
   python manage.py migrate
   ```

4. **(Optional) Load SQL scripts for additional constraints and sample data:**
   ```sql
   -- Run in SQL Server Management Studio
   -- First: setup_constraints.sql (database constraints & triggers)
   -- Then: seed_data.sql (sample teachers, students, classes)
   ```

### Run the Server

```bash
python manage.py runserver
```

**Access the app at:** http://127.0.0.1:8000/

---

## Default Test Accounts

| Role    | Username   | Password    |
|---------|------------|-------------|
| Admin   | admin      | admin123    |
| Teacher | teacher1   | teacher123  |
| Student | student1   | student123  |

---

## Project Structure

```
ClassManagementWebsite/
├── ClassManagementWebsite/    # Django project settings
│   ├── settings.py            # Database & app configuration
│   └── urls.py                # Root URL routing
├── accounts/                  # Authentication (login/signup)
├── core/                      # Data models (Student, Teacher, Class, etc.)
├── dashboard/                 # Admin, Teacher, Student dashboards
├── templates/                 # Global HTML templates
├── static/                    # CSS, JS, images
├── media/                     # User uploads
├── setup_constraints.sql      # SQL Server constraints & triggers
├── seed_data.sql              # Sample data for testing
└── requirements.txt           # Python dependencies
```

---

## Features by Role

### Admin
- Manage students, teachers, classes
- Handle enrollment requests
- Enter grades and view statistics

### Teacher
- View assigned classes
- Create assignments & materials
- QR code attendance
- Communicate with students

### Student
- Browse and enroll in courses
- View schedule and grades
- Submit assignments
- Give course feedback

---

## Tech Stack

| Layer     | Technology             |
|-----------|------------------------|
| Backend   | Django 5.x             |
| Database  | Microsoft SQL Server   |
| Frontend  | HTML, Tailwind CSS, JS |
| Icons     | Lucide Icons           |

---

## Troubleshooting

**ODBC Driver Error:**  
Download [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

**Connection Failed:**  
Ensure SQL Server is running and TCP/IP is enabled in SQL Server Configuration Manager.

**Migration Issues:**  
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.
