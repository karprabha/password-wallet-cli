import json
import os
import base64
from datetime import datetime
from typing import List, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PasswordVault:
    def __init__(self, vault_path: str = "data/vault.enc"):
        self.vault_path = vault_path
        self.salt_path = "data/salt.key"
        self.entries: List[Dict] = []
        self.fernet = None
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(vault_path), exist_ok=True)
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from master password using PBKDF2HMAC"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _get_or_create_salt(self) -> bytes:
        """Get existing salt or create new one"""
        if os.path.exists(self.salt_path):
            with open(self.salt_path, 'rb') as f:
                return f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_path, 'wb') as f:
                f.write(salt)
            return salt
    
    def initialize_vault(self, master_password: str) -> bool:
        """Initialize new vault with master password"""
        try:
            salt = self._get_or_create_salt()
            key = self._derive_key(master_password, salt)
            self.fernet = Fernet(key)
            self.entries = []
            self._save_vault()
            return True
        except Exception as e:
            print(f"Error initializing vault: {e}")
            return False
    
    def unlock_vault(self, master_password: str) -> bool:
        """Unlock existing vault with master password"""
        try:
            if not os.path.exists(self.vault_path):
                return False
            
            salt = self._get_or_create_salt()
            key = self._derive_key(master_password, salt)
            self.fernet = Fernet(key)
            
            # Try to decrypt vault to verify password
            with open(self.vault_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            self.entries = json.loads(decrypted_data.decode())
            return True
        
        except Exception:
            return False
    
    def vault_exists(self) -> bool:
        """Check if vault file exists"""
        return os.path.exists(self.vault_path)
    
    def add_entry(self, site: str, username: str, password: str) -> bool:
        """Add new password entry"""
        if not self.fernet:
            return False
        
        # Check for existing entry
        existing_index = self._find_entry_index(site)
        
        new_entry = {
            "site": site,
            "username": username,
            "password": password,
            "created_at": datetime.now().isoformat()
        }
        
        if existing_index is not None:
            self.entries[existing_index] = new_entry
        else:
            self.entries.append(new_entry)
        
        return self._save_vault()
    
    def get_entries(self) -> List[Dict]:
        """Get all entries without passwords"""
        return [
            {
                "site": entry["site"],
                "username": entry["username"],
                "created_at": entry.get("created_at", "Unknown")
            }
            for entry in self.entries
        ]
    
    def search_entries(self, keyword: str) -> List[Dict]:
        """Search entries by site keyword"""
        keyword_lower = keyword.lower()
        matches = []
        
        for i, entry in enumerate(self.entries):
            if keyword_lower in entry["site"].lower():
                matches.append({
                    "index": i,
                    "site": entry["site"],
                    "username": entry["username"],
                    "created_at": entry.get("created_at", "Unknown")
                })
        
        return matches
    
    def get_password(self, site: str) -> Optional[str]:
        """Get password for specific site"""
        for entry in self.entries:
            if entry["site"].lower() == site.lower():
                return entry["password"]
        return None
    
    def entry_exists(self, site: str) -> bool:
        """Check if entry exists for site"""
        return any(entry["site"].lower() == site.lower() for entry in self.entries)
    
    def _find_entry_index(self, site: str) -> Optional[int]:
        """Find index of entry by site"""
        for i, entry in enumerate(self.entries):
            if entry["site"].lower() == site.lower():
                return i
        return None
    
    def _save_vault(self) -> bool:
        """Save and encrypt vault to file"""
        try:
            if not self.fernet:
                return False
            
            data = json.dumps(self.entries, indent=2)
            encrypted_data = self.fernet.encrypt(data.encode())
            
            with open(self.vault_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"Error saving vault: {e}")
            return False 