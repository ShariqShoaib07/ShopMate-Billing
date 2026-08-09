# 🧾 ShopMate Billing

> A modular Windows desktop POS and billing system for ready-made ladies clothing shops.

ShopMate Billing is a local Windows desktop billing/POS application built with **Python and PySide6**.

It is designed as a reusable product rather than a shop-specific application. Shop information, products, prices, invoices, and other business data are stored in SQLite instead of being hard-coded into the application.

The first example configuration is **Maha's Collection**.

---

## ✨ Features

### ✅ Currently Implemented

- 🖥️ Modern PySide6 desktop application
- 🧾 New Bill workflow
- 👤 Customer name and mobile fields
- 📦 Product management
- ➕ Add products to invoices
- ⚡ Product keyboard shortcuts
- 🔢 Sequential invoice numbering
- 🧮 Editable invoice line items
- 🔢 Editable quantities
- 💰 Editable selling prices
- 🧮 Automatic amount calculation
- 💵 Automatic invoice total
- ❌ Remove invoice items
- 🧹 Clear current bill
- 💾 SQLite-based local database
- 💾 Invoice persistence
- 🏪 Database-driven shop information
- 💾 SQLite database backup service
- 🖨️ Print service abstraction
- 🧪 Automated tests with pytest
- 🧱 Modular application architecture

### 🚧 Currently In Development

- 📊 Sales History
- 🔎 Invoice searching
- 🧾 Invoice detail viewing
- 🖨️ Invoice reprinting
- 📅 Date-based invoice filtering

### 🔮 Planned

- ⚙️ Shop Settings UI
- 🧾 Receipt design
- 👀 Print preview
- 🖨️ Thermal printer integration
- 💾 Backup & restore UI
- 📦 Windows `.exe` packaging
- 🚀 Production deployment

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python 3.x** | Core application development |
| **PySide6** | Desktop GUI |
| **SQLite** | Local database |
| **sqlite3** | Python SQLite integration |
| **pytest** | Automated testing |
| **PyInstaller** | Windows executable packaging |

---

# 📁 Project Structure

```text
ShopMate-Billing/
│
├── app/
│   ├── config/          # Application configuration
│   ├── database/        # SQLite connection, schema & repositories
│   ├── models/          # Core data models / dataclasses
│   ├── services/        # Business and service layer
│   ├── ui/              # PySide6 windows and pages
│   └── utils/           # Paths, currency & date/time utilities
│
├── data/                # Local development database
├── backups/             # Local database backup output
├── tests/               # pytest test suite
│
├── main.py              # Application entry point
├── pytest.ini           # pytest configuration
├── requirements.txt     # Python dependencies
├── .gitignore
└── README.md
🚀 Getting Started
1. Clone the Repository
git clone https://github.com/ShariqShoaib07/ShopMate-Billing.git
cd ShopMate-Billing
2. Create a Virtual Environment
python -m venv .venv
3. Activate the Virtual Environment
Windows PowerShell
.venv\Scripts\Activate.ps1

If PowerShell blocks script execution:

.venv\Scripts\activate
4. Install Dependencies
pip install -r requirements.txt
▶️ Running the Application

Start the application with:

python main.py

On the first run, ShopMate Billing initializes the SQLite database and creates the required tables and example shop/product data.

🧪 Running Tests

Run the complete test suite:

pytest

The tests use temporary SQLite databases where appropriate and are designed not to modify the main development database.

🗄️ Database

ShopMate Billing uses SQLite for local data storage.

The development database is stored inside:

data/

The exact database filename/path is centralized through the application's configuration and path utilities.

Database paths are managed through:

app/config/settings.py
app/utils/paths.py

This keeps database access independent from business logic and allows the application to later use appropriate user-accessible application-data locations when packaged as a Windows executable.

Current Database Tables
products
shop_settings
invoices
invoice_items

SQLite foreign-key enforcement is enabled for database connections.

🧩 Architecture

The project follows a modular architecture that separates the GUI, business logic, database access, and utilities.

┌─────────────────────────────┐
│          PySide6 UI         │
│     Windows & UI Pages      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Service Layer         │
│   Billing & Business Logic  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Repository Layer       │
│       Database Access       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│           SQLite            │
│      Local Application DB   │
└─────────────────────────────┘

The architecture is intentionally modular so new POS functionality can be added without tightly coupling UI code, business logic, and database operations.

📌 Current Implementation Status
✅ Completed
Project foundation and modular structure
SQLite schema creation
First-run database initialization
Example shop and product seed data
Product repository
Invoice repository
Shop settings repository
Service layer foundations
SQLite database backup service
Print service abstraction
PySide6 application shell
Basic navigation
Products & Shortcuts management
Product add/edit/disable functionality
Product validation
New Bill workflow
Customer information fields
Product keyboard shortcuts
Editable bill rows
Quantity editing
Selling price editing
Automatic amount calculation
Automatic bill total
Remove invoice items
Clear bill functionality
SQLite invoice saving
Sequential invoice numbers
Invoice item persistence
Customer information persistence
Invoice date/time persistence
Preservation of historical selling prices
Automated tests for implemented functionality
🚧 Current Phase

Phase 6 — Sales History

Current work focuses on:

Sales History screen
Previous invoice listing
Invoice searching
Invoice number search
Customer name search
Mobile number search
Invoice detail viewing
Invoice reprinting
Date-based filtering
🔮 Upcoming
Phase 7 — Shop Configuration
Phase 8 — Receipt / Bill Design
Phase 9 — Thermal Printer
Phase 10 — Backup & Restore
Phase 11 — UX / Polish
Phase 12 — Production Testing
Phase 13 — Windows EXE Build
Phase 14 — Real Shop Deployment
🗺️ Development Roadmap

The project is being developed incrementally to reduce regressions and keep each feature independently testable.

Phase 1 — Project Foundation
Project architecture
SQLite foundation
PySide6 application shell
Basic navigation
Development environment
Testing foundation

STATUS: ✅ COMPLETED

Phase 2 — Database Foundation
SQLite connection system
Database initialization
Products table
Shop settings table
Invoices table
Invoice items table
Repository layer
Seed data
Database tests

STATUS: ✅ COMPLETED

Phase 3 — Product Management
Products screen
Display products
Add product
Edit product
Disable/enable product
Product search
Shortcut validation
Price validation
Product name validation
Active/inactive handling
Product management tests

STATUS: ✅ COMPLETED

Phase 4 — Billing Screen
Customer information
Invoice number
Date/time
Product selection
Keyboard shortcuts
Add products
Quantity editing
Selling price editing
Automatic calculations
Bill total
Remove items
Clear bill
Edit existing line items
New Bill
Keyboard navigation
Billing validation
Billing tests

STATUS: ✅ COMPLETED

Phase 5 — Invoice System
Generate invoice number
Auto-increment invoice number
Save invoice to SQLite
Save invoice items
Save customer information
Save exact selling price
Save invoice date
Save invoice time
Preserve historical invoice data
Invoice tests

STATUS: ✅ COMPLETED

Phase 6 — Sales History
Sales History screen
Display previous invoices
Search invoices
Search by invoice number
Search by customer name
Search by mobile number
View invoice details
Reprint invoice
Date-based filtering

STATUS: ✅ COMPLETED

Advanced reporting is intentionally excluded from V1.

Phase 7 — Shop Configuration
Settings screen
Edit shop name
Edit address
Edit phone 1
Edit phone 2
Save settings
Load settings dynamically
Use dynamic shop information in bills
Product management access through Settings

STATUS: ✅ COMPLETED

Phase 8 — Receipt / Bill Design
Receipt template
Shop name
Shop address
Phone numbers
Invoice number
Date
Time
Customer information
Item table
Quantity
Rate
Amount
Total
Rupees in words
Thank-you message
Print preview

STATUS: ✅ COMPLETED

Phase 9 — Thermal Printer

Waiting for the actual printer model and paper size.

Identify printer model
Identify paper width
Determine communication method
Configure printer
Connect print service
Basic printing
Complete receipt printing
Long receipt testing
Text alignment
Paper cutting
Multiple bills
Printer error handling

STATUS: ⏳ WAITING FOR PRINTER

Phase 10 — Backup & Restore
Backup database
Backup button
Backup timestamp
Backup folder
Automatic backup
Restore backup
Restore confirmation
Accidental restore protection
Backup tests
Restore tests

STATUS: 🔵 PLANNED

A backup service foundation already exists.

Phase 11 — UX / Polish
Review entire UI
Improve readability
Ensure buttons are large enough
Ensure labels are clear
Remove unnecessary controls
Keyboard navigation
Mouse navigation
Confirmation dialogs
Friendly error messages
Loading states
Empty states
Prevent accidental bill deletion
Prevent accidental application close with unsaved bill
Test workflow with someone unfamiliar with the software
UX Goal

Can a shopkeeper use the application without someone standing beside them explaining every button?

If yes, the UX is successful.

STATUS: 🔵 PLANNED

Phase 12 — Production Testing
Billing
One-product bill
Multiple-product bill
Quantity 2
Quantity 10+
Change selling price
Empty customer name
Empty customer mobile
Customer information
Large total
Invalid quantity handling
Database
Close/reopen application
Bills remain saved
Products remain saved
Settings remain saved
History
Find old bill
View old bill
Reprint old bill
Backup
Create backup
Replace/delete test database
Restore backup
Verify restored data
Printer
Normal bill
Long bill
Multiple bills
Reprint bill

STATUS: 🔵 PLANNED

Phase 13 — Windows EXE
Configure PyInstaller
Create Windows build
Test .exe
Test without Python installed
Test database path
Test backup path
Test printer
Test application reopening
Test all features
Fix packaging issues
Create final release build

STATUS: 🔵 PLANNED

Phase 14 — Real Shop Deployment
Install on shop laptop
Configure shop information
Configure actual products
Configure shortcuts
Configure prices
Configure printer
Test actual bills
Test actual printer
Test with shopkeeper
Let shopkeeper use independently
Fix usability issues
Take final backup
Final release

STATUS: 🔵 PLANNED

🏪 Example Shop

The initial project configuration uses:

Maha's Collection

The application is intentionally designed so shop-specific information and products are stored in the database rather than hard-coded into the billing system.

This allows the same application architecture to be adapted for other clothing shops in the future.

🔐 Data & Privacy

ShopMate Billing is designed as a local-first desktop application.

Application data is stored locally using SQLite.

No cloud database or external backend is required for the current version.

## 🎨 UI Preservation Rules

ShopMate Billing has an established visual language.

AI coding agents MUST preserve the existing UI unless a task explicitly requests a redesign.

### Existing UI principles

- Light application theme
- Off-white/light main background
- White content surfaces
- Dark navy/black typography
- Teal primary accent
- Rounded input fields and buttons
- Clear left sidebar navigation
- Large readable controls
- Clean vertical content flow
- Minimal and practical POS-oriented interface

### Strict Rules

1. Do not introduce a dark theme.
2. Do not allow native widgets/popups to introduce an inconsistent dark palette.
3. Do not redesign existing screens while implementing unrelated functionality.
4. Do not change spacing, typography, colors, buttons, or navigation unless explicitly requested.
5. Do not use arbitrary fixed heights to solve layout problems.
6. Do not use absolute positioning for normal application layouts.
7. Prefer Qt layouts, size policies, stretch factors, and scroll areas.
8. Content must flow naturally from top to bottom.
9. Tables must never be visually hidden behind other widgets.
10. If content exceeds the window height, the PAGE should scroll naturally.
11. Do not create unnecessary nested scrolling areas.
12. Preserve existing working workflows and interactions.

The goal is consistency, not redesign.

📦 Packaging

Windows executable packaging will be implemented using PyInstaller.

The planned production workflow is:

Python Application
       │
       ▼
   PyInstaller
       │
       ▼
 Windows .exe
       │
       ▼
 End User Installation

Packaging is intentionally postponed until the core application has been fully tested.

🤝 Development

ShopMate Billing is being developed incrementally in phases.

Each phase is intended to:

Implement a focused set of functionality.
Preserve existing functionality.
Add appropriate tests.
Verify existing workflows before moving forward.
Avoid unnecessary architectural or UI changes.

The application should remain modular so new features can be introduced without tightly coupling the GUI, business logic, and database layers.

📄 License

License information will be added when the project reaches its release stage.

👨‍💻 Author

Shariq Shoaib

GitHub: @ShariqShoaib07