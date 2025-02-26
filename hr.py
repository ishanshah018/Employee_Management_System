import sqlite3
import os
from tabulate import tabulate
from termcolor import colored
from datetime import date
import matplotlib.pyplot as plt


class HR:
    def __init__(self, hr_id, name):
        self.hr_id = hr_id
        self.name = name
        self.db = 'ems_data.db'

    @staticmethod
    def login():
        conn = sqlite3.connect('ems_data.db')
        cursor = conn.cursor()

        print(colored("\nHR Login", "cyan", attrs=['bold']))
        hr_id = input("Enter your HR ID: ").strip()
        password = input("Enter your Password: ").strip()

        cursor.execute("SELECT hr_id, name FROM HR WHERE hr_id = ? AND password = ?", (hr_id, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            print(colored(f"\nLogin successful! Welcome, {user[1]}.", "green", attrs=['bold']))
            return HR(user[0], user[1])
        else:
            print(colored("\nInvalid HR ID or Password. Please try again.", "red", attrs=['bold']))
            return None

    def show_menu(self):
        options = [
            ["1", "Manage Employees"],
            ["2", "Manage Leaves of Employees"],
            ["3", "Manage Salary of Employees"],
            ["4", "Generate Salary Report"],
            ["5", "Job Posting"],
            ["6", "Employee Rating"],
            ["7", "Employee Attendance Report"],
            ["8", "Logout"]
        ]
        print(colored("\nHR Menu", "green", attrs=['bold']))
        print(tabulate(options, headers=[colored("Option", "cyan"), colored("Action", "yellow")], tablefmt="double_grid"))

    # --------- Manage Employees --------- #

    def add_employee(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Fixed departments and positions
        departments = {
            "IT": ["Software Engineer", "Data Analyst", "System Admin", "Backend Developer", "QA Engineer"],
            "Finance": ["Accountant", "Financial Analyst", "Auditor", "Finance Manager"],
            "Marketing": ["Marketing Executive", "SEO Specialist", "Content Strategist", "Brand Manager"],
            "Operations": ["Operations Manager", "Logistics Coordinator", "Inventory Manager", "Supply Chain Analyst"]
        }

        print(colored("\nAdd New Employee", "cyan", attrs=['bold']))
        name = input("Enter Name: ").strip()
        password = input("Enter Password: ").strip()
        age = input("Enter Age: ").strip()
        gender = input("Enter Gender (Male/Female): ").strip()
        address = input("Enter Address: ").strip()

        # Display departments
        print(colored("\nAvailable Departments:", "green"))
        print(tabulate([[d] for d in departments.keys()], headers=["Department"], tablefmt="double_grid"))

        department = input("\nSelect a Department: ").strip()
        if department not in departments:
            print(colored("\nInvalid Department! Please select from the available options.", "red"))
            conn.close()
            return

        # Display positions based on chosen department
        print(colored(f"\nAvailable Positions in {department}:", "cyan"))
        print(tabulate([[p] for p in departments[department]], headers=["Position"], tablefmt="double_grid"))

        position = input("\nSelect a Position: ").strip()
        if position not in departments[department]:
            print(colored("\nInvalid Position! Please select from the available options.", "red"))
            conn.close()
            return

        salary = input("Enter Salary: ").strip()
        if not salary.isdigit() or int(salary) <= 0:
            print(colored("\nInvalid Salary! Please enter a positive number.", "red"))
            conn.close()
            return

        email = input("Enter Email: ").strip()
        contactnumber = input("Enter Contact Number: ").strip()
        joining_date = str(date.today())
        degree = input("Enter Degree: ").strip()

        try:
            cursor.execute("""
                INSERT INTO Employee (name, password, age, gender, address, department, position, salary, email, contactnumber, joining_date, degree)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, password, age, gender, address, department, position, salary, email, contactnumber, joining_date, degree))
            conn.commit()
            print(colored("\nEmployee added successfully!", "green"))
        except sqlite3.IntegrityError:
            print(colored("\nError: Email or contact number already exists!", "red"))

        conn.close()

    def delete_employee(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute("SELECT emp_id, name FROM Employee")
        employees = cursor.fetchall()

        if not employees:
            print(colored("\nNo employees found.", "red"))
            conn.close()
            return

        print(colored("\nCurrent Employees:", "green"))
        print(tabulate(employees, headers=["Employee ID", "Name"], tablefmt="double_grid"))

        emp_id = input("\nEnter the Employee ID to delete: ").strip()
        cursor.execute("SELECT * FROM Employee WHERE emp_id = ?", (emp_id,))
        if not cursor.fetchone():
            print(colored("\nInvalid Employee ID!", "red"))
        else:
            cursor.execute("DELETE FROM Employee WHERE emp_id = ?", (emp_id,))
            conn.commit()
            print(colored("\nEmployee deleted successfully!", "green"))

        conn.close()

    def update_employee(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute("SELECT emp_id, name FROM Employee")
        employees = cursor.fetchall()

        if not employees:
            print(colored("\nNo employees found.", "red"))
            conn.close()
            return

        print(colored("\nCurrent Employees:", "green"))
        print(tabulate(employees, headers=["Employee ID", "Name"], tablefmt="double_grid"))

        emp_id = input("\nEnter the Employee ID to update: ").strip()
        cursor.execute("SELECT * FROM Employee WHERE emp_id = ?", (emp_id,))
        if not cursor.fetchone():
            print(colored("\nInvalid Employee ID!", "red"))
            conn.close()
            return

        print(colored("\nUpdate Employee Details (Leave blank to skip):", "cyan"))

        password = input("Enter new Password: ").strip()
        age = input("Enter new Age: ").strip()
        email = input("Enter new Email: ").strip()
        contactnumber = input("Enter new Contact Number: ").strip()
        degree = input("Enter new Degree: ").strip()

        updates = {}
        if password: updates["password"] = password
        if age: updates["age"] = age
        if email: updates["email"] = email
        if contactnumber: updates["contactnumber"] = contactnumber
        if degree: updates["degree"] = degree

        if updates:
            query = "UPDATE Employee SET " + ", ".join(f"{col} = ?" for col in updates.keys()) + " WHERE emp_id = ?"
            values = list(updates.values()) + [emp_id]
            cursor.execute(query, values)
            conn.commit()
            print(colored("\nEmployee details updated successfully!", "green"))
        else:
            print(colored("\nNo updates made.", "yellow"))

        conn.close()

    def search_employee(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        print(colored("\nSearch Employee", "cyan"))
        search_by = input("Search by (1: ID, 2: Name): ").strip()

        if search_by == "1":
            emp_id = input("Enter Employee ID: ").strip()
            cursor.execute("SELECT * FROM Employee WHERE emp_id = ?", (emp_id,))
        elif search_by == "2":
            name = input("Enter Employee Name: ").strip()
            cursor.execute("SELECT * FROM Employee WHERE name LIKE ?", ('%' + name + '%',))
        else:
            print(colored("\nInvalid choice!", "red"))
            conn.close()
            return

        result = cursor.fetchall()
        if result:
            print(colored("\nEmployee Details:", "green"))
            print(tabulate(result, headers=["ID", "Name", "Password", "Age", "Gender", "Address", "Dept", "Position", "Salary", "Email", "Contact", "Join Date", "Degree"], tablefmt="double_grid"))
        else:
            print(colored("\nNo employee found!", "red"))

        conn.close()


    def manage_employees(self):
        options = [
            ["1", "Add Employee"],
            ["2", "Delete Employee"],
            ["3", "Update Employee"],
            ["4", "Search Employee"],
            ["5", "Back to Main Menu"]
        ]
        print(colored("\nManage Employees", "green", attrs=['bold']))
        print(tabulate(options, headers=[colored("Option", "cyan"), colored("Action", "yellow")], tablefmt="double_grid"))

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            self.add_employee()
        elif choice == "2":
            self.delete_employee()
        elif choice == "3":
            self.update_employee()
        elif choice == "4":
            self.search_employee()
        elif choice == "5":
            return
        else:
            print(colored("\nInvalid choice!", "red"))

    # --------- Manage Leaves of Employees --------- #

    def manage_leaves(self):
        options = [
            ["1", "View Pending Leaves"],
            ["2", "Approve/Reject Leave Requests"],
            ["3", "View Leave History"],
            ["4", "Back to Main Menu"]
        ]
        print(colored("\nManage Leaves of Employees", "green", attrs=['bold']))
        print(tabulate(options, headers=[colored("Option", "cyan"), colored("Action", "yellow")], tablefmt="double_grid"))

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            self.view_pending_leaves()
        elif choice == "2":
            self.approve_or_reject_leave()
        elif choice == "3":
            self.view_leave_history()
        elif choice == "4":
            return
        else:
            print(colored("\nInvalid choice!", "red"))

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

            # Ask if HR wants to save to file
            save_to_file = input("\nWould you like to save this report to a file? (yes/no): ").strip().lower()
            if save_to_file == "yes":
                filename = f"Leave_History_EmpID_{emp_id}.txt"
                with open(filename, "w") as file:
                    file.write(f"Leave History for Employee ID {emp_id}\n\n")
                    file.write(tabulate(leave_history, headers=["Leave ID", "Employee Name", "Leave Type", "Start Date", "End Date", "Status"], tablefmt="grid"))
                print(colored(f"\nLeave history saved to {filename}!", "green"))
        else:
            print(colored("\nNo leave history found for the given Employee ID.", "red"))

        conn.close()


        # --------- Manage Salary of Employees --------- #

    def manage_salaries(self):
        options = [
            ["1", "View Employee Salary"],
            ["2", "Update Employee Salary"],
            ["3", "Back to Main Menu"]
        ]
        print(colored("\nManage Salaries of Employees", "green", attrs=['bold']))
        print(tabulate(options, headers=[colored("Option", "cyan"), colored("Action", "yellow")], tablefmt="double_grid"))

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            self.view_salary()
        elif choice == "2":
            self.update_salary()
        elif choice == "3":
            return
        else:
            print(colored("\nInvalid choice!", "red"))

    # View Employee Salary
    def view_salary(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Show all employee IDs and names
        cursor.execute("SELECT emp_id, name FROM Employee")
        employees = cursor.fetchall()

        if not employees:
            print(colored("\nNo employees found.", "red"))
            conn.close()
            return

        print(colored("\nAvailable Employees:", "green"))
        print(tabulate(employees, headers=["Employee ID", "Name"], tablefmt="double_grid"))

        # Ask for Employee ID to view salary
        emp_id = input("\nEnter Employee ID to view salary: ").strip()

        # Fetch salary for the chosen employee
        cursor.execute("SELECT emp_id, name, salary FROM Employee WHERE emp_id = ?", (emp_id,))
        employee = cursor.fetchone()

        if employee:
            print(colored(f"\nSalary Details for {employee[1]}:", "green"))
            print(tabulate([employee], headers=["Employee ID", "Name", "Salary"], tablefmt="double_grid"))
        else:
            print(colored("\nInvalid Employee ID!", "red"))

        conn.close()

    # Update Employee Salary
    def update_salary(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Show all employee IDs and names
        cursor.execute("SELECT emp_id, name FROM Employee")
        employees = cursor.fetchall()

        if not employees:
            print(colored("\nNo employees found.", "red"))
            conn.close()
            return

        print(colored("\nAvailable Employees:", "green"))
        print(tabulate(employees, headers=["Employee ID", "Name"], tablefmt="double_grid"))

        # Ask for Employee ID to update salary
        emp_id = input("\nEnter Employee ID to update salary: ").strip()

        # Fetch current salary
        cursor.execute("SELECT emp_id, name, salary FROM Employee WHERE emp_id = ?", (emp_id,))
        employee = cursor.fetchone()

        if not employee:
            print(colored("\nInvalid Employee ID!", "red"))
            conn.close()
            return

        print(colored(f"\nCurrent Salary Details for {employee[1]}:", "cyan"))
        print(tabulate([employee], headers=["Employee ID", "Name", "Current Salary"], tablefmt="double_grid"))

        # Ask for new salary
        new_salary = input("\nEnter new salary: ").strip()
        if not new_salary.isdigit() or int(new_salary) <= 0:
            print(colored("\nInvalid salary amount! Please enter a positive number.", "red"))
            conn.close()
            return

        # Update salary in Employee table
        cursor.execute("UPDATE Employee SET salary = ? WHERE emp_id = ?", (new_salary, emp_id))
        conn.commit()
        print(colored(f"\nSalary updated successfully to {new_salary}!", "green"))

        conn.close()

    def generate_salary_report(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Get distinct departments
        cursor.execute("SELECT DISTINCT department FROM Employee LIMIT 5")
        departments = cursor.fetchall()

        if not departments:
            print(colored("\nNo departments found.", "red"))
            conn.close()
            return

        # Display departments
        print(colored("\nAvailable Departments:", "green"))
        print(tabulate(departments, headers=["Department"], tablefmt="double_grid"))

        # Ask HR for department selection
        selected_department = input("\nEnter the department to generate the salary report: ").strip()

        # Calculate total salary by department
        cursor.execute("""
            SELECT department, SUM(salary)
            FROM Employee
            WHERE department = ?
            GROUP BY department
        """, (selected_department,))
        result = cursor.fetchone()

        if not result:
            print(colored(f"\nNo salary data found for department: {selected_department}", "red"))
            conn.close()
            return

        # Plotting the salary report
        departments = [result[0]]
        salaries = [result[1]]

        plt.bar(departments, salaries, color='skyblue')
        plt.title(f'Salary Report for {selected_department}')
        plt.xlabel('Department')
        plt.ylabel('Total Salary (INR)')
        plt.show()

        conn.close()

        # --------- Job Posting --------- #

    def job_posting(self):
        departments = ["IT", "Finance", "Marketing", "Operations"]
        positions = {
            "IT": ["Software Engineer", "Data Analyst", "System Admin", "Backend Developer", "QA Engineer"],
            "Finance": ["Accountant", "Financial Analyst", "Auditor", "Finance Manager"],
            "Marketing": ["Marketing Executive", "SEO Specialist", "Content Strategist", "Brand Manager"],
            "Operations": ["Operations Manager", "Logistics Coordinator", "Inventory Manager", "Supply Chain Analyst"]
        }

        print(colored("\nAvailable Departments:", "green"))
        print(tabulate([[d] for d in departments], headers=["Department"], tablefmt="double_grid"))

        selected_department = input("\nSelect a department: ").strip()

        if selected_department not in departments:
            print(colored("\nInvalid department choice!", "red"))
            return

        print(colored(f"\nAvailable Positions in {selected_department}:", "cyan"))
        print(tabulate([[p] for p in positions[selected_department]], headers=["Position"], tablefmt="double_grid"))

        selected_position = input("\nSelect a position: ").strip()

        if selected_position not in positions[selected_department]:
            print(colored("\nInvalid position choice!", "red"))
            return

        no_of_positions = input("Enter the number of positions: ").strip()

        if not no_of_positions.isdigit() or int(no_of_positions) <= 0:
            print(colored("\nInvalid number of positions!", "red"))
            return

        # Insert into Job_posting table
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Job_posting (department, position, no_of_positions)
            VALUES (?, ?, ?)
        """, (selected_department, selected_position, no_of_positions))
        conn.commit()
        conn.close()

        print(colored("\nJob posting added successfully!", "green"))

        # --------- Employee Rating --------- #

    def employee_rating(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Fetch employees
        cursor.execute("SELECT emp_id, name FROM Employee")
        employees = cursor.fetchall()

        if not employees:
            print(colored("\nNo employees found.", "red"))
            conn.close()
            return

        print(colored("\nAvailable Employees:", "green"))
        print(tabulate(employees, headers=["Employee ID", "Name"], tablefmt="double_grid"))

        emp_id = input("\nEnter Employee ID to rate: ").strip()

        # Validate employee ID
        cursor.execute("SELECT emp_id FROM Employee WHERE emp_id = ?", (emp_id,))
        if not cursor.fetchone():
            print(colored("\nInvalid Employee ID!", "red"))
            conn.close()
            return

        rating = input("Enter Rating (1-5): ").strip()
        if rating not in ["1", "2", "3", "4", "5"]:
            print(colored("\nInvalid rating! Please enter a value between 1-5.", "red"))
            conn.close()
            return

        comments = input("Enter Comments: ").strip()

        # Insert into Employee_performance table
        cursor.execute("""
            INSERT INTO Employee_performance (employee_id, ratedbyhr_name, rating, comments)
            VALUES (?, ?, ?, ?)
        """, (emp_id, self.name, rating, comments))
        conn.commit()
        conn.close()

        print(colored("\nEmployee rating submitted successfully!", "green"))

    def employee_attendance_report(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Fetch total work hours grouped by emp_id
        cursor.execute("""
            SELECT emp_id, SUM(total_work_hours)
            FROM Employee_Attendance
            GROUP BY emp_id
        """)
        attendance_data = cursor.fetchall()

        if not attendance_data:
            print(colored("\nNo attendance data found.", "red"))
            conn.close()
            return

        # Extract employee IDs and work hours
        emp_ids = [str(row[0]) for row in attendance_data]
        work_hours = [row[1] for row in attendance_data]

        # Plotting the bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(emp_ids, work_hours, color='skyblue')
        plt.title('Employee Attendance Report')
        plt.xlabel('Employee ID')
        plt.ylabel('Total Working Hours')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        conn.close()

    def run(self):
        while True:
            self.show_menu()
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.manage_employees()
            elif choice == "2":
                self.manage_leaves()
            elif choice == "3":
                self.manage_salaries()
            elif choice == "4":
                self.generate_salary_report()
            elif choice == "5":
                self.job_posting()
            elif choice == "6":
                self.employee_rating()
            elif choice == "7":
                self.employee_attendance_report()
                break
            elif choice == "8":
                print(colored("\nLogging out...", "cyan"))
                break
            else:
                print(colored("\nInvalid choice! Please try again.", "red"))

# Login and menu loop
while True:
    hr = HR.login()
    if hr:
        hr.run()
        break