/**
 * physics.js — 2D Verlet Integration physics engine for biomechanics simulation.
 */

class Point {
    constructor(x, y, mass = 1.0, isStatic = false, name = '') {
        this.x = x; this.y = y;
        this.px = x; this.py = y;
        this.mass = mass;
        this.isStatic = isStatic;
        this.fx = 0; this.fy = 0;
        this.name = name;
    }

    applyForce(fx, fy) {
        if (this.isStatic) return;
        this.fx += fx;
        this.fy += fy;
    }

    update(dt, gravity, damping) {
        if (this.isStatic) return;
        let ax = this.fx / this.mass;
        let ay = (this.fy / this.mass) + gravity;
        let vx = (this.x - this.px) * damping;
        let vy = (this.y - this.py) * damping;
        let nx = this.x + vx + ax * dt * dt;
        let ny = this.y + vy + ay * dt * dt;
        this.px = this.x; this.py = this.y;
        this.x = nx; this.y = ny;
        this.fx = 0; this.fy = 0;
    }

    constrainGround(floorY, friction = 0.82) {
        if (this.isStatic || this.y <= floorY) return;
        let dx = this.x - this.px;
        this.y = floorY;
        this.py = floorY;
        this.x = this.px + dx * friction;
    }
}

class Bone {
    constructor(p1, p2, stiffness = 1.0, name = '') {
        this.p1 = p1; this.p2 = p2;
        this.stiffness = stiffness;
        this.name = name;
        let dx = p2.x - p1.x, dy = p2.y - p1.y;
        this.targetLength = Math.sqrt(dx * dx + dy * dy);
    }

    resolve() {
        let dx = this.p2.x - this.p1.x;
        let dy = this.p2.y - this.p1.y;
        let d = Math.sqrt(dx * dx + dy * dy);
        if (d < 0.001) return;
        let diff = this.targetLength - d;
        let percent = (diff / d) * this.stiffness * 0.5;
        let ox = dx * percent, oy = dy * percent;
        if (!this.p1.isStatic) { this.p1.x -= ox; this.p1.y -= oy; }
        if (!this.p2.isStatic) { this.p2.x += ox; this.p2.y += oy; }
    }
}

class AngleConstraint {
    constructor(p1, p2, p3, minAngle, maxAngle, stiffness = 0.3, name = '') {
        this.p1 = p1; this.p2 = p2; this.p3 = p3;
        this.minAngle = minAngle; this.maxAngle = maxAngle;
        this.stiffness = stiffness; this.name = name;
    }

    resolve() {
        let dx1 = this.p1.x - this.p2.x, dy1 = this.p1.y - this.p2.y;
        let dx2 = this.p3.x - this.p2.x, dy2 = this.p3.y - this.p2.y;
        let len1 = Math.sqrt(dx1*dx1 + dy1*dy1);
        let len2 = Math.sqrt(dx2*dx2 + dy2*dy2);
        if (len1 < 0.01 || len2 < 0.01) return;

        let a1 = Math.atan2(dy1, dx1);
        let a2 = Math.atan2(dy2, dx2);
        let diff = a2 - a1;
        while (diff < 0) diff += Math.PI * 2;
        while (diff > Math.PI * 2) diff -= Math.PI * 2;

        let targetAngle = diff;
        let violated = false;
        if (diff < this.minAngle) { targetAngle = this.minAngle; violated = true; }
        else if (diff > this.maxAngle) { targetAngle = this.maxAngle; violated = true; }
        if (!violated) return;

        // Clamp adjustment to prevent overshoot oscillation
        let adjustment = (targetAngle - diff) * this.stiffness;
        adjustment = Math.max(-0.4, Math.min(0.4, adjustment));
        let halfAdj = adjustment * 0.5;

        if (!this.p1.isStatic) {
            let r = a1 - halfAdj;
            this.p1.x = this.p2.x + Math.cos(r) * len1;
            this.p1.y = this.p2.y + Math.sin(r) * len1;
        }
        if (!this.p3.isStatic) {
            let r = a2 + halfAdj;
            this.p3.x = this.p2.x + Math.cos(r) * len2;
            this.p3.y = this.p2.y + Math.sin(r) * len2;
        }
    }
}

class Muscle {
    constructor(p1, p2, stiffness = 0.1, maxContraction = 0.3, maxForce = 500, name = '') {
        this.p1 = p1; this.p2 = p2;
        this.stiffness = stiffness;
        this.maxContraction = maxContraction;
        this.maxForce = maxForce;
        this.name = name;
        let dx = p2.x - p1.x, dy = p2.y - p1.y;
        this.restLength = Math.sqrt(dx * dx + dy * dy);
        this.currentRestLength = this.restLength;
        this.activation = 0.0;
        this.tension = 0.0;
    }

    setActivation(level) {
        this.activation = Math.max(0, Math.min(1, level));
        this.currentRestLength = this.restLength * (1 - this.activation * this.maxContraction);
    }

    resolve() {
        let dx = this.p2.x - this.p1.x, dy = this.p2.y - this.p1.y;
        let d = Math.sqrt(dx * dx + dy * dy);
        if (d < 0.001) return;
        if (d > this.currentRestLength) {
            let diff = d - this.currentRestLength;
            let percent = (diff / d) * this.stiffness * 0.5;
            let ox = dx * percent, oy = dy * percent;
            if (!this.p1.isStatic) { this.p1.x += ox; this.p1.y += oy; }
            if (!this.p2.isStatic) { this.p2.x -= ox; this.p2.y -= oy; }
            let activeStiffness = this.stiffness * (1 + this.activation * 2);
            this.tension = diff * activeStiffness * 20;
        } else {
            this.tension = 0;
        }
    }

    getStrain() {
        return Math.max(0, this.tension / this.maxForce);
    }
}

class PhysicsEngine {
    constructor() {
        this.points = [];
        this.bones = [];
        this.angleConstraints = [];
        this.muscles = [];
        this.floorY = 510;          // Aligned with visual floor
        this.gravity = 15.0;
        this.damping = 0.98;
        this.iterations = 12;       // Higher = stiffer/more stable
        this.draggedPoint = null;
        this.dragStrength = 0.15;
        this.dragX = 0; this.dragY = 0;
    }

    addPoint(x, y, mass = 1.0, isStatic = false, name = '') {
        let p = new Point(x, y, mass, isStatic, name);
        this.points.push(p);
        return p;
    }

    addBone(p1, p2, stiffness = 1.0, name = '') {
        let b = new Bone(p1, p2, stiffness, name);
        this.bones.push(b);
        return b;
    }

    addAngleConstraint(p1, p2, p3, min, max, stiffness = 0.3, name = '') {
        let ac = new AngleConstraint(p1, p2, p3, min, max, stiffness, name);
        this.angleConstraints.push(ac);
        return ac;
    }

    addMuscle(p1, p2, stiffness = 0.1, maxContraction = 0.3, maxForce = 500, name = '') {
        let m = new Muscle(p1, p2, stiffness, maxContraction, maxForce, name);
        this.muscles.push(m);
        return m;
    }

    getPointByName(name) { return this.points.find(p => p.name === name); }
    getMuscleByName(name) { return this.muscles.find(m => m.name === name); }

    step(dt) {
        // 1. Verlet integration
        for (let p of this.points) p.update(dt, this.gravity, this.damping);

        // 2. Iterative constraint solving
        for (let i = 0; i < this.iterations; i++) {
            // Drag
            this.resolveDrag();

            // Muscles (soft springs)
            for (let m of this.muscles) m.resolve();

            // Bones (rigid distance)
            for (let b of this.bones) b.resolve();

            // Ground collision BEFORE angle constraints — keeps feet grounded first
            for (let p of this.points) p.constrainGround(this.floorY);

            // Angle limits last (range-of-motion)
            for (let ac of this.angleConstraints) ac.resolve();
        }
    }

    setDragTarget(point) { this.draggedPoint = point; }
    clearDragTarget() { this.draggedPoint = null; }
    setDragPosition(x, y) { this.dragX = x; this.dragY = y; }

    resolveDrag() {
        if (!this.draggedPoint) return;
        let dx = this.dragX - this.draggedPoint.x;
        let dy = this.dragY - this.draggedPoint.y;
        this.draggedPoint.x += dx * this.dragStrength;
        this.draggedPoint.y += dy * this.dragStrength;
    }
}
