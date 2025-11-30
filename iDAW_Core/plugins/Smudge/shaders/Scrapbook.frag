/**
 * Scrapbook.frag - Fragment Shader for The Smudge visualization
 * 
 * Profile: 'Convolution Reverb' with Scrapbook UI
 * 
 * Features:
 * - Blueprint background
 * - Photo texture with paper grain overlay
 * - Paper tear animation on IR switch
 */

#version 330 core

in vec2 fragTexCoord;
out vec4 fragColor;

uniform float time;
uniform sampler2D photoTexture;
uniform float photoCornerX;
uniform float photoCornerY;
uniform float paperGrain;
uniform float tearProgress;
uniform vec4 blueprintColor;

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

// Blueprint grid
float blueprintGrid(vec2 uv) {
    vec2 grid = fract(uv * 20.0);
    float lines = step(0.95, grid.x) + step(0.95, grid.y);
    
    vec2 majorGrid = fract(uv * 4.0);
    float majorLines = step(0.98, majorGrid.x) + step(0.98, majorGrid.y);
    
    return max(lines * 0.3, majorLines * 0.6);
}

// Paper texture
vec3 paperTexture(vec2 uv, float grainAmount) {
    float grain = fbm(uv * 100.0, 4);
    float fiber = noise(uv * 50.0);
    
    vec3 paper = vec3(0.95, 0.93, 0.88);
    paper -= grain * grainAmount * 0.1;
    paper -= fiber * grainAmount * 0.05;
    
    return paper;
}

// Photo with corner drag
vec4 photoWithTransform(vec2 uv, vec2 corner) {
    // Simple perspective-like warp based on corner position
    vec2 offset = (corner - vec2(0.5)) * 0.1;
    vec2 warped = uv + offset * (1.0 - uv.y);
    
    // Photo bounds (centered, with border)
    vec2 photoUV = (warped - 0.2) / 0.6;
    
    if (photoUV.x >= 0.0 && photoUV.x <= 1.0 && 
        photoUV.y >= 0.0 && photoUV.y <= 1.0) {
        return texture(photoTexture, photoUV);
    }
    
    return vec4(0.0);
}

// Paper tear effect
float tearMask(vec2 uv, float progress) {
    if (progress <= 0.0) return 1.0;
    
    float tearLine = 0.5 + sin(uv.y * 20.0) * 0.05;
    float tear = smoothstep(tearLine - 0.01, tearLine + 0.01, uv.x * progress);
    
    // Jagged edge
    float jagged = noise(uv * 50.0) * 0.02;
    tear *= smoothstep(tearLine - jagged, tearLine + 0.01, uv.x * progress);
    
    return 1.0 - tear;
}

void main() {
    vec2 uv = fragTexCoord;
    
    // Blueprint background
    vec3 blueprint = blueprintColor.rgb;
    float grid = blueprintGrid(uv);
    blueprint += grid * 0.2;
    
    // Paper layer with grain
    vec3 paper = paperTexture(uv, paperGrain);
    
    // Photo
    vec4 photo = photoWithTransform(uv, vec2(photoCornerX, photoCornerY));
    
    // Apply paper grain to photo
    if (photo.a > 0.0) {
        photo.rgb = mix(photo.rgb, paper, paperGrain * 0.3);
    }
    
    // Combine layers
    vec3 color = blueprint;
    color = mix(color, paper, 0.3);
    color = mix(color, photo.rgb, photo.a * 0.9);
    
    // Apply tear mask
    float tear = tearMask(uv, tearProgress);
    color *= tear;
    
    // Vignette
    float vignette = 1.0 - length(uv - 0.5) * 0.5;
    color *= vignette;
    
    fragColor = vec4(color, 1.0);
}
