#!/usr/bin/env python3

import getpass
import os
import sys
from tabulate import tabulate
from vault import PasswordVault
from password_generator import PasswordGenerator


class PasswordWalletCLI:
    def __init__(self):
        self.vault = PasswordVault()
        self.generator = PasswordGenerator()
        self.is_authenticated = False
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print application header"""
        print("=" * 50)
        print("🔐 PASSWORD WALLET CLI")
        print("=" * 50)
        print()
    
    def authenticate(self) -> bool:
        """Handle master password authentication"""
        if self.vault.vault_exists():
            print("🔓 Existing vault found. Please enter your master password.")
            master_password = getpass.getpass("Master Password: ")
            
            if self.vault.unlock_vault(master_password):
                print("✅ Vault unlocked successfully!")
                return True
            else:
                print("❌ Invalid master password. Access denied.")
                return False
        else:
            print("🆕 No vault found. Let's create a new one!")
            print("⚠️  Choose a strong master password - you'll need it to access your vault.")
            
            while True:
                master_password = getpass.getpass("Create Master Password: ")
                if len(master_password) < 6:
                    print("❌ Master password must be at least 6 characters long.")
                    continue
                
                confirm_password = getpass.getpass("Confirm Master Password: ")
                if master_password != confirm_password:
                    print("❌ Passwords don't match. Please try again.")
                    continue
                
                break
            
            if self.vault.initialize_vault(master_password):
                print("✅ Vault created successfully!")
                return True
            else:
                print("❌ Failed to create vault.")
                return False
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "=" * 30)
        print("📋 MAIN MENU")
        print("=" * 30)
        print("1. Add New Entry")
        print("2. View All Entries")
        print("3. Search by Site")
        print("4. Generate Password")
        print("5. Exit")
        print("=" * 30)
    
    def get_user_input(self, prompt: str, required: bool = True) -> str:
        """Get user input with validation"""
        while True:
            value = input(prompt).strip()
            if not required or value:
                return value
            print("❌ This field is required. Please enter a value.")
    
    def add_new_entry(self):
        """Add new password entry"""
        print("\n➕ ADD NEW ENTRY")
        print("-" * 20)
        
        site = self.get_user_input("Site/Service: ")
        username = self.get_user_input("Username: ")
        
        # Check if entry already exists
        if self.vault.entry_exists(site):
            print(f"⚠️  Entry for '{site}' already exists.")
            overwrite = input("Overwrite existing entry? (y/n): ").lower().strip()
            if overwrite != 'y':
                print("❌ Entry not added.")
                return
        
        # Option to generate password
        generate = input("Generate password? (y/n): ").lower().strip()
        if generate == 'y':
            password = self.generate_password_interactive()
            if not password:
                return
        else:
            password = getpass.getpass("Password: ")
            if not password.strip():
                print("❌ Password cannot be empty.")
                return
        
        if self.vault.add_entry(site, username, password):
            print("✅ Entry added successfully!")
        else:
            print("❌ Failed to add entry.")
    
    def view_all_entries(self):
        """Display all entries without passwords"""
        print("\n📋 ALL ENTRIES")
        print("-" * 20)
        
        entries = self.vault.get_entries()
        if not entries:
            print("📭 Vault is empty. No entries found.")
            return
        
        # Prepare data for tabulate
        headers = ["Site", "Username", "Created"]
        table_data = []
        
        for entry in entries:
            created_date = entry["created_at"]
            if "T" in created_date:
                created_date = created_date.split("T")[0]  # Show only date part
            
            table_data.append([
                entry["site"],
                entry["username"],
                created_date
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\n📊 Total entries: {len(entries)}")
    
    def search_by_site(self):
        """Search entries by site and optionally reveal password"""
        print("\n🔍 SEARCH BY SITE")
        print("-" * 20)
        
        keyword = self.get_user_input("Enter search keyword: ")
        matches = self.vault.search_entries(keyword)
        
        if not matches:
            print(f"❌ No entries found matching '{keyword}'.")
            return
        
        print(f"\n🎯 Found {len(matches)} matching entries:")
        
        # Display matches
        headers = ["#", "Site", "Username", "Created"]
        table_data = []
        
        for i, match in enumerate(matches, 1):
            created_date = match["created_at"]
            if "T" in created_date:
                created_date = created_date.split("T")[0]
            
            table_data.append([
                i,
                match["site"],
                match["username"],
                created_date
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Option to reveal password
        reveal = input("\n🔓 Reveal password for an entry? (y/n): ").lower().strip()
        if reveal == 'y':
            try:
                choice = int(input("Enter entry number: ")) - 1
                if 0 <= choice < len(matches):
                    site = matches[choice]["site"]
                    password = self.vault.get_password(site)
                    print(f"\n🔑 Password for '{site}': {password}")
                else:
                    print("❌ Invalid entry number.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def generate_password_interactive(self) -> str:
        """Interactive password generation"""
        print("\n🎲 PASSWORD GENERATOR")
        print("-" * 25)
        
        try:
            length = int(input("Password length (default 12): ") or "12")
            if length < 4:
                print("⚠️  Minimum length is 4. Setting to 4.")
                length = 4
            elif length > 128:
                print("⚠️  Maximum length is 128. Setting to 128.")
                length = 128
        except ValueError:
            length = 12
        
        include_uppercase = input("Include uppercase letters? (Y/n): ").lower().strip() != 'n'
        include_numbers = input("Include numbers? (Y/n): ").lower().strip() != 'n'
        include_special = input("Include special characters? (Y/n): ").lower().strip() != 'n'
        
        password = self.generator.generate_password(
            length=length,
            include_uppercase=include_uppercase,
            include_numbers=include_numbers,
            include_special=include_special
        )
        
        strength = self.generator.get_password_strength(password)
        
        print(f"\n🎯 Generated Password: {password}")
        print(f"💪 Strength: {strength}")
        
        use_password = input("\nUse this password? (y/n): ").lower().strip()
        if use_password == 'y':
            return password
        else:
            regenerate = input("Generate another password? (y/n): ").lower().strip()
            if regenerate == 'y':
                return self.generate_password_interactive()
            return ""
    
    def generate_password_only(self):
        """Generate password without adding entry"""
        password = self.generate_password_interactive()
        if password:
            print(f"\n📋 Your generated password: {password}")
            input("\nPress Enter to continue...")
    
    def run(self):
        """Main application loop"""
        try:
            self.clear_screen()
            self.print_header()
            
            # Authentication
            if not self.authenticate():
                print("\n👋 Goodbye!")
                sys.exit(1)
            
            self.is_authenticated = True
            
            while True:
                self.show_menu()
                choice = input("\nSelect option (1-5): ").strip()
                
                if choice == '1':
                    self.add_new_entry()
                elif choice == '2':
                    self.view_all_entries()
                elif choice == '3':
                    self.search_by_site()
                elif choice == '4':
                    self.generate_password_only()
                elif choice == '5':
                    print("\n👋 Goodbye! Your vault has been saved securely.")
                    break
                else:
                    print("❌ Invalid option. Please select 1-5.")
                
                input("\nPress Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Your vault has been saved securely.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            sys.exit(1)


def main():
    app = PasswordWalletCLI()
    app.run()


if __name__ == "__main__":
    main() 