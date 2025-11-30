/**
 * HandDrawn.frag - GLSL Fragment Shader for Dream State UI
 * 
 * The Da Vinci Protocol:
 * - Uses Perlin Noise to displace UV coordinates over time
 * - Creates a "wobble" effect for hand-drawn appearance
 * - Applied to UI lines and borders in Side B (Dream State)
 * 
 * Usage in JUCE:
 *   OpenGLShaderProgram::setUniform("time", timeValue);
 *   OpenGLShaderProgram::setUniform("resolution", width, height);
 */

#version 330 core

// Inputs
in vec2 fragTexCoord;

// Outputs
out vec4 fragColor;

// Uniforms
uniform float time;
uniform vec2 resolution;
uniform vec4 lineColor;        // Base line color (cyan)
uniform vec4 backgroundColor;  // Blueprint background
uniform float wobbleIntensity; // 0.0 - 1.0, controls wobble amount
uniform float gridSpacing;     // Spacing between grid lines

// ============================================================================
// Noise Functions
// ============================================================================

// Simplified noise for GPU (hash-based)
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

// Fractal Brownian Motion for smoother wobble
float fbm(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    
    for (int i = 0; i < 4; i++) {
        value += amplitude * noise(p * frequency);
        amplitude *= 0.5;
        frequency *= 2.0;
    }
    
    return value;
}

// ============================================================================
// Hand-Drawn Line Effect
// ============================================================================

float handDrawnLine(vec2 uv, vec2 linePos, float thickness, float wobble) {
    // Add noise-based displacement
    float displacement = fbm(uv * 10.0 + time * 0.5) * wobble;
    
    // Calculate distance with displacement
    float dist = abs(uv.y - linePos.y + displacement);
    
    // Soft edge for pencil-like appearance
    float edge = smoothstep(thickness, thickness * 0.3, dist);
    
    // Add slight opacity variation (pencil pressure)
    float pressure = 0.8 + 0.2 * noise(uv * 50.0 + time);
    
    return edge * pressure;
}

// ============================================================================
// Grid Pattern
// ============================================================================

vec4 drawGrid(vec2 uv) {
    vec4 color = backgroundColor;
    
    // Wobble UV coordinates using FBM noise
    float wobbleX = fbm(vec2(uv.y * 5.0, time * 0.3)) * wobbleIntensity * 0.02;
    float wobbleY = fbm(vec2(uv.x * 5.0, time * 0.3 + 100.0)) * wobbleIntensity * 0.02;
    
    vec2 wobbledUV = uv + vec2(wobbleX, wobbleY);
    
    // Grid lines
    float gridSize = gridSpacing / resolution.x;
    
    // Vertical lines
    float vLine = mod(wobbledUV.x, gridSize);
    float vLineAlpha = 1.0 - smoothstep(0.0, 0.003, min(vLine, gridSize - vLine));
    
    // Horizontal lines  
    float hLine = mod(wobbledUV.y, gridSize);
    float hLineAlpha = 1.0 - smoothstep(0.0, 0.003, min(hLine, gridSize - hLine));
    
    // Combine lines with opacity variation (sketchy effect)
    float lineAlpha = max(vLineAlpha, hLineAlpha);
    lineAlpha *= 0.3 + 0.1 * noise(wobbledUV * 100.0);
    
    color = mix(color, lineColor, lineAlpha);
    
    return color;
}

// ============================================================================
// Knob Animation Effect (Scribble)
// ============================================================================

float scribbleEffect(vec2 uv, float progress) {
    // Zigzag mask that reveals with progress
    float zigzag = sin(uv.y * 50.0 + uv.x * 30.0) * 0.5 + 0.5;
    float reveal = smoothstep(0.0, 1.0, progress - zigzag * 0.3);
    
    // Add hand-drawn wobble to the reveal edge
    float wobble = noise(uv * 20.0 + time * 2.0) * 0.1;
    reveal += wobble * (1.0 - progress);
    
    return clamp(reveal, 0.0, 1.0);
}

// ============================================================================
// Glow Effect for Knob Highlights
// ============================================================================

vec4 addGlow(vec4 color, vec2 uv, vec2 center, float radius, vec4 glowColor) {
    float dist = length(uv - center);
    float glow = 1.0 - smoothstep(radius * 0.5, radius, dist);
    glow *= 0.5;  // Subtle glow
    
    return mix(color, glowColor, glow);
}

// ============================================================================
// Main
// ============================================================================

void main() {
    vec2 uv = fragTexCoord;
    
    // Draw blueprint grid with hand-drawn wobble
    fragColor = drawGrid(uv);
    
    // Add vignette for depth
    float vignette = 1.0 - length(uv - 0.5) * 0.5;
    fragColor.rgb *= vignette;
    
    // Subtle color variation (old paper/blueprint effect)
    float paperNoise = noise(uv * 200.0) * 0.02;
    fragColor.rgb += vec3(paperNoise);
    
    // Cyan highlight pulse
    float pulse = sin(time * 0.5) * 0.1 + 0.9;
    fragColor.rgb *= pulse;
}
