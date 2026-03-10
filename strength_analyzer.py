import math

def calculate_entropy(password):
    """Calculates the Shannon entropy of a password."""
    pool_size = 0
    if any(c.islower() for c in password): pool_size += 26
    if any(c.isupper() for c in password): pool_size += 26
    if any(c.isdigit() for c in password): pool_size += 10
    
    symbols = "!@#$%^&*()-_+=~`[]{}|:;\"'<>,.?/"
    if any(c in symbols for c in password): pool_size += 32
    
    if pool_size == 0 or len(password) == 0:
        return 0, pool_size
        
    entropy = len(password) * math.log2(pool_size)
    return entropy, pool_size

def analyze_password(password, dictionary_words=None):
    """
    Analyzes password strength based on length, complexity, entropy, and dictionary checks.
    """
    if dictionary_words is None:
        dictionary_words = set()
    else:
        dictionary_words = set(w.lower() for w in dictionary_words)
        
    analysis = {
        'password': password,
        'length': len(password),
        'has_lower': any(c.islower() for c in password),
        'has_upper': any(c.isupper() for c in password),
        'has_digit': any(c.isdigit() for c in password),
        'has_symbol': any(c in "!@#$%^&*()-_+=~`[]{}|:;\"'<>,.?/" for c in password),
        'entropy': 0,
        'charset_size': 0,
        'strength': 'Unknown',
        'is_dictionary_word': False,
        'recommendations': []
    }
    
    entropy, pool_size = calculate_entropy(password)
    analysis['entropy'] = round(entropy, 2)
    analysis['charset_size'] = pool_size
    
    # Dictionary Check
    if password.lower() in dictionary_words:
        analysis['is_dictionary_word'] = True
        analysis['recommendations'].append("Avoid common dictionary words.")
        
    # Complexity Rules
    if analysis['length'] < 8:
        analysis['recommendations'].append("Increase password length to at least 8-12 characters.")
    if not analysis['has_lower']:
        analysis['recommendations'].append("Add lowercase letters.")
    if not analysis['has_upper']:
        analysis['recommendations'].append("Add uppercase letters.")
    if not analysis['has_digit']:
        analysis['recommendations'].append("Add numbers.")
    if not analysis['has_symbol']:
        analysis['recommendations'].append("Add special symbols.")
        
    # Determine overall strength
    if analysis['is_dictionary_word']:
        analysis['strength'] = 'Very Weak (Dictionary Word)'
    elif entropy < 40:
        analysis['strength'] = 'Weak'
    elif entropy < 60:
        analysis['strength'] = 'Moderate'
    elif entropy < 80:
        analysis['strength'] = 'Strong'
    else:
        analysis['strength'] = 'Very Strong'
        
    if len(password) >= 8 and len(analysis['recommendations']) == 0 and not analysis['is_dictionary_word']:
        if analysis['strength'] in ['Weak', 'Moderate']:
            # Adjust strength if it meets all complexity rules but is short (< 12)
            if analysis['length'] >= 12:
                analysis['strength'] = 'Strong'
            else:
                analysis['recommendations'].append("Increase length for higher entropy.")
                
    return analysis

def print_analysis(analysis):
    """Helper to nicely print the analysis dictionary."""
    print(f"--- Analysis for '{analysis['password']}' ---")
    print(f"Length: {analysis['length']} | Charset Size: {analysis['charset_size']}")
    print(f"Complexity: Lower[{'x' if analysis['has_lower'] else ' '}] "
          f"Upper[{'x' if analysis['has_upper'] else ' '}] "
          f"Digit[{'x' if analysis['has_digit'] else ' '}] "
          f"Symbol[{'x' if analysis['has_symbol'] else ' '}]")
    print(f"Entropy: {analysis['entropy']} bits")
    print(f"Overall Strength: {analysis['strength']}")
    if analysis['recommendations']:
        print("Recommendations:")
        for r in analysis['recommendations']:
            print(f"  - {r}")
    print("-" * 40)

if __name__ == "__main__":
    print("--- Strength Analyzer Test ---")
    
    sample_dictionary = ["password", "admin", "admin123", "qwerty"]
    
    passwords_to_test = [
        "password",
        "qwerty1234",
        "P@ssw0rd1",
        "CorrectHorseBatteryStaple",
        "A3!b@9$xLp2Qz#"
    ]
    
    for p in passwords_to_test:
        res = analyze_password(p, sample_dictionary)
        print_analysis(res)
