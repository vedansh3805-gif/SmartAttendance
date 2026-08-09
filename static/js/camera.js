/* ═══════════════════════════════════════════════════════════════
   SmartAttend – camera.js
   Handles: face capture (registration) + live recognition (attendance)
═══════════════════════════════════════════════════════════════ */

/* ══════════════════════════════════════════════════════════════
   SECTION 1 — FACE CAPTURE  (face_capture.html)
══════════════════════════════════════════════════════════════ */

let captureStream      = null;
let autoCaptureTimer   = null;
let capturedTotal      = 0;
let captureIndex       = 0;

function initCapturePage() {
  capturedTotal = window.CAPTURED || 0;
  captureIndex  = capturedTotal;
  updateCaptureUI(capturedTotal);

  // Auto-capture checkbox
  const auto = document.getElementById('autoCapture');
  if (auto) {
    auto.addEventListener('change', () => {
      if (auto.checked && captureStream) {
        startAutoCapture();
      } else {
        stopAutoCapture();
      }
    });
  }
}

/* ── Camera controls ────────────────────────────────────────── */
async function startCamera() {
  try {
    captureStream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
    });
    const video = document.getElementById('videoEl');
    const idle  = document.getElementById('camIdle');
    const fi    = document.getElementById('faceIndicator');

    video.srcObject = captureStream;
    video.style.display = 'block';
    if (idle) idle.style.display = 'none';
    if (fi)   fi.style.display  = 'flex';

    document.getElementById('btnStartCam').style.display = 'none';
    document.getElementById('btnStopCam').style.display  = 'inline-flex';
    document.getElementById('btnCapture').disabled = false;

    setFaceMsg('Camera ready — position your face');

    // Auto-capture if already checked
    if (document.getElementById('autoCapture')?.checked) {
      startAutoCapture();
    }

  } catch (err) {
    showToast('Camera access denied: ' + err.message, 'error');
  }
}

function stopCamera() {
  stopAutoCapture();
  if (captureStream) {
    captureStream.getTracks().forEach(t => t.stop());
    captureStream = null;
  }
  const video  = document.getElementById('videoEl');
  const idle   = document.getElementById('camIdle');
  const fi     = document.getElementById('faceIndicator');
  if (video)  { video.srcObject = null; video.style.display = 'none'; }
  if (idle)   idle.style.display = 'flex';
  if (fi)     fi.style.display  = 'none';

  document.getElementById('btnStartCam').style.display = 'inline-flex';
  document.getElementById('btnStopCam').style.display  = 'none';
  document.getElementById('btnCapture').disabled       = true;
}

function startAutoCapture() {
  stopAutoCapture();
  autoCaptureTimer = setInterval(captureFrame, 1500);
}

function stopAutoCapture() {
  if (autoCaptureTimer) { clearInterval(autoCaptureTimer); autoCaptureTimer = null; }
}

/* ── Capture frame ──────────────────────────────────────────── */
async function captureFrame() {
  if (!captureStream) { showToast('Start the camera first', 'warning'); return; }
  if (capturedTotal >= window.REQUIRED) {
    stopAutoCapture();
    showToast('All images captured! Click Train now.', 'success');
    return;
  }

  const video  = document.getElementById('videoEl');
  const canvas = document.createElement('canvas');
  canvas.width  = video.videoWidth  || 640;
  canvas.height = video.videoHeight || 480;
  canvas.getContext('2d').drawImage(video, 0, 0);
  const frame = canvas.toDataURL('image/jpeg', 0.85);

  setFaceMsg('Sending…');

  try {
    const res = await postJSON('/api/face/capture', {
      student_id: window.STUDENT_ID,
      frame: frame,
      index: captureIndex
    });

    if (res.success) {
      captureIndex++;
      capturedTotal = res.total;
      updateCaptureUI(capturedTotal);
      addThumb(frame);
      setFaceMsg(`${capturedTotal} / ${window.REQUIRED} captured`);

      if (capturedTotal >= window.REQUIRED) {
        stopAutoCapture();
        document.getElementById('autoCapture').checked = false;
        document.getElementById('btnTrain').disabled   = false;
        showToast(`${window.REQUIRED} images captured — train the model!`, 'success');
        setFaceMsg('Capture complete ✓');
      }
    } else {
      setFaceMsg(res.message || 'No face detected');
    }
  } catch (e) {
    setFaceMsg('Network error');
  }
}

/* ── Train model ────────────────────────────────────────────── */
async function trainModel() {
  const btn = document.getElementById('btnTrain');
  const msg = document.getElementById('trainMsg');
  btn.disabled   = true;
  btn.innerHTML  = '<i class="fa-solid fa-spinner spin"></i> Training…';
  if (msg) msg.textContent = 'Processing face encodings…';

  try {
    const res = await postJSON('/api/face/train', { student_id: window.STUDENT_ID });
    if (res.success) {
      showToast(res.message, 'success');
      if (msg) msg.textContent = '✓ ' + res.message;
      btn.innerHTML = '<i class="fa-solid fa-circle-check"></i> Trained!';
      btn.style.background = 'linear-gradient(135deg,#10d4a3,#059669)';
      const trainStatus = document.getElementById('trainStatus');
      if (trainStatus) {
        trainStatus.innerHTML = `
          <div class="train-done">
            <i class="fa-solid fa-circle-check"></i>
            <span>Face model trained successfully</span>
          </div>`;
      }
    } else {
      showToast(res.message, 'error');
      if (msg) msg.textContent = '✗ ' + res.message;
      btn.disabled  = false;
      btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Retry Training';
    }
  } catch (e) {
    showToast('Training failed: ' + e.message, 'error');
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Retry Training';
  }
}

/* ── UI helpers ─────────────────────────────────────────────── */
function updateCaptureUI(count) {
  const countEl = document.getElementById('captureCount');
  const fill    = document.getElementById('progressFill');
  const imgCnt  = document.getElementById('trainImgCount');
  const pctEl   = document.getElementById('trainPct');
  const pct     = Math.min(100, Math.round(count / window.REQUIRED * 100));

  if (countEl) countEl.textContent = count;
  if (fill)    fill.style.width    = pct + '%';
  if (imgCnt)  imgCnt.textContent  = count;
  if (pctEl)   pctEl.textContent   = pct + '%';

  // Enable train button if enough images
  const trainBtn = document.getElementById('btnTrain');
  if (trainBtn && count >= window.REQUIRED) trainBtn.disabled = false;
}

function addThumb(dataUrl) {
  const grid  = document.getElementById('thumbGrid');
  const empty = document.getElementById('thumbEmpty');
  if (!grid) return;
  if (empty) empty.remove();

  const img = document.createElement('img');
  img.src       = dataUrl;
  img.className = 'thumb-img';
  grid.appendChild(img);
}

function setFaceMsg(text) {
  const el = document.getElementById('faceMsg');
  if (el) el.textContent = text;
}


/* ══════════════════════════════════════════════════════════════
   SECTION 2 — LIVE ATTENDANCE  (attendance.html)
══════════════════════════════════════════════════════════════ */

let attStream         = null;
let recognitionTimer  = null;
let isRecognizing     = false;
let markedToday       = new Set();

function initAttendancePage() {
  // Populate marked set from server-side list
  document.querySelectorAll('[data-marked-id]').forEach(el => {
    markedToday.add(el.dataset.markedId);
  });
}

/* ── Attendance camera ──────────────────────────────────────── */
async function startAttCamera() {
  try {
    attStream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
    });
    const video   = document.getElementById('attVideo');
    const canvas  = document.getElementById('attCanvas');
    const idle    = document.getElementById('attIdle');

    video.srcObject = attStream;
    video.style.display  = 'block';
    canvas.style.display = 'block';
    if (idle) idle.style.display = 'none';

    document.getElementById('btnStartAtt').style.display = 'none';
    document.getElementById('btnStopAtt').style.display  = 'inline-flex';

    setAttStatus('active', 'Camera active — select subject and start recognition');
  } catch (err) {
    showToast('Camera error: ' + err.message, 'error');
  }
}

function stopAttCamera() {
  stopRecognition();
  if (attStream) {
    attStream.getTracks().forEach(t => t.stop());
    attStream = null;
  }
  const video  = document.getElementById('attVideo');
  const canvas = document.getElementById('attCanvas');
  const idle   = document.getElementById('attIdle');
  const ctx    = canvas?.getContext('2d');

  if (video)  { video.srcObject = null; video.style.display = 'none'; }
  if (canvas) { canvas.style.display = 'none'; if (ctx) ctx.clearRect(0,0,canvas.width,canvas.height); }
  if (idle)   idle.style.display = 'flex';

  document.getElementById('btnStartAtt').style.display = 'inline-flex';
  document.getElementById('btnStopAtt').style.display  = 'none';
  setAttStatus('idle', 'Camera stopped');
}

/* ── Recognition ────────────────────────────────────────────── */
function startRecognition() {
  const subjectEl = document.getElementById('subjectSelect');
  if (!subjectEl?.value) { showToast('Select a subject first', 'warning'); return; }
  if (!attStream)        { showToast('Start camera first', 'warning'); return; }

  isRecognizing = true;
  document.getElementById('btnStartRec').style.display = 'none';
  document.getElementById('btnStopRec').style.display  = 'inline-flex';
  setAttStatus('active', `Recognising — ${subjectEl.value}`);

  // Send frame every 2 seconds
  recognitionTimer = setInterval(sendFrameForRecognition, 2000);
}

function stopRecognition() {
  isRecognizing = false;
  if (recognitionTimer) { clearInterval(recognitionTimer); recognitionTimer = null; }

  const startBtn = document.getElementById('btnStartRec');
  const stopBtn  = document.getElementById('btnStopRec');
  if (startBtn) startBtn.style.display = 'inline-flex';
  if (stopBtn)  stopBtn.style.display  = 'none';

  // Clear canvas
  const canvas = document.getElementById('attCanvas');
  if (canvas) canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);

  setAttStatus('idle', 'Recognition stopped');
}

async function sendFrameForRecognition() {
  const video   = document.getElementById('attVideo');
  const canvas  = document.getElementById('attCanvas');
  const subject = document.getElementById('subjectSelect')?.value;
  if (!video || !canvas || !subject || !attStream) return;

  // Sync canvas size
  canvas.width  = video.videoWidth  || 640;
  canvas.height = video.videoHeight || 480;

  // Draw current frame on hidden canvas for capture
  const offscreen = document.createElement('canvas');
  offscreen.width  = canvas.width;
  offscreen.height = canvas.height;
  offscreen.getContext('2d').drawImage(video, 0, 0);
  const frame = offscreen.toDataURL('image/jpeg', 0.75);

  try {
    const res = await postJSON('/api/recognize', { frame, subject });
    if (!res.success) { console.warn('Recognition error:', res.error); return; }

    drawFaceBoxes(canvas, video, res.faces);

    res.marked?.forEach(sid => {
      if (!markedToday.has(sid)) {
        markedToday.add(sid);
        const face = res.faces.find(f => f.student_id === sid);
        if (face) addLiveEntry(face.name, face.student_id, subject);
      }
    });

    // Unknown face detection
    const unknownCount = res.faces.filter(f => !f.student_id).length;
    if (unknownCount > 0) {
      setAttStatus('active', `${res.faces.length} face(s) detected · ${unknownCount} unknown`);
    } else if (res.faces.length > 0) {
      setAttStatus('active', `${res.faces.length} face(s) recognised`);
    }
  } catch (e) {
    console.error('Frame error:', e);
  }
}

/* ── Canvas drawing ─────────────────────────────────────────── */
function drawFaceBoxes(canvas, video, faces) {
  const ctx    = canvas.getContext('2d');
  const scaleX = canvas.width  / (video.videoWidth  || 640);
  const scaleY = canvas.height / (video.videoHeight || 480);

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  faces.forEach(face => {
    const { top, right, bottom, left } = face.location;
    const x = left  * scaleX;
    const y = top   * scaleY;
    const w = (right - left)  * scaleX;
    const h = (bottom - top)  * scaleY;

    const known = !!face.student_id;
    const color = known ? '#10d4a3' : '#ef4444';

    // Box
    ctx.strokeStyle = color;
    ctx.lineWidth   = 2;
    ctx.strokeRect(x, y, w, h);

    // Corner accents
    const cs = 14;
    ctx.lineWidth = 3;
    [[x,y,1,1],[x+w,y,-1,1],[x,y+h,1,-1],[x+w,y+h,-1,-1]].forEach(([cx,cy,dx,dy]) => {
      ctx.beginPath();
      ctx.moveTo(cx, cy + dy * cs);
      ctx.lineTo(cx, cy);
      ctx.lineTo(cx + dx * cs, cy);
      ctx.stroke();
    });

    // Label background
    const label = known ? `${face.name}  ${face.confidence}%` : 'Unknown';
    ctx.font  = 'bold 12px Inter, sans-serif';
    const tw  = ctx.measureText(label).width;
    ctx.fillStyle = known ? 'rgba(16,212,163,.85)' : 'rgba(239,68,68,.85)';
    ctx.beginPath();
    ctx.roundRect(x - 1, y - 26, tw + 16, 22, 6);
    ctx.fill();

    // Label text
    ctx.fillStyle = '#fff';
    ctx.fillText(label, x + 7, y - 9);
  });
}

/* ── Live entry list ────────────────────────────────────────── */
function addLiveEntry(name, studentId, subject) {
  const list = document.getElementById('liveEntryList');
  const empty= document.getElementById('liveEmpty');
  if (!list) return;
  if (empty) empty.remove();

  const now  = new Date().toLocaleTimeString('en-IN', { hour:'2-digit', minute:'2-digit' });
  const item = document.createElement('div');
  item.className = 'live-entry';
  item.innerHTML = `
    <div class="entry-avatar">${name[0]?.toUpperCase() || '?'}</div>
    <div>
      <div class="entry-name">${name}</div>
      <div class="entry-meta">${studentId} · ${subject}</div>
    </div>
    <div class="entry-time">${now}</div>
  `;
  list.prepend(item);

  // Update count badge
  const badge = document.getElementById('markedCount');
  if (badge) badge.textContent = parseInt(badge.textContent || 0) + 1;

  showToast(`✓ ${name} marked present`, 'success', 2000);
}

/* ── Manual mark ────────────────────────────────────────────── */
async function manualMark() {
  const sid     = document.getElementById('manualSid')?.value?.trim();
  const subject = document.getElementById('subjectSelect')?.value;
  const status  = document.getElementById('manualStatus')?.value || 'Present';

  if (!sid)     { showToast('Enter a student ID', 'warning'); return; }
  if (!subject) { showToast('Select a subject',   'warning'); return; }

  const res = await postJSON('/api/attendance/mark', { student_id: sid, subject, status });
  if (res.success) {
    showToast(res.message, 'success');
    document.getElementById('manualSid').value = '';
    // Add to live list
    const name = document.getElementById('manualNameDisplay')?.textContent || sid;
    addLiveEntry(name, sid, subject);
  } else {
    showToast(res.message, 'error');
  }
}

/* ── Status bar ─────────────────────────────────────────────── */
function setAttStatus(state, text) {
  const dot  = document.getElementById('statusDot');
  const msg  = document.getElementById('statusMsg');
  if (dot) { dot.className = `status-dot ${state}`; }
  if (msg) msg.textContent = text;
}
