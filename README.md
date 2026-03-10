#Host link 
https://password-cracking-credential-attack.vercel.app/

# Password Cracking & Credential Attack Suite

An educational toolkit designed for exploring password policy testing, dictionary generation, credential security assessment, and ethical password cracking methodologies.

## Purpose

Weak passwords are a leading cause of account takeovers and data breaches. This suite provides an ethical, controlled environment to understand how passwords are cracked, how they are stored securely (or insecurely), and how defenders can audit and enforce strong password policies.

**Disclaimer:** This toolkit is for ethical learning, auditing authorization, and secure defense environments. Do NOT use these tools against systems or accounts without explicit permission.

## Modules

The toolkit consists of multiple functional modules orchestrated through a central CLI menu (`main.py`):

1. **Dictionary Generator (`dictionary_generator.py`)**
   - Generates custom wordlists from defined patterns (names, DOBS, etc.).
   - Employs mutation rules such as capitalization, leet-speak conversions, and appended numerals (e.g., `admin` to `!dm1n99`).

2. **Hash Extractor (`hash_extractor.py`)**
   - Parses Linux `/etc/shadow` dumps.
   - Parses Windows SAM/SYSTEM registry mock dumps (`pwdump` formats).
   - Identifies underlying hashing algorithms (NTLM, MD5, SHA-256, SHA-512) and parses user, salt, and hash.

3. **Password Strength Analyzer (`strength_analyzer.py`)**
   - Analyzes raw passwords for complexity requirements and Shannon entropy.
   - Detects if passwords are based on predictable dictionary keywords.
   - Provides granular improvement recommendations.

4. **Brute-Force Simulator (`brute_force_simulator.py`)**
   - Simulates a brute-force environment to analyze "time-to-crack" metrics against offline hashes.
   - Executes dictionary-based cracking operations on raw and simulated target hashes.

## Usage

You need Python 3.x to execute this suite. 

```bash
# Run the interactive toolkit menu
python main.py
```

### Flowchart / Architecture

```text
START
  ↓
Input Data (Base words, Hashes)
  ↓
  ├─→ Generate Dictionary (Mutations)
  ├─→ Extract Password Hashes (Linux Shadow / SAM)
  ├─→ Simulate Dictionary/Brute-Force Attack
  └─→ Analyze Password Strength (Entropy/Complexity Check)
  ↓
Generate Final Audit Report (Weaknesses & Cracking Times)
  ↓
END
```

## Security Audit Report
By using Option 5 in the main menu, an aggregate report (`audit_report.txt`) is automatically generated containing:
- Detected vulnerable passwords.
- Estimated and Actual cracking simulation timing.
- Identified standard weaknesses using Shannon entropy levels.
- Re-enforcement techniques and policy recommendations.
