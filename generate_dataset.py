import os
import random
import pandas as pd  # type: ignore

def generate_clean_code(i):
    templates = [
        f"def clean_func_{i}(a, b):\n    return a + b",
        f"def process_data_{i}(data):\n    result = []\n    for item in data:\n        result.append(item * 2)\n    return result",
        f"class DataHandler_{i}:\n    def __init__(self, val):\n        self.val = val\n    def get_val(self):\n        return self.val",
        f"def calculate_area_{i}(radius):\n    import math\n    return math.pi * radius ** 2",
        f"def greet_{i}(name='World'):\n    return f'Hello, {{name}}!'"
    ]
    return random.choice(templates)

def generate_smelly_code(i, smell_type):
    if smell_type == "SQL_Injection":
        return f"def sql_inj_{i}(user):\n    query = 'SELECT * FROM users WHERE name = ' + user\n    execute(query)"
    elif smell_type == "Unvalidated_Input":
        templates = [
            f"def process_input_{i}():\n    data = input('Enter data: ')\n    db.save(data)",
            f"def update_profile_{i}():\n    bio = input('New bio: ')\n    user.bio = bio",
            f"def search_query_{i}():\n    q = input('Search: ')\n    results = find(q)",
            f"def set_config_{i}():\n    val = input('Value: ')\n    config['val'] = val"
        ]
        return random.choice(templates)
    elif smell_type == "Hardcoded_Credentials":
        return f"def auth_{i}():\n    password = 'secret_pass_{i}'\n    login('admin', password)"
    elif smell_type == "Unsafe_API":
        apis = ['eval', 'system', 'exec']
        api = random.choice(apis)
        return f"def unsafe_api_{i}(cmd):\n    os.{api}(cmd)"
    elif smell_type == "Missing_Sanitization":
        return f"def post_{i}(comment):\n    db.save('INSERT INTO comments VALUES (?)', comment)"
    elif smell_type == "Missing_Auth":
        return f"def delete_user_{i}(userId):\n    users.delete(userId) # No check"
    elif smell_type == "Improper_Error_Handling":
        return f"def division_{i}(a, b):\n    try:\n        return a/b\n    except:\n        pass"
    elif smell_type == "Insecure_File":
        return f"def read_file_{i}(filename):\n    with open('/tmp/' + filename, 'r') as f:\n        return f.read()"
    elif smell_type == "Long_Method":
        return f"def long_method_{i}():\n" + "\n".join([f"    x_{j} = {j}" for j in range(100)])
    elif smell_type == "Duplicate_Code":
        code = f"def dup_{i}():\n    print('Doing task A')\n    print('Doing task B')\n"
        return code + code.replace(f"dup_{i}", f"dup_v2_{i}")
    elif smell_type == "God_Class":
        return f"class God_{i}:\n" + "\n".join([f"    def m_{j}(self):\n        return {j}" for j in range(50)])
    elif smell_type == "Dead_Code":
        return f"def dead_{i}():\n    return 1\n    print('Never reached')"
    elif smell_type == "Magic_Value":
        return f"def calc_{i}(val):\n    return val * 0.0825 # Magic tax rate"
    return generate_clean_code(i)

def main():
    print("Generating comprehensive dataset...")
    smell_types = [
        "SQL_Injection", "Unvalidated_Input", "Hardcoded_Credentials", 
        "Unsafe_API", "Missing_Sanitization", "Missing_Auth", 
        "Improper_Error_Handling", "Insecure_File", "Long_Method", 
        "Duplicate_Code", "God_Class", "Dead_Code", "Magic_Value"
    ]
    
    data = []
    num_per_type = 200 # Total ~2800 samples
    
    # Generate Smelly samples
    for smell in smell_types:
        for i in range(num_per_type):
            code = generate_smelly_code(i, smell)
            data.append({"code_snippet": code, "smell_label": smell})
            
    # Generate Clean samples
    for i in range(num_per_type * 2):
        code = generate_clean_code(i)
        data.append({"code_snippet": code, "smell_label": "clean_code"})

    df = pd.DataFrame(data)
    df = df.sample(frac=1).reset_index(drop=True) # Shuffle
    df.to_csv("code_smell_dataset.csv", index=False)
    print(f"Generated {len(df)} samples in code_smell_dataset.csv")

if __name__ == "__main__":
    main()
