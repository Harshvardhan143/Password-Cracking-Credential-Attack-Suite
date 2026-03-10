import os
import sys
import datetime

# Import project modules
from dictionary_generator import generate_dictionary, save_dictionary
from hash_extractor import extract_linux_hashes, extract_windows_hashes
from brute_force_simulator import brute_force_dictionary, simulate_incremental_bruteforce, format_time
from strength_analyzer import analyze_password

def print_banner():
    print("="*60)
    print("      Password Cracking & Credential Attack Suite       ")
    print("              Educational/Audit Toolkit                 ")
    print("="*60)

def generate_audit_report(results, filename="audit_report.txt"):
    try:
        with open(filename, "w") as f:
            f.write("="*60 + "\n")
            f.write("            PASSWORD SECURITY AUDIT REPORT            \n")
            f.write("="*60 + "\n")
            f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Module 1: Hash Extraction Summary
            f.write("--- 1. Hashes Extracted ---\n")
            if 'extracted_hashes' in results and results['extracted_hashes']:
                f.write(f"Total Hashes Extracted: {len(results['extracted_hashes'])}\n")
                for h in results['extracted_hashes']:
                    f.write(f"  User: {h['username']} | OS: {h['os']} | Algo: {h['algorithm']}\n")
            else:
                f.write("None\n")
            
            f.write("\n--- 2. Dictionary Analysis ---\n")
            if 'generated_dict_len' in results:
                f.write(f"Generated Custom Dictionary with {results['generated_dict_len']} entries.\n")
            else:
                f.write("None\n")
                
            f.write("\n--- 3. Password Strength Analysis ---\n")
            if 'strength_results' in results and results['strength_results']:
                for r in results['strength_results']:
                    f.write(f"Password Sample: {r['password']}\n")
                    f.write(f"  Strength: {r['strength']} (Entropy: {r['entropy']})\n")
                    if r['recommendations']:
                        f.write("  Recommendations:\n")
                        for rec in r['recommendations']:
                            f.write(f"    - {rec}\n")
                    f.write("\n")
            else:
                f.write("None\n")
                
            f.write("\n--- 4. Brute-Force Simulation ---\n")
            if 'bruteforce_time' in results:
                f.write(f"Estimated time to crack 8-char alphanumeric: {results['bruteforce_time']}\n")
            if 'cracked_hashes' in results and results['cracked_hashes']:
                f.write("Cracked Hashes (Dictionary Attack):\n")
                for c in results['cracked_hashes']:
                    f.write(f"  User: {c['user']} | Password: {c['password']} | Attempts: {c['attempts']} | Time: {c['time']:.4f}s\n")
            else:
                f.write("No hashes cracked via dictionary (or simulation not run).\n")
                
            f.write("\n" + "="*60 + "\n")
            
        print(f"\n[+] Audit Report generated successfully: {filename}")
    except Exception as e:
        print(f"[-] Error writing audit report: {e}")

def main():
    print_banner()
    results = {}
    wordlist = []
    
    while True:
        print("\nMain Menu:")
        print("1. Generate Custom Dictionary")
        print("2. Extract & Parse Hashes (Mock/Offline)")
        print("3. Analyze Password Strength")
        print("4. Simulate Crack / Dictionary Attack")
        print("5. Generate Audit Report")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            base_words_str = input("Enter base words separated by commas (e.g. admin, password, P4ss): ")
            base_words = [w.strip() for w in base_words_str.split(',') if w.strip()]
            if base_words:
                print("[*] Generating mutations (Leet-Speak, Casings, Appended Numbers)...")
                wordlist = generate_dictionary(base_words, max_number=99)
                results['generated_dict_len'] = len(wordlist)
                print(f"[+] Generated {len(wordlist)} unique variants.")
                
                save_choice = input("Save dictionary to file? (y/n): ").strip().lower()
                if save_choice == 'y':
                    filename = input("Enter filename (e.g. wordlist.txt): ").strip()
                    save_dictionary(wordlist, filename)
            else:
                print("[-] No base words provided.")
                
        elif choice == '2':
            print("1. Linux Shadow File")
            print("2. Windows SAM/SYSTEM Dump (pwdump format)")
            os_choice = input("Select OS (1/2): ").strip()
            filepath = input("Enter path to file: ").strip()
            
            if not os.path.exists(filepath):
                print("[-] File not found.")
                continue
                
            extracted = []
            if os_choice == '1':
                extracted = extract_linux_hashes(filepath)
            elif os_choice == '2':
                extracted = extract_windows_hashes(filepath)
            else:
                print("[-] Invalid selection.")
                continue
                
            results['extracted_hashes'] = extracted
            print(f"[+] Successfully extracted {len(extracted)} valid hashes.")
            for h in extracted:
                print(f"   {h['username']} ({h['algorithm']}) -> {h['hash'][:20]}...")
                
        elif choice == '3':
            pwd_to_test = input("Enter password to analyze: ").strip()
            if pwd_to_test:
                # Basic standard dictionary words for simple checking
                dummy_dict = {"password", "admin", "123456", "qwerty", "welcome"}
                if wordlist:
                    dummy_dict.update(wordlist)
                    
                analysis = analyze_password(pwd_to_test, dictionary_words=dummy_dict)
                print("\n[+] Analysis Results:")
                print(f"Strength: {analysis['strength']}")
                print(f"Entropy: {analysis['entropy']} bits")
                print("Recommendations:")
                for r in analysis['recommendations']:
                    print(f" - {r}")
                    
                if 'strength_results' not in results:
                    results['strength_results'] = []
                results['strength_results'].append(analysis)
                
        elif choice == '4':
            print("1. Estimate Time-To-Crack (Incremental Brute-Force)")
            print("2. Simulated Dictionary Attack on Extracted Hashes")
            atk_choice = input("Select operation (1/2): ").strip()
            
            if atk_choice == '1':
                length = input("Enter max password length to simulate (e.g. 8): ").strip()
                try:
                    length = int(length)
                    secs = simulate_incremental_bruteforce(length, use_lower=True, use_upper=True, use_digits=True, use_symbols=True)
                    results['bruteforce_time'] = format_time(secs)
                except ValueError:
                    print("[-] Please enter a valid number.")
            
            elif atk_choice == '2':
                if 'extracted_hashes' not in results or not results['extracted_hashes']:
                    print("[-] No hashes extracted. Please run Hash Extraction (Option 2) first.")
                    continue
                if not wordlist:
                    print("[-] No dictionary loaded. Please generate a dictionary first (Option 1).")
                    continue
                    
                cracked = []
                for h in results['extracted_hashes']:
                    if h['algorithm'] in ['NTLM', 'MD5', 'SHA-1', 'SHA-256', 'SHA-512']:
                        print(f"[*] Attacking hash for {h['username']} ({h['algorithm']})...")
                        res = brute_force_dictionary(h['hash'], h['algorithm'], wordlist)
                        if res.get('found'):
                            print(f"[+] CRACKED {h['username']}: {res['password']} in {res['attempts']} attempts")
                            cracked.append({
                                'user': h['username'],
                                'password': res['password'],
                                'attempts': res['attempts'],
                                'time': res['time']
                            })
                        else:
                            print(f"[-] Failed to crack {h['username']}")
                    else:
                        print(f"[-] Skipping {h['username']} (Unsupported Algorithm: {h['algorithm']})")
                results['cracked_hashes'] = cracked
                
        elif choice == '5':
            filename = input("Enter report filename [default: audit_report.txt]: ").strip()
            if not filename:
                filename = "audit_report.txt"
            generate_audit_report(results, filename)
            
        elif choice == '6':
            print("Exiting...")
            sys.exit(0)
        else:
            print("[-] Invalid choice.")

if __name__ == "__main__":
    main()
