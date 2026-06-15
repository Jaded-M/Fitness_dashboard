/**
 * simulation.js — Biomechanical skeleton, presets, telemetry & canvas rendering.
 */

class BiomechanicsSim {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.physics = new PhysicsEngine();
        this.layers = { bones: true, muscles: true, angles: true, com: true, vectors: true };
        this.loadDumbbell = 0;
        this.loadBackpack = 0;
        this.mousePoint = { x: 0, y: 0 };
        this.hoveredPoint = null;
        this._setupMouse();
        this.buildSkeleton();
        this.loadPreset('standing');
    }

    buildSkeleton() {
        let p = this.physics;

        // === JOINTS ===
        let head   = p.addPoint(300,  70, 4.5,  false, 'Head');
        let neck   = p.addPoint(300, 118, 1.5,  false, 'Neck');
        let chest  = p.addPoint(300, 168, 15.0, false, 'Chest');
        let lumbar = p.addPoint(292, 238, 10.0, false, 'Lumbar');
        let hip    = p.addPoint(292, 318, 18.0, false, 'Hip');

        let kneeF  = p.addPoint(292, 406, 4.0, false, 'Knee_F');
        let ankleF = p.addPoint(292, 485, 1.5, false, 'Ankle_F');
        let footF  = p.addPoint(322, 508, 1.0, false, 'Foot_F');

        let kneeB  = p.addPoint(284, 406, 4.0, false, 'Knee_B');
        let ankleB = p.addPoint(284, 485, 1.5, false, 'Ankle_B');
        let footB  = p.addPoint(314, 508, 1.0, false, 'Foot_B');

        let elbowF = p.addPoint(252, 220, 2.0, false, 'Elbow_F');
        let handF  = p.addPoint(208, 260, 1.5, false, 'Hand_F');
        let elbowB = p.addPoint(348, 220, 2.0, false, 'Elbow_B');
        let handB  = p.addPoint(392, 260, 1.5, false, 'Hand_B');

        // === BONES ===
        p.addBone(head, neck,    1.0, 'Cervical Spine');
        p.addBone(neck, chest,   1.0, 'Upper Spine');
        p.addBone(chest, lumbar, 1.0, 'Mid Spine');
        p.addBone(lumbar, hip,   1.0, 'Lower Spine');

        p.addBone(chest, elbowF, 0.9, 'Upper Arm F');
        p.addBone(elbowF, handF, 0.9, 'Forearm F');
        p.addBone(chest, elbowB, 0.9, 'Upper Arm B');
        p.addBone(elbowB, handB, 0.9, 'Forearm B');

        p.addBone(hip, kneeF,   1.0, 'Femur F');
        p.addBone(kneeF, ankleF, 1.0, 'Tibia F');
        p.addBone(ankleF, footF, 1.0, 'Foot F');
        p.addBone(hip, kneeB,   1.0, 'Femur B');
        p.addBone(kneeB, ankleB, 1.0, 'Tibia B');
        p.addBone(ankleB, footB, 1.0, 'Foot B');

        // === JOINT LIMITS ===
        p.addAngleConstraint(head, neck, chest,     0.0, 1.0,  0.3, 'Neck Joint');
        p.addAngleConstraint(neck, chest, lumbar,   4.7, 5.9,  0.3, 'Upper Spine Joint');
        p.addAngleConstraint(chest, lumbar, hip,    4.7, 5.9,  0.3, 'Lumbar Joint');
        p.addAngleConstraint(hip, kneeF, ankleF,    2.0, 3.14, 0.4, 'Knee F');
        p.addAngleConstraint(kneeF, ankleF, footF,  1.2, 2.0,  0.4, 'Ankle F');
        p.addAngleConstraint(hip, kneeB, ankleB,    2.0, 3.14, 0.4, 'Knee B');
        p.addAngleConstraint(kneeB, ankleB, footB,  1.2, 2.0,  0.4, 'Ankle B');
        p.addAngleConstraint(chest, elbowF, handF,  0.5, 3.1,  0.25, 'Elbow F');
        p.addAngleConstraint(chest, elbowB, handB,  0.5, 3.1,  0.25, 'Elbow B');

        // === MUSCLES ===
        p.addMuscle(chest, head,    0.15, 0.35, 300,  'Neck Extensors');
        p.addMuscle(hip,   chest,   0.20, 0.30, 800,  'Erector Spinae');
        p.addMuscle(hip,   chest,   0.18, 0.28, 600,  'Abdominals');
        p.addMuscle(hip,   kneeF,   0.15, 0.30, 900,  'Quadriceps (F)');
        p.addMuscle(hip,   ankleF,  0.14, 0.35, 750,  'Hamstrings/Glutes (F)');
        p.addMuscle(hip,   kneeB,   0.15, 0.30, 900,  'Quadriceps (B)');
        p.addMuscle(hip,   ankleB,  0.14, 0.35, 750,  'Hamstrings/Glutes (B)');
    }

    _setupMouse() {
        let canvas = this.canvas;
        const pos = (e) => {
            let r = canvas.getBoundingClientRect();
            return {
                x: (e.clientX - r.left) * (canvas.width / r.width),
                y: (e.clientY - r.top) * (canvas.height / r.height)
            };
        };
        canvas.addEventListener('mousedown', (e) => {
            let mp = pos(e);
            this.mousePoint = mp;
            let closest = null, minD = 22;
            for (let pt of this.physics.points) {
                let d = Math.hypot(pt.x - mp.x, pt.y - mp.y);
                if (d < minD) { minD = d; closest = pt; }
            }
            if (closest) {
                this.physics.setDragTarget(closest);
                this.physics.setDragPosition(mp.x, mp.y);
            }
        });
        canvas.addEventListener('mousemove', (e) => {
            let mp = pos(e);
            this.mousePoint = mp;
            this.physics.setDragPosition(mp.x, mp.y);
            let hovered = null, minD = 16;
            for (let pt of this.physics.points) {
                let d = Math.hypot(pt.x - mp.x, pt.y - mp.y);
                if (d < minD) { minD = d; hovered = pt; }
            }
            this.hoveredPoint = hovered;
        });
        window.addEventListener('mouseup', () => this.physics.clearDragTarget());

        // Touch support
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            let t = e.touches[0];
            let r = canvas.getBoundingClientRect();
            let mp = { x: (t.clientX - r.left) * (canvas.width / r.width), y: (t.clientY - r.top) * (canvas.height / r.height) };
            this.mousePoint = mp;
            let closest = null, minD = 30;
            for (let pt of this.physics.points) {
                let d = Math.hypot(pt.x - mp.x, pt.y - mp.y);
                if (d < minD) { minD = d; closest = pt; }
            }
            if (closest) { this.physics.setDragTarget(closest); this.physics.setDragPosition(mp.x, mp.y); }
        }, { passive: false });
        canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            let t = e.touches[0];
            let r = canvas.getBoundingClientRect();
            let mp = { x: (t.clientX - r.left) * (canvas.width / r.width), y: (t.clientY - r.top) * (canvas.height / r.height) };
            this.mousePoint = mp;
            this.physics.setDragPosition(mp.x, mp.y);
        }, { passive: false });
        window.addEventListener('touchend', () => this.physics.clearDragTarget());
    }

    loadPreset(name) {
        const presets = {
            standing: {
                joints: {
                    Head:    { x: 300, y: 68  }, Neck:   { x: 300, y: 118 }, Chest:  { x: 300, y: 168 },
                    Lumbar:  { x: 292, y: 238 }, Hip:    { x: 292, y: 318 },
                    Knee_F:  { x: 295, y: 402 }, Ankle_F:{ x: 295, y: 482 }, Foot_F: { x: 322, y: 508 },
                    Knee_B:  { x: 284, y: 402 }, Ankle_B:{ x: 284, y: 482 }, Foot_B: { x: 312, y: 508 },
                    Elbow_F: { x: 252, y: 215 }, Hand_F: { x: 210, y: 255 },
                    Elbow_B: { x: 348, y: 215 }, Hand_B: { x: 390, y: 255 }
                },
                activations: { neck: 15, back: 20, core: 15, quads: 15 },
                loads: { dumbbell: 0, backpack: 0 }
            },
            slouch: {
                joints: {
                    Head:    { x: 348, y: 168 }, Neck:   { x: 322, y: 173 }, Chest:  { x: 288, y: 196 },
                    Lumbar:  { x: 268, y: 260 }, Hip:    { x: 282, y: 320 },
                    Knee_F:  { x: 290, y: 402 }, Ankle_F:{ x: 290, y: 482 }, Foot_F: { x: 318, y: 508 },
                    Knee_B:  { x: 278, y: 402 }, Ankle_B:{ x: 278, y: 482 }, Foot_B: { x: 306, y: 508 },
                    Elbow_F: { x: 302, y: 232 }, Hand_F: { x: 338, y: 252 },
                    Elbow_B: { x: 282, y: 228 }, Hand_B: { x: 318, y: 248 }
                },
                activations: { neck: 5, back: 5, core: 10, quads: 10 },
                loads: { dumbbell: 0, backpack: 0 }
            },
            badlift: {
                joints: {
                    Head:    { x: 395, y: 238 }, Neck:   { x: 374, y: 268 }, Chest:  { x: 340, y: 280 },
                    Lumbar:  { x: 280, y: 284 }, Hip:    { x: 248, y: 322 },
                    Knee_F:  { x: 268, y: 414 }, Ankle_F:{ x: 278, y: 486 }, Foot_F: { x: 308, y: 508 },
                    Knee_B:  { x: 252, y: 414 }, Ankle_B:{ x: 262, y: 486 }, Foot_B: { x: 292, y: 508 },
                    Elbow_F: { x: 350, y: 330 }, Hand_F: { x: 360, y: 378 },
                    Elbow_B: { x: 336, y: 330 }, Hand_B: { x: 346, y: 378 }
                },
                activations: { neck: 15, back: 10, core: 5, quads: 10 },
                loads: { dumbbell: 20, backpack: 0 }
            },
            squat: {
                joints: {
                    Head:    { x: 298, y: 168 }, Neck:   { x: 290, y: 205 }, Chest:  { x: 275, y: 250 },
                    Lumbar:  { x: 248, y: 308 }, Hip:    { x: 222, y: 375 },
                    Knee_F:  { x: 300, y: 390 }, Ankle_F:{ x: 280, y: 486 }, Foot_F: { x: 310, y: 508 },
                    Knee_B:  { x: 282, y: 390 }, Ankle_B:{ x: 262, y: 486 }, Foot_B: { x: 292, y: 508 },
                    Elbow_F: { x: 290, y: 304 }, Hand_F: { x: 305, y: 358 },
                    Elbow_B: { x: 276, y: 304 }, Hand_B: { x: 290, y: 358 }
                },
                activations: { neck: 25, back: 40, core: 35, quads: 55 },
                loads: { dumbbell: 20, backpack: 0 }
            },
            backpack: {
                joints: {
                    Head:    { x: 294, y: 78  }, Neck:   { x: 278, y: 124 }, Chest:  { x: 265, y: 174 },
                    Lumbar:  { x: 276, y: 244 }, Hip:    { x: 286, y: 320 },
                    Knee_F:  { x: 295, y: 402 }, Ankle_F:{ x: 290, y: 482 }, Foot_F: { x: 320, y: 508 },
                    Knee_B:  { x: 282, y: 402 }, Ankle_B:{ x: 278, y: 482 }, Foot_B: { x: 308, y: 508 },
                    Elbow_F: { x: 248, y: 218 }, Hand_F: { x: 234, y: 268 },
                    Elbow_B: { x: 344, y: 218 }, Hand_B: { x: 356, y: 268 }
                },
                activations: { neck: 20, back: 35, core: 25, quads: 20 },
                loads: { dumbbell: 0, backpack: 15 }
            }
        };

        let data = presets[name];
        if (!data) return null;
        for (let jn in data.joints) {
            let pt = this.physics.getPointByName(jn);
            if (!pt) continue;
            pt.x = data.joints[jn].x; pt.px = pt.x;
            pt.y = data.joints[jn].y; pt.py = pt.y;
        }
        this.loadDumbbell = data.loads.dumbbell;
        this.loadBackpack  = data.loads.backpack;
        return data;
    }

    applyExternalLoads() {
        let handF = this.physics.getPointByName('Hand_F');
        let handB = this.physics.getPointByName('Hand_B');
        let chest = this.physics.getPointByName('Chest');
        let g = this.physics.gravity * 0.45;
        if (this.loadDumbbell > 0) {
            handF.applyForce(0, this.loadDumbbell * g * 0.7);
            handB.applyForce(0, this.loadDumbbell * g * 0.3);
        }
        if (this.loadBackpack > 0) {
            chest.applyForce(-this.loadBackpack * g * 0.25, this.loadBackpack * g * 0.97);
        }
    }

    calculateTelemetry() {
        let head   = this.physics.getPointByName('Head');
        let neck   = this.physics.getPointByName('Neck');
        let chest  = this.physics.getPointByName('Chest');
        let lumbar = this.physics.getPointByName('Lumbar');
        let hip    = this.physics.getPointByName('Hip');
        let footF  = this.physics.getPointByName('Foot_F');
        let footB  = this.physics.getPointByName('Foot_B');
        let handF  = this.physics.getPointByName('Hand_F');

        let cervicalAngle = Math.round(Math.max(0, Math.atan2(head.x - neck.x, neck.y - head.y) * 180 / Math.PI));
        let lumbarAngle   = Math.round(Math.abs(Math.atan2(chest.x - lumbar.x, lumbar.y - chest.y) * 180 / Math.PI));

        let totalMass = 0, sumX = 0, sumY = 0;
        for (let pt of this.physics.points) {
            let m = pt.mass;
            if (pt.name === 'Hand_F') m += this.loadDumbbell * 0.7;
            if (pt.name === 'Hand_B') m += this.loadDumbbell * 0.3;
            if (pt.name === 'Chest') m += this.loadBackpack;
            totalMass += m; sumX += pt.x * m; sumY += pt.y * m;
        }
        let comX = sumX / totalMass, comY = sumY / totalMass;
        let minFX = Math.min(footF.x, footB.x) - 14;
        let maxFX = Math.max(footF.x, footB.x) + 14;
        let baseCenter = (minFX + maxFX) / 2;
        let comOffset = (comX - baseCenter) * 0.15;
        let balanced  = comX >= minFX && comX <= maxFX;

        const pxM = 0.012;
        let lumbarTorque = 0;
        lumbarTorque += chest.mass * 9.81 * (chest.x - lumbar.x) * pxM;
        lumbarTorque += head.mass  * 9.81 * (head.x  - lumbar.x) * pxM;
        lumbarTorque += neck.mass  * 9.81 * (neck.x  - lumbar.x) * pxM;
        if (this.loadDumbbell > 0) lumbarTorque += this.loadDumbbell * 9.81 * (handF.x - lumbar.x) * pxM;
        if (this.loadBackpack > 0) lumbarTorque += this.loadBackpack * 9.81 * ((chest.x - 12) - lumbar.x) * pxM;
        lumbarTorque = Math.abs(Math.round(lumbarTorque));

        let neckP  = Math.max(0, cervicalAngle - 8) * 1.8;
        let lumP   = Math.max(0, lumbarAngle - 10) * 1.3;
        let balP   = Math.max(0, Math.abs(comOffset) - 3) * 6;
        let strain = 0;
        for (let m of this.physics.muscles) strain += m.getStrain();
        let strainP = strain * 8;
        let postureScore = Math.max(0, Math.min(100, Math.round(100 - neckP - lumP - balP - strainP)));

        return { cervicalAngle, lumbarAngle, comX, comY, minFX, maxFX, comOffset, balanced, lumbarTorque, postureScore };
    }

    draw(tel) {
        let ctx = this.ctx;
        let W = this.canvas.width, H = this.canvas.height;
        ctx.clearRect(0, 0, W, H);

        if (this.layers.ideal) {
            this.drawIdealGhost();
        }

        // Grid
        ctx.strokeStyle = 'rgba(255,255,255,0.025)';
        ctx.lineWidth = 1;
        for (let x = 0; x < W; x += 40) { ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); }
        for (let y = 0; y < H; y += 40) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }

        let fY = this.physics.floorY;

        // Floor
        ctx.strokeStyle = 'rgba(255,255,255,0.18)';
        ctx.lineWidth = 2.5;
        ctx.beginPath(); ctx.moveTo(30, fY); ctx.lineTo(W - 30, fY); ctx.stroke();
        let fg = ctx.createLinearGradient(0, fY, 0, fY + 28);
        fg.addColorStop(0, 'rgba(99,179,237,0.07)'); fg.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = fg; ctx.fillRect(30, fY, W - 60, 28);

        // Support base
        if (this.layers.com) {
            ctx.fillStyle   = tel.balanced ? 'rgba(52,211,153,0.12)' : 'rgba(239,68,68,0.12)';
            ctx.strokeStyle = tel.balanced ? '#34d399' : '#ef4444';
            ctx.lineWidth = 1.5;
            ctx.fillRect(tel.minFX, fY - 5, tel.maxFX - tel.minFX, 10);
            ctx.strokeRect(tel.minFX, fY - 5, tel.maxFX - tel.minFX, 10);
        }

        // Backpack visual
        if (this.loadBackpack > 0) {
            let ch = this.physics.getPointByName('Chest');
            let lu = this.physics.getPointByName('Lumbar');
            let ang = Math.atan2(ch.y - lu.y, ch.x - lu.x) - Math.PI/2;
            ctx.save();
            ctx.translate(ch.x, ch.y);
            ctx.rotate(ang);
            ctx.fillStyle   = 'rgba(251,146,60,0.35)';
            ctx.strokeStyle = 'rgba(251,146,60,0.9)';
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.roundRect(-22, -8, 17, 44, 7); ctx.fill(); ctx.stroke();
            ctx.fillStyle = '#fff'; ctx.font = 'bold 7px monospace'; ctx.textAlign = 'center';
            ctx.fillText(this.loadBackpack + 'kg', -13, 18);
            ctx.restore();
        }

        const isBack = (name) => name && name.endsWith('_B');

        // Muscles
        if (this.layers.muscles) {
            for (let m of this.physics.muscles) {
                let back = isBack(m.p1.name) || isBack(m.p2.name);
                ctx.globalAlpha = back ? 0.28 : 0.88;
                let s = m.getStrain();
                let color = s < 0.25 ? '#34d399' : (s < 0.75 ? '#fbbf24' : '#ef4444');
                ctx.strokeStyle = color;
                ctx.lineWidth = back ? 7 : 11;
                ctx.lineCap = 'round';
                let sx = m.p1.x, sy = m.p1.y, ex = m.p2.x, ey = m.p2.y;
                if (m.name === 'Erector Spinae') { sx -= 11; ex -= 11; }
                else if (m.name === 'Abdominals') { sx += 9; ex += 9; }
                else if (m.name === 'Neck Extensors') { sx -= 6; ex -= 6; }
                ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(ex, ey); ctx.stroke();
                if (m.activation > 0.05) {
                    ctx.strokeStyle = 'rgba(255,255,255,0.18)';
                    ctx.lineWidth = 1.5;
                    ctx.setLineDash([4, 6]);
                    ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(ex, ey); ctx.stroke();
                    ctx.setLineDash([]);
                }
            }
            ctx.globalAlpha = 1;
        }

        // Bones
        if (this.layers.bones) {
            for (let b of this.physics.bones) {
                let back = isBack(b.p1.name) || isBack(b.p2.name);
                ctx.globalAlpha = back ? 0.32 : 1;
                ctx.strokeStyle = back ? '#2d3748' : '#e2e8f0';
                ctx.lineWidth = back ? 4 : 6;
                ctx.lineCap = 'round';
                ctx.beginPath(); ctx.moveTo(b.p1.x, b.p1.y); ctx.lineTo(b.p2.x, b.p2.y); ctx.stroke();
            }
            ctx.globalAlpha = 1;
        }

        // Dumbbell
        if (this.loadDumbbell > 0) {
            let hF = this.physics.getPointByName('Hand_F');
            ctx.fillStyle = 'rgba(99,179,237,0.38)';
            ctx.strokeStyle = '#63b3ed'; ctx.lineWidth = 2;
            [-9, 9].forEach(ox => { ctx.beginPath(); ctx.arc(hF.x + ox, hF.y, 13, 0, Math.PI*2); ctx.fill(); ctx.stroke(); });
            ctx.strokeStyle = '#fff'; ctx.lineWidth = 4;
            ctx.beginPath(); ctx.moveTo(hF.x - 12, hF.y); ctx.lineTo(hF.x + 12, hF.y); ctx.stroke();
            ctx.fillStyle = '#fff'; ctx.font = 'bold 8px monospace'; ctx.textAlign = 'center';
            ctx.fillText(this.loadDumbbell + ' kg', hF.x, hF.y - 20);
        }

        // Joint angle arcs
        if (this.layers.angles) {
            let hd = this.physics.getPointByName('Head'), nk = this.physics.getPointByName('Neck');
            let ch = this.physics.getPointByName('Chest'), lu = this.physics.getPointByName('Lumbar');
            let hp = this.physics.getPointByName('Hip');
            this._drawAngleArc(ch, nk, hd, tel.cervicalAngle + '°', '#63b3ed');
            this._drawAngleArc(hp, lu, ch, tel.lumbarAngle + '°', '#fbbf24');
        }

        // Joints (nodes)
        for (let pt of this.physics.points) {
            let back = isBack(pt.name);
            ctx.globalAlpha = back ? 0.38 : 1;
            let hov = this.hoveredPoint === pt;
            ctx.fillStyle = hov ? '#63b3ed' : (back ? '#2d3748' : '#475569');
            ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5;
            ctx.beginPath(); ctx.arc(pt.x, pt.y, hov ? 8 : 5, 0, Math.PI * 2);
            ctx.fill(); ctx.stroke();
        }
        ctx.globalAlpha = 1;

        // CoM
        if (this.layers.com) {
            let cx = tel.comX, cy = tel.comY;
            let col = tel.balanced ? '#34d399' : '#ef4444';
            ctx.strokeStyle = col; ctx.fillStyle = col + '66'; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.arc(cx, cy, 9, 0, Math.PI*2); ctx.fill(); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(cx-14,cy); ctx.lineTo(cx+14,cy); ctx.moveTo(cx,cy-14); ctx.lineTo(cx,cy+14); ctx.stroke();
            ctx.strokeStyle = col + 'aa'; ctx.lineWidth = 1.5; ctx.setLineDash([6, 5]);
            ctx.beginPath(); ctx.moveTo(cx, cy+10); ctx.lineTo(cx, fY); ctx.stroke();
            ctx.setLineDash([]);
            ctx.fillStyle = col; ctx.font = 'bold 9px monospace'; ctx.textAlign = 'center';
            ctx.fillText('CoM', cx, cy - 18);
        }

        // Force vectors
        if (this.layers.vectors) {
            const arrow = (pt, fx, fy, col, lbl) => {
                let ex = pt.x + fx, ey = pt.y + fy;
                ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = 2; ctx.lineCap = 'round';
                ctx.beginPath(); ctx.moveTo(pt.x, pt.y); ctx.lineTo(ex, ey); ctx.stroke();
                let a = Math.atan2(fy, fx);
                ctx.beginPath(); ctx.moveTo(ex, ey);
                ctx.lineTo(ex - 7*Math.cos(a-Math.PI/6), ey - 7*Math.sin(a-Math.PI/6));
                ctx.lineTo(ex - 7*Math.cos(a+Math.PI/6), ey - 7*Math.sin(a+Math.PI/6));
                ctx.closePath(); ctx.fill();
                if (lbl) { ctx.fillStyle = '#fff'; ctx.font = '8px monospace'; ctx.textAlign = 'left'; ctx.fillText(lbl, ex+4, ey+3); }
            };
            let hd = this.physics.getPointByName('Head');
            let fF = this.physics.getPointByName('Foot_F'), fB = this.physics.getPointByName('Foot_B');
            arrow(hd, 0, hd.mass * 4.5, 'rgba(239,68,68,0.55)', 'W_head');
            arrow(fF, 0, -34, '#34d399', 'GRF_F');
            arrow(fB, 0, -34, 'rgba(52,211,153,0.6)', 'GRF_B');
            if (this.loadDumbbell > 0) {
                let hF = this.physics.getPointByName('Hand_F');
                arrow(hF, 0, this.loadDumbbell * 4, 'rgba(239,68,68,0.8)', 'Load:' + this.loadDumbbell + 'kg');
            }
            if (this.loadBackpack > 0) {
                let ch = this.physics.getPointByName('Chest');
                arrow(ch, -10, this.loadBackpack * 3.5, 'rgba(251,146,60,0.8)', 'Pack:' + this.loadBackpack + 'kg');
            }
            if (this.physics.draggedPoint) {
                let dp = this.physics.draggedPoint;
                arrow(dp, (this.mousePoint.x - dp.x) * 0.7, (this.mousePoint.y - dp.y) * 0.7, '#63b3ed', 'F_pull');
            }
        }
    }

    _drawAngleArc(p1, vertex, p2, label, color) {
        let ctx = this.ctx;
        let a1 = Math.atan2(p1.y - vertex.y, p1.x - vertex.x);
        let a2 = Math.atan2(p2.y - vertex.y, p2.x - vertex.x);
        let s = a1, e = a2;
        if (s > e) { let t = s; s = e; e = t; }
        if (e - s > Math.PI) { s += Math.PI * 2; let t = s; s = e; e = t; }
        ctx.strokeStyle = color; ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(vertex.x, vertex.y, 22, s, e); ctx.stroke();
        let mid = (s + e) / 2;
        ctx.fillStyle = '#fff'; ctx.font = 'bold 9px monospace'; ctx.textAlign = 'center';
        ctx.fillText(label, vertex.x + 36 * Math.cos(mid), vertex.y + 36 * Math.sin(mid) + 3);
    }

    drawIdealGhost() {
        const ctx = this.ctx;
        ctx.save();
        
        // Ideal coords aligned with the 'standing' preset
        const ideal = [
            { x: 300, y: 150 }, // Head
            { x: 300, y: 190 }, // Cervical
            { x: 295, y: 270 }, // Thoracic
            { x: 300, y: 350 }, // Lumbar
            { x: 300, y: 390 }, // Pelvis
            { x: 310, y: 510 }, // Foot (F)
            { x: 270, y: 510 }  // Foot (B)
        ];

        ctx.strokeStyle = 'rgba(167, 139, 250, 0.25)'; // Accent purple ghost
        ctx.lineWidth = 8;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.setLineDash([10, 10]);

        ctx.beginPath();
        // Spine
        ctx.moveTo(ideal[0].x, ideal[0].y);
        for (let i = 1; i <= 4; i++) ctx.lineTo(ideal[i].x, ideal[i].y);
        ctx.stroke();

        // Legs
        ctx.beginPath();
        ctx.moveTo(ideal[4].x, ideal[4].y); ctx.lineTo(ideal[5].x, ideal[5].y); // Front leg
        ctx.moveTo(ideal[4].x, ideal[4].y); ctx.lineTo(ideal[6].x, ideal[6].y); // Back leg
        ctx.stroke();

        // Ghost label
        ctx.fillStyle = 'rgba(167, 139, 250, 0.6)';
        ctx.font = '10px Inter';
        ctx.setLineDash([]);
        ctx.fillText('IDEAL POSTURE ALIGNMENT', ideal[0].x + 20, ideal[0].y);

        ctx.restore();
    }
}
