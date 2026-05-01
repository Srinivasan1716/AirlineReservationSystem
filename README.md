<div align="center">

# ✈️ Airline Reservation System

### A Full-Stack Flight Booking Web Application Built with Python & Flask

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Razorpay](https://img.shields.io/badge/Razorpay-Payment_API-02042B?style=for-the-badge&logo=razorpay&logoColor=white)](https://razorpay.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## 📌 Project Title & Description

**Airline Reservation System** is a production-oriented web application that digitizes the end-to-end flight booking lifecycle — from flight discovery and seat selection to payment processing and booking management. Built on a modular Flask architecture, it demonstrates real-world software engineering practices including layered data access, form validation, payment gateway integration, transactional email delivery, and role-based access control.

---

## 🎯 Problem Statement / Objective

Traditional airline ticketing involves fragmented workflows, manual seat allocation, and error-prone booking confirmations. This system addresses those challenges by providing:

- A **unified digital platform** for passengers to search, book, and manage flights
- **Real-time seat availability** enforcement with transactional integrity
- **Secure online payment** via Razorpay with signature verification
- **Automated email notifications** for booking confirmations and cancellations
- An **admin interface** for fleet and booking management

The objective is to deliver a scalable, maintainable, and extensible reservation system that mirrors the architecture of commercial airline portals.

---

## ✨ Features

### Passenger-Facing
| Feature | Description |
|---|---|
| 🔐 User Authentication | Secure registration, login, and logout with hashed passwords (Werkzeug) |
| 🔍 Flight Search | Search by origin, destination, date, and number of passengers with validation |
| 🛫 Flight Details | View seat availability, pricing, route, duration, and aircraft type |
| 🪑 Seat Selection | Interactive seat map with First Class (rows 1–2), Business (rows 3–10), and Economy (rows 11+) class tiers |
| 👥 Multi-Passenger Booking | Book for up to 9 passengers per transaction with per-passenger form validation |
| 💳 Payment Integration | Razorpay payment gateway with server-side signature verification |
| 📧 Email Notifications | Automated booking confirmation and cancellation emails via SMTP |
| 🎫 Booking Management | View, track, and cancel reservations with 6-character unique booking references |
| 🏆 Frequent Flyer Points | Points system allowing balance redemption during checkout |
| 🗺️ Travel Recommendations | Budget- and season-aware destination recommendation engine |
| 👤 User Profile | Personal dashboard with booking history and points balance |

### Admin-Facing
| Feature | Description |
|---|---|
| 📊 Admin Dashboard | Aggregate stats: total flights, active bookings, total users |
| ✈️ Flight CRUD | Add, edit, and update flights with full input validation |
| 📋 Booking Overview | View all recent bookings with user and flight cross-references |
| 🔎 Flight Search & Filter | Filter flights by number, origin, destination, and status |

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Language** | Python | 3.10+ | Core application language |
| **Web Framework** | Flask | 3.1.0 | HTTP routing, request handling, and templating |
| **ORM** | Flask-SQLAlchemy | 3.1.1 | Database abstraction layer |
| **Database** | SQLite | — | Relational data persistence |
| **Authentication** | Flask-Login | 0.6.3 | Session-based user authentication |
| **Forms & Validation** | Flask-WTF / WTForms | 1.2.2 / 3.2.1 | Form rendering, CSRF protection, field validation |
| **Payment Gateway** | Razorpay SDK | 1.4.2 | Payment order creation and signature verification |
| **Email** | Flask-Mail | 0.10.0 | SMTP transactional email delivery |
| **Templating** | Jinja2 | 3.1.6 | Server-side HTML rendering |
| **Frontend** | Bootstrap 5 | CDN | Responsive UI components and layout |
| **Security** | Werkzeug | 3.1.3 | Password hashing (PBKDF2-SHA256) |
| **Configuration** | python-dotenv | 1.1.0 | Environment variable management |
| **Dependency Manager** | pip / uv | — | Package management |

---

## 🏗️ System Architecture / Workflow

```
┌──────────────┐       HTTP        ┌─────────────────────────────────────────┐
│   Browser    │◄─────────────────►│           Flask Application             │
│  (Bootstrap) │                   │                                         │
└──────────────┘                   │  ┌───────────┐   ┌────────────────────┐ │
                                   │  │  routes.py│   │     booking.py     │ │
                                   │  │ (HTTP     │   │  (Booking workflow)│ │
                                   │  │  handlers)│   └────────────────────┘ │
                                   │  └─────┬─────┘              │           │
                                   │        │                     │           │
                                   │  ┌─────▼──────────────────────────────┐ │
                                   │  │           data.py (DAL)            │ │
                                   │  │  get_flight_by_id / search_flights │ │
                                   │  │  get_user_bookings / add_user      │ │
                                   │  └─────┬──────────────────────────────┘ │
                                   │        │                                 │
                                   │  ┌─────▼──────────────────────────────┐ │
                                   │  │     SQLAlchemy ORM (models.py)     │ │
                                   │  │  User · Flight · Booking           │ │
                                   │  │  Passenger · Seat                  │ │
                                   │  └─────┬──────────────────────────────┘ │
                                   │        │                                 │
                                   │  ┌─────▼──────┐  ┌──────────────────┐  │
                                   │  │ SQLite DB  │  │  External APIs   │  │
                                   │  │airlines.db │  │ Razorpay · SMTP  │  │
                                   │  └────────────┘  └──────────────────┘  │
                                   └─────────────────────────────────────────┘
```

### Booking Workflow

```
User Login ──► Flight Search ──► Flight Details ──► Passenger Form
                                                          │
                                        ┌─────────────────▼─────────────────┐
                                        │  BookingForm Validation (WTForms)  │
                                        │  • Passenger name, DOB, passport   │
                                        │  • Seat selection                  │
                                        │  • Frequent flyer points redemption│
                                        └─────────────────┬─────────────────┘
                                                          │
                                        ┌─────────────────▼─────────────────┐
                                        │       Razorpay Order Creation      │
                                        │       (server-side, INR amount)    │
                                        └─────────────────┬─────────────────┘
                                                          │
                                        ┌─────────────────▼─────────────────┐
                                        │  Payment Callback + Sig Verification│
                                        │  ► Booking status: Confirmed       │
                                        │  ► Seat count decremented          │
                                        │  ► Confirmation email dispatched   │
                                        └────────────────────────────────────┘
```

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.10 or higher
- `pip` package manager (or `uv`)
- A Razorpay account (for payment features)
- A Gmail account with App Password (for email features)

### 1. Clone the Repository

```bash
git clone https://github.com/Srinivasan1716/AirlineReservationSystem.git
cd AirlineReservationSystem/AirlineReservationSystem
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (`AirlineReservationSystem/`) with:

```dotenv
SESSION_SECRET=your_random_secret_key_here
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

> **Note:** For production, also update `MAIL_USERNAME`, `MAIL_PASSWORD`, and `MAIL_DEFAULT_SENDER` in `app.py` or via environment variables.

### 5. Initialize the Database

```bash
python init_db.py
```

This creates `instance/airlines.db` and populates it with sample flights, airports, and a default admin user.

### 6. Run the Application

```bash
python main.py
```

The application will be available at `http://127.0.0.1:5000`.

---

## 🚀 Usage

### Passenger Workflow

1. **Register / Login** — Create an account at `/register` or sign in at `/login`
2. **Search Flights** — Enter origin, destination, date, and passenger count on the home page
3. **Select a Flight** — Review flight details, duration, and pricing
4. **Book & Pay** — Fill in passenger details, choose seats, and complete payment via Razorpay
5. **Manage Bookings** — View active reservations and cancel if needed at `/my-bookings`
6. **Travel Recommendations** — Use the recommendation engine to discover budget-friendly destinations

### Admin Workflow

1. Log in with an admin account
2. Navigate to `/admin/dashboard` for an operational overview
3. Manage flights at `/admin/flights` (add, edit, update status)
4. Monitor recent bookings and user activity

### Default Admin Credentials *(after `init_db.py`)*

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |

> ⚠️ Change these credentials immediately in any non-development environment.

---

## 📸 Screenshots or Demo

> Screenshots will be added here. To generate them, run the application locally and capture the following key pages:

| Page | Route |
|---|---|
| Home / Flight Search | `/` |
| Search Results | `/flights/search` |
| Flight Details | `/flights/<id>` |
| Booking Form | `/flights/<id>/book` |
| Booking Confirmation | `/booking/<id>/confirm` |
| My Bookings | `/my-bookings` |
| Admin Dashboard | `/admin/dashboard` |

---

## 🔌 API Integration

### Razorpay Payment Gateway

The system integrates with the [Razorpay REST API](https://razorpay.com/docs/api/) for payment processing.

| Endpoint | Method | Description |
|---|---|---|
| `/create_order` | `POST` | Creates a Razorpay order with amount in paise (INR × 100) |
| `/verify_payment` | `POST` | Verifies `razorpay_signature` using HMAC-SHA256 |

**Payment Flow:**
1. Server creates an order via `razorpay_client.order.create()`
2. Client-side Razorpay Checkout handles card/UPI/netbanking UI
3. Server verifies the payment signature before confirming the booking

### Email (SMTP)

Transactional emails are delivered via Gmail SMTP (port 587, TLS):

| Trigger | Email Content |
|---|---|
| Booking confirmed | Flight details, booking reference, total price |
| Booking cancelled | Cancellation notice with support contact |

### Travel Recommendations API

| Endpoint | Method | Parameters |
|---|---|---|
| `/recommendations` | `POST` | `budget` (float), `travel_date` (YYYY-MM-DD), `highlights` (comma-separated) |

Returns JSON array of destinations filtered by budget range, seasonality, and travel highlights from `sample_data.csv`.

---

## 📁 Folder Structure

```
AirlineReservationSystem/
├── AirlineReservationSystem/          # Application source root
│   ├── app.py                         # Application factory, extension init, mail config
│   ├── main.py                        # Entry point
│   ├── routes.py                      # HTTP route handlers (search, booking, auth, admin)
│   ├── booking.py                     # Booking-specific route registration
│   ├── models.py                      # SQLAlchemy ORM models (User, Flight, Booking, Passenger, Seat)
│   ├── forms.py                       # WTForms form classes with custom validators
│   ├── data.py                        # Data Access Layer (DAL) — DB queries & airport data
│   ├── utils.py                       # Utilities: formatting, email dispatch, seat classification
│   ├── extensions.py                  # Flask extension instances (db)
│   ├── recommend.py                   # Budget/season/highlights-based recommendation engine
│   ├── destinations.py                # Destination data loader from CSV
│   ├── init_db.py                     # Database initialization and seed data script
│   ├── sample_data.csv                # Destination dataset for recommendations
│   ├── requirements.txt               # Python dependencies
│   ├── pyproject.toml                 # Project metadata
│   ├── .env                           # Environment variables (not committed)
│   ├── templates/                     # Jinja2 HTML templates
│   │   ├── base.html                  # Base layout with Bootstrap 5
│   │   ├── index.html                 # Home / flight search
│   │   ├── search.html                # Flight search results
│   │   ├── flight_details.html        # Flight detail view
│   │   ├── booking.html               # Passenger & seat input form
│   │   ├── booking_confirm.html       # Post-payment confirmation page
│   │   ├── user_reservations.html     # User's booking history
│   │   ├── user_profile.html          # User profile page
│   │   ├── login.html / register.html # Authentication pages
│   │   ├── payment_failed.html        # Payment failure page
│   │   └── admin/                     # Admin panel templates
│   │       ├── dashboard.html
│   │       └── flights.html
│   └── static/                        # Static assets
│       ├── css/                       # Custom stylesheets
│       └── js/                        # Custom JavaScript
└── README.md                          # Project documentation
```

---

## 🔮 Future Enhancements / Roadmap

| Priority | Enhancement |
|---|---|
| 🔴 High | Migrate from SQLite to PostgreSQL for production-grade concurrency |
| 🔴 High | Implement JWT-based REST API for mobile client support |
| 🟠 Medium | Add round-trip and multi-city flight search |
| 🟠 Medium | Integrate a real-time flight status API (e.g., AviationStack) |
| 🟠 Medium | Add PDF e-ticket generation and download |
| 🟡 Low | Implement check-in workflow with boarding pass generation |
| 🟡 Low | Add loyalty tier system (Silver, Gold, Platinum) based on flight segments |
| 🟡 Low | Containerize with Docker and add CI/CD pipeline (GitHub Actions) |
| 🟡 Low | Add rate limiting and API key authentication for public endpoints |
| 🟡 Low | Integrate ML-based dynamic pricing based on demand and lead time |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Commit your changes** with a descriptive message
   ```bash
   git commit -m "feat: add round-trip flight search"
   ```
4. **Push** to your fork and **open a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Standards

- Follow [PEP 8](https://pep8.org/) for Python code style
- Add docstrings to new functions and classes
- Validate all user inputs server-side using WTForms validators
- Do not commit secrets, `.env` files, or database files (`*.db`)

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 👤 Author / Contact

**Srinivasan**

- 🐙 GitHub: [@Srinivasan1716](https://github.com/Srinivasan1716)
- 📧 Email: *(available on GitHub profile)*

---

<div align="center">

⭐ If you found this project useful, please consider starring the repository!

</div>
