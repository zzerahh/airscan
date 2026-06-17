# AirScan Inventory Management System

A secure inventory management web application built with Django for the Secure Software Development (IKB 21503) course at UniKL MIIT.

## 1. Project Description

AirScan is a role-based inventory management system. Users can register, log in, and manage inventory items (create, read, update, delete). Administrators can view all items and an audit log, while normal users can only manage their own items. The application was built following secure coding practices aligned with the OWASP Top 10.

## 2. Installation Steps

```bash
# Clone the repository 
git clone https://github.com/zzerahh/airscan.git 
cd airscan 
pip install django python-dotenv bcrypt

```

## 3. Security Features Summary

- Input validation using whitelist rules (Django validators + regex)
- SQL injection prevention via the Django ORM (parameterized queries)
- XSS prevention through Django template auto-escaping
- CSRF protection on all forms
- Passwords hashed with bcrypt; minimum 12-character password policy
- Secure sessions: 30-minute timeout, HttpOnly / Secure / SameSite cookies
- Role-Based Access Control (Administrator vs Normal User)
- IDOR prevention (users can only access their own items)
- Security headers: Content-Security-Policy, hidden server header, CORS hardening
- Audit logging of logins, logouts, failed attempts, and CRUD actions

## 4. How to Run the App

```bash
python manage.py runserver
```

Then open **http://127.0.0.1:8000** in a browser. Log in as the administrator created above, or register a new normal user.

## 5. Dependencies

```
Django>=5.2.8
python-dotenv>=1.2.2
bcrypt>=4.1.2
```

Python 3.10 or newer is required.

## 6. Screenshots

Login Page <img width="1554" height="808" alt="image" src="https://github.com/user-attachments/assets/b97e5a01-8b15-44c9-8af3-3102223fb787" />
Dashboard <img width="1547" height="795" alt="image" src="https://github.com/user-attachments/assets/7463d718-bde0-4ea6-93f1-6a96a7ec9ac9" />
Inventory List <img width="1578" height="757" alt="image" src="https://github.com/user-attachments/assets/c280c1ac-ea3b-4d49-a3cc-4716e8942783" />
Audit Log <img width="1542" height="820" alt="image" src="https://github.com/user-attachments/assets/0860b1fe-1c90-49d9-b4d7-90a98e355dcc" />
