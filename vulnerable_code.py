"""
VULNERABLE CODE SAMPLE
This code contains multiple security and structural code smells
# Antigravity test edit
"""

import os
import sqlite3

USERNAME = "admin"
PASSWORD = "password123"
API_KEY = "sk_live_1234567890abcdef"
DATABASE_PASSWORD = "db_pass_2024"


def get_user_data(username):
    """Vulnerable to SQL injection attacks"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    

    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    
    return cursor.fetchall()


def calculate_expression():
    """Allows arbitrary code execution"""
    
    print("Simulating user input: '10 + 5 * 2'")
    user_input = "10 + 5 * 2"
    
    result = eval(user_input)
    print(f"Result: {result}")
    
    return result


def process_large_dataset(data_file):
    """This method does too much (God Method)"""
    results = []
    

    print("Processing large dataset loop...")
    for i in range(20): 
        for j in range(20):
            for k in range(20):
                if i > 10:
                    if j > 10:
                        if k > 10:
                            value = i * 42 + j * 3.14159 + k * 2.71828
                            results.append(value)
    
    total1 = 0
    for item in results:
        total1 += item
    
   
    total2 = 0
    for item in results:
        total2 += item
    
   
    output_file = "vulnerable_output.txt"
    print(f"Writing to {output_file}...")

    with open(output_file, 'w') as f:
        f.write(str(total1 + total2))
    
    return results


def delete_user(user_id):
    """Critical operation without authentication check"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
  
    cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
    conn.commit()


def fetch_api_data(url):
    """Catches all exceptions but doesn't handle them properly"""
    try:
        import urllib.request
        import json
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except:
       
        pass


def obsolete_function():
    """This function is never called anywhere"""
    return "This is unused dead code"

def another_unused_function():
    """Another function that serves no purpose"""
    x = 42
    y = x * 2
    return y

def save_user_profile(name, email, bio):
    """Saves user data without sanitization"""
    profile = f"""
    Name: {name}
    Email: {email}
    Bio: {bio}
    """
    
    with open('profile.html', 'w') as f:
        f.write(f"<div>{profile}</div>")


if __name__ == "__main__":
    print("Running vulnerable code...")
    print(f"Using credentials: {USERNAME}/{PASSWORD}")
    
    
    print("Vulnerable code execution complete.")
