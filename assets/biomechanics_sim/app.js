/**
 * app.js — Main app controller: navigation, sliders, physics loop, EMG chart, telemetry.
 */

document.addEventListener('DOMContentLoaded', () => {

    // ─── PAGE NAVIGATION ───────────────────────────────────────────────────────
    const pages     = document.querySelectorAll('.page');
    const navBtns   = document.querySelectorAll('.nav-btn');

    const pageTitles = {
        'page-overview': 'Overview',
        'page-biomech':  'Biomechanics Simulator',
        'page-about':    'How It Works'
    };

    function showPage(id) {
        pages.forEach(p => p.classList.toggle('active', p.id === id));
        navBtns.forEach(b => b.classList.toggle('active', b.dataset.page === id));
        const titleEl = document.getElementById('pageTitle');
        if (titleEl) titleEl.textContent = pageTitles[id] || 'FitCore';
        if (id === 'page-biomech') setTimeout(resizeEmg, 60);
    }

    navBtns.forEach(b => b.addEventListener('click', () => showPage(b.dataset.page)));
    showPage('page-overview');

    // ─── SIMULATION INIT ───────────────────────────────────────────────────────
    const sim = new BiomechanicsSim('simCanvas');

    // ─── EMG CHART ─────────────────────────────────────────────────────────────
    const emgCanvas = document.getElementById('emgCanvas');
    const emgCtx    = emgCanvas.getContext('2d');
    const emgHist   = { neck: new Array(120).fill(0), back: new Array(120).fill(0) };

    function resizeEmg() {
        const rect = emgCanvas.parentElement.getBoundingClientRect();
        emgCanvas.width  = rect.width;
        emgCanvas.height = rect.height || 80;
    }
    resizeEmg();
    window.addEventListener('resize', resizeEmg);

    // ─── PLAYBACK STATE ────────────────────────────────────────────────────────
    let isRunning = true;
    let timeScale = 1.0;
    let lastTime  = performance.now();

    // ─── PRESETS ───────────────────────────────────────────────────────────────
    const presetBtns = {
        standing: document.getElementById('presetStanding'),
        slouch:   document.getElementById('presetSlouch'),
        badlift:  document.getElementById('presetBadLift'),
        squat:    document.getElementById('presetSquat'),
        backpack: document.getElementById('presetBackpack')
    };

    function markActivePreset(name) {
        Object.entries(presetBtns).forEach(([k, btn]) =>
            btn.classList.toggle('active', k === name));
    }

    function loadPresetUI(name) {
        const data = sim.loadPreset(name);
        if (!data) return;
        markActivePreset(name);

        setSlider('loadDumbbell', 'valDumbbell', data.loads.dumbbell, v => sim.loadDumbbell = v, v => v + ' kg');
        setSlider('loadBackpack', 'valBackpack', data.loads.backpack,  v => sim.loadBackpack = v, v => v + ' kg');

        setSlider('actNeck',  'valActNeck',  data.activations.neck,  v => sim.physics.getMuscleByName('Neck Extensors').setActivation(v/100), v => v + '%');
        setSlider('actBack',  'valActBack',  data.activations.back,  v => sim.physics.getMuscleByName('Erector Spinae').setActivation(v/100), v => v + '%');
        setSlider('actCore',  'valActCore',  data.activations.core,  v => sim.physics.getMuscleByName('Abdominals').setActivation(v/100), v => v + '%');
        setSlider('actQuads', 'valActQuads', data.activations.quads, v => {
            sim.physics.getMuscleByName('Quadriceps (F)').setActivation(v/100);
            sim.physics.getMuscleByName('Quadriceps (B)').setActivation(v/100);
            sim.physics.getMuscleByName('Hamstrings/Glutes (F)').setActivation(v * 0.7/100);
            sim.physics.getMuscleByName('Hamstrings/Glutes (B)').setActivation(v * 0.7/100);
        }, v => v + '%');
    }

    function setSlider(sliderId, labelId, value, onChange, fmt) {
        const el = document.getElementById(sliderId);
        const lb = document.getElementById(labelId);
        if (el) el.value = value;
        if (lb) lb.textContent = fmt(value);
        onChange(value);
    }

    Object.entries(presetBtns).forEach(([name, btn]) =>
        btn.addEventListener('click', () => loadPresetUI(name)));

    // ─── LOAD SLIDERS ──────────────────────────────────────────────────────────
    bindSlider('loadDumbbell', 'valDumbbell', v => { sim.loadDumbbell = v; markActivePreset(''); }, v => v + ' kg');
    bindSlider('loadBackpack',  'valBackpack',  v => { sim.loadBackpack  = v; markActivePreset(''); }, v => v + ' kg');

    // ─── MUSCLE SLIDERS ────────────────────────────────────────────────────────
    bindSlider('actNeck', 'valActNeck', v => {
        sim.physics.getMuscleByName('Neck Extensors').setActivation(v/100); markActivePreset('');
    }, v => v + '%');
    bindSlider('actBack', 'valActBack', v => {
        sim.physics.getMuscleByName('Erector Spinae').setActivation(v/100); markActivePreset('');
    }, v => v + '%');
    bindSlider('actCore', 'valActCore', v => {
        sim.physics.getMuscleByName('Abdominals').setActivation(v/100); markActivePreset('');
    }, v => v + '%');
    bindSlider('actQuads', 'valActQuads', v => {
        sim.physics.getMuscleByName('Quadriceps (F)').setActivation(v/100);
        sim.physics.getMuscleByName('Quadriceps (B)').setActivation(v/100);
        sim.physics.getMuscleByName('Hamstrings/Glutes (F)').setActivation(v * 0.7/100);
        sim.physics.getMuscleByName('Hamstrings/Glutes (B)').setActivation(v * 0.7/100);
        markActivePreset('');
    }, v => v + '%');

    // ─── PHYSICS SLIDERS ───────────────────────────────────────────────────────
    bindSlider('paramGravity', 'valGravity', v => sim.physics.gravity = v, v => v + ' m/s²');
    bindSlider('paramDamping', 'valDamping', v => sim.physics.damping = v/100, v => (v/100).toFixed(2));

    // ─── LAYER TOGGLES ─────────────────────────────────────────────────────────
    sim.layers.ideal = false; // Add default
    ['bones','muscles','angles','com','vectors', 'ideal'].forEach(layer => {
        const btn = document.getElementById('toggle_' + layer);
        if (!btn) return;
        btn.addEventListener('click', () => {
            sim.layers[layer] = !sim.layers[layer];
            btn.classList.toggle('active', sim.layers[layer]);
        });
    });

    // ─── PLAY / PAUSE / RESET ──────────────────────────────────────────────────
    const btnPlay = document.getElementById('btnPlayPause');
    const playIcon = document.getElementById('playIcon');
    const playText = document.getElementById('playText');

    btnPlay.addEventListener('click', () => {
        isRunning = !isRunning;
        playIcon.textContent = isRunning ? '⏸' : '▶';
        playText.textContent = isRunning ? 'Pause' : 'Resume';
        btnPlay.classList.toggle('primary-btn', isRunning);
        if (isRunning) lastTime = performance.now();
    });

    document.getElementById('btnReset').addEventListener('click', () => {
        const active = Object.entries(presetBtns).find(([, b]) => b.classList.contains('active'));
        loadPresetUI(active ? active[0] : 'standing');
    });

    document.getElementById('simSpeed').addEventListener('change', e => timeScale = parseFloat(e.target.value));

    // ─── HELPERS ───────────────────────────────────────────────────────────────
    function bindSlider(sliderId, labelId, onChange, fmt) {
        const el = document.getElementById(sliderId);
        if (!el) return;
        el.addEventListener('input', e => {
            const v = parseFloat(e.target.value);
            const lb = document.getElementById(labelId);
            if (lb) lb.textContent = fmt(v);
            onChange(v);
        });
    }

    // ─── INITIAL LOAD ──────────────────────────────────────────────────────────
    loadPresetUI('standing');

    // ─── EMG DRAW ──────────────────────────────────────────────────────────────
    function drawEMG() {
        const neckM = sim.physics.getMuscleByName('Neck Extensors');
        const backM = sim.physics.getMuscleByName('Erector Spinae');
        emgHist.neck.push(neckM ? neckM.getStrain() : 0); if (emgHist.neck.length > 120) emgHist.neck.shift();
        emgHist.back.push(backM ? backM.getStrain() : 0); if (emgHist.back.length > 120) emgHist.back.shift();

        emgCtx.clearRect(0, 0, emgCanvas.width, emgCanvas.height);

        const gridLine = (val, col, lbl) => {
            let y = emgCanvas.height - val * emgCanvas.height;
            emgCtx.strokeStyle = col; emgCtx.lineWidth = 0.5;
            emgCtx.beginPath(); emgCtx.moveTo(0,y); emgCtx.lineTo(emgCanvas.width,y); emgCtx.stroke();
            emgCtx.fillStyle = col; emgCtx.font = '7px monospace'; emgCtx.fillText(lbl, 6, y - 3);
        };
        gridLine(0.1, 'rgba(52,211,153,0.18)',  'RELAXED');
        gridLine(0.5, 'rgba(251,191,36,0.18)',  'WARNING');
        gridLine(0.9, 'rgba(239,68,68,0.18)',   'CRITICAL');

        const line = (hist, col) => {
            if (hist.length < 2) return;
            emgCtx.strokeStyle = col; emgCtx.lineWidth = 1.5;
            emgCtx.beginPath();
            const dx = emgCanvas.width / 120;
            hist.forEach((v, i) => {
                let x = i * dx;
                let y = emgCanvas.height - (Math.min(1.2, v) / 1.2) * (emgCanvas.height - 10) - 5;
                i === 0 ? emgCtx.moveTo(x, y) : emgCtx.lineTo(x, y);
            });
            emgCtx.stroke();
        };
        line(emgHist.neck, '#63b3ed');
        line(emgHist.back, '#fbbf24');

        emgCtx.font = '8px monospace';
        emgCtx.fillStyle = '#63b3ed'; emgCtx.textAlign = 'left'; emgCtx.fillText('● Neck', emgCanvas.width - 110, 12);
        emgCtx.fillStyle = '#fbbf24'; emgCtx.fillText('● Back', emgCanvas.width - 60, 12);
    }

    // ─── DASHBOARD UPDATE ──────────────────────────────────────────────────────
    function updateUI(tel) {
        // Posture score
        const scoreEl = document.getElementById('postureScore');
        const commentEl = document.getElementById('postureComment');
        if (scoreEl) {
            scoreEl.textContent = tel.postureScore;
            scoreEl.className = 'score-value ' + (tel.postureScore >= 80 ? 'excellent' : tel.postureScore >= 55 ? 'fair' : 'poor');
        }
        if (commentEl) {
            commentEl.textContent = tel.postureScore >= 80
                ? 'Optimal spinal alignment — keep it up!'
                : tel.postureScore >= 55
                ? 'Moderate strain detected. Adjust posture.'
                : 'HIGH RISK — Critical spinal load!';
        }

        // Balance badge
        const badge = document.getElementById('balanceBadge');
        if (badge) {
            badge.textContent = tel.balanced ? 'BALANCED' : 'FALL RISK';
            badge.className = 'status-badge ' + (tel.balanced ? 'ok' : 'danger');
        }

        // Telemetry rows
        setTel('telNeck',   tel.cervicalAngle + '°',    tel.cervicalAngle  > 25 ? 'warn' : tel.cervicalAngle  > 12 ? 'mid' : 'ok');
        setTel('telSpine',  tel.lumbarAngle + '°',      tel.lumbarAngle    > 30 ? 'warn' : tel.lumbarAngle    > 15 ? 'mid' : 'ok');
        setTel('telCom',    Math.abs(tel.comOffset).toFixed(1) + ' cm ' + (tel.comOffset > 0 ? '▶' : tel.comOffset < 0 ? '◀' : ''), Math.abs(tel.comOffset) > 6 ? 'warn' : Math.abs(tel.comOffset) > 3 ? 'mid' : 'ok');
        setTel('telTorque', tel.lumbarTorque + ' N·m',  tel.lumbarTorque   > 120 ? 'warn' : tel.lumbarTorque  > 60 ? 'mid' : 'ok');

        // Muscle strain bars
        setStrain('Neck', sim.physics.getMuscleByName('Neck Extensors'));
        setStrain('Back', sim.physics.getMuscleByName('Erector Spinae'));
        setStrain('Core', sim.physics.getMuscleByName('Abdominals'));
        setStrain('Quads', sim.physics.getMuscleByName('Quadriceps (F)'));

        const gF = sim.physics.getMuscleByName('Hamstrings/Glutes (F)');
        const gB = sim.physics.getMuscleByName('Hamstrings/Glutes (B)');
        const avgG = gF && gB ? (gF.getStrain() + gB.getStrain()) / 2 : 0;
        setStrainRaw('Glutes', avgG);

        // Overview cards (sync score card there too)
        const ovScore = document.getElementById('ovScore');
        if (ovScore) {
            ovScore.textContent = tel.postureScore;
            ovScore.style.color = tel.postureScore >= 80 ? 'var(--success)' : tel.postureScore >= 55 ? 'var(--warning)' : 'var(--danger)';
        }
        const ovScoreBar = document.getElementById('ovScoreBar');
        if (ovScoreBar) ovScoreBar.style.width = tel.postureScore + '%';
        const ovTorque = document.getElementById('ovTorque');
        if (ovTorque) {
            ovTorque.textContent = tel.lumbarTorque + ' N·m';
            ovTorque.style.color = tel.lumbarTorque > 120 ? 'var(--danger)' : tel.lumbarTorque > 60 ? 'var(--warning)' : 'var(--primary)';
        }
        const ovBalance = document.getElementById('ovBalance');
        if (ovBalance) {
            ovBalance.textContent = tel.balanced ? 'OK' : 'RISK';
            ovBalance.style.color = tel.balanced ? 'var(--success)' : 'var(--danger)';
        }
        const ovNeck = document.getElementById('ovNeck');
        if (ovNeck) {
            ovNeck.textContent = tel.cervicalAngle + '°';
            ovNeck.style.color = tel.cervicalAngle > 25 ? 'var(--danger)' : tel.cervicalAngle > 12 ? 'var(--warning)' : 'var(--primary)';
        }
    }

    function setTel(id, txt, cls) {
        const el = document.getElementById(id);
        if (!el) return;
        el.textContent = txt;
        el.className = 'tel-val ' + cls;
    }

    function setStrain(key, muscle) {
        const s = muscle ? muscle.getStrain() : 0;
        setStrainRaw(key, s);
    }

    function setStrainRaw(key, s) {
        const pct = Math.round(s * 100);
        const lbl = document.getElementById('lbl' + key);
        const bar = document.getElementById('bar' + key);
        if (lbl) lbl.textContent = pct + '%';
        if (bar) {
            bar.style.width = Math.min(100, pct) + '%';
            bar.className = 'bar-fill ' + (pct < 25 ? 'ok' : pct < 75 ? 'mid' : 'warn');
        }
    }

    // ─── MAIN LOOP ─────────────────────────────────────────────────────────────
    function frame(time) {
        let dt = Math.min((time - lastTime) / 1000, 0.1);
        lastTime = time;

        if (isRunning) {
            const sub = (dt * timeScale) / 3;
            for (let i = 0; i < 3; i++) { sim.applyExternalLoads(); sim.physics.step(sub); }
        }

        const tel = sim.calculateTelemetry();
        sim.draw(tel);
        drawEMG();
        updateUI(tel);

        requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
});
