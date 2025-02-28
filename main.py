import os
from tabulate import tabulate
from termcolor import colored

def main():
    options = [["1", colored("HR", "yellow")], ["2", colored("Employee", "yellow")], ["3", colored("Manager", "yellow")]]
    
    while True:
        print(colored("\nWelcome to Employee Management System", "green"))
        print(tabulate(options, headers=[colored("Option", "green"), colored("Role", "green")], tablefmt="double_grid"))
        
        choice = input(colored("Enter your choice (1/2/3): ", "cyan")).strip()
        
        if choice == "1":
            os.system('python3 hr.py')
            break
        elif choice == "2":
            os.system('python3 employee.py')
            break
        elif choice == "3":
            os.system('python3 manager.py')
            break
        else:
            print(colored("Invalid choice! Please enter 1, 2, or 3.", "red"))


main()