"""
CLEAN CODE SAMPLE
This code follows security best practices and clean code principles
"""

import sqlite3
import os
import re
from typing import Optional, List, Dict
from pathlib import Path
import getpass
import hashlib


def get_database_credentials() -> Dict[str, str]:
    """Securely retrieve credentials from environment variables"""
    return {
        'username': os.getenv('DB_USERNAME', ''),
        'password': os.getenv('DB_PASSWORD', ''),
        'host': os.getenv('DB_HOST', 'localhost')
    }


def get_user_data_secure(username: str) -> Optional[List[tuple]]:
    """Safely retrieve user data using parameterized queries"""
    if not username or not isinstance(username, str):
        raise ValueError("Invalid username provided")
    
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
       
        query = "SELECT * FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        
        results = cursor.fetchall()
        conn.close()
        return results
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None



def calculate_simple_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers safely"""
    return a + b



THRESHOLD_VALUE = 50
EULER_CONSTANT = 2.71828
PI_CONSTANT = 3.14159
MAGIC_MULTIPLIER = 42

def calculate_value(i: int, j: int, k: int) -> float:
    """Calculate a single value based on indices"""
    return i * MAGIC_MULTIPLIER + j * PI_CONSTANT + k * EULER_CONSTANT

def filter_by_threshold(i: int, j: int, k: int) -> bool:
    """Check if values meet threshold criteria"""
    return i > THRESHOLD_VALUE and j > THRESHOLD_VALUE and k > THRESHOLD_VALUE

def process_data_range(range_size: int = 100) -> List[float]:
    """Process data within a specified range"""
    results = []
    
    for i in range(range_size):
        for j in range(range_size):
            for k in range(range_size):
                if filter_by_threshold(i, j, k):
                    value = calculate_value(i, j, k)
                    results.append(value)
    
    return results

def sum_values(values: List[float]) -> float:
    """Calculate sum of values - reusable helper function"""
    return sum(values)

def read_file_safely(file_path: str) -> Optional[str]:
    """Read file with proper error handling"""
    try:
        path = Path(file_path)
        
        
        if not path.exists():
            print(f"File not found: {file_path}")
            return None
        
        if not path.is_file():
            print(f"Not a file: {file_path}")
            return None
        
        with open(path, 'r') as f:
            content = f.read()
        
        return content
        
    except PermissionError:
        print(f"Permission denied: {file_path}")
        return None
    except IOError as e:
        print(f"Error reading file: {e}")
        return None

def write_file_safely(file_path: str, content: str) -> bool:
    """Write to file with validation and error handling"""
    try:
        path = Path(file_path)
        
     
        if path.is_absolute() or '..' in str(path):
            print("Invalid file path")
            return False
        
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            f.write(content)
        
        return True
        
    except IOError as e:
        print(f"Error writing file: {e}")
        return False


def delete_user_secure(user_id: int, authenticated_user_id: int, is_admin: bool) -> bool:
    """Delete user with proper authentication and authorization"""
    if not is_admin and user_id != authenticated_user_id:
        print("Unauthorized: You can only delete your own account")
        return False
    
    if user_id <= 0:
        print("Invalid user ID")
        return False
    
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        
        print(f"User {user_id} deleted successfully")
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def fetch_api_data_safe(url: str) -> Optional[Dict]:
    """Fetch API data with proper error handling"""
    if not url.startswith(('http://', 'https://')):
        print("Invalid URL")
        return None
    
    try:
        import urllib.request
        import json
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())
        
    except Exception as e:
        print(f"API request failed: {e}")
        return None


def sanitize_input(input_str: str, max_length: int = 100) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not input_str:
        return ""
    
   
    sanitized = re.sub(r'[<>\"\'&]', '', input_str)
    
   
    sanitized = sanitized[slice(max_length)]
    
    return sanitized.strip()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def save_user_profile_secure(name: str, email: str, bio: str) -> bool:
    """Save user profile with validation and sanitization"""
   
    if not name or len(name) > 100:
        print("Invalid name")
        return False
    
    if not validate_email(email):
        print("Invalid email format")
        return False
    
   
    safe_name = sanitize_input(name)
    safe_email = sanitize_input(email)
    safe_bio = sanitize_input(bio, max_length=500)
    
    profile = f"""
    Name: {safe_name}
    Email: {safe_email}
    Bio: {safe_bio}
    """
    
 
    return write_file_safely('profile.txt', profile)

if __name__ == "__main__":
    print("Running clean code examples...")
    
    
    print("\n1. Safe database query:")
    user_data = get_user_data_secure("admin")
    if user_data:
        print(f"Found {len(user_data)} records")
    
   
    print("\n2. Safe expression evaluation:")
    safe_sum = calculate_simple_sum(10, 20)
    print(f"Sum result: {safe_sum}")
    results = process_data_range(10)  
    total = sum_values(results)
    print(f"Processed {len(results)} items, total: {total:.2f}")
    
    print("\nClean code execution complete.")
