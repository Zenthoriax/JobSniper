import sys
import os

# Fix imports to allow finding src/modules
sys.path.append(os.path.join(os.getcwd(), "src"))

from modules.profile_manager import ProfileManager

def print_menu():
    print("\n--- 🛠️  JobSniper Profile Manager ---")
    print("1. View Profile")
    print("2. Add Skill")
    print("3. Remove Skill")
    print("4. Add Project")
    print("5. Delete Project")
    print("6. Exit")
    print("-------------------------------------")

def main():
    manager = ProfileManager()

    while True:
        print_menu()
        choice = input("Select an option (1-6): ").strip()

        if choice == '1':
            manager.list_profile()

        elif choice == '2':
            skill = input("Enter new skill: ").strip()
            if skill: manager.add_skill(skill)

        elif choice == '3':
            skill = input("Enter skill to remove: ").strip()
            if skill: manager.remove_skill(skill)

        elif choice == '4':
            print("\n--- New Project Details ---")
            name = input("Project Name: ").strip()
            tech = input("Tech Stack (comma separated): ").strip()
            desc = input("Description: ").strip()
            if name: manager.add_project(name, tech, desc)

        elif choice == '5':
            name = input("Enter exact name of project to delete: ").strip()
            if name: manager.delete_project(name)

        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    main()