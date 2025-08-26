document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('disclaimer-modal');
    const checkbox = document.getElementById('disclaimer-checkbox');
    const closeBtn = document.getElementById('close-disclaimer');
    const loginBtn = document.getElementById('login-btn');
    
    // Disclaimer modal'ı göster
    loginBtn.addEventListener('click', function() {
        modal.style.display = 'flex';
    });
    
    // Checkbox durumuna göre close butonunu etkinleştir/devre dışı bırak
    checkbox.addEventListener('change', function() {
        closeBtn.disabled = !this.checked;
    });
    
    // Modal'ı kapat ve giriş işlemini başlat
    closeBtn.addEventListener('click', function() {
        if (checkbox.checked) {
            modal.style.display = 'none';
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            // Demo modu için hızlı geçiş (API bağlantısı olmadan)
            console.log('Giriş yapılıyor...');
            
            // API'ye giriş isteği gönder
            try {
                fetch('http://localhost:8080/api', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        action: 'auth',
                        username: username,
                        password: password
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log('API yanıtı:', data);
                    if (data.status === 'success') {
                        // Giriş başarılı, demo modu bilgisini localStorage'a kaydet
                        localStorage.setItem('demo_mode', data.demo_mode);
                        
                        // Dashboard sayfasına yönlendir
                        window.location.href = 'dashboard.html';
                    } else {
                        alert('Giriş başarısız: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Giriş hatası:', error);
                    
                    // API bağlantısı olmadan demo modunda devam et
                    console.log('Demo modunda devam ediliyor...');
                    localStorage.setItem('demo_mode', true);
                    window.location.href = 'dashboard.html';
                });
            } catch (error) {
                console.error('Fetch hatası:', error);
                
                // API bağlantısı olmadan demo modunda devam et
                console.log('Demo modunda devam ediliyor...');
                localStorage.setItem('demo_mode', true);
                window.location.href = 'dashboard.html';
            }
        }
    });
});