import os
from flask import Flask, render_template, request, jsonify

# Import toolkit modules
from dictionary_generator import generate_dictionary
from hash_extractor import extract_linux_hashes, extract_windows_hashes
from strength_analyzer import analyze_password
from brute_force_simulator import brute_force_dictionary, simulate_incremental_bruteforce, format_time

app = Flask(__name__)

# Mock path for uploaded/tested files in a real app,
# Here we'll just write submitted text to temp files for the extractors to read.
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate_dictionary', methods=['POST'])
def api_generate_dict():
    data = request.json
    base_words_str = data.get('base_words', '')
    max_number = int(data.get('max_number', 99))
    include_leet = data.get('include_leet', True)
    include_caps = data.get('include_caps', True)
    
    base_words = [w.strip() for w in base_words_str.split(',') if w.strip()]
    
    if not base_words:
        return jsonify({'error': 'No base words provided'}), 400
        
    try:
        wordlist = generate_dictionary(
            base_words, 
            include_leet=include_leet, 
            include_caps=include_caps, 
            append_numbers=True, 
            max_number=max_number
        )
        return jsonify({
            'count': len(wordlist),
            'sample': wordlist[:20] + (['...'] if len(wordlist) > 20 else []),
            'full_list': wordlist
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze_password', methods=['POST'])
def api_analyze_password():
    data = request.json
    password = data.get('password', '')
    
    if not password:
        return jsonify({'error': 'Password is required'}), 400
        
    try:
        raw_analysis = analyze_password(password)
        # Convert set to list if any sets exist (they usually don't in my implementation, but safe measure for JSON serialization)
        return jsonify(raw_analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract_hashes', methods=['POST'])
def api_extract_hashes():
    data = request.json
    file_content = data.get('file_content', '')
    os_type = data.get('os_type', 'linux') # 'linux' or 'windows'
    
    if not file_content:
        return jsonify({'error': 'No content provided'}), 400
        
    temp_file = os.path.join(TEMP_DIR, 'upload.txt')
    try:
        with open(temp_file, 'w') as f:
            f.write(file_content)
            
        if os_type == 'linux':
            extracted = extract_linux_hashes(temp_file)
        else:
            extracted = extract_windows_hashes(temp_file)
            
        return jsonify({'hashes': extracted})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulate_bruteforce', methods=['POST'])
def api_simulate_bruteforce():
    data = request.json
    attack_type = data.get('attack_type', 'incremental') # 'incremental' or 'dictionary'
    
    if attack_type == 'incremental':
        max_len = int(data.get('max_length', 8))
        use_lower = data.get('use_lower', True)
        use_upper = data.get('use_upper', True)
        use_digits = data.get('use_digits', True)
        use_symbols = data.get('use_symbols', False)
        hash_rate = int(data.get('hash_rate', 1000000000))
        
        try:
            total_secs = simulate_incremental_bruteforce(max_len, use_lower, use_upper, use_digits, use_symbols, hash_rate)
            return jsonify({
                'type': 'incremental',
                'time_seconds': total_secs,
                'formatted_time': format_time(total_secs)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    elif attack_type == 'dictionary':
        target_hash = data.get('target_hash', '')
        hash_algorithm = data.get('hash_algorithm', 'MD5')
        wordlist = data.get('wordlist', [])
        
        if not target_hash or not wordlist:
            return jsonify({'error': 'Target hash and wordlist are required'}), 400
            
        try:
            result = brute_force_dictionary(target_hash, hash_algorithm, wordlist)
            return jsonify({'type': 'dictionary', 'result': result})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid attack type'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
