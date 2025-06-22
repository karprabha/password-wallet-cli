import random
import string
from typing import List


class PasswordGenerator:
    @staticmethod
    def generate_password(
        length: int = 12,
        include_uppercase: bool = True,
        include_numbers: bool = True,
        include_special: bool = True
    ) -> str:
        """Generate a random password with specified criteria"""
        
        if length < 4:
            length = 4
        
        # Base character set (lowercase letters)
        chars = string.ascii_lowercase
        
        # Required characters to ensure at least one of each type
        required_chars: List[str] = []
        
        if include_uppercase:
            chars += string.ascii_uppercase
            required_chars.append(random.choice(string.ascii_uppercase))
        
        if include_numbers:
            chars += string.digits
            required_chars.append(random.choice(string.digits))
        
        if include_special:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            chars += special_chars
            required_chars.append(random.choice(special_chars))
        
        # Always include at least one lowercase letter
        required_chars.append(random.choice(string.ascii_lowercase))
        
        # Generate remaining characters
        remaining_length = length - len(required_chars)
        random_chars = [random.choice(chars) for _ in range(remaining_length)]
        
        # Combine and shuffle
        password_chars = required_chars + random_chars
        random.shuffle(password_chars)
        
        return ''.join(password_chars)
    
    @staticmethod
    def get_password_strength(password: str) -> str:
        """Evaluate password strength"""
        score = 0
        
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        
        if score <= 2:
            return "Weak"
        elif score <= 4:
            return "Medium"
        else:
            return "Strong" 