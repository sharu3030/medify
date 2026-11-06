let userLat = null, userLng = null;

function setStatus(msg) { document.getElementById('status').textContent = 'Status: ' + msg; }

function buildMapsUrl(dept) {
  const lat = userLat !== null ? userLat : 20;
  const lng = userLng !== null ? userLng : 78;
  const q = encodeURIComponent(`${dept} hospitals near ${lat},${lng}`);
  return `https://www.google.com/maps/search/${q}/@${lat},${lng},14z?output=embed`;
}

function buildMapsListUrl(dept) {
  const lat = userLat !== null ? userLat : 20;
  const lng = userLng !== null ? userLng : 78;
  const q = encodeURIComponent(`${dept} hospitals near ${lat},${lng}`);
  return `https://www.google.com/maps/search/${q}/@${lat},${lng},14z`;
}

function showMap(dept) {
  document.getElementById('mapDept').textContent = dept;
  document.getElementById('mapBlock').style.display = 'block';
  document.getElementById('listBlock').style.display = 'block';
  document.getElementById('deptBadge').textContent = dept;
  document.getElementById('listDeptName').textContent = dept;
  document.getElementById('btnOpenMap').onclick = () => window.open(buildMapsListUrl(dept), '_blank');
  document.getElementById('btnViewList').onclick = () => window.open(buildMapsListUrl(dept), '_blank');
  window.scrollTo({ top: document.getElementById('mapBlock').offsetTop, behavior: 'smooth' });
}

function getLocation() {
  setStatus('Requesting GPS permission...');
  if (!navigator.geolocation) { setStatus('Geolocation not supported.'); return; }
  navigator.geolocation.getCurrentPosition(
    pos => {
      userLat = pos.coords.latitude;
      userLng = pos.coords.longitude;
      setStatus(`Live GPS location: ${userLat.toFixed(5)}, ${userLng.toFixed(5)}`);
    },
    err => {
      setStatus('GPS denied/unavailable: ' + err.message + '. Using default map view.');
    },
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
  );
}

async function searchHospitals() {
  const text = document.getElementById('symptoms').value.trim();
  if (!text) { setStatus('Please enter symptoms first.'); return; }

  setStatus('Analyzing symptoms...');
  try {
    const res = await fetch('/api/symptoms/analyze', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ symptoms: text })
    });
    const data = await res.json();
    if (!data.success) { setStatus(data.message || 'Analysis failed.'); return; }

    const dept = data.department;
    const box = document.getElementById('deptBox');
    box.classList.remove('d-none');
    box.innerHTML = `<strong>Recommended department:</strong> ${dept}<br><small>${data.message}</small>`;

    setStatus('Loading hospitals on Google Maps...');
    showMap(dept);
  } catch (e) {
    setStatus('Symptom analysis failed.');
  }
}

function navigate() {
  const name = document.getElementById('destName').value.trim();
  if (!name) { setStatus('Enter a hospital name/place.'); return; }
  const origin = userLat !== null && userLng !== null ? `${userLat},${userLng}` : '';
  const url = origin
    ? `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${encodeURIComponent(name)}`
    : `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(name)}`;
  window.open(url, '_blank');
  setStatus('Opened Google Maps directions.');
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btnLoc').addEventListener('click', getLocation);
  document.getElementById('btnRefresh').addEventListener('click', getLocation);
  document.getElementById('btnSearch').addEventListener('click', searchHospitals);
  document.getElementById('btnNavigate').addEventListener('click', navigate);

  /* ---------- AI Chatbot ---------- */
  let chatOpen = false;
  const btnToggle = document.getElementById('btnToggleChat');
  const chatBox = document.getElementById('chatBox');
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const btnSend = document.getElementById('btnSend');

  btnToggle.addEventListener('click', () => {
    chatOpen = !chatOpen;
    chatBox.style.display = chatOpen ? 'block' : 'none';
    btnToggle.textContent = chatOpen ? 'Hide Chat' : 'Open Chat';
    if (chatOpen) chatInput.focus();
  });

  function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = sender === 'user' ? 'text-end mb-2' : 'text-start mb-2';
    const bubble = document.createElement('span');
    bubble.className = sender === 'user'
      ? 'badge bg-primary text-white'
      : 'badge bg-light text-dark border';
    bubble.style.padding = '8px 12px';
    bubble.style.borderRadius = '10px';
    bubble.style.maxWidth = '85%';
    bubble.style.display = 'inline-block';
    bubble.style.wordBreak = 'break-word';
    bubble.textContent = text;
    div.appendChild(bubble);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async function sendChat() {
    const text = chatInput.value.trim();
    if (!text) return;
    addMessage(text, 'user');
    chatInput.value = '';
    setStatus('AI typing...');
    try {
      const res = await fetch('/api/chat', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message: text, lang: 'en' })
      });
      const data = await res.json();
      if (data.success) {
        addMessage(data.reply, 'bot');
        setStatus('Ready.');
      } else {
        addMessage(data.message || 'AI assistant unavailable.', 'bot');
        setStatus('AI error.');
      }
    } catch (e) {
      addMessage('AI assistant temporarily unavailable.', 'bot');
      setStatus('AI error.');
    }
  }

  btnSend.addEventListener('click', sendChat);
  chatInput.addEventListener('keypress', e => { if (e.key === 'Enter') sendChat(); });

  setStatus('Ready. Type your question in the chat below.');
});
