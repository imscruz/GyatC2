document.addEventListener('DOMContentLoaded', function() {
    // Demo modu kontrolü
    const demoMode = localStorage.getItem('demo_mode') === 'true';
    const safeBanner = document.getElementById('safe-mode-banner');
    safeBanner.style.display = demoMode ? 'block' : 'none';
    
    // Demo modu toggle'ını ayarla
    const demoToggle = document.getElementById('demo-mode-toggle');
    demoToggle.checked = demoMode;
    
    // Sayfa değiştirme
    const menuItems = document.querySelectorAll('.menu-item');
    const contentPages = document.querySelectorAll('.content-page');
    
    menuItems.forEach(item => {
        if (item.id !== 'logout-btn') {
            item.addEventListener('click', function() {
                // Aktif menü öğesini güncelle
                menuItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
                
                // İlgili sayfayı göster
                const pageId = this.getAttribute('data-page') + '-page';
                contentPages.forEach(page => {
                    page.style.display = page.id === pageId ? 'block' : 'none';
                });
            });
        }
    });
    
    // Çıkış butonu
    document.getElementById('logout-btn').addEventListener('click', function() {
        localStorage.removeItem('demo_mode');
        window.location.href = 'index.html';
    });
    
    // Saldırı türüne göre port alanını göster/gizle
    const attackType = document.getElementById('attack-type');
    const portGroup = document.getElementById('port-group');
    
    attackType.addEventListener('change', function() {
        portGroup.style.display = this.value === 'L4' ? 'block' : 'none';
    });
    
    // Saldırı başlatma
    document.getElementById('start-attack-btn').addEventListener('click', function() {
        const type = document.getElementById('attack-type').value;
        const target = document.getElementById('attack-target').value;
        const duration = document.getElementById('attack-duration').value;
        const concurrency = document.getElementById('attack-concurrency').value;
        
        if (!target) {
            alert('Lütfen bir hedef girin.');
            return;
        }
        
        const attackData = {
            action: 'start_attack',
            type: type,
            target: target,
            duration: duration,
            concurrency: concurrency
        };
        
        if (type === 'L4') {
            attackData.port = document.getElementById('attack-port').value;
        }
        
        // Saldırı başlatma animasyonu
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
        this.disabled = true;
        
        try {
            // API'ye saldırı isteği gönder
            fetch('http://localhost:8080/api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(attackData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Saldırı başarıyla başlatıldı
                    addTerminalLog(`Attack started: ${type} - Target: ${target}`, 'success');
                    updateStats();
                    
                    // Popup göster
                    showAttackPopup();
                    
                    // Saldırı sayfasından dashboard'a geç
                    document.querySelector('[data-page="dashboard"]').click();
                } else {
                    // Saldırı başlatılamadı
                    addTerminalLog(`Attack failed: ${data.message}`, 'error');
                    alert('Saldırı başlatılamadı: ' + data.message);
                }
                
                // Butonu sıfırla
                this.innerHTML = 'Start Attack';
                this.disabled = false;
            })
            .catch(error => {
                console.error('Saldırı hatası:', error);
                addTerminalLog(`Attack error: ${error}`, 'error');
                
                // Demo modunda başarılı gibi davran
                if (localStorage.getItem('demo_mode') === 'true') {
                    const attackId = Math.floor(Math.random() * 1000);
                    addTerminalLog(`Attack started: ${type} - Target: ${target} (DEMO MODE)`, 'success');
                    
                    // Demo modunda saldırı simülasyonu
                    const demoAttack = {
                        id: attackId,
                        type: type,
                        target: target,
                        port: type === 'L4' ? document.getElementById('attack-port').value : null,
                        duration: duration,
                        elapsed: 0
                    };
                    
                    // Demo saldırı listesini güncelle
                updateAttacksList([demoAttack]);
                
                // Popup göster
                showAttackPopup();
                
                // Saldırı sayfasından dashboard'a geç
                document.querySelector('[data-page="dashboard"]').click();
                } else {
                    alert('Sunucuya bağlanılamadı. Lütfen sunucunun çalıştığından emin olun.');
                }
                
                // Butonu sıfırla
                this.innerHTML = 'Start Attack';
                this.disabled = false;
            });
        } catch (error) {
            console.error('Fetch hatası:', error);
            
            // Demo modunda başarılı gibi davran
            if (localStorage.getItem('demo_mode') === 'true') {
                const attackId = Math.floor(Math.random() * 1000);
                addTerminalLog(`Attack started: ${type} - Target: ${target} (DEMO MODE)`, 'success');
                
                // Demo modunda saldırı simülasyonu
                const demoAttack = {
                    id: attackId,
                    type: type,
                    target: target,
                    port: type === 'L4' ? document.getElementById('attack-port').value : null,
                    duration: duration,
                    elapsed: 0
                };
                
                // Demo saldırı listesini güncelle
                updateAttacksList([demoAttack]);
                
                // Popup göster
                showAttackPopup();
                
                // Saldırı sayfasından dashboard'a geç
                document.querySelector('[data-page="dashboard"]').click();
            } else {
                alert('Sunucuya bağlanılamadı. Lütfen sunucunun çalıştığından emin olun.');
            }
            
            // Butonu sıfırla
            this.innerHTML = 'Start Attack';
            this.disabled = false;
        }
    });
    
    // Yapılandırma kaydetme
    document.getElementById('save-config-btn').addEventListener('click', function() {
        const demoMode = document.getElementById('demo-mode-toggle').checked;
        const fakeBots = document.getElementById('fake-bots').value;
        const fakeAttacks = document.getElementById('fake-attacks').value;
        const fakeAttacksRandom = document.getElementById('fake-attacks-random').value;
        
        try {
            // API'ye yapılandırma isteği gönder
            fetch('http://localhost:8080/api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'update_config',
                    username: 'root', // Sadece root kullanıcısı için izin
                    demo_mode: demoMode,
                    fake_bots: fakeBots,
                    fake_attacks: fakeAttacks,
                    fake_attacks_random_range: fakeAttacksRandom
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Yapılandırma başarıyla güncellendi
                    localStorage.setItem('demo_mode', demoMode);
                    safeBanner.style.display = demoMode ? 'block' : 'none';
                    addTerminalLog('Configuration updated', 'info');
                    alert('Yapılandırma güncellendi.');
                } else {
                    // Yapılandırma güncellenemedi
                    addTerminalLog(`Configuration update failed: ${data.message}`, 'error');
                    alert('Yapılandırma güncellenemedi: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Yapılandırma hatası:', error);
                // API bağlantısı olmasa bile yerel olarak kaydet
                localStorage.setItem('demo_mode', demoMode);
                safeBanner.style.display = demoMode ? 'block' : 'none';
                addTerminalLog('Configuration saved locally (server offline)', 'warning');
            });
        } catch (error) {
            console.error('Fetch hatası:', error);
            // API bağlantısı olmasa bile yerel olarak kaydet
            localStorage.setItem('demo_mode', demoMode);
            safeBanner.style.display = demoMode ? 'block' : 'none';
            addTerminalLog('Configuration saved locally (server offline)', 'warning');
        }
    });
    
    // Terminal log ekleme
    function addTerminalLog(message, type = '') {
        const terminal = document.getElementById('terminal');
        const timestamp = new Date().toLocaleTimeString();
        
        const logLine = document.createElement('div');
        logLine.className = 'terminal-line';
        
        if (type) {
            logLine.classList.add(`terminal-${type}`);
        }
        
        logLine.textContent = `[${timestamp}] ${message}`;
        terminal.appendChild(logLine);
        
        // Otomatik kaydırma
        terminal.scrollTop = terminal.scrollHeight;
    }
    
    // İstatistikleri güncelleme
    function updateStats() {
        try {
            fetch('http://localhost:8080/api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'get_stats'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('bot-count').textContent = data.bots;
                    document.getElementById('attack-count').textContent = data.attacks;
                }
            })
            .catch(error => {
                console.error('İstatistik hatası:', error);
                document.getElementById('server-status').textContent = 'Offline';
                document.getElementById('server-status').style.color = 'var(--danger-color)';
                
                // Demo modunda örnek veriler
                document.getElementById('bot-count').textContent = Math.floor(Math.random() * 5);
                document.getElementById('attack-count').textContent = '0';
            });
        } catch (error) {
            console.error('Fetch hatası:', error);
            document.getElementById('server-status').textContent = 'Offline';
            document.getElementById('server-status').style.color = 'var(--danger-color)';
            
            // Demo modunda örnek veriler
            document.getElementById('bot-count').textContent = Math.floor(Math.random() * 5);
            document.getElementById('attack-count').textContent = '0';
        }
    }
    
    // Aktif saldırıları güncelleme
    function updateAttacks() {
        try {
            fetch('http://localhost:8080/api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'get_attacks'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateAttacksList(data.attacks);
                }
            })
            .catch(error => {
                console.error('Saldırı listesi hatası:', error);
                // Demo modunda boş liste göster
                updateAttacksList([]);
            });
        } catch (error) {
            console.error('Fetch hatası:', error);
            // Demo modunda boş liste göster
            updateAttacksList([]);
        }
    }
    
    // Saldırı listesini güncelleme
    function updateAttacksList(attacks) {
        const attacksList = document.getElementById('active-attacks-list');
        attacksList.innerHTML = '';
        
        if (attacks.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="7" style="text-align: center;">No active attacks</td>';
            attacksList.appendChild(row);
        } else {
            attacks.forEach(attack => {
                const row = document.createElement('tr');
                
                // Progress hesaplama
                const progress = Math.min(100, Math.round((attack.elapsed / attack.duration) * 100));
                
                row.innerHTML = `
                    <td>${attack.id}</td>
                    <td>${attack.type}</td>
                    <td>${attack.target}${attack.port ? ':' + attack.port : ''}</td>
                    <td>${attack.duration}s</td>
                    <td>
                        <div style="width: 100%; background-color: #eee; border-radius: 5px; height: 10px;">
                            <div style="width: ${progress}%; background-color: var(--primary-color); height: 10px; border-radius: 5px;"></div>
                        </div>
                        <div style="text-align: center; font-size: 0.8rem; margin-top: 5px;">${attack.elapsed}s / ${attack.duration}s</div>
                    </td>
                    <td><span class="status-badge status-active">Active</span></td>
                    <td>
                        <button class="btn btn-danger action-btn stop-attack" data-id="${attack.id}">Stop</button>
                    </td>
                `;
                
                attacksList.appendChild(row);
            });
            
            // Saldırı durdurma butonları
            document.querySelectorAll('.stop-attack').forEach(btn => {
                btn.addEventListener('click', function() {
                    const attackId = this.getAttribute('data-id');
                    
                    try {
                        fetch('http://localhost:8080/api', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                action: 'stop_attack',
                                attack_id: attackId
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success') {
                                addTerminalLog(`Attack stopped: ${attackId}`, 'warning');
                                updateStats();
                                updateAttacks();
                            } else {
                                alert('Saldırı durdurulamadı: ' + data.message);
                            }
                        })
                        .catch(error => {
                            console.error('Saldırı durdurma hatası:', error);
                            // Demo modunda başarılı gibi davran
                            addTerminalLog(`Attack stopped: ${attackId}`, 'warning');
                            updateStats();
                            updateAttacks();
                        });
                    } catch (error) {
                        console.error('Fetch hatası:', error);
                        // Demo modunda başarılı gibi davran
                        addTerminalLog(`Attack stopped: ${attackId}`, 'warning');
                        updateStats();
                        updateAttacks();
                    }
                });
            });
        }
    }
    
    // Periyodik güncelleme
    updateStats();
    updateAttacks();
    
    setInterval(() => {
        updateStats();
        updateAttacks();
    }, 5000);
});