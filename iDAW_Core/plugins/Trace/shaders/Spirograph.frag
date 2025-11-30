/**
 * Spirograph.frag - Fragment Shader for The Trace visualization
 * 
 * Profile: 'Tape/Digital Delay' with Spirograph UI
 * 
 * Uses parametric equations:
 * x = R * cos(t) + r * cos(k * t)
 * y = R * sin(t) + r * sin(k * t)
 * 
 * Mapping:
 * - Feedback -> Number of loops (k)
 * - Time -> Radius (R)
 */

#version 330 core

in vec2 fragTexCoord;
out vec4 fragColor;

uniform float time;
uniform float outerRadius;      // R (delay time)
uniform float innerRadius;      // r
uniform float loopCount;        // k (feedback)
uniform float rotationSpeed;
uniform float lineThickness;
uniform float traceProgress;
uniform vec4 traceColor;
uniform vec4 backgroundColor;

// Noise for Da Vinci sketch effect
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    
    return mix(
        mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
        mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x),
        u.y
    );
}

// Spirograph point calculation
vec2 spirographPoint(float t, float R, float r, float k) {
    float x = R * cos(t) + r * cos(k * t);
    float y = R * sin(t) + r * sin(k * t);
    return vec2(x, y);
}

// Distance from point to spirograph curve
float spirographDistance(vec2 p, float R, float r, float k, float maxT) {
    float minDist = 1000.0;
    
    // Sample the curve
    const int samples = 200;
    for (int i = 0; i < samples; i++) {
        float t = float(i) / float(samples) * maxT;
        vec2 curvePoint = spirographPoint(t, R, r, k);
        float dist = length(p - curvePoint);
        minDist = min(minDist, dist);
    }
    
    return minDist;
}

// Pencil/graphite stroke effect
float pencilStroke(float dist, float thickness, vec2 uv) {
    float base = smoothstep(thickness, thickness * 0.5, dist);
    
    // Add graphite texture
    float grain = noise(uv * 200.0 + time * 0.1);
    base *= 0.7 + 0.3 * grain;
    
    // Sketch-like variation
    float sketch = noise(uv * 50.0);
    base *= 0.8 + 0.2 * sketch;
    
    return base;
}

// Paper texture
vec3 paperBackground() {
    vec2 uv = fragTexCoord;
    vec3 paper = backgroundColor.rgb;
    
    float grain = noise(uv * 100.0) * 0.05;
    paper -= grain;
    
    return paper;
}

void main() {
    vec2 uv = fragTexCoord;
    vec2 centered = (uv - 0.5) * 2.0;  // -1 to 1
    
    // ==========================================================================
    // SAFETY: Clamp all uniform values to prevent NaN/Infinity
    // ==========================================================================
    float safeOuterRadius = clamp(outerRadius, 0.1, 1.5);
    float safeInnerRadius = clamp(innerRadius, 0.01, 0.5);
    float safeLoopCount = clamp(loopCount, 1.0, 50.0);
    float safeRotationSpeed = clamp(rotationSpeed, 0.0, 10.0);
    float safeLineThickness = clamp(lineThickness, 0.001, 0.2);
    float safeTraceProgress = clamp(traceProgress, 0.0, 1.0);
    
    // Paper background
    vec3 color = paperBackground();
    
    // Spirograph parameters
    float R = safeOuterRadius * 0.4;
    float r = safeInnerRadius * 0.15;
    float k = safeLoopCount;
    
    // Animation: rotate over time
    float rotation = time * safeRotationSpeed * 0.5;
    float c = cos(rotation);
    float s = sin(rotation);
    centered = vec2(centered.x * c - centered.y * s, 
                    centered.x * s + centered.y * c);
    
    // Calculate how much of the curve to draw
    float maxT = 6.28318 * (k + 1.0) * safeTraceProgress;
    
    // Distance to spirograph curve
    float dist = spirographDistance(centered, R, r, k, maxT);
    
    // Pencil stroke
    float thickness = safeLineThickness * 0.02;
    float stroke = pencilStroke(dist, thickness, uv);
    
    // Multiple passes for sketch effect
    float stroke2 = pencilStroke(dist + 0.005, thickness * 0.8, uv + 0.01) * 0.5;
    float stroke3 = pencilStroke(dist - 0.003, thickness * 0.6, uv - 0.01) * 0.3;
    
    float totalStroke = min(stroke + stroke2 + stroke3, 1.0);
    
    // Apply graphite color
    vec3 graphite = traceColor.rgb;
    color = mix(color, graphite, totalStroke * 0.9);
    
    // Center point (pen holder)
    float centerDist = length(centered);
    float centerDot = smoothstep(0.02, 0.01, centerDist);
    color = mix(color, vec3(0.3), centerDot);
    
    // Outer ring (gear)
    float ringDist = abs(centerDist - R);
    float ring = smoothstep(0.015, 0.005, ringDist);
    color = mix(color, vec3(0.4), ring * 0.5);
    
    // Inner gear
    float innerDist = abs(centerDist - r * 2.0);
    float innerRing = smoothstep(0.01, 0.005, innerDist);
    color = mix(color, vec3(0.5), innerRing * 0.3);
    
    // Vignette
    float vignette = 1.0 - length(uv - 0.5) * 0.6;
    color *= vignette;
    
    // Age/sepia tint
    color = mix(color, vec3(0.9, 0.85, 0.75), 0.1);
    
    fragColor = vec4(color, 1.0);
}
