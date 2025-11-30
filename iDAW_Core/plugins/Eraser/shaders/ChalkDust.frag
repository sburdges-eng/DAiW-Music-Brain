/**
 * ChalkDust.frag - Fragment Shader for Eraser Particle Visualization
 * 
 * Renders the "Chalk Dust" particles that emanate from erased frequencies.
 * Creates a soft, diffuse particle effect reminiscent of chalk or pencil dust.
 * 
 * Used in Side B visualization when the Eraser cursor is active.
 */

#version 330 core

// Inputs from vertex shader
in vec2 fragTexCoord;
in float fragLife;
in float fragSize;
in float fragBrightness;

// Output
out vec4 fragColor;

// Uniforms
uniform float time;
uniform vec4 dustColor;  // Base chalk dust color (white/cyan)

// ============================================================================
// Noise Functions
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

// ============================================================================
// Particle Shape
// ============================================================================

float particleShape(vec2 uv, float size) {
    // Distance from center
    float dist = length(uv - 0.5);
    
    // Soft circular falloff
    float circle = 1.0 - smoothstep(0.0, 0.5 * size, dist);
    
    // Add noise for chalk-like texture
    float noiseVal = noise(uv * 20.0 + time * 0.5);
    circle *= 0.7 + 0.3 * noiseVal;
    
    return circle;
}

// ============================================================================
// Main
// ============================================================================

void main() {
    // Calculate particle alpha
    float alpha = particleShape(fragTexCoord, fragSize);
    
    // Apply life decay
    alpha *= fragLife;
    
    // Apply brightness
    alpha *= fragBrightness;
    
    // Discard nearly invisible pixels
    if (alpha < 0.01) {
        discard;
    }
    
    // Color with slight variation
    vec3 color = dustColor.rgb;
    float colorNoise = noise(fragTexCoord * 10.0 + time);
    color = mix(color, vec3(1.0), colorNoise * 0.2);
    
    // Add glow at center
    float centerDist = length(fragTexCoord - 0.5);
    float glow = exp(-centerDist * 5.0) * 0.3;
    color += vec3(glow);
    
    fragColor = vec4(color, alpha * dustColor.a);
}
