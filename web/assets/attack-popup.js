function showAttackPopup() {
    // Ses dosyasını çal
    const fartSound = new Audio('https://www.myinstants.com/media/sounds/fart-with-reverb.mp3');
    fartSound.play();
    
    // Popup oluştur
    const popup = document.createElement('div');
    popup.className = 'attack-popup';
    
    // Kapatma butonu
    const closeBtn = document.createElement('button');
    closeBtn.className = 'close-btn';
    closeBtn.innerHTML = '&times;';
    closeBtn.onclick = function() {
        document.body.removeChild(popup);
    };
    
    // GIF ekle
    const gif = document.createElement('img');
    gif.src = 'attack.gif';
    gif.alt = 'GYAT C2 Attack GIF';
    
    // Başlık ekle
    const title = document.createElement('h2');
    title.textContent = 'ATTACK BAŞLATILDI!';
    
    // Elementleri popup'a ekle
    popup.appendChild(closeBtn);
    popup.appendChild(gif);
    popup.appendChild(title);
    
    // Popup'ı sayfaya ekle
    document.body.appendChild(popup);
    
    // 5 saniye sonra otomatik kapat
    setTimeout(() => {
        if (document.body.contains(popup)) {
            document.body.removeChild(popup);
        }
    }, 5000);
}