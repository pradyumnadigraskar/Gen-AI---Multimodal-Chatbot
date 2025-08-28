// const vidFile = document.getElementById('vidFile');
// const vidQueryBtn = document.getElementById('vidQueryBtn');
// const vidAnalysis = document.getElementById('vidAnalysis');
// const vidPrompt = document.getElementById('vidPrompt');
// const vidGenBtn = document.getElementById('vidGenBtn');
// const vidPlayer = document.getElementById('vidPlayer');

// vidQueryBtn.onclick = async ()=>{
//   if(!vidFile.files[0]) return alert('Pick a video');
//   const fd = new FormData();
//   fd.append('file', vidFile.files[0]);
//   const r = await fetch('/api/video/query', {method:'POST', body: fd, credentials:'include'});
//   const data = await r.json();
//   vidAnalysis.textContent = data.analysis || 'No analysis';
// };


// // frontend/static/js/video.js
// vidGenBtn.onclick = async ()=>{
//   const prompt = vidPrompt.value.trim();
//   if(!prompt) return;
//   const r = await fetch('/api/video/generate', {
//     method:'POST',
//     headers:{'Content-Type':'application/x-www-form-urlencoded'},
//     body: new URLSearchParams({prompt}),
//     credentials:'include'
//   });
//   const data = await r.json();
//   const url = `/${data.video_path}?t=${Date.now()}`; // cache buster
//   vidPlayer.src = url;
//   vidPlayer.load();
//   vidPlayer.play().catch(()=>{ /* ignore autoplay block */ });
// };




// vidGenBtn.onclick = async () => {
//   const prompt = vidPrompt.value.trim();
//   if (!prompt) return;
//   const r = await fetch('/api/video/generate', {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
//     body: new URLSearchParams({ prompt }),
//     credentials: 'include'
//   });
//   const data = await r.json();

//   // Use correct field from backend response
//   const url = `${data.video_url}?t=${Date.now()}`;
//   vidPlayer.src = url;

//   try {
//     await vidPlayer.load();
//     await vidPlayer.play();
//   } catch (e) {
//     console.debug('Autoplay blocked or error:', e);
//   }
// };


// frontend/static/js/video.js
// const vidFile = document.getElementById('vidFile');
// const vidQueryBtn = document.getElementById('vidQueryBtn');
// const vidAnalysis = document.getElementById('vidAnalysis');
// const vidPrompt = document.getElementById('vidPrompt');
// const vidGenBtn = document.getElementById('vidGenBtn');
// const vidPlayer = document.getElementById('vidPlayer');

// vidQueryBtn.onclick = async () => {
//   if (!vidFile.files[0]) return alert('Pick a video');
//   const fd = new FormData();
//   fd.append('file', vidFile.files[0]);

//   try {
//     const r = await fetch('/api/video/query', {
//       method: 'POST',
//       body: fd,
//       credentials: 'include'
//     });
//     if (!r.ok) {
//       const txt = await r.text();
//       console.error('Analyze failed:', r.status, txt);
//       alert('Analyze failed: ' + txt);
//       return;
//     }
//     const data = await r.json();
//     vidAnalysis.textContent = data.analysis || 'No analysis';
//   } catch (e) {
//     console.error('Analyze network error:', e);
//     alert('Analyze network error. Check console for details.');
//   }
// };

// vidGenBtn.onclick = async () => {
//   const prompt = vidPrompt.value.trim();
//   if (!prompt) return;

//   try {
//     const r = await fetch('/api/video/generate', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
//       body: new URLSearchParams({ prompt }),
//       credentials: 'include'
//     });
//     if (!r.ok) {
//       const txt = await r.text();
//       console.error('Generate failed:', r.status, txt);
//       alert('Generate failed: ' + txt);
//       return;
//     }
//     const data = await r.json();

//     // backend may return video_url (new) or video_path (old)
//     const srcRaw = data.video_url || data.video_path;
//     if (!srcRaw) {
//       console.error('No video URL/path returned:', data);
//       alert('No video path returned by server');
//       return;
//     }

//     // ensure it starts with one leading slash; add cache-buster
//     const src = `/${srcRaw.replace(/^\/+/, '')}?t=${Date.now()}`;
//     vidPlayer.src = src;
//     vidPlayer.load();
//     try {
//       await vidPlayer.play();
//     } catch (e) {
//       console.debug('Autoplay blocked or play error:', e);
//     }
//   } catch (e) {
//     console.error('Generate network error:', e);
//     alert('Generate network error. Check console for details.');
//   }
// };

// frontend/static/js/video.js
const vidFile = document.getElementById('vidFile');
const vidQueryBtn = document.getElementById('vidQueryBtn');
const vidAnalysis = document.getElementById('vidAnalysis');
const vidPrompt = document.getElementById('vidPrompt');
const vidGenBtn = document.getElementById('vidGenBtn');
const vidPlayer = document.getElementById('vidPlayer');

vidQueryBtn.onclick = async () => {
  if (!vidFile.files[0]) return alert('Pick a video');
  const fd = new FormData();
  fd.append('file', vidFile.files[0]);
  try {
    const r = await fetch('/api/video/query', { method: 'POST', body: fd, credentials: 'include' });
    const data = await r.json();
    vidAnalysis.textContent = data.analysis || 'No analysis';
  } catch (e) {
    console.error('Analyze failed:', e);
    vidAnalysis.textContent = 'Analyze failed. Check console.';
  }
};

vidGenBtn.onclick = async () => {
  const prompt = vidPrompt.value.trim();
  if (!prompt) return;
  try {
    const r = await fetch('/api/video/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ prompt }),
      credentials: 'include'
    });
    const data = await r.json();
    const url = `${data.video_url || data.video_path}?t=${Date.now()}`;
    vidPlayer.src = url;
    await vidPlayer.load();
    await vidPlayer.play().catch(()=>{});
  } catch (e) {
    console.error('Generate failed:', e);
  }
};
