/**
 * ChalkDust.vert - Vertex Shader for Eraser Particle Visualization
 * 
 * Handles particle positioning and passes per-particle attributes
 * to the fragment shader for chalk dust rendering.
 */

#version 330 core

// Vertex attributes
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoord;
layout(location = 2) in float life;
layout(location = 3) in float size;
layout(location = 4) in float brightness;

// Outputs to fragment shader
out vec2 fragTexCoord;
out float fragLife;
out float fragSize;
out float fragBrightness;

// Uniforms
uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;

void main() {
    fragTexCoord = texCoord;
    fragLife = life;
    fragSize = size;
    fragBrightness = brightness;
    
    // Scale particle based on size
    vec3 scaledPosition = position * size;
    
    gl_Position = projectionMatrix * viewMatrix * vec4(scaledPosition, 1.0);
}
