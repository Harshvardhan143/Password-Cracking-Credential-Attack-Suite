import os
import re

def identify_linux_hash_type(hash_string):
    """
    Identifies the hashing algorithm from a Linux /etc/shadow hash string.
    Format: $id$salt$hashed
    """
    if not hash_string.startswith('$'):
        return "Unknown/DES"
        
    parts = hash_string.split('$')
    if len(parts) >= 3:
        alg_id = parts[1]
        algo_map = {
            '1': 'MD5',
            '2a': 'Blowfish (bcrypt)',
            '2y': 'Blowfish (bcrypt)',
            '5': 'SHA-256',
            '6': 'SHA-512',
            'y': 'yescrypt'
        }
        return algo_map.get(alg_id, f"Unknown ID (${alg_id}$)")
    return "Unknown Format"

def extract_linux_hashes(shadow_path):
    """
    Parses a Linux shadow file format and extracts hashes.
    Expected format per line: username:password_hash:lastchange:min:max:warn:inactive:expire
    """
    extracted = []
    try:
        with open(shadow_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(':')
                if len(parts) >= 2:
                    username = parts[0]
                    hash_val = parts[1]
                    # * or ! means account is locked or has no password
                    if hash_val not in ('*', '!', '!!') and len(hash_val) > 2:
                        algo = identify_linux_hash_type(hash_val)
                        extracted.append({
                            'os': 'Linux',
                            'username': username,
                            'hash': hash_val,
                            'algorithm': algo
                        })
        return extracted
    except Exception as e:
        print(f"[-] Error reading shadow file: {e}")
        return []

def extract_windows_hashes(pwdump_path):
    """
    Parses a Windows SAM dump file (e.g., pwdump format) and extracts hashes.
    Expected format per line: username:RID:LM_HASH:NT_HASH:::
    Note: Actual extraction from SAM registry binary requires external tools like secretsdump.
    This module simulates parsing the output of such tools.
    """
    extracted = []
    try:
        with open(pwdump_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(':')
                if len(parts) >= 4:
                    username = parts[0]
                    # parts[1] is RID
                    lm_hash = parts[2]
                    nt_hash = parts[3]
                    
                    if nt_hash and nt_hash != 'empty':
                        extracted.append({
                            'os': 'Windows',
                            'username': username,
                            'hash': nt_hash,
                            'algorithm': 'NTLM'
                        })
        return extracted
    except Exception as e:
        print(f"[-] Error reading Windows dump file: {e}")
        return []

if __name__ == "__main__":
    print("--- Hash Extractor Test ---")
    
    # Create mock shadow file
    mock_shadow = "root:$6$xyzsalt$longhashvaluehere:18000:0:99999:7:::\nuser1:$1$somesalt$md5hashhere:18000:0:99999:7:::\nnobody:*:18000:0:99999:7:::\n"
    with open("mock_shadow.txt", "w") as f:
        f.write(mock_shadow)
        
    print("[*] Parsing Linux Shadow File...")
    linux_hashes = extract_linux_hashes("mock_shadow.txt")
    for h in linux_hashes:
        print(f"  User: {h['username']}, Algo: {h['algorithm']}, Hash: {h['hash']}")
        
    # Create mock pwdump file
    mock_sam = "Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::\nGuest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::\n"
    with open("mock_pwdump.txt", "w") as f:
        f.write(mock_sam)
        
    print("\n[*] Parsing Windows SAM Dump...")
    win_hashes = extract_windows_hashes("mock_pwdump.txt")
    for h in win_hashes:
        print(f"  User: {h['username']}, Algo: {h['algorithm']}, Hash: {h['hash']}")
