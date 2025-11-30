/**
 * Graphite.frag - Fragment Shader for The Pencil visualization
 * 
 * Profile: 'Graphite' (Tube Saturation / Additive EQ)
 * 
 * Visual mapping:
 * - Drive amount → LineThickness and LineNoise
 * - High Drive = Thicker, grainier charcoal lines
 * - Low Drive = Clean, precise pencil strokes
 * 
 * Used in Side B visualization when The Pencil is active.
 */

#version 330 core

// Inputs
in vec2 fragTexCoord;

// Outputs
out vec4 fragColor;

// Uniforms from processor
uniform float time;
uniform float lineThickness;    // 1.0 (clean) to 4.0 (heavy charcoal)
uniform float lineNoise;        // 0.0 (clean) to 1.0 (maximum grain)
uniform vec3 bandLevels;        // Per-band output levels
uniform vec4 backgroundColor;   // Paper color
uniform vec4 graphiteColor;     // Pencil/charcoal color

// ============================================================================
// Noise Functions
// ============================================================================

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
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

// Fractal Brownian Motion for paper texture
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
// Pencil Line Effect
// ============================================================================

// Simulate pencil stroke texture
float pencilStroke(vec2 uv, float thickness, float noiseAmount) {
    // Base stroke with slight waviness
    float waveFreq = 50.0;
    float wave = sin(uv.x * waveFreq + time * 0.5) * 0.002 * thickness;
    
    // Stroke line (horizontal)
    float line = abs(uv.y + wave - 0.5);
    float strokeAlpha = smoothstep(thickness * 0.01, 0.0, line);
    
    // Add graphite grain/noise
    float grain = noise(uv * 200.0 + time * 0.1);
    float grainPattern = noise(uv * 50.0);
    
    // Combine for pencil texture
    float pencilTexture = grain * 0.5 + grainPattern * 0.5;
    
    // More grain with more noise amount
    strokeAlpha *= 1.0 - noiseAmount * (1.0 - pencilTexture) * 0.5;
    
    // Irregular edges (charcoal effect at high noise)
    float edgeNoise = noise(uv * 100.0) * noiseAmount;
    strokeAlpha *= 1.0 - edgeNoise * 0.3;
    
    return strokeAlpha;
}

// Simulate charcoal smudge at high drive
float charcoalSmudge(vec2 uv, float intensity) {
    float smudge = fbm(uv * 20.0 + time * 0.1, 4);
    smudge = pow(smudge, 2.0 - intensity);
    
    // Directional smudge (as if rubbed horizontally)
    float directionBias = noise(vec2(uv.x * 5.0, uv.y * 50.0));
    smudge *= 0.7 + 0.3 * directionBias;
    
    return smudge * intensity;
}

// ============================================================================
// Band Level Visualization
// ============================================================================

float drawBandMeter(vec2 uv, float level, float xPos, float width) {
    // Vertical meter bar
    float barStart = xPos - width * 0.5;
    float barEnd = xPos + width * 0.5;
    
    if (uv.x >= barStart && uv.x <= barEnd) {
        // Level from bottom
        float meterHeight = level * 0.8;  // Max 80% height
        
        if (uv.y < meterHeight) {
            // Add graphite texture to meter
            float texture = noise(uv * 100.0);
            return 0.8 + 0.2 * texture;
        }
    }
    
    return 0.0;
}

// ============================================================================
// Paper Texture
// ============================================================================

vec3 paperTexture(vec2 uv) {
    // Base paper color with slight variation
    vec3 paper = backgroundColor.rgb;
    
    // Fine paper grain
    float fineGrain = noise(uv * 500.0) * 0.05;
    
    // Larger paper fiber pattern
    float fiber = fbm(uv * 30.0, 3) * 0.03;
    
    // Subtle color variation
    float warmth = noise(uv * 10.0) * 0.02;
    
    paper += vec3(fineGrain - 0.025);
    paper += vec3(fiber - 0.015);
    paper.r += warmth;
    
    return paper;
}

// ============================================================================
// Main
// ============================================================================

void main() {
    vec2 uv = fragTexCoord;
    
    // Paper background
    vec3 paper = paperTexture(uv);
    
    // Initialize with paper color
    vec3 color = paper;
    float alpha = 1.0;
    
    // Draw pencil strokes based on band levels
    // Low band (left third)
    float lowStroke = pencilStroke(vec2(uv.x * 3.0, uv.y), 
                                    lineThickness * bandLevels.x, 
                                    lineNoise);
    
    // Mid band (center third)  
    float midStroke = pencilStroke(vec2((uv.x - 0.33) * 3.0, uv.y), 
                                    lineThickness * bandLevels.y,
                                    lineNoise);
    
    // High band (right third)
    float highStroke = pencilStroke(vec2((uv.x - 0.66) * 3.0, uv.y),
                                     lineThickness * bandLevels.z,
                                     lineNoise);
    
    // Combine strokes
    float strokeIntensity = max(max(lowStroke, midStroke), highStroke);
    
    // Add charcoal smudge effect at high noise levels
    if (lineNoise > 0.5) {
        float smudge = charcoalSmudge(uv, (lineNoise - 0.5) * 2.0);
        strokeIntensity = max(strokeIntensity, smudge * 0.3);
    }
    
    // Mix graphite color with paper
    color = mix(paper, graphiteColor.rgb, strokeIntensity * 0.9);
    
    // Add overall graphite dust/residue based on noise level
    float dust = fbm(uv * 100.0 + time * 0.05, 3) * lineNoise * 0.1;
    color = mix(color, graphiteColor.rgb, dust);
    
    // Vignette (worn paper edges)
    float vignette = 1.0 - length(uv - 0.5) * 0.3;
    color *= vignette;
    
    // Output
    fragColor = vec4(color, alpha);
}
