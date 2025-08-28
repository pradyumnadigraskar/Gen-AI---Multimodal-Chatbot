const audFile = document.getElementById('audFile');
const audQueryBtn = document.getElementById('audQueryBtn');
const audTranscript = document.getElementById('audTranscript');
const audText = document.getElementById('audText');
const audGenBtn = document.getElementById('audGenBtn');
const audPlayer = document.getElementById('audPlayer');

audQueryBtn.onclick = async ()=>{
  if(!audFile.files[0]) return alert('Pick an audio file');
  const fd = new FormData();
  fd.append('file', audFile.files[0]);
  const r = await fetch('/api/audio/query', {method:'POST', body: fd, credentials:'include'});
  const data = await r.json();
  audTranscript.textContent = data.transcript || 'No transcript';
};

// frontend/static/js/audio.js
audGenBtn.onclick = async () => {
  const text = audText.value.trim();
  if (!text) return;

  const r = await fetch('/api/audio/generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: new URLSearchParams({ text }),
    credentials: 'include'
  });
  const data = await r.json();

  audPlayer.src = `/${data.audio_path}?t=${Date.now()}`;
  audPlayer.load();
  try { await audPlayer.play(); } catch (e) { console.warn(e); }

  // Most browsers require a user gesture to play; this is a click handler, so it's fine
  try {
    await audPlayer.play();
  } catch (e) {
    console.warn('Autoplay blocked or other play error:', e);
  }
};


