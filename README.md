# Personal Expense Tracker (CLI)

A lightweight, command-line-based expense tracker built with Python and SQLite for managing daily expenses efficiently.

This project was developed as part of the Evaao internship assignment. It allows users to add, view, update, delete, and summarize their expenses with persistent storage.

---

## Features

### Must-Have
- Add expense (amount, date, note, category)
- View expenses
- Update expense
- Delete expense
- Save data (SQLite DB: `expenses.db`)
- Basic validation & error handling

### Good-to-Have (Implemented)
- Categories (e.g., food, travel, bills)
- Summary reports (total spent, grouped by category)
- Filters (by date range or category)
- Simple, intuitive CLI interface

---

##  Setup

No installation required.  
Just ensure **Python 3.8+** is installed.

1. Clone the repository or unzip the project folder.
2. Open a terminal in the project directory.
3. Run commands as shown below.

---

##  Usage

Run the CLI from the directory containing `expense_tracker.py`:

```bash
# Add an expense
python3 expense_tracker.py add --amount 250.50 --date 2025-10-01 --category food --note "lunch"

# View expenses
python3 expense_tracker.py view
python3 expense_tracker.py view --limit 5 --category food
python3 expense_tracker.py view --start 2025-09-01 --end 2025-10-05

# Update expense
python3 expense_tracker.py update 1 --amount 300 --note "dinner"

# Delete expense
python3 expense_tracker.py delete 1

# Summary reports
python3 expense_tracker.py summary
python3 expense_tracker.py summary --group-by category
python3 expense_tracker.py summary --month 2025-10
 Assumptions & Design
Date input accepted in YYYY-MM-DD or DD-MM-YYYY.
Internally stored in ISO YYYY-MM-DD format.

Category is optional; default is uncategorized.

Amount must be positive.

Data is stored persistently in a local SQLite database (expenses.db).

The program is dependency-free — runs on any system with Python 3.

 Sample Inputs/Outputs
Example CLI Run
bash
Copy code
$ python3 expense_tracker.py add --amount 250.50 --date 2025-10-01 --category food --note "lunch"
Expense added successfully (ID: 1)

$ python3 expense_tracker.py view
ID | Date       | Category | Amount | Note
1  | 2025-10-01 | food     | 250.50 | lunch

$ python3 expense_tracker.py summary --group-by category
Category   | Total Spent
food       | 250.50
More examples can be found in sample_run.txt.

Files Included
File	Description
expense_tracker.py	Main CLI application
README.md	Project documentation
sample_run.txt	Sample run demonstrating functionality
expenses.db	SQLite DB (created automatically on first run)

📧 Author
Esha Joshi
Department of Electronics and Communication Engineering
Indian Institute of Information Technology, Pune (IIIT Pune)
