import sqlite3
import os
from tabulate import tabulate
from termcolor import colored
from datetime import datetime, date
import matplotlib.pyplot as plt


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
# -----------------------------------------------------------------------------------------------------------------------------------

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
# -----------------------------------------------------------------------------------------------------------------------------------

    def show_main_menu(self):
        options = [
            ["1", "Manage HRs"],
            ["2", "Manage Employees"],
            ["3", "Logout"]
        ]
        print(colored("\nManager Dashboard", "green", attrs=['bold']))
        print(tabulate(options, headers=[colored("Option", "cyan"), colored("Action", "yellow")], tablefmt="double_grid"))
# -----------------------------------------------------------------------------------------------------------------------------------
    
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

# -----------------------------------------------------------------------------------------------------------------------------------

    def add_hr(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        print(colored("\nAdd HR", "cyan"))

        # Name input validation
        while True:
            name = input("Enter HR Name: ").strip()
            if name.replace(" ", "").isalpha():
                break
            print(colored("\nInvalid name! Name should only contain letters.", "red"))

        # Email validation
        while True:
            email = input("Enter Email: ").strip()
            if "@" in email and "." in email.split("@")[-1]:
                break
            print(colored("\nInvalid email! Please enter a valid email address.", "red"))

        # Password input
        while True:
            password = input("Enter Password: ").strip()
            if len(password) >= 4:
                break
            print(colored("\nPassword too short! Must be at least 4 characters.", "red"))

        # Contact number validation (only 10 digits)
        while True:
            contactnumber = input("Enter Contact Number: ").strip()
            if contactnumber.isdigit() and len(contactnumber) == 10:
                break
            print(colored("\nInvalid contact number! Must be exactly 10 digits.", "red"))

        # Salary validation (should be a number)
        while True:
            salary = input("Enter Salary: ").strip()
            if salary.isdigit():
                salary = int(salary)
                break
            print(colored("\nInvalid salary! Salary must be a numeric value.", "red"))

        # Degree input without validation
        degree = input("Enter Degree: ").strip()

        # Insert data into HR table
        cursor.execute("INSERT INTO HR (name, email, password, contactnumber, salary, degree) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, email, password, contactnumber, salary, degree))
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

        # Get HR ID
        hr_id = input("\nEnter HR ID to update (or 'skip' to cancel): ").strip()
        if hr_id.lower() == "skip":
            print(colored("\nNo changes made.", "yellow"))
            conn.close()
            return

        if not hr_id.isdigit():
            print(colored("\nInvalid HR ID! Must be a numeric value.", "red"))
            conn.close()
            return

        cursor.execute("SELECT * FROM HR WHERE hr_id = ?", (hr_id,))
        if not cursor.fetchone():
            print(colored("\nHR ID not found!", "red"))
            conn.close()
            return

        # Collect updates
        email = input("Enter new Email (or 'skip' to keep unchanged): ").strip()
        contact = input("Enter new Contact Number (or 'skip' to keep unchanged): ").strip()
        salary = input("Enter new Salary (or 'skip' to keep unchanged): ").strip()
        degree = input("Enter new Degree (or 'skip' to keep unchanged): ").strip()

        # Prepare updates
        updates = []
        values = []

        if email.lower() != "skip":
            if "@" in email and "." in email.split("@")[-1]:
                updates.append("email = ?")
                values.append(email)
            else:
                print(colored("\nInvalid Email! Skipping email update.", "yellow"))

        if contact.lower() != "skip":
            if contact.isdigit() and len(contact) == 10:
                updates.append("contactnumber = ?")
                values.append(contact)
            else:
                print(colored("\nInvalid Contact Number! Skipping contact update.", "yellow"))

        if salary.lower() != "skip":
            if salary.isdigit():
                updates.append("salary = ?")
                values.append(int(salary))
            else:
                print(colored("\nInvalid Salary! Skipping salary update.", "yellow"))

        if degree.lower() != "skip":
            updates.append("degree = ?")
            values.append(degree)

        # Update if any changes
        if updates:
            query = f"UPDATE HR SET {', '.join(updates)} WHERE hr_id = ?"
            values.append(hr_id)
            cursor.execute(query, values)
            conn.commit()
            print(colored("\nHR details updated successfully!", "green"))
        else:
            print(colored("\nNo changes made.", "yellow"))

        conn.close()

    
# -----------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------

    def manage_employees(self):
        while True:
            options = [
                ["1", "Manage Employee Leaves"],
                ["2", "Manage Company Accounts Passwords"],
                ["3", "View Employee Performance"],
                ["4", "Remove an Employee"],
                ["5", "Generate Salary Report (Employees & HRs)"],
                ["6", "To Give Promotion [Increase Salary of Employees/HR]"],
                ["7", "View Employee Attendance Report"],
                ["8", "Back to Main Menu"]
            ]
            print(colored("\nManage Employees", "cyan", attrs=['bold']))
            print(tabulate(options, headers=[colored("Option", "cyan"), colored("Action", "yellow")], tablefmt="double_grid"))
            
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                self.manage_leaves()
            elif choice == "2":
                self.manage_company_passwords()
            elif choice == "3":
                self.view_employee_performance()
            elif choice == "4":
                self.remove_employee()
            elif choice == "5":
                self.generate_salary_report()
            elif choice == "6":
                self.promote_employee_or_hr()
            elif choice == "7":
                self.employee_attendance_report()
            elif choice == "8":
                break
            else:
                print(colored("\nInvalid choice or functionality not implemented yet!", "red"))
# -----------------------------------------------------------------------------------------------------------------------------------

    def manage_leaves(self):
        options = [
            ["1", "Approve/Reject Leave Requests"],
            ["2", "View Leave History"],
            ["3", "Back to Main Menu"]
        ]
        print(colored("\nManage Leaves of Employees", "green", attrs=['bold']))
        print(tabulate(options, headers=[colored("Option", "cyan"), colored("Action", "yellow")], tablefmt="double_grid"))

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            self.approve_or_reject_leave()
        elif choice == "2":
            self.view_leave_history()
        elif choice == "3":
            return
        else:
            print(colored("\nInvalid choice!", "red"))

    def approve_or_reject_leave(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Show pending leaves
        cursor.execute("""
            SELECT L.leave_id, E.name, L.leavetype, L.startdate, L.enddate, L.status
            FROM Leaves L
            JOIN Employee E ON L.emp_id = E.emp_id
            WHERE L.status = 'PENDING'
        """)
        pending_leaves = cursor.fetchall()

        if not pending_leaves:
            print(colored("\nNo pending leave requests.", "red"))
            conn.close()
            return  # Exit if no pending leaves

        print(colored("\nPending Leave Requests:", "green"))
        print(tabulate(pending_leaves, headers=["Leave ID", "Employee Name", "Leave Type", "Start Date", "End Date", "Status"], tablefmt="double_grid"))

        # Get Leave ID
        leave_id = input("\nEnter the Leave ID to process: ").strip()
        cursor.execute("SELECT leave_id FROM Leaves WHERE leave_id = ? AND status = 'PENDING'", (leave_id,))
        if not cursor.fetchone():
            print(colored("\nInvalid Leave ID or Leave is not pending.", "red"))
            conn.close()
            return

        # Approve or Reject
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

    def view_leave_history(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Display available employees with IDs
        cursor.execute("SELECT emp_id, name FROM Employee")
        employees = cursor.fetchall()

        if not employees:
            print(colored("\nNo employees found.", "red"))
            conn.close()
            return

        print(colored("\nAvailable Employees:", "cyan"))
        print(tabulate(employees, headers=["Employee ID", "Name"], tablefmt="double_grid"))

        # Get valid Employee ID
        emp_ids = [str(emp[0]) for emp in employees]
        emp_id = input("\nEnter Employee ID to view leave history: ").strip()

        if emp_id not in emp_ids:
            print(colored("\nInvalid Employee ID! Please select from the list above.", "red"))
            conn.close()
            return

        # Fetch leave history
        cursor.execute("""
            SELECT L.leave_id, E.name, L.leavetype, L.startdate, L.enddate, L.status
            FROM Leaves L
            JOIN Employee E ON L.emp_id = E.emp_id
            WHERE L.emp_id = ?
        """, (emp_id,))
        leave_history = cursor.fetchall()

        # Display leave history
        if leave_history:
            print(colored(f"\nLeave History for Employee ID {emp_id}:", "green"))
            print(tabulate(leave_history, headers=["Leave ID", "Employee Name", "Leave Type", "Start Date", "End Date", "Status"], tablefmt="double_grid"))

            # Option to save to file
            if input("\nWould you like to save this report to a file? (yes/no): ").strip().lower() == "yes":
                filename = f"Leave_History_EmpID_{emp_id}.txt"
                with open(filename, "w") as file:
                    file.write(f"Leave History for Employee ID {emp_id}\n\n")
                    file.write(tabulate(leave_history, headers=["Leave ID", "Employee Name", "Leave Type", "Start Date", "End Date", "Status"], tablefmt="grid"))
                print(colored(f"\nLeave history saved to {filename}!", "green"))
        else:
            print(colored("\nNo leave history found for the given Employee ID.", "red"))

        conn.close()
# -----------------------------------------------------------------------------------------------------------------------------------

    def manage_company_passwords(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        while True:
            print(colored("\nManage Company Passwords", "cyan"))
            print(tabulate([
                ["1", "Change HR Password"],
                ["2", "Change Employee Password"],
                ["3", "Change Own (Manager) Password"],
                ["4", "Exit"]
            ], headers=["Option", "Action"], tablefmt="double_grid"))

            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == "1":
                # Show available HRs
                cursor.execute("SELECT hr_id, name FROM HR")
                hrs = cursor.fetchall()
                print(colored("\nAvailable HRs:", "cyan"))
                print(tabulate(hrs, headers=["HR ID", "Name"], tablefmt="double_grid"))

                hr_id = input("\nEnter HR ID to change password: ").strip()
                cursor.execute("SELECT password FROM HR WHERE hr_id = ?", (hr_id,))
                current_password = cursor.fetchone()

                if current_password:
                    print(colored(f"\nCurrent HR Password: {current_password[0]}", "yellow"))
                    while True:
                        new_password = input("Enter new Password: ").strip()
                        if len(new_password) >= 4:
                            cursor.execute("UPDATE HR SET password = ? WHERE hr_id = ?", (new_password, hr_id))
                            conn.commit()
                            print(colored("\nHR password updated successfully!", "green"))
                            break
                        print(colored("\nPassword too short! Must be at least 4 characters.", "red"))
                else:
                    print(colored("\nInvalid HR ID!", "red"))

            elif choice == "2":
                # Show available Employees
                cursor.execute("SELECT emp_id, name FROM Employee")
                emps = cursor.fetchall()
                print(colored("\nAvailable Employees:", "cyan"))
                print(tabulate(emps, headers=["Employee ID", "Name"], tablefmt="double_grid"))

                emp_id = input("\nEnter Employee ID to change password: ").strip()
                cursor.execute("SELECT password FROM Employee WHERE emp_id = ?", (emp_id,))
                current_password = cursor.fetchone()

                if current_password:
                    print(colored(f"\nCurrent Employee Password: {current_password[0]}", "yellow"))
                    while True:
                        new_password = input("Enter new Password: ").strip()
                        if len(new_password) >= 4:
                            cursor.execute("UPDATE Employee SET password = ? WHERE emp_id = ?", (new_password, emp_id))
                            conn.commit()
                            print(colored("\nEmployee password updated successfully!", "green"))
                            break
                        print(colored("\nPassword too short! Must be at least 4 characters.", "red"))
                else:
                    print(colored("\nInvalid Employee ID!", "red"))

            elif choice == "3":
                # Change Manager password
                cursor.execute("SELECT password FROM Manager WHERE id = 1")
                current_password = cursor.fetchone()

                print(colored(f"\nCurrent Manager Password: {current_password[0]}", "yellow"))
                while True:
                    new_password = input("Enter new Password: ").strip()
                    if len(new_password) >= 4:
                        cursor.execute("UPDATE Manager SET password = ? WHERE id = 1", (new_password,))
                        conn.commit()
                        print(colored("\nManager password updated successfully!", "green"))
                        break
                    print(colored("\nPassword too short! Must be at least 4 characters.", "red"))

            elif choice == "4":
                print(colored("\nExiting password management...", "yellow"))
                break

            else:
                print(colored("\nInvalid choice! Please enter a number between 1 and 4.", "red"))

        conn.close()

# -----------------------------------------------------------------------------------------------------------------------------------

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
# -----------------------------------------------------------------------------------------------------------------------------------

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
# -----------------------------------------------------------------------------------------------------------------------------------

    def generate_salary_report(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        while True:
            print(colored("\nGenerate Salary Report", "cyan"))
            print(tabulate([
                ["1", "Employee Salary Report"],
                ["2", "HR Salary Report"],
                ["3", "Exit"]
            ], headers=["Option", "Report Type"], tablefmt="double_grid"))

            choice = input("\nEnter your choice (1-3): ").strip()

            if choice == "1":
                # Employee Salary Report
                cursor.execute("SELECT DISTINCT department FROM Employee LIMIT 5")
                departments = cursor.fetchall()

                if not departments:
                    print(colored("\nNo departments found.", "red"))
                    continue

                print(colored("\nAvailable Departments:", "green"))
                print(tabulate(departments, headers=["Department"], tablefmt="double_grid"))

                selected_department = input("\nEnter the department to generate the salary report: ").strip()

                cursor.execute("""
                    SELECT department, SUM(salary)
                    FROM Employee
                    WHERE department = ?
                    GROUP BY department
                """, (selected_department,))
                result = cursor.fetchone()

                if not result:
                    print(colored(f"\nNo salary data found for department: {selected_department}", "red"))
                    continue

                # Plotting
                departments = [result[0]]
                salaries = [result[1]]

                plt.bar(departments, salaries, color='skyblue')
                plt.title(f'Salary Report for {selected_department}')
                plt.xlabel('Department')
                plt.ylabel('Total Salary (INR)')
                plt.show()

            elif choice == "2":
                # HR Salary Report
                cursor.execute("SELECT hr_id, salary FROM HR")
                hr_data = cursor.fetchall()

                if not hr_data:
                    print(colored("\nNo HR salary data found.", "red"))
                    continue

                print(colored("\nHR Salary Data:", "green"))
                print(tabulate(hr_data, headers=["HR ID", "Salary (INR)"], tablefmt="double_grid"))

                hr_ids = [str(row[0]) for row in hr_data]
                salaries = [row[1] for row in hr_data]

                plt.bar(hr_ids, salaries, color='orange')
                plt.title('HR Salary Report')
                plt.xlabel('HR ID')
                plt.ylabel('Salary (INR)')
                plt.show()

            elif choice == "3":
                print(colored("\nExiting salary report generation...", "yellow"))
                break

            else:
                print(colored("\nInvalid choice! Please enter a number between 1 and 3.", "red"))

        conn.close()
# -----------------------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------------------

    def promote_employee_or_hr(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        while True:
            print(colored("\nPromotion Menu:", "green"))
            print("1) Promote HR\n2) Promote Employee\n3) Exit")

            choice = input("\nEnter your choice (1/2/3): ").strip()
            if choice == "3":
                break
            elif choice not in ["1", "2"]:
                print(colored("\nInvalid choice! Please enter 1, 2, or 3.", "red"))
                continue

            if choice == "1":  # Promote HR
                cursor.execute("SELECT hr_id, name, salary FROM HR")
                hrs = cursor.fetchall()

                if not hrs:
                    print(colored("\nNo HR available for promotion.", "red"))
                    continue

                print(colored("\nAvailable HR for Promotion:", "green"))
                print(tabulate(hrs, headers=["HR ID", "Name", "Current Salary (INR)"], tablefmt="double_grid"))

                hr_ids = [str(hr[0]) for hr in hrs]
                hr_id = input("\nEnter HR ID to promote: ").strip()
                if hr_id not in hr_ids:
                    print(colored("\nInvalid HR ID. Please select from the list.", "red"))
                    continue

                current_salary = next(hr[2] for hr in hrs if str(hr[0]) == hr_id)
                print(colored(f"\nCurrent Salary for HR ID {hr_id}: INR {current_salary}", "yellow"))

                while True:
                    new_salary = input("Enter new salary (must be higher than current salary): ").strip()
                    if not new_salary:
                        print(colored("\nSalary cannot be empty. Please enter a value.", "red"))
                        continue

                    try:
                        new_salary = float(new_salary)
                        if new_salary <= current_salary:
                            print(colored("\nNew salary must be greater than the current salary!", "red"))
                            continue

                        cursor.execute("UPDATE HR SET salary = ? WHERE hr_id = ?", (new_salary, hr_id))
                        conn.commit()
                        print(colored("\nHR salary updated successfully!", "green"))
                        break
                    except ValueError:
                        print(colored("\nInvalid salary amount. Please enter a valid number.", "red"))

            elif choice == "2":  # Promote Employee
                cursor.execute("SELECT emp_id, name, department, position, salary FROM Employee")
                employees = cursor.fetchall()

                if not employees:
                    print(colored("\nNo employees available for promotion.", "red"))
                    continue

                print(colored("\nAvailable Employees for Promotion:", "green"))
                print(tabulate(employees, headers=["Emp ID", "Name", "Department", "Position", "Current Salary (INR)"], tablefmt="double_grid"))

                emp_ids = [str(emp[0]) for emp in employees]
                emp_id = input("\nEnter Employee ID to promote: ").strip()
                if emp_id not in emp_ids:
                    print(colored("\nInvalid Employee ID. Please select from the list.", "red"))
                    continue

                current_salary = next(emp[4] for emp in employees if str(emp[0]) == emp_id)
                print(colored(f"\nCurrent Salary for Employee ID {emp_id}: INR {current_salary}", "yellow"))

                while True:
                    new_salary = input("Enter new salary (must be higher than current salary): ").strip()
                    if not new_salary:
                        print(colored("\nSalary cannot be empty. Please enter a value.", "red"))
                        continue

                    try:
                        new_salary = float(new_salary)
                        if new_salary <= current_salary:
                            print(colored("\nNew salary must be greater than the current salary!", "red"))
                            continue

                        cursor.execute("UPDATE Employee SET salary = ? WHERE emp_id = ?", (new_salary, emp_id))
                        conn.commit()
                        print(colored("\nEmployee salary updated successfully!", "green"))
                        break
                    except ValueError:
                        print(colored("\nInvalid salary amount. Please enter a valid number.", "red"))

        conn.close()

# -----------------------------------------------------------------------------------------------------------------------------------

    def employee_attendance_report(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Ask for the date to filter attendance records
        while True:
            date = input("\nEnter the date to view attendance (YYYY-MM-DD): ").strip()
            if not date:
                print(colored("\nDate cannot be empty. Please enter a valid date.", "red"))
                continue
            
            # Check if records exist for the entered date
            cursor.execute("""
                SELECT emp_id, SUM(total_work_hours)
                FROM Employee_Attendance
                WHERE date = ?
                GROUP BY emp_id
            """, (date,))
            attendance_data = cursor.fetchall()

            if attendance_data:
                break
            else:
                print(colored(f"\nNo attendance data found for {date}. Please enter a valid date.", "red"))

        # Display attendance data in a table
        print(colored(f"\nEmployee Attendance Report for {date}:", "green"))
        print(tabulate(attendance_data, headers=["Employee ID", "Total Working Hours"], tablefmt="double_grid"))

        # Extract employee IDs and work hours for plotting
        emp_ids = [str(row[0]) for row in attendance_data]
        work_hours = [row[1] for row in attendance_data]

        # Plotting the bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(emp_ids, work_hours, color='skyblue')
        plt.title(f'Employee Attendance Report - {date}')
        plt.xlabel('Employee ID')
        plt.ylabel('Total Working Hours')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        conn.close()
# -----------------------------------------------------------------------------------------------------------------------------------


# Login and menu loop
while True:
    manager = Manager.login()
    if manager:
        manager.run()
        break
