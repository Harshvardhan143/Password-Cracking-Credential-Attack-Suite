import hashlib
import time

def ntlm_hash(password):
    """Calculates the NTLM hash of a password."""
    try:
        # This works on older Python versions or systems where OpenSSL still allows MD4
        return hashlib.new('md4', password.encode('utf-16le')).hexdigest()
    except ValueError:
        try:
            # Fallback for Python 3.10+ where OpenSSL disables MD4
            from passlib.hash import nthash
            return nthash.hash(password).lower()
        except ImportError:
            print("[-] Warning: MD4 disabled in this Python version. Please 'pip install passlib' to check NTLM.")
            return "MD4_UNSUPPORTED"

def brute_force_dictionary(target_hash, hash_type, wordlist):
    """
    Attempts to crack a hash using a dictionary of words.
    Supports NTLM, and raw MD5, SHA1, SHA256, SHA512.
    """
    start_time = time.time()
    attempts = 0
    target_hash = target_hash.lower()
    
    for word in wordlist:
        attempts += 1
        word = word.strip()
        guessed_hash = None
        
        if hash_type == 'NTLM':
            guessed_hash = ntlm_hash(word)
        elif hash_type == 'MD5':
            guessed_hash = hashlib.md5(word.encode()).hexdigest()
        elif hash_type == 'SHA-1':
            guessed_hash = hashlib.sha1(word.encode()).hexdigest()
        elif hash_type == 'SHA-256':
            guessed_hash = hashlib.sha256(word.encode()).hexdigest()
        elif hash_type == 'SHA-512':
            guessed_hash = hashlib.sha512(word.encode()).hexdigest()
        else:
            return {'error': f"Unsupported hash type: {hash_type}"}
            
        if guessed_hash == target_hash:
            elapsed = time.time() - start_time
            return {'found': True, 'password': word, 'attempts': attempts, 'time': elapsed}
            
    elapsed = time.time() - start_time
    return {'found': False, 'password': None, 'attempts': attempts, 'time': elapsed}

def estimate_crack_time(charset_size, length, hashes_per_second=1000000000):
    """
    Estimates time to crack a password of given length and charset size.
    Default speed: 1 Billion hashes per second (simulating modern GPU hardware like RTX 3090 / Hashcat).
    """
    combinations = charset_size ** length
    seconds = combinations / hashes_per_second
    return seconds

def format_time(seconds):
    if seconds < 1:
        return "Less than a second"
    elif seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.2f} minutes"
    elif seconds < 86400:
        return f"{seconds/3600:.2f} hours"
    elif seconds < 31536000:
        return f"{seconds/86400:.2f} days"
    else:
        return f"{seconds/31536000:.2f} years"

def simulate_incremental_bruteforce(max_length, use_lower=True, use_upper=False, use_digits=False, use_symbols=False, hashes_per_sec=1000000000):
    """
    Simulates estimating the time for an incremental brute-force attack.
    """
    charset_size = 0
    if use_lower: charset_size += 26
    if use_upper: charset_size += 26
    if use_digits: charset_size += 10
    if use_symbols: charset_size += 32
    
    if charset_size == 0:
        return 0
        
    print(f"[*] Simulating incremental brute-force (max length {max_length}, charset size {charset_size})")
    print(f"[*] Assumed Hash Rate: {hashes_per_sec:,} hashes/second")
    total_seconds = 0
    
    for i in range(1, max_length + 1):
        secs = estimate_crack_time(charset_size, i, hashes_per_sec)
        total_seconds += secs
        print(f"  Length {i}: {format_time(secs)}")
        
    print(f"[*] Total estimated time to exhaust space up to length {max_length}: {format_time(total_seconds)}")
    return total_seconds

if __name__ == "__main__":
    print("--- Brute Force Simulator Test ---")
    
    # 1. Test Dictionary Attack on NTLM Hash for "admin123"
    target_pwd = "admin"
    target_ntlm = ntlm_hash(target_pwd)
    
    print(f"[*] Target NTLM Hash: {target_ntlm} (Password: {target_pwd})")
    print("[*] Running dictionary attack...")
    
    sample_wordlist = ["password", "123456", "admin", "admin123", "root"]
    result = brute_force_dictionary(target_ntlm, "NTLM", sample_wordlist)
    print(f"  Result: {result}")
    
    # 2. Test Time Estimation
    print("\n[*] Running Incremental Brute-Force Simulation (Length 8, Alphanumeric)...")
    simulate_incremental_bruteforce(8, use_lower=True, use_upper=True, use_digits=True, use_symbols=False)
