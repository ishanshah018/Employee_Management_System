import sqlite3
import os
from tabulate import tabulate
from termcolor import colored
from datetime import datetime, date

class Employee:
    def __init__(self, emp_id, name):
        self.emp_id = emp_id
        self.name = name
        self.db = 'ems_data.db'

    @staticmethod
    def login():
        conn = sqlite3.connect('ems_data.db')
        cursor = conn.cursor()

        print(colored("\nEmployee Login", "cyan", attrs=['bold']))
        emp_id = input("Enter your Employee ID: ").strip()
        password = input("Enter your Password: ").strip()

        cursor.execute("SELECT emp_id, name FROM Employee WHERE emp_id = ? AND password = ?", (emp_id, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            print(colored(f"\nLogin successful! Welcome, {user[1]}.", "green", attrs=['bold']))
            return Employee(user[0], user[1])
        else:
            print(colored("\nInvalid Employee ID or Password. Please try again.", "red", attrs=['bold']))
            return None

    def show_menu(self):
        options = [
            ["1", "Mark Attendance"],
            ["2", "Apply Leave"],
            ["3", "View Applied Leaves"],
            ["4", "Check Salary"],
            ["5", "Request Job Position Change"],
            ["6", "View & Update Your Profile"],
            ["7", "Logout"]
        ]
        print(colored("\nEmployee Menu", "green", attrs=['bold']))
        print(tabulate(options, headers=[colored("Option", "cyan"), colored("Action", "yellow")], tablefmt="double_grid"))

    def mark_attendance(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        print(colored("\n1) Check-in", "cyan"))
        print(colored("2) Check-out", "red"))

        choice = input("Enter your choice (1/2): ").strip()

        today_date = date.today().isoformat()
        now_time = datetime.now().strftime("%H:%M:%S")

        if choice == "1":
            cursor.execute(
                "INSERT INTO Employee_Attendance (emp_id, date, check_in_time) VALUES (?, ?, ?)",
                (self.emp_id, today_date, now_time)
            )
            conn.commit()
            print(colored("\nCheck-in recorded successfully!", "green"))

        elif choice == "2":
            cursor.execute(
                "SELECT check_in_time FROM Employee_Attendance WHERE emp_id = ? AND date = ?",
                (self.emp_id, today_date)
            )
            check_in = cursor.fetchone()
            
            if check_in:
                check_in_time = datetime.strptime(check_in[0], "%H:%M:%S")
                check_out_time = datetime.strptime(now_time, "%H:%M:%S")
                total_hours = (check_out_time - check_in_time).seconds / 3600
                status = "Full Day" if total_hours >= 8 else "Half Day"

                cursor.execute(
                    "UPDATE Employee_Attendance SET check_out_time = ?, total_work_hours = ?, type = ? WHERE emp_id = ? AND date = ?",
                    (now_time, total_hours, status, self.emp_id, today_date)
                )
                conn.commit()
                print(colored(f"\nCheck-out recorded! Total hours worked: {total_hours:.2f}. Status: {status}", "green"))
            else:
                print(colored("\nYou must check-in first!", "red"))

        else:
            print(colored("\nInvalid choice!", "red"))

        conn.close()

    def apply_leave(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        leave_types = [["1", "Sick Leave"], ["2", "Vacation Leave"], ["3", "Casual Leave"]]
        print(tabulate(leave_types, headers=[colored("Option", "cyan"), colored("Leave Type", "yellow")], tablefmt="double_grid"))

        choice = input("Select Leave Type (1/2/3): ").strip()
        leave_type = {"1": "Sick Leave", "2": "Vacation Leave", "3": "Casual Leave"}.get(choice)

        if not leave_type:
            print(colored("\nInvalid choice!", "red"))
            return

        start_date = input("Enter Start Date (YYYY-MM-DD): ").strip()
        end_date = input("Enter End Date (YYYY-MM-DD): ").strip()

        if start_date < str(date.today()) or end_date < start_date:
            print(colored("\nInvalid dates! Start date must be after today and end date after start date.", "red"))
            return

        cursor.execute(
            "INSERT INTO Leaves (emp_id, leavetype, startdate, enddate, status) VALUES (?, ?, ?, ?, ?)",
            (self.emp_id, leave_type, start_date, end_date, "PENDING")
        )
        conn.commit()
        conn.close()

        print(colored("\nLeave request submitted successfully! Status: PENDING", "green"))

    def view_applied_leaves(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute("SELECT leavetype, startdate, enddate, status FROM Leaves WHERE emp_id = ?", (self.emp_id,))
        leaves = cursor.fetchall()

        if leaves:
            print(colored("\nYour Applied Leaves:", "green"))
            print(tabulate(leaves, headers=["Leave Type", "Start Date", "End Date", "Status"], tablefmt="double_grid"))
        else:
            print(colored("\nNo applied leaves found.", "red"))

        conn.close()

    def check_salary(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        cursor.execute("SELECT salary FROM Employee WHERE emp_id = ?", (self.emp_id,))
        salary = cursor.fetchone()

        if salary:
            print(colored(f"\nYour current salary is: {salary[0]} USD", "green"))
        else:
            print(colored("\nSalary details not found.", "red"))

        conn.close()

    def request_job_position_change(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Fetch current employee's department and position
        cursor.execute("SELECT department, position FROM Employee WHERE emp_id = ?", (self.emp_id,))
        current_data = cursor.fetchone()
        current_department, current_position = current_data

        print(colored("\nYour Current Details:", "cyan"))
        print(tabulate([[current_department, current_position]], headers=["Department", "Position"], tablefmt="double_grid"))

        # Fetch job postings only from employee's department
        cursor.execute("SELECT posting_id, department, position, no_of_positions FROM Job_posting WHERE department = ?", (current_department,))
        job_postings = cursor.fetchall()

        if not job_postings:
            print(colored(f"\nNo job postings available in your department ({current_department}).", "red"))
            conn.close()
            return

        print(colored(f"\nAvailable Job Postings in {current_department}:", "green"))
        print(tabulate(job_postings, headers=["Posting ID", "Department", "Position", "No. of Positions"], tablefmt="double_grid"))

        # Ask user for new position
        new_position = input("\nEnter the new position you want to apply for: ").strip()

        # Validate new_position exists in job postings for the employee's department
        valid_positions = [job[2] for job in job_postings]
        if new_position not in valid_positions:
            print(colored("\nInvalid position! Choose a position from the available job postings in your department.", "red"))
            conn.close()
            return

        # Insert into Job_Position_Change_Request table with 'PENDING' status
        cursor.execute(
            "INSERT INTO Job_Position_Change_Request (emp_id, department, old_position, new_position, status) VALUES (?, ?, ?, ?, ?)",
            (self.emp_id, current_department, current_position, new_position, "PENDING")
        )
        conn.commit()
        conn.close()

        print(colored("\nJob Position Change Request Submitted Successfully! Status: PENDING", "green"))

    def view_and_update_profile(self):
        conn = sqlite3.connect(self.db)
        cursor = conn.cursor()

        # Fetch employee details
        cursor.execute(
            "SELECT age, gender, address, department, position, salary, email, contactnumber, joining_date, degree FROM Employee WHERE emp_id = ?",
            (self.emp_id,)
        )
        data = cursor.fetchone()

        headers = ["Age", "Gender", "Address", "Department", "Position", "Salary", "Email", "Contact No.", "Joining Date", "Degree"]
        print(colored("\nYour Profile Details:", "green"))
        print(tabulate([data], headers=headers, tablefmt="double_grid"))

        # Ask user for fields to update (with skip option)
        print(colored("\nUpdate Your Profile (Press Enter to skip any field):", "cyan"))

        updates = {}
        new_age = input("Enter new Age: ").strip()
        if new_age:
            updates["age"] = new_age

        new_address = input("Enter new Address: ").strip()
        if new_address:
            updates["address"] = new_address

        new_contact = input("Enter new Contact Number: ").strip()
        if new_contact:
            updates["contactnumber"] = new_contact

        new_degree = input("Enter new Degree: ").strip()
        if new_degree:
            updates["degree"] = new_degree

        # Prepare and execute update query
        if updates:
            query = "UPDATE Employee SET " + ", ".join(f"{col} = ?" for col in updates.keys()) + " WHERE emp_id = ?"
            values = list(updates.values()) + [self.emp_id]
            cursor.execute(query, values)
            conn.commit()
            print(colored("\nProfile updated successfully!", "green"))
        else:
            print(colored("\nNo changes made to your profile.", "yellow"))

        conn.close()

    def run(self):
        while True:
            self.show_menu()
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.mark_attendance()
            elif choice == "2":
                self.apply_leave()
            elif choice == "3":
                self.view_applied_leaves()
            elif choice == "4":
                self.check_salary()
            elif choice == "5":
                self.request_job_position_change()
            elif choice == "6":
                self.view_and_update_profile()
            elif choice == "7":
                print(colored("\nLogging out...", "cyan"))
                break
            else:
                print(colored("\nInvalid choice! Please try again.", "red"))
                
# Login and menu loop
while True:
    employee = Employee.login()
    if employee:
        employee.run()
        break