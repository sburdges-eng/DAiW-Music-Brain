/**
 * Watercolor.frag - Fragment Shader for The Palette visualization
 * 
 * Profile: 'Wavetable Synth' with Watercolor UI
 * 
 * Uses Diffusion-Reaction system (Gray-Scott model) for paint bleeding.
 * 
 * Mapping:
 * - Filter Cutoff -> Blur Strength
 * - Resonance -> Edge Sharpening (Coffee Ring effect)
 * - Wavetable -> Color (Blue=Sine, Red=Saw, Yellow=Square)
 */

#version 330 core

in vec2 fragTexCoord;
out vec4 fragColor;

uniform float time;
uniform float blurStrength;
uniform float edgeSharpening;
uniform float colorR;
uniform float colorG;
uniform float colorB;
uniform float diffusionRate;
uniform vec4 backgroundColor;

// Noise functions
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

float fbm(vec2 p, int octaves) {
    float value = 0.0;
    float amplitude = 0.5;
    for (int i = 0; i < octaves; i++) {
        value += amplitude * noise(p);
        p *= 2.0;
        amplitude *= 0.5;
    }
    return value;
}

// Watercolor paper texture
vec3 paperTexture(vec2 uv) {
    vec3 paper = backgroundColor.rgb;
    
    // Fine grain
    float grain = noise(uv * 200.0) * 0.08;
    
    // Fiber pattern
    float fiber = fbm(uv * 30.0, 3) * 0.05;
    
    // Subtle bumps
    float bumps = fbm(uv * 80.0, 2) * 0.03;
    
    paper -= grain + fiber + bumps;
    
    return paper;
}

// Paint blob shape
float paintBlob(vec2 uv, vec2 center, float size) {
    vec2 d = uv - center;
    float dist = length(d);
    
    // Organic shape with noise
    float angle = atan(d.y, d.x);
    float noiseVal = noise(vec2(angle * 3.0 + time * 0.5, dist * 10.0));
    float radius = size * (0.8 + noiseVal * 0.4);
    
    return smoothstep(radius, radius * 0.5, dist);
}

// Diffusion-reaction simulation (simplified Gray-Scott)
float grayScott(vec2 uv, float t) {
    // Feed and kill rates
    float f = 0.055;
    float k = 0.062;
    
    // Simulate a few iterations
    float u = 1.0;
    float v = noise(uv * 10.0 + t * 0.1);
    
    // Laplacian approximation
    float laplacian = fbm(uv * 20.0, 3) - 0.5;
    
    // Reaction
    float uvv = u * v * v;
    float du = diffusionRate * laplacian - uvv + f * (1.0 - u);
    float dv = diffusionRate * 0.5 * laplacian + uvv - (f + k) * v;
    
    u += du * 0.1;
    v += dv * 0.1;
    
    return v;
}

// Coffee ring effect (edge darkening)
float coffeeRing(vec2 uv, vec2 center, float size, float sharpening) {
    float dist = length(uv - center) / size;
    
    // Ring at the edge
    float ring = exp(-pow((dist - 0.9) * 10.0, 2.0));
    
    // More pronounced with higher sharpening
    ring *= sharpening * 2.0;
    
    return ring;
}

// Watercolor bleed effect
float watercolorBleed(vec2 uv, float blur) {
    float bleed = 0.0;
    
    // Sample in multiple directions
    const int samples = 8;
    for (int i = 0; i < samples; i++) {
        float angle = float(i) / float(samples) * 6.28318;
        vec2 offset = vec2(cos(angle), sin(angle)) * blur * 0.1;
        
        // Random bleed strength
        float strength = noise(uv * 50.0 + float(i) * 10.0);
        bleed += strength;
    }
    
    return bleed / float(samples);
}

// Paint wash with color bleeding
vec3 paintWash(vec2 uv, vec3 paintColor, float blur, float sharpening) {
    vec2 center = vec2(0.5, 0.5);
    float size = 0.4;
    
    // Base paint blob
    float paint = paintBlob(uv, center, size);
    
    // Apply diffusion
    float diffusion = grayScott(uv, time);
    paint = mix(paint, paint * diffusion, blur);
    
    // Watercolor bleed
    float bleed = watercolorBleed(uv, blur);
    paint = mix(paint, paint * (1.0 + bleed * 0.5), blur);
    
    // Coffee ring effect
    float ring = coffeeRing(uv, center, size, sharpening);
    
    // Apply color with variation
    vec3 color = paintColor;
    
    // Color variation (paint not perfectly mixed)
    float variation = noise(uv * 30.0 + time * 0.1);
    color = mix(color, color * 0.7, variation * 0.3);
    
    // Edge darkening from coffee ring
    color *= 1.0 - ring * 0.3;
    
    // Transparency at edges
    float alpha = paint * (1.0 - blur * 0.5);
    
    return color * alpha;
}

// Wet edge effect
float wetEdge(vec2 uv, float dist, float blur) {
    float edge = smoothstep(0.0, blur * 0.2, dist);
    float wet = noise(uv * 100.0 + time) * blur;
    return edge * (1.0 + wet * 0.2);
}

void main() {
    vec2 uv = fragTexCoord;
    
    // ==========================================================================
    // SAFETY: Clamp all uniform values to prevent NaN/Infinity
    // ==========================================================================
    float safeBlurStrength = clamp(blurStrength, 0.0, 1.0);
    float safeEdgeSharpening = clamp(edgeSharpening, 0.0, 2.0);
    float safeColorR = clamp(colorR, 0.0, 1.0);
    float safeColorG = clamp(colorG, 0.0, 1.0);
    float safeColorB = clamp(colorB, 0.0, 1.0);
    
    // Paper background
    vec3 paper = paperTexture(uv);
    
    // Paint color from synth state (using safe values)
    vec3 paintColor = vec3(safeColorR, safeColorG, safeColorB);
    
    // Apply watercolor wash
    vec3 paint = paintWash(uv, paintColor, safeBlurStrength, safeEdgeSharpening);
    
    // Multiple wash layers for depth
    vec3 paint2 = paintWash(uv + vec2(0.1, 0.05), 
                            paintColor * 0.8, 
                            safeBlurStrength * 0.7, 
                            safeEdgeSharpening * 0.5) * 0.5;
    vec3 paint3 = paintWash(uv - vec2(0.05, 0.1), 
                            paintColor * 0.6, 
                            safeBlurStrength * 0.5, 
                            safeEdgeSharpening * 0.3) * 0.3;
    
    // Combine layers
    vec3 totalPaint = paint + paint2 + paint3;
    
    // Blend with paper
    vec3 color = paper;
    color = mix(color, totalPaint, min(length(totalPaint), 1.0));
    
    // Paper showing through (watercolor transparency)
    float transparency = fbm(uv * 50.0, 3) * 0.2;
    color = mix(color, paper, transparency);
    
    // Water stains
    float stain = fbm(uv * 20.0 + time * 0.05, 4);
    stain = smoothstep(0.4, 0.6, stain);
    color = mix(color, color * 0.95, stain * 0.1);
    
    // Vignette (wet paper edges)
    float vignette = 1.0 - pow(length(uv - 0.5) * 1.5, 2.0);
    color *= 0.8 + vignette * 0.2;
    
    fragColor = vec4(color, 1.0);
}
