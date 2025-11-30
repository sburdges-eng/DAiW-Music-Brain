/**
 * Heartbeat.frag - Fragment Shader for The Press visualization
 * 
 * Profile: 'VCA Workhorse' (Clean, RMS Detection, Feed-Forward)
 * 
 * Visual mapping:
 * - Gain Reduction → Heart Scale (Systole/Diastole)
 * - Release Time → Heart Relaxation Rate
 * 
 * Uses Da Vinci sketch rendering for organic appearance.
 */

#version 330 core

// Inputs
in vec2 fragTexCoord;

// Outputs
out vec4 fragColor;

// Uniforms from processor
uniform float time;
uniform float heartScale;         // 0.7 (compressed) to 1.0 (relaxed)
uniform float heartRelaxationRate; // Animation speed
uniform float gainReductionDb;    // For meter display
uniform float inputLevel;         // Input level in dB
uniform float outputLevel;        // Output level in dB
uniform vec4 heartColor;          // Heart color (red)
uniform vec4 backgroundColor;     // Background

// ============================================================================
// Noise Functions (Da Vinci sketch style)
// ============================================================================

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    
    vec2 u = f * f * (3.0 - 2.0 * f);
    
    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

float fbm(vec2 p, int octaves) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    
    for (int i = 0; i < octaves; i++) {
        value += amplitude * noise(p * frequency);
        amplitude *= 0.5;
        frequency *= 2.0;
    }
    
    return value;
}

// ============================================================================
// Heart Shape (Signed Distance Function)
// ============================================================================

float heartSDF(vec2 p) {
    // Transform for heart shape
    p.y -= 0.25;
    p.x = abs(p.x);
    
    // Heart curve
    if (p.y + p.x > 1.0) {
        return sqrt(dot(p - vec2(0.25, 0.75), p - vec2(0.25, 0.75))) - 0.25;
    }
    
    return sqrt(min(
        dot(p - vec2(0.0, 1.0), p - vec2(0.0, 1.0)),
        dot(p - 0.5 * max(p.x + p.y, 0.0), p - 0.5 * max(p.x + p.y, 0.0))
    )) * sign(p.x - p.y);
}

// Anatomical heart shape (more realistic)
float anatomicalHeart(vec2 p, float scale) {
    p /= scale;
    p.y -= 0.1;
    
    // Main body
    float body = length(p * vec2(1.0, 0.8)) - 0.4;
    
    // Top lobes
    vec2 p1 = p - vec2(-0.2, 0.25);
    vec2 p2 = p - vec2(0.2, 0.25);
    float lobe1 = length(p1) - 0.2;
    float lobe2 = length(p2) - 0.2;
    float lobes = min(lobe1, lobe2);
    
    // Bottom point
    vec2 pBottom = p - vec2(0.0, -0.35);
    float point = length(pBottom * vec2(2.0, 0.8)) - 0.15;
    
    // Combine
    float heart = min(body, lobes);
    heart = min(heart, point);
    
    // Aorta (top pipe)
    vec2 pAorta = p - vec2(0.05, 0.4);
    float aorta = length(pAorta * vec2(3.0, 1.0)) - 0.08;
    heart = min(heart, aorta);
    
    return heart;
}

// ============================================================================
// Da Vinci Sketch Style
// ============================================================================

float sketchLine(vec2 uv, float dist, float thickness) {
    // Base line with noise
    float line = smoothstep(thickness, 0.0, abs(dist));
    
    // Add sketch strokes
    float strokes = noise(uv * 50.0 + time * 0.2);
    line *= 0.7 + 0.3 * strokes;
    
    // Hand-drawn wobble
    float wobble = noise(uv * 20.0) * 0.005;
    
    return line;
}

vec3 sketchShading(vec2 uv, float dist, vec3 baseColor) {
    // Cross-hatching for shading
    float shade = smoothstep(0.0, -0.2, dist);
    
    // Hatching lines
    float hatch1 = step(0.5, fract(uv.x * 30.0 + uv.y * 30.0));
    float hatch2 = step(0.5, fract(uv.x * 30.0 - uv.y * 30.0));
    
    float hatching = mix(1.0, 0.7, shade * hatch1 * 0.5);
    hatching *= mix(1.0, 0.8, shade * hatch2 * 0.3);
    
    return baseColor * hatching;
}

// ============================================================================
// Heartbeat Animation
// ============================================================================

float heartbeat(float t, float rate) {
    // Double-bump heartbeat pattern
    float beat = sin(t * rate * 3.14159) * 0.5 + 0.5;
    beat = pow(beat, 4.0);
    
    // Second bump (dicrotic notch)
    float beat2 = sin((t + 0.1) * rate * 3.14159) * 0.5 + 0.5;
    beat2 = pow(beat2, 8.0) * 0.3;
    
    return beat + beat2;
}

// ============================================================================
// Meter Display
// ============================================================================

float drawMeter(vec2 uv, float level, float x, float width, float height) {
    // Vertical meter bar
    if (uv.x >= x && uv.x <= x + width) {
        if (uv.y >= 0.1 && uv.y <= 0.1 + height) {
            // Normalize level (-60 to 0 dB)
            float normalizedLevel = clamp((level + 60.0) / 60.0, 0.0, 1.0);
            float meterY = (uv.y - 0.1) / height;
            
            if (meterY <= normalizedLevel) {
                return 1.0;
            }
        }
    }
    return 0.0;
}

float drawGRMeter(vec2 uv, float gr, float x, float width, float height) {
    // GR meter (fills from top)
    if (uv.x >= x && uv.x <= x + width) {
        if (uv.y >= 0.1 && uv.y <= 0.1 + height) {
            // Normalize GR (0 to 20 dB)
            float normalizedGR = clamp(gr / 20.0, 0.0, 1.0);
            float meterY = (uv.y - 0.1) / height;
            
            if (meterY >= 1.0 - normalizedGR) {
                return 1.0;
            }
        }
    }
    return 0.0;
}

// ============================================================================
// Main
// ============================================================================

void main() {
    vec2 uv = fragTexCoord;
    vec2 center = vec2(0.5, 0.5);
    
    // ==========================================================================
    // SAFETY: Clamp all uniform values to prevent NaN/Infinity
    // ==========================================================================
    float safeHeartScale = clamp(heartScale, 0.1, 2.0);
    float safeRelaxationRate = clamp(heartRelaxationRate, 0.0, 10.0);
    float safeGainReduction = clamp(gainReductionDb, 0.0, 60.0);
    float safeInputLevel = clamp(inputLevel, -120.0, 6.0);
    float safeOutputLevel = clamp(outputLevel, -120.0, 6.0);
    
    // Paper/parchment background
    vec3 paper = vec3(0.95, 0.93, 0.88);
    float paperNoise = fbm(uv * 100.0, 3) * 0.05;
    paper -= paperNoise;
    
    vec3 color = paper;
    
    // Calculate heart animation
    float beatRate = 1.0 + safeRelaxationRate * 2.0;  // 1-3 Hz
    float beat = heartbeat(time, beatRate);
    
    // Apply heartScale with beat animation
    float animatedScale = safeHeartScale * (0.95 + beat * 0.1);
    
    // Heart position (centered, slightly up)
    vec2 heartPos = (uv - vec2(0.5, 0.55)) * 2.0;
    
    // Calculate heart SDF
    float heartDist = anatomicalHeart(heartPos, animatedScale * 0.8);
    
    // Da Vinci sketch rendering
    // Multiple sketch lines for hand-drawn effect
    float outline = 0.0;
    for (int i = 0; i < 3; i++) {
        float offset = float(i) * 0.003;
        vec2 wobble = vec2(
            noise(uv * 30.0 + float(i) * 10.0) * 0.01,
            noise(uv * 30.0 + float(i) * 20.0) * 0.01
        );
        float d = anatomicalHeart(heartPos + wobble, animatedScale * 0.8);
        outline += sketchLine(uv, d - offset, 0.015);
    }
    outline = clamp(outline, 0.0, 1.0);
    
    // Heart fill with sketch shading
    vec3 heartBaseColor = vec3(0.7, 0.2, 0.2);  // Sepia-ish red
    vec3 heartShaded = sketchShading(uv, heartDist, heartBaseColor);
    
    // Apply heart
    if (heartDist < 0.0) {
        color = mix(color, heartShaded, 0.6);
    }
    
    // Apply outline
    color = mix(color, vec3(0.2, 0.1, 0.1), outline * 0.8);
    
    // Draw veins/arteries (sketch lines)
    vec2 veinPos = heartPos + vec2(0.0, 0.4);
    float vein = length(veinPos * vec2(5.0, 1.0)) - 0.1;
    float veinLine = sketchLine(uv, vein, 0.008);
    color = mix(color, vec3(0.3, 0.15, 0.15), veinLine * 0.5);
    
    // Meters on the right side
    // Input meter (green)
    float inputMeter = drawMeter(uv, safeInputLevel, 0.85, 0.03, 0.3);
    color = mix(color, vec3(0.2, 0.6, 0.2), inputMeter);
    
    // Output meter (blue)
    float outputMeter = drawMeter(uv, safeOutputLevel, 0.9, 0.03, 0.3);
    color = mix(color, vec3(0.2, 0.4, 0.7), outputMeter);
    
    // GR meter (orange, fills from top)
    float grMeter = drawGRMeter(uv, safeGainReduction, 0.8, 0.03, 0.3);
    color = mix(color, vec3(0.9, 0.5, 0.1), grMeter);
    
    // Vignette
    float vignette = 1.0 - length(uv - 0.5) * 0.5;
    color *= vignette;
    
    // Age/sepia tint
    color = mix(color, vec3(0.9, 0.85, 0.7), 0.1);
    
    fragColor = vec4(color, 1.0);
}
