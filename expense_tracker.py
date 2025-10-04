#!/usr/bin/env python3
"""
Personal Expense Tracker (CLI)
"""
import argparse
import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    create_sql = (
        "CREATE TABLE IF NOT EXISTS expenses ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "amount REAL NOT NULL,"
        "category TEXT DEFAULT 'uncategorized',"
        "note TEXT,"
        "date TEXT NOT NULL"
        ")"
    )
    c.execute(create_sql)
    conn.commit()
    conn.close()

def valid_date(s):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            dt = datetime.strptime(s, fmt).date()
            return dt.isoformat()
        except ValueError:
            continue
    raise argparse.ArgumentTypeError("Date must be YYYY-MM-DD or DD-MM-YYYY")

def add_expense(amount: float, date_str: str, note: Optional[str], category: Optional[str]):
    if amount <= 0:
        raise ValueError("Amount must be positive")
    iso_date = valid_date(date_str)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO expenses (amount, category, note, date) VALUES (?, ?, ?, ?)",
              (amount, category or "uncategorized", note or "", iso_date))
    conn.commit()
    rowid = c.lastrowid
    conn.close()
    print(f"Added expense id={rowid}, amount={amount}, date={iso_date}, category={category or 'uncategorized'}")

def view_expenses(limit: int = None, category: Optional[str] = None, start: Optional[str]=None, end: Optional[str]=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    q = "SELECT id, amount, category, note, date FROM expenses"
    clauses = []
    params = []
    if category:
        clauses.append("category = ?"); params.append(category)
    if start:
        clauses.append("date >= ?"); params.append(valid_date(start))
    if end:
        clauses.append("date <= ?"); params.append(valid_date(end))
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY date DESC, id DESC"
    if limit:
        q += f" LIMIT {int(limit)}"
    c.execute(q, params)
    rows = c.fetchall()
    conn.close()
    if not rows:
        print("No expenses found.")
        return
    print(f"{'ID':>3} {'AMOUNT':>10}  {'CATEGORY':>12}  {'DATE':>10}  NOTE")
    print("-"*60)
    for r in rows:
        print(f"{r[0]:>3} {r[1]:10.2f}  {r[2]:12}  {r[4]:>10}  {r[3]}")

def update_expense(expense_id: int, amount: Optional[float], date_str: Optional[str], note: Optional[str], category: Optional[str]):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
    if not c.fetchone():
        conn.close()
        raise ValueError("Expense id not found")
    updates = []
    params = []
    if amount is not None:
        if amount <= 0:
            conn.close(); raise ValueError("Amount must be positive")
        updates.append("amount = ?"); params.append(amount)
    if date_str is not None:
        updates.append("date = ?"); params.append(valid_date(date_str))
    if note is not None:
        updates.append("note = ?"); params.append(note)
    if category is not None:
        updates.append("category = ?"); params.append(category)
    if not updates:
        conn.close(); raise ValueError("No update fields provided")
    q = "UPDATE expenses SET " + ", ".join(updates) + " WHERE id = ?"
    params.append(expense_id)
    c.execute(q, params)
    conn.commit()
    conn.close()
    print(f"Updated expense id={expense_id}")

def delete_expense(expense_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
    if not c.fetchone():
        conn.close()
        raise ValueError("Expense id not found")
    c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    print(f"Deleted expense id={expense_id}")

def summary_report(group_by: Optional[str]=None, month: Optional[str]=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    q = "SELECT SUM(amount) FROM expenses"
    params = []
    clauses = []
    if month:
        # accept YYYY-MM or MM-YYYY
        try:
            dt = datetime.strptime(month, "%Y-%m").date()
            clauses.append("date LIKE ?"); params.append(f"{dt.year:04d}-{dt.month:02d}-%")
        except Exception:
            try:
                dt = datetime.strptime(month, "%m-%Y").date()
                clauses.append("date LIKE ?"); params.append(f"{dt.year:04d}-{dt.month:02d}-%")
            except Exception:
                raise ValueError("Month format should be YYYY-MM or MM-YYYY")
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    c.execute(q, params)
    total = c.fetchone()[0] or 0.0
    print(f"Total spent: {total:.2f}")
    if group_by == "category":
        q2 = "SELECT category, SUM(amount) FROM expenses"
        if clauses:
            q2 += " WHERE " + " AND ".join(clauses)
        q2 += " GROUP BY category ORDER BY SUM(amount) DESC"
        c.execute(q2, params)
        rows = c.fetchall()
        print("\\nBy category:")
        for cat, amt in rows:
            print(f"  {cat:12} : {amt:.2f}")
    conn.close()

def parse_args():
    parser = argparse.ArgumentParser(prog="expense_tracker", description="Personal Expense Tracker CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add an expense")
    p_add.add_argument("--amount", type=float, required=True)
    p_add.add_argument("--date", type=str, required=True, help="YYYY-MM-DD or DD-MM-YYYY")
    p_add.add_argument("--note", type=str, default="")
    p_add.add_argument("--category", type=str, default="uncategorized")

    p_view = sub.add_parser("view", help="View expenses")
    p_view.add_argument("--limit", type=int, default=None)
    p_view.add_argument("--category", type=str, default=None)
    p_view.add_argument("--start", type=str, default=None, help="start date YYYY-MM-DD or DD-MM-YYYY")
    p_view.add_argument("--end", type=str, default=None, help="end date YYYY-MM-DD or DD-MM-YYYY")

    p_update = sub.add_parser("update", help="Update an expense by id")
    p_update.add_argument("id", type=int)
    p_update.add_argument("--amount", type=float, default=None)
    p_update.add_argument("--date", type=str, default=None)
    p_update.add_argument("--note", type=str, default=None)
    p_update.add_argument("--category", type=str, default=None)

    p_delete = sub.add_parser("delete", help="Delete expense by id")
    p_delete.add_argument("id", type=int)

    p_sum = sub.add_parser("summary", help="Summary report")
    p_sum.add_argument("--group-by", choices=["category"], default=None)
    p_sum.add_argument("--month", type=str, default=None, help="YYYY-MM or MM-YYYY")

    return parser.parse_args()

def main():
    init_db()
    args = parse_args()
    try:
        if args.cmd == "add":
            add_expense(args.amount, args.date, args.note, args.category)
        elif args.cmd == "view":
            view_expenses(limit=args.limit, category=args.category, start=args.start, end=args.end)
        elif args.cmd == "update":
            update_expense(args.id, args.amount, args.date, args.note, args.category)
        elif args.cmd == "delete":
            delete_expense(args.id)
        elif args.cmd == "summary":
            summary_report(group_by=args.group_by, month=args.month)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
