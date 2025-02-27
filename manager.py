import sqlite3
import os
from tabulate import tabulate
from termcolor import colored
from datetime import datetime, date

class Manager:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.db = 'ems_data.db'

    @staticmethod
    def login():
        conn = sqlite3.connect('ems_data.db')
        cursor = conn.cursor()

        print(colored("\nManager Login", "cyan", attrs=['bold']))
        manager_id = input("Enter your Manager ID: ").strip()
        password = input("Enter your Password: ").strip()

        cursor.execute("SELECT id, name FROM Manager WHERE id = ? AND password = ?", (manager_id, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            print(colored(f"\nLogin successful! Welcome, {user[1]}", "green", attrs=['bold']))
            return Manager(user[0], user[1])
        else:
            print(colored("\nInvalid Manager ID or Password. Please try again.", "red", attrs=['bold']))
            return None

    def run(self):
        while True:
            self.show_main_menu()
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.manage_hrs()
            elif choice == "2":
                self.manage_employees()
            elif choice == "3":
                print(colored("\nLogging out...", "cyan"))
                break
            else:
                print(colored("\nInvalid choice! Please try again.", "red"))

    def show_main_menu(self):
        options = [
            ["1", "Manage HRs"],
            ["2", "Manage Employees"],
            ["3", "Logout"]
        ]
        print(colored("\nManager Dashboard", "green", attrs=['bold']))
        print(tabulate(options, headers=[colored("Option", "cyan"), colored("Action", "yellow")], tablefmt="double_grid"))
    
    def manage_hrs(self):
        while True:
            options = [
                ["1", "Add HR"],
                ["2", "Remove HR"],
                ["3", "Update HR Details"],
                ["4", "Back to Main Menu"]
            ]
            print(colored("\nManage HRs", "cyan", attrs=['bold']))
            print(tabulate(options, headers=[colored("Option", "cyan"), colored("Action", "yellow")], tablefmt="double_grid"))
            
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                self.add_hr()
            elif choice == "2":
                self.remove_hr()
            elif choice == "3":
                self.update_hr_details()
            elif choice == "4":
                break
            else:
                print(colored("\nInvalid choice! Please try again.", "red"))


    def add_hr(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        print(colored("\nAdd HR", "cyan"))

        # Name input validation
        name = input("Enter HR Name: ").strip()
        if not name.replace(" ", "").isalpha():
            print(colored("\nInvalid name! Name should only contain letters.", "red"))
            conn.close()
            return

        # Email validation
        email = input("Enter Email: ").strip()
        if "@" not in email or "." not in email.split("@")[-1]:
            print(colored("\nInvalid email! Please enter a valid email address.", "red"))
            conn.close()
            return

        # Password input
        password = input("Enter Password: ").strip()
        if len(password) < 4:
            print(colored("\nPassword too short! Must be at least 4 characters.", "red"))
            conn.close()
            return

        # Contact number validation (only 10 digits)
        contactnumber = input("Enter Contact Number: ").strip()
        if not contactnumber.isdigit() or len(contactnumber) != 10:
            print(colored("\nInvalid contact number! Must be exactly 10 digits.", "red"))
            conn.close()
            return

        # Salary validation (should be a number)
        salary = input("Enter Salary: ").strip()
        if not salary.isdigit():
            print(colored("\nInvalid salary! Salary must be a numeric value.", "red"))
            conn.close()
            return

        # Degree validation (should only contain letters)
        degree = input("Enter Degree: ").strip()
        if not degree.replace(" ", "").isalpha():
            print(colored("\nInvalid degree! Degree should only contain letters.", "red"))
            conn.close()
            return

        # Insert data into HR table
        cursor.execute("INSERT INTO HR (name, email, password, contactnumber, salary, degree) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, email, password, contactnumber, int(salary), degree))
        conn.commit()
        conn.close()

        print(colored("\nHR added successfully!", "green"))


    def remove_hr(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Fetch and display available HRs
        cursor.execute("SELECT hr_id, name FROM HR")
        hrs = cursor.fetchall()

        if not hrs:
            print(colored("\nNo HRs found.", "red"))
            conn.close()
            return

        print(colored("\nHR List:", "cyan"))
        print(tabulate(hrs, headers=["HR ID", "Name"], tablefmt="double_grid"))

        # Get HR ID input with validation
        hr_id = input("\nEnter HR ID to remove: ").strip()
        if not hr_id.isdigit():
            print(colored("\nInvalid HR ID! Must be a numeric value.", "red"))
            conn.close()
            return

        cursor.execute("SELECT * FROM HR WHERE hr_id = ?", (hr_id,))
        if not cursor.fetchone():
            print(colored("\nHR ID not found!", "red"))
            conn.close()
            return

        # Confirm before deletion
        confirm = input("Are you sure you want to remove this HR? (yes/no): ").strip().lower()
        if confirm != "yes":
            print(colored("\nHR removal canceled.", "yellow"))
            conn.close()
            return

        cursor.execute("DELETE FROM HR WHERE hr_id = ?", (hr_id,))
        conn.commit()
        conn.close()

        print(colored("\nHR removed successfully!", "green"))


    def update_hr_details(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Fetch and display available HRs
        cursor.execute("SELECT hr_id, name FROM HR")
        hrs = cursor.fetchall()

        if not hrs:
            print(colored("\nNo HRs found.", "red"))
            conn.close()
            return

        print(colored("\nHR List:", "cyan"))
        print(tabulate(hrs, headers=["HR ID", "Name"], tablefmt="double_grid"))

        hr_id = input("\nEnter HR ID to update: ").strip()
        if not hr_id.isdigit():
            print(colored("\nInvalid HR ID! Must be a numeric value.", "red"))
            conn.close()
            return

        cursor.execute("SELECT * FROM HR WHERE hr_id = ?", (hr_id,))
        if not cursor.fetchone():
            print(colored("\nHR ID not found!", "red"))
            conn.close()
            return

        updates = {}

        new_name = input("Enter new Name (Press Enter to skip): ").strip()
        if new_name and any(char.isdigit() for char in new_name):
            print(colored("\nInvalid Name! It should not contain numbers.", "red"))
        elif new_name:
            updates["name"] = new_name

        new_email = input("Enter new Email (Press Enter to skip): ").strip()
        if new_email and "@" not in new_email:
            print(colored("\nInvalid Email! It must contain '@'.", "red"))
        elif new_email:
            updates["email"] = new_email

        new_contact = input("Enter new Contact Number (Press Enter to skip): ").strip()
        if new_contact and (not new_contact.isdigit() or len(new_contact) != 10):
            print(colored("\nInvalid Contact Number! It must be a 10-digit number.", "red"))
        elif new_contact:
            updates["contactnumber"] = new_contact

        new_salary = input("Enter new Salary (Press Enter to skip): ").strip()
        if new_salary and not new_salary.isdigit():
            print(colored("\nInvalid Salary! It must be a numeric value.", "red"))
        elif new_salary:
            updates["salary"] = new_salary

        new_degree = input("Enter new Degree (Press Enter to skip): ").strip()
        if new_degree and any(char.isdigit() for char in new_degree):
            print(colored("\nInvalid Degree! It should not contain numbers.", "red"))
        elif new_degree:
            updates["degree"] = new_degree

        if updates:
            query = "UPDATE HR SET " + ", ".join(f"{col} = ?" for col in updates.keys()) + " WHERE hr_id = ?"
            values = list(updates.values()) + [hr_id]
            cursor.execute(query, values)
            conn.commit()
            print(colored("\nHR details updated successfully!", "green"))
        else:
            print(colored("\nNo valid changes made.", "yellow"))

        conn.close()

    

    def manage_employees(self):
        while True:
            options = [
                ["1", "Manage Employee Leaves"],
                ["2", "Manage Company Accounts"],
                ["3", "View Employee Performance"],
                ["4", "Remove an Employee"],
                ["5", "Generate Salary Report (Employees & HRs)"],
                ["6", "Manage Employee Position Change Requests"],
                ["7", "Approve Promotions (Salary/Position Changes)"],
                ["8", "View Employee Attendance"],
                ["9", "Employee Attendance Analytics (Graph)"],
                ["10", "Back to Main Menu"]
            ]
            print(colored("\nManage Employees", "cyan", attrs=['bold']))
            print(tabulate(options, headers=[colored("Option", "cyan"), colored("Action", "yellow")], tablefmt="double_grid"))
            
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                self.manage_employee_leaves()
            elif choice == "2":
                self.manage_company_accounts()
            elif choice == "3":
                self.view_employee_performance()
            elif choice == "4":
                self.remove_employee()
            elif choice == "5":
                self.generate_salary_report()
            elif choice == "6":
                self.manage_position_change_requests()
            elif choice == "7":
                self.approve_promotions()
            elif choice == "8":
                self.view_employee_attendance()
            elif choice == "9":
                self.employee_attendance_analytics()
            elif choice == "10":
                break
            else:
                print(colored("\nInvalid choice or functionality not implemented yet!", "red"))

    def manage_employee_leaves(self):
        while True:
            options = [
                ["1", "Check Leaves of Each Employee"],
                ["2", "Approve/Reject Leave Requests"],
                ["3", "Back to Employee Management"]
            ]
            print(colored("\nManage Employee Leaves", "cyan", attrs=['bold']))
            print(tabulate(options, headers=[colored("Option", "cyan"), colored("Action", "yellow")], tablefmt="double_grid"))
            
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                self.view_leave_history()
            elif choice == "2":
                self.approve_or_reject_leave()
            elif choice == "3":
                break
            else:
                print(colored("\nInvalid choice or functionality not implemented yet!", "red"))

    def view_leave_history(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        emp_id = input("\nEnter Employee ID to view leave history: ").strip()

        cursor.execute("""
            SELECT L.leave_id, E.name, L.leavetype, L.startdate, L.enddate, L.status
            FROM Leaves L
            JOIN Employee E ON L.emp_id = E.emp_id
            WHERE L.emp_id = ?
        """, (emp_id,))
        leave_history = cursor.fetchall()

        if leave_history:
            print(colored(f"\nLeave History for Employee ID {emp_id}:", "green"))
            print(tabulate(leave_history, headers=["Leave ID", "Employee Name", "Leave Type", "Start Date", "End Date", "Status"], tablefmt="double_grid"))
        else:
            print(colored("\nNo leave history found for the given Employee ID.", "red"))

        conn.close()

    def view_pending_leaves(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT L.leave_id, E.name, L.leavetype, L.startdate, L.enddate, L.status
            FROM Leaves L
            JOIN Employee E ON L.emp_id = E.emp_id
            WHERE L.status = 'PENDING'
        """)
        pending_leaves = cursor.fetchall()

        if pending_leaves:
            print(colored("\nPending Leave Requests:", "green"))
            print(tabulate(pending_leaves, headers=["Leave ID", "Employee Name", "Leave Type", "Start Date", "End Date", "Status"], tablefmt="double_grid"))
        else:
            print(colored("\nNo pending leave requests.", "red"))

        conn.close()

    def approve_or_reject_leave(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        self.view_pending_leaves()
        leave_id = input("\nEnter the Leave ID to process: ").strip()

        # Check if the leave ID is valid and pending
        cursor.execute("SELECT leave_id FROM Leaves WHERE leave_id = ? AND status = 'PENDING'", (leave_id,))
        if not cursor.fetchone():
            print(colored("\nInvalid Leave ID or Leave is not pending.", "red"))
            conn.close()
            return

        decision = input("Approve or Reject the leave? (A/R): ").strip().upper()
        if decision not in ["A", "R"]:
            print(colored("\nInvalid choice! Enter 'A' for Approve or 'R' for Reject.", "red"))
            conn.close()
            return

        new_status = "APPROVED" if decision == "A" else "REJECTED"
        cursor.execute("UPDATE Leaves SET status = ? WHERE leave_id = ?", (new_status, leave_id))
        conn.commit()
        print(colored(f"\nLeave request {new_status} successfully!", "green"))

        conn.close()

    def view_employee_performance(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ep_id, employee_id, ratedbyhr_name, rating, comments 
            FROM Employee_performance
        """)
        performance_records = cursor.fetchall()

        if performance_records:
            print(colored("\nEmployee Performance Records:", "green"))
            print(tabulate(performance_records, headers=["EP ID", "Employee ID", "Rated by HR", "Rating", "Comments"], tablefmt="double_grid"))
        else:
            print(colored("\nNo performance records found.", "red"))

        conn.close()

    def remove_employee(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute("SELECT emp_id, name FROM Employee")
        employees = cursor.fetchall()

        if not employees:
            print(colored("\nNo employees found.", "red"))
            conn.close()
            return

        print(colored("\nEmployee List:", "cyan"))
        print(tabulate(employees, headers=["Employee ID", "Name"], tablefmt="double_grid"))

        while True:
            emp_id = input("\nEnter the Employee ID to remove: ").strip()

            # Validate input is numeric
            if not emp_id.isdigit():
                print(colored("\nInvalid input! Please enter a valid numeric Employee ID.", "red"))
                continue

            emp_id = int(emp_id)

            # Check if Employee ID exists
            cursor.execute("SELECT emp_id FROM Employee WHERE emp_id = ?", (emp_id,))
            if not cursor.fetchone():
                print(colored("\nEmployee ID not found! Please enter a valid ID from the list.", "red"))
                continue

            # Proceed with deletion
            cursor.execute("DELETE FROM Employee WHERE emp_id = ?", (emp_id,))
            conn.commit()
            print(colored(f"\nEmployee with ID {emp_id} has been removed successfully!", "green"))
            break

        conn.close()

# Login and menu loop
while True:
    manager = Manager.login()
    if manager:
        manager.run()
        break
