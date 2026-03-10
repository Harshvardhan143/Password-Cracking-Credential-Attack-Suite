document.addEventListener('DOMContentLoaded', () => {
    
    // --- Navigation Tabs ---
    const navItems = document.querySelectorAll('.nav-links li');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const pageTitle = document.getElementById('page-title');

    const titles = {
        'dashboard': 'Dashboard Overview',
        'dictionary': 'Wordlist Profiler',
        'extractor': 'Credential Harvester',
        'analyzer': 'Entropy Analysis Engine',
        'simulator': 'Attack Simulation Engine'
    };

    window.switchTab = (tabId) => {
        navItems.forEach(item => item.classList.remove('active'));
        tabPanes.forEach(pane => {
            pane.classList.remove('active');
            pane.classList.remove('fade-in');
        });

        const activeNav = document.querySelector(`.nav-links li[data-tab="${tabId}"]`);
        if (activeNav) activeNav.classList.add('active');
        
        const activePane = document.getElementById(tabId);
        if (activePane) {
            activePane.classList.add('active');
            // Force redraw for animation
            void activePane.offsetWidth;
            activePane.classList.add('fade-in');
        }

        pageTitle.innerText = titles[tabId] || 'Audit Suite';
    };

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            switchTab(item.getAttribute('data-tab'));
        });
    });

    // --- Utility: Toasts ---
    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? 'ph-check-circle' : 'ph-warning-circle';
        toast.innerHTML = `<i class="ph ${icon}" style="font-size: 1.5rem; color: var(--accent-${type==='success'?'success':'danger'})"></i> 
                           <span>${message}</span>`;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // --- Dictionary Generator ---
    document.getElementById('dict-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const baseWords = document.getElementById('base-words').value;
        const submitBtn = e.target.querySelector('button');
        submitBtn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Generating...';
        
        try {
            const res = await fetch('/api/generate_dictionary', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    base_words: baseWords,
                    include_leet: document.getElementById('inc-leet').checked,
                    include_caps: document.getElementById('inc-caps').checked,
                    max_number: document.getElementById('max-number').value
                })
            });
            const data = await res.json();
            
            if (res.ok) {
                document.getElementById('dict-badge').innerText = `${data.count} words`;
                document.getElementById('dict-output').innerText = data.sample.join('\n') + 
                    (data.count > 20 ? '\n\n... (Displaying preview only)' : '');
                showToast(`Generated ${data.count} permutations.`);
                
                // Store globally for the simulator later
                window.generatedWordlist = data.full_list;
                if(document.getElementById('sim-wordlist')) {
                    document.getElementById('sim-wordlist').value = data.sample.slice(0, 10).join(', ');
                }
            } else {
                showToast(data.error, 'error');
            }
        } catch (error) {
            showToast('Network error', 'error');
        } finally {
            submitBtn.innerHTML = '<i class="ph ph-lightning"></i> Generate Words';
        }
    });

    // --- Hash Extractor ---
    document.getElementById('extract-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const content = document.getElementById('hash-content').value;
        const osType = document.querySelector('input[name="os_type"]:checked').value;
        const submitBtn = e.target.querySelector('button');
        submitBtn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Parsing...';
        
        try {
            const res = await fetch('/api/extract_hashes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file_content: content, os_type: osType })
            });
            const data = await res.json();
            
            if (res.ok) {
                document.getElementById('hash-count').innerText = `${data.hashes.length} extracted`;
                
                const tableContainer = document.getElementById('hash-results-table');
                if (data.hashes.length === 0) {
                    tableContainer.innerHTML = '<div class="placeholder-text text-brand">No valid hashes found in input.</div>';
                } else {
                    let html = '<table class="results-table"><thead><tr><th>User</th><th>Algorithm</th><th>Hash Snippet</th></tr></thead><tbody>';
                    data.hashes.forEach(h => {
                        const snippet = h.hash.length > 30 ? h.hash.substring(0, 30) + '...' : h.hash;
                        html += `<tr>
                                    <td><strong>${h.username}</strong></td>
                                    <td><span class="badge">${h.algorithm}</span></td>
                                    <td class="monospace">${snippet}</td>
                                 </tr>`;
                    });
                    html += '</tbody></table>';
                    tableContainer.innerHTML = html;
                    showToast('Extraction complete');
                }
            } else {
                showToast(data.error, 'error');
            }
        } catch(e) {
            showToast('Network error', 'error');
        } finally {
            submitBtn.innerHTML = '<i class="ph ph-magnifying-glass"></i> Parse & Extract';
        }
    });

    // --- Strength Analyzer ---
    document.getElementById('toggle-pwd').addEventListener('click', (e) => {
        const input = document.getElementById('analyze-pwd');
        const icon = e.currentTarget.querySelector('i');
        if (input.type === 'password') {
            input.type = 'text';
            icon.className = 'ph ph-eye-slash';
        } else {
            input.type = 'password';
            icon.className = 'ph ph-eye';
        }
    });

    document.getElementById('btn-analyze').addEventListener('click', async () => {
        const pwd = document.getElementById('analyze-pwd').value;
        const btn = document.getElementById('btn-analyze');
        if (!pwd) { showToast('Enter password', 'error'); return; }
        
        btn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Analyzing...';
        
        try {
            const res = await fetch('/api/analyze_password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: pwd })
            });
            const data = await res.json();
            
            if (res.ok) {
                const resultsDiv = document.getElementById('analyze-results');
                resultsDiv.classList.remove('hidden');
                
                document.getElementById('res-strength').innerText = data.strength;
                document.getElementById('res-entropy').innerText = data.entropy;
                document.getElementById('res-length').innerText = data.length;
                document.getElementById('res-charset').innerText = data.charset_size;
                
                // Color code strength
                const strengthEl = document.getElementById('res-strength');
                strengthEl.style.color = data.entropy >= 60 ? 'var(--accent-success)' : 
                                         data.entropy >= 40 ? 'var(--accent-warning)' : 'var(--accent-danger)';

                const recList = document.getElementById('res-recs');
                const recBox = document.querySelector('.recommendations-box');
                
                if (data.recommendations.length > 0) {
                    recBox.classList.remove('good');
                    recList.innerHTML = data.recommendations.map(r => `<li>${r}</li>`).join('');
                } else {
                    recBox.classList.add('good');
                    recList.innerHTML = '<li>✓ Password complies with strong policy requirements.</li>';
                }
                showToast('Analysis complete');
            } else {
                showToast(data.error, 'error');
            }
        } catch(e) {
            showToast('Network error', 'error');
        } finally {
            btn.innerHTML = 'Run Analysis';
        }
    });

    // --- Simulator Mini Tabs ---
    window.switchSimType = (type) => {
        document.querySelectorAll('.mini-tab').forEach(t => t.classList.remove('active'));
        event.currentTarget.classList.add('active');
        
        if(type === 'incremental') {
            document.getElementById('sim-incr-form').classList.remove('hidden');
            document.getElementById('sim-dict-form').classList.add('hidden');
        } else {
            document.getElementById('sim-incr-form').classList.add('hidden');
            document.getElementById('sim-dict-form').classList.remove('hidden');
            
            // Auto fill with generated if available
            if(window.generatedWordlist && document.getElementById('sim-wordlist').value === '') {
                document.getElementById('sim-wordlist').value = window.generatedWordlist.slice(0, 100).join(', ');
            }
        }
    };

    // Incremental Submit
    document.getElementById('sim-incr-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = e.target.querySelector('button');
        submitBtn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Processing...';
        
        try {
            const res = await fetch('/api/simulate_bruteforce', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    attack_type: 'incremental',
                    max_length: document.getElementById('sim-max-len').value,
                    use_lower: document.getElementById('sim-lower').checked,
                    use_upper: document.getElementById('sim-upper').checked,
                    use_digits: document.getElementById('sim-digits').checked,
                    use_symbols: document.getElementById('sim-symbols').checked,
                    hash_rate: document.getElementById('sim-hash-rate').value
                })
            });
            const data = await res.json();
            
            if (res.ok) {
                const container = document.getElementById('sim-output-container');
                container.innerHTML = `
                    <div class="sim-block">
                        <h4 style="margin:0 0 0.5rem 0; color:var(--text-muted)">Incremental Exhaustion Estimate</h4>
                        <div><strong>Max Length:</strong> ${document.getElementById('sim-max-len').value}</div>
                        <div><strong>Total Estimated Time:</strong> <span class="text-brand" style="font-size:1.2rem">${data.formatted_time}</span></div>
                        <div style="font-size:0.8rem; color:var(--text-muted); margin-top:0.5rem">Based on ${document.getElementById('sim-hash-rate').value} H/s</div>
                    </div>
                `;
                showToast('Estimation calculated');
            } else {
                showToast(data.error, 'error');
            }
        } catch(e) {
            showToast('Network error', 'error');
        } finally {
            submitBtn.innerHTML = '<i class="ph ph-play"></i> Simulate Exhaustion';
        }
    });

    // Dictionary Attack Submit
    document.getElementById('sim-dict-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = e.target.querySelector('button');
        submitBtn.innerHTML = '<i class="ph ph-spinner ph-spin"></i> Attacking...';
        
        const words = document.getElementById('sim-wordlist').value.split(',').map(w => w.trim()).filter(w => w);
        
        try {
            const res = await fetch('/api/simulate_bruteforce', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    attack_type: 'dictionary',
                    hash_algorithm: document.getElementById('sim-algo').value,
                    target_hash: document.getElementById('sim-target-hash').value.trim(),
                    wordlist: words
                })
            });
            const data = await res.json();
            
            if (res.ok) {
                const container = document.getElementById('sim-output-container');
                const r = data.result;
                
                if (r.found) {
                    container.innerHTML = `
                        <div class="sim-block sim-success">
                            <h4 style="margin:0 0 0.5rem 0; color:var(--accent-success)"><i class="ph ph-check-circle"></i> Hash Cracked!</h4>
                            <div><strong>Recovered Password:</strong> <span style="font-size:1.5rem; color:#fff">${r.password}</span></div>
                            <div style="margin-top:0.5rem"><strong>Attempts:</strong> ${r.attempts}</div>
                            <div><strong>Time Elapsed:</strong> ${r.time.toFixed(4)}s</div>
                        </div>
                    `;
                    showToast('CRACKED!', 'success');
                } else {
                    container.innerHTML = `
                        <div class="sim-block sim-fail">
                            <h4 style="margin:0 0 0.5rem 0; color:var(--accent-danger)"><i class="ph ph-warning"></i> Exhausted Wordlist</h4>
                            <div><strong>Target Hash:</strong> ${document.getElementById('sim-target-hash').value.substring(0,20)}...</div>
                            <div style="margin-top:0.5rem"><strong>Attempts:</strong> ${r.attempts}</div>
                            <div><strong>Time Elapsed:</strong> ${r.time.toFixed(4)}s</div>
                            <div style="margin-top:0.5rem; color:var(--text-muted)"><em>Password not found in provided dictionary.</em></div>
                        </div>
                    `;
                    showToast('Failed to crack', 'error');
                }
            } else {
                showToast(data.error, 'error');
            }
        } catch(e) {
            showToast('Network error', 'error');
        } finally {
            submitBtn.innerHTML = '<i class="ph ph-skull"></i> Execute Attack';
        }
    });
});
