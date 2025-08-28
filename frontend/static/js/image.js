const imgFile = document.getElementById('imgFile');
const imgQueryBtn = document.getElementById('imgQueryBtn');
const imgCaption = document.getElementById('imgCaption');
const imgPrompt = document.getElementById('imgPrompt');
const imgGenBtn = document.getElementById('imgGenBtn');
const imgOut = document.getElementById('imgOut');

imgQueryBtn.onclick = async ()=>{
  if(!imgFile.files[0]) return alert('Pick an image');
  const fd = new FormData();
  fd.append('file', imgFile.files[0]);
  const r = await fetch('/api/image/query', {method:'POST', body: fd, credentials:'include'});
  const data = await r.json();
  imgCaption.textContent = data.caption || 'No caption';
};

imgGenBtn.onclick = async ()=>{
  const prompt = imgPrompt.value.trim();
  if(!prompt) return;
  const r = await fetch('/api/image/generate', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body: new URLSearchParams({prompt}), credentials:'include'});
  const data = await r.json();
  imgOut.innerHTML = `<img src="/${data.image_path}" style="max-width:100%">`;
};

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const prompt = new FormData(form).get('prompt');
  const r = await fetch('/api/image/generate', { method: 'POST', body: new FormData(form) });
  const data = await r.json();
  const img = document.getElementById('generatedImg'); // your <img> element
  img.src = `${data.image_path}?t=${Date.now()}`;       // 👈 cache-buster
});
