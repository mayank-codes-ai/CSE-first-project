import sqlite3
from datetime import datetime

DB_NAME = "hospital.db"

# ---------- Database Setup ----------

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Patients table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        phone TEXT
    )
    """)

    # Doctors table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT,
        phone TEXT
    )
    """)

    # Appointments table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id),
        FOREIGN KEY(doctor_id) REFERENCES doctors(id)
    )
    """)

    # Bills table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        appointment_id INTEGER,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(patient_id) REFERENCES patients(id),
        FOREIGN KEY(appointment_id) REFERENCES appointments(id)
    )
    """)

    # Bill items table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bill_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY(bill_id) REFERENCES bills(id)
    )
    """)

    conn.commit()
    conn.close()

# ---------- Patient Functions ----------

def add_patient():
    print("\n--- Add New Patient ---")
    name = input("Name: ")
    age = int(input("Age: "))
    gender = input("Gender (M/F/O): ")
    phone = input("Phone: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO patients (name, age, gender, phone) VALUES (?, ?, ?, ?)",
        (name, age, gender, phone)
    )
    conn.commit()
    print(f"✅ Patient added with ID: {cur.lastrowid}")
    conn.close()

def list_patients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, gender, phone FROM patients ORDER BY id")
    rows = cur.fetchall()

    print("\n--- Patients List ---")
    if not rows:
        print("No patients found.")
    else:
        for r in rows:
            print(f"ID: {r[0]} | {r[1]} | Age: {r[2]} | Gender: {r[3]} | Phone: {r[4]}")
    conn.close()

def search_patient():
    term = input("Enter patient ID or name to search: ").strip()
    conn = get_connection()
    cur = conn.cursor()

    if term.isdigit():
        cur.execute(
            "SELECT id, name, age, gender, phone FROM patients WHERE id = ?",
            (int(term),)
        )
    else:
        cur.execute(
            "SELECT id, name, age, gender, phone FROM patients WHERE name LIKE ?",
            (f"%{term}%",)
        )

    rows = cur.fetchall()
    print("\n--- Search Results ---")
    if not rows:
        print("No matching patients found.")
    else:
        for r in rows:
            print(f"ID: {r[0]} | {r[1]} | Age: {r[2]} | Gender: {r[3]} | Phone: {r[4]}")
    conn.close()

# ---------- Doctor Functions ----------

def add_doctor():
    print("\n--- Add New Doctor ---")
    name = input("Name: ")
    specialization = input("Specialization: ")
    phone = input("Phone: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO doctors (name, specialization, phone) VALUES (?, ?, ?)",
        (name, specialization, phone)
    )
    conn.commit()
    print(f"✅ Doctor added with ID: {cur.lastrowid}")
    conn.close()

def list_doctors():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, specialization, phone FROM doctors ORDER BY id")
    rows = cur.fetchall()

    print("\n--- Doctors List ---")
    if not rows:
        print("No doctors found.")
    else:
        for r in rows:
            print(f"ID: {r[0]} | Dr. {r[1]} | {r[2]} | Phone: {r[3]}")
    conn.close()

# ---------- Appointment Functions ----------

def add_appointment():
    print("\n--- Schedule Appointment ---")
    patient_id = int(input("Patient ID: "))
    doctor_id = int(input("Doctor ID: "))
    date = input("Date (YYYY-MM-DD): ")
    time = input("Time (HH:MM): ")
    notes = input("Notes (optional): ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO appointments (patient_id, doctor_id, date, time, notes) VALUES (?, ?, ?, ?, ?)",
        (patient_id, doctor_id, date, time, notes)
    )
    conn.commit()
    print(f"✅ Appointment created with ID: {cur.lastrowid}")
    conn.close()

def list_appointments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, p.name, d.name, a.date, a.time, a.notes
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        ORDER BY a.date, a.time
    """)
    rows = cur.fetchall()

    print("\n--- Appointments ---")
    if not rows:
        print("No appointments scheduled.")
    else:
        for r in rows:
            print(
                f"ID: {r[0]} | Patient: {r[1]} | Doctor: Dr. {r[2]} | "
                f"{r[3]} {r[4]} | Notes: {r[5] or ''}"
            )
    conn.close()

# ---------- Billing Functions ----------

def create_bill():
    print("\n--- Create Bill ---")
    patient_id = int(input("Patient ID: "))
    appointment_id_input = input("Appointment ID (optional, press enter to skip): ").strip()
    appointment_id = int(appointment_id_input) if appointment_id_input else None

    items = []
    while True:
        desc = input("Service description (or 'done' to finish): ").strip()
        if desc.lower() == "done":
            break
        amount = float(input("Amount: "))
        items.append((desc, amount))

    if not items:
        print("No items added. Bill cancelled.")
        return

    total = sum(a for _, a in items)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bills (patient_id, appointment_id, total_amount, status, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (patient_id, appointment_id, total, "UNPAID", now)
    )
    bill_id = cur.lastrowid

    for desc, amount in items:
        cur.execute(
            "INSERT INTO bill_items (bill_id, description, amount) VALUES (?, ?, ?)",
            (bill_id, desc, amount)
        )

    conn.commit()
    conn.close()
    print(f"✅ Bill created with ID: {bill_id}, Total: Rs. {total:.2f}")

def list_bills():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.id, p.name, b.total_amount, b.status, b.created_at
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        ORDER BY b.created_at DESC
    """)
    rows = cur.fetchall()

    print("\n--- Bills ---")
    if not rows:
        print("No bills found.")
    else:
        for r in rows:
            print(
                f"ID: {r[0]} | Patient: {r[1]} | Total: Rs. {r[2]:.2f} | "
                f"Status: {r[3]} | Created: {r[4]}"
            )
    conn.close()

def view_bill_details():
    bill_id = int(input("Enter Bill ID: "))
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT b.id, p.name, b.total_amount, b.status, b.created_at
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE b.id = ?
    """, (bill_id,))
    bill = cur.fetchone()

    if not bill:
        print("Bill not found.")
        conn.close()
        return

    print("\n--- Bill Summary ---")
    print(f"Bill ID: {bill[0]}")
    print(f"Patient: {bill[1]}")
    print(f"Total: Rs. {bill[2]:.2f}")
    print(f"Status: {bill[3]}")
    print(f"Created At: {bill[4]}")

    cur.execute("SELECT description, amount FROM bill_items WHERE bill_id = ?", (bill_id,))
    items = cur.fetchall()

    print("\nItems:")
    for desc, amount in items:
        print(f"- {desc}: Rs. {amount:.2f}")
    conn.close()

def pay_bill():
    bill_id = int(input("Enter Bill ID to mark as PAID: "))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE bills SET status = 'PAID' WHERE id = ?", (bill_id,))

    if cur.rowcount == 0:
        print("Bill not found.")
    else:
        conn.commit()
        print("✅ Bill marked as PAID.")
    conn.close()

def revenue_report():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT IFNULL(SUM(total_amount), 0) FROM bills WHERE status = 'PAID'")
    total_paid = cur.fetchone()[0]

    cur.execute("SELECT IFNULL(SUM(total_amount), 0) FROM bills WHERE status = 'UNPAID'")
    total_unpaid = cur.fetchone()[0]

    print("\n--- Revenue Report ---")
    print(f"Total collected (PAID): Rs. {total_paid:.2f}")
    print(f"Pending amount (UNPAID): Rs. {total_unpaid:.2f}")
    conn.close()

# ---------- Menus ----------

def patient_menu():
    while True:
        print("\n=== Patient Management ===")
        print("1. Add patient")
        print("2. List patients")
        print("3. Search patient")
        print("0. Back to main menu")
        choice = input("Enter choice: ")

        if choice == "1":
            add_patient()
        elif choice == "2":
            list_patients()
        elif choice == "3":
            search_patient()
        elif choice == "0":
            break
        else:
            print("Invalid choice, try again.")

def doctor_menu():
    while True:
        print("\n=== Doctor Management ===")
        print("1. Add doctor")
        print("2. List doctors")
        print("0. Back to main menu")
        choice = input("Enter choice: ")

        if choice == "1":
            add_doctor()
        elif choice == "2":
            list_doctors()
        elif choice == "0":
            break
        else:
            print("Invalid choice, try again.")

def appointment_menu():
    while True:
        print("\n=== Appointment Management ===")
        print("1. Schedule appointment")
        print("2. List appointments")
        print("0. Back to main menu")
        choice = input("Enter choice: ")

        if choice == "1":
            add_appointment()
        elif choice == "2":
            list_appointments()
        elif choice == "0":
            break
        else:
            print("Invalid choice, try again.")

def billing_menu():
    while True:
        print("\n=== Billing & Payments ===")
        print("1. Create bill")
        print("2. List bills")
        print("3. View bill details")
        print("4. Mark bill as PAID")
        print("5. Revenue report")
        print("0. Back to main menu")
        choice = input("Enter choice: ")

        if choice == "1":
            create_bill()
        elif choice == "2":
            list_bills()
        elif choice == "3":
            view_bill_details()
        elif choice == "4":
            pay_bill()
        elif choice == "5":
            revenue_report()
        elif choice == "0":
            break
        else:
            print("Invalid choice, try again.")

def main_menu():
    init_db()
    print("Welcome to Hospital Administration System (Console Version)")
    while True:
        print("\n===== Main Menu =====")
        print("1. Patient Management")
        print("2. Doctor Management")
        print("3. Appointment Management")
        print("4. Billing & Payments")
        print("0. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            patient_menu()
        elif choice == "2":
            doctor_menu()
        elif choice == "3":
            appointment_menu()
        elif choice == "4":
            billing_menu()
        elif choice == "0":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main_menu()