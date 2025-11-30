/**
 * Feather.frag - Fragment shader for The Parrot plugin
 * 
 * Visual representation of vocal/instrument companion:
 * - Pitch -> Hue (low = red/warm, high = blue/cool)
 * - Volume -> Feather brightness/intensity
 * - Harmony spread -> Feather fan angle
 * - Listening state -> Ear animation
 * - Singing state -> Beak animation
 */

#version 330 core

// Inputs
in vec2 v_texCoord;
in vec2 v_position;

// Outputs
out vec4 fragColor;

// Uniforms from ParrotProcessor
uniform float u_time;
uniform float u_pitchHue;           // 0-1 (pitch mapped to color)
uniform float u_volumeIntensity;    // 0-1 (volume level)
uniform float u_harmonySpread;      // 0-1 (number of harmony voices)
uniform float u_phraseProgress;     // 0-1 (playback position)
uniform bool u_isListening;         // Ear animation trigger
uniform bool u_isSinging;           // Beak animation trigger
uniform float u_echoTrailLength;    // Echo visualization
uniform vec2 u_resolution;

// Constants
const float PI = 3.14159265359;
const vec3 PARROT_GREEN = vec3(0.2, 0.8, 0.3);
const vec3 PARROT_RED = vec3(0.9, 0.2, 0.1);
const vec3 PARROT_BLUE = vec3(0.1, 0.5, 0.9);
const vec3 PARROT_YELLOW = vec3(0.95, 0.85, 0.2);

// === Utility Functions ===

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
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

// === Color Functions ===

vec3 hueToRGB(float hue) {
    vec3 rgb = clamp(abs(mod(hue * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    return rgb;
}

vec3 getPitchColor(float hue) {
    // Blend between warm (low pitch) and cool (high pitch)
    vec3 warm = mix(PARROT_RED, PARROT_YELLOW, hue * 2.0);
    vec3 cool = mix(PARROT_GREEN, PARROT_BLUE, (hue - 0.5) * 2.0);
    return hue < 0.5 ? warm : cool;
}

// === Shape Functions ===

float sdEllipse(vec2 p, vec2 ab) {
    p = abs(p);
    if (p.x > p.y) { p = p.yx; ab = ab.yx; }
    float l = ab.y * ab.y - ab.x * ab.x;
    float m = ab.x * p.x / l;
    float m2 = m * m;
    float n = ab.y * p.y / l;
    float n2 = n * n;
    float c = (m2 + n2 - 1.0) / 3.0;
    float c3 = c * c * c;
    float q = c3 + m2 * n2 * 2.0;
    float d = c3 + m2 * n2;
    float g = m + m * n2;
    float co;
    if (d < 0.0) {
        float h = acos(q / c3) / 3.0;
        float s = cos(h);
        float t = sin(h) * sqrt(3.0);
        float rx = sqrt(-c * (s + t + 2.0) + m2);
        float ry = sqrt(-c * (s - t + 2.0) + m2);
        co = (ry + sign(l) * rx + abs(g) / (rx * ry) - m) / 2.0;
    } else {
        float h = 2.0 * m * n * sqrt(d);
        float s = sign(q + h) * pow(abs(q + h), 1.0 / 3.0);
        float u = sign(q - h) * pow(abs(q - h), 1.0 / 3.0);
        float rx = -s - u - c * 4.0 + 2.0 * m2;
        float ry = (s - u) * sqrt(3.0);
        float rm = sqrt(rx * rx + ry * ry);
        co = (ry / sqrt(rm - rx) + 2.0 * g / rm - m) / 2.0;
    }
    vec2 r = ab * vec2(co, sqrt(1.0 - co * co));
    return length(r - p) * sign(p.y - r.y);
}

// Feather shape
float feather(vec2 p, float angle, float length, float width) {
    // Rotate
    float c = cos(angle);
    float s = sin(angle);
    p = vec2(c * p.x - s * p.y, s * p.x + c * p.y);
    
    // Feather is elongated ellipse with barbule pattern
    float spine = sdEllipse(p, vec2(width * 0.1, length));
    float vane = sdEllipse(p, vec2(width, length * 0.9));
    
    // Barbule texture
    float barbules = sin(p.y * 50.0 + p.x * 20.0) * 0.02;
    
    return min(spine - 0.01, vane + barbules);
}

// Parrot body
float parrotBody(vec2 p) {
    // Body ellipse
    float body = sdEllipse(p - vec2(0.0, -0.1), vec2(0.25, 0.35));
    
    // Head
    float head = sdEllipse(p - vec2(0.0, 0.25), vec2(0.15, 0.18));
    
    // Beak
    vec2 beakP = p - vec2(0.12, 0.28);
    float beakAngle = -0.3;
    float c = cos(beakAngle);
    float s = sin(beakAngle);
    beakP = vec2(c * beakP.x - s * beakP.y, s * beakP.x + c * beakP.y);
    float beak = sdEllipse(beakP, vec2(0.12, 0.05));
    
    return min(min(body, head), beak);
}

// === Animation Functions ===

float listeningPulse(float time) {
    return 0.5 + 0.5 * sin(time * 3.0);
}

float singingPulse(float time) {
    return 0.5 + 0.5 * sin(time * 8.0);
}

// === Main Shader ===

void main() {
    vec2 uv = v_texCoord;
    vec2 aspect = vec2(u_resolution.x / u_resolution.y, 1.0);
    vec2 p = (uv - 0.5) * 2.0 * aspect;
    
    // Background - soft gradient
    vec3 bgColor = mix(
        vec3(0.05, 0.08, 0.12),
        vec3(0.1, 0.15, 0.2),
        uv.y
    );
    
    // Add noise texture to background
    float bgNoise = fbm(uv * 10.0 + u_time * 0.1, 4) * 0.05;
    bgColor += bgNoise;
    
    vec3 color = bgColor;
    
    // === Draw Parrot ===
    float parrot = parrotBody(p);
    
    if (parrot < 0.0) {
        // Base parrot color
        vec3 parrotColor = PARROT_GREEN;
        
        // Head is more colorful
        vec2 headP = p - vec2(0.0, 0.25);
        if (length(headP) < 0.2) {
            parrotColor = mix(PARROT_GREEN, PARROT_YELLOW, smoothstep(0.2, 0.1, length(headP)));
        }
        
        // Beak
        vec2 beakP = p - vec2(0.12, 0.28);
        if (length(beakP) < 0.15) {
            parrotColor = vec3(0.2, 0.2, 0.2);  // Dark beak
            
            // Beak animation when singing
            if (u_isSinging) {
                float beakOpen = singingPulse(u_time) * 0.05;
                parrotColor = mix(parrotColor, vec3(0.9, 0.3, 0.3), beakOpen * 5.0);
            }
        }
        
        // Eye
        vec2 eyeP = p - vec2(0.05, 0.3);
        if (length(eyeP) < 0.03) {
            parrotColor = vec3(0.0);  // Black eye
            if (length(eyeP) < 0.01) {
                parrotColor = vec3(1.0);  // Eye highlight
            }
        }
        
        color = parrotColor;
    }
    
    // === Draw Feathers (Harmony Visualization) ===
    float numFeathers = 5.0 + u_harmonySpread * 10.0;
    float featherSpread = 0.3 + u_harmonySpread * 0.7;
    
    for (float i = 0.0; i < 15.0; i++) {
        if (i >= numFeathers) break;
        
        float angle = (i / numFeathers - 0.5) * featherSpread * PI;
        angle += sin(u_time + i) * 0.05;  // Subtle animation
        
        vec2 featherOrigin = vec2(-0.15, -0.3);
        vec2 featherP = p - featherOrigin;
        
        float f = feather(featherP, angle - PI * 0.5, 0.4, 0.08);
        
        if (f < 0.0) {
            // Feather color based on pitch
            float featherHue = fract(u_pitchHue + i * 0.1);
            vec3 featherColor = getPitchColor(featherHue);
            
            // Add iridescence
            float iridescence = sin(featherP.y * 30.0 + u_time) * 0.2 + 0.8;
            featherColor *= iridescence;
            
            // Intensity based on volume
            featherColor *= 0.5 + u_volumeIntensity * 0.5;
            
            color = mix(color, featherColor, 0.8);
        }
    }
    
    // === Listening Indicator ===
    if (u_isListening) {
        // Pulsing ear highlight
        float pulse = listeningPulse(u_time);
        vec2 earP = p - vec2(-0.1, 0.3);
        float ear = smoothstep(0.08, 0.05, length(earP));
        color = mix(color, PARROT_YELLOW, ear * pulse * 0.5);
        
        // Sound wave rings
        for (float i = 0.0; i < 3.0; i++) {
            float radius = 0.3 + i * 0.15 + fract(u_time * 0.5 + i * 0.33) * 0.2;
            float ring = abs(length(p - vec2(-0.3, 0.2)) - radius);
            ring = smoothstep(0.02, 0.0, ring);
            color = mix(color, PARROT_YELLOW, ring * (1.0 - fract(u_time * 0.5 + i * 0.33)) * 0.5);
        }
    }
    
    // === Echo Trail ===
    if (u_echoTrailLength > 0.0) {
        for (float i = 1.0; i <= 3.0; i++) {
            float offset = i * 0.15 * u_echoTrailLength;
            float alpha = (1.0 - i / 4.0) * 0.3;
            
            vec2 echoP = p + vec2(offset, 0.0);
            float echoParrot = parrotBody(echoP);
            
            if (echoParrot < 0.0) {
                color = mix(color, getPitchColor(u_pitchHue), alpha);
            }
        }
    }
    
    // === Phrase Progress Indicator ===
    if (u_phraseProgress > 0.0 && u_phraseProgress < 1.0) {
        float progressBar = smoothstep(0.01, 0.0, abs(p.y + 0.7));
        float progressFill = step(p.x + 0.5, u_phraseProgress - 0.5);
        color = mix(color, PARROT_BLUE, progressBar * progressFill * 0.8);
        color = mix(color, vec3(0.3), progressBar * (1.0 - progressFill) * 0.3);
    }
    
    // === Musical Notes (when singing) ===
    if (u_isSinging) {
        for (float i = 0.0; i < 5.0; i++) {
            float noteTime = fract(u_time * 0.3 + i * 0.2);
            vec2 noteP = p - vec2(0.3 + noteTime * 0.5, 0.3 + sin(noteTime * PI * 2.0 + i) * 0.2);
            
            // Simple note shape
            float noteHead = length(noteP) - 0.03;
            float noteStem = max(abs(noteP.x - 0.02), abs(noteP.y - 0.05)) - 0.01;
            float note = min(noteHead, noteStem);
            
            if (note < 0.0) {
                float alpha = (1.0 - noteTime) * 0.7;
                color = mix(color, getPitchColor(fract(u_pitchHue + i * 0.15)), alpha);
            }
        }
    }
    
    // === Vignette ===
    float vignette = 1.0 - length(uv - 0.5) * 0.8;
    color *= vignette;
    
    // Output
    fragColor = vec4(color, 1.0);
}
