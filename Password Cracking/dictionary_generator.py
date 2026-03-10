import itertools

def generate_leet_speak(word):
    """Generates leet-speak mutations of a word."""
    leet_map = {
        'a': ['a', '@', '4'],
        'e': ['e', '3'],
        'i': ['i', '1', '!'],
        'o': ['o', '0'],
        's': ['s', '$', '5'],
        't': ['t', '7'],
    }
    
    options = [leet_map.get(c.lower(), [c]) for c in word]
    mutations = [''.join(combo) for combo in itertools.product(*options)]
    return mutations

def generate_capitalizations(word):
    """Generates capitalization mutations of a word."""
    return [word.lower(), word.upper(), word.capitalize()]

def generate_appended_numbers(word, max_number=99):
    """Appends numbers to a word."""
    mutations = [word]
    for i in range(max_number + 1):
        mutations.append(f"{word}{i}")
        if i < 10:
            mutations.append(f"{word}0{i}")
    return mutations

def generate_dictionary(base_words: list[str], include_leet: bool=True, include_caps: bool=True, append_numbers: bool=True, max_number: int=99) -> list[str]:
    """
    Generates a full dictionary based on input words and mutation rules.
    Returns a sorted list of unique passwords.
    """
    result_set: set[str] = set()
    
    for word in base_words:
        current_mutations = set([word])
        
        # 1. Capitalization
        if include_caps:
            caps_mutations = set()
            for w in current_mutations:
                caps_mutations.update(generate_capitalizations(w))
            current_mutations.update(caps_mutations)
            
        # 2. Leet Speak
        if include_leet:
            leet_mutations = set()
            for w in current_mutations:
                leet_mutations.update(generate_leet_speak(w))
            current_mutations.update(leet_mutations)
            
        # 3. Appended Numbers
        if append_numbers:
            num_mutations = set()
            for w in current_mutations:
                num_mutations.update(generate_appended_numbers(w, max_number))
            current_mutations.update(num_mutations)
            
        result_set.update(current_mutations)
        
    return sorted(list(result_set))

def save_dictionary(wordlist, filename):
    """Saves the generated wordlist to a file."""
    try:
        with open(filename, 'w') as f:
            for word in wordlist:
                f.write(f"{word}\n")
        print(f"[*] Successfully saved {len(wordlist)} words to {filename}")
        return True
    except Exception as e:
        print(f"[-] Error saving dictionary: {e}")
        return False

if __name__ == "__main__":
    print("--- Dictionary Generator Test ---")
    base = ["admin", "password"]
    print(f"Base words: {base}")
    
    print("\nGenerating dictionary with default mutations (caps, leet, appended nums up to 9)...")
    dictionary = generate_dictionary(base, max_number=9)
    print(f"Generated {len(dictionary)} unique combinations.")
    
    # Show a small sample
    sample_start = [dictionary[i] for i in range(min(10, len(dictionary)))]
    sample_end = [dictionary[i] for i in range(max(0, len(dictionary) - 10), len(dictionary))]
    print(f"Sample entries: {sample_start} ... {sample_end}")
    save_dictionary(dictionary, "test_wordlist.txt")
