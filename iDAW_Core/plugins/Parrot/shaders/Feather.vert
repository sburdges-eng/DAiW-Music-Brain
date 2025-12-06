/**
 * Feather.vert - Vertex shader for The Parrot plugin
 * 
 * Simple pass-through with subtle vertex animation for organic feel
 */

#version 330 core

// Inputs
layout(location = 0) in vec2 a_position;
layout(location = 1) in vec2 a_texCoord;

// Outputs
out vec2 v_texCoord;
out vec2 v_position;

// Uniforms
uniform float u_time;
uniform float u_volumeIntensity;
uniform bool u_isSinging;

void main() {
    vec2 pos = a_position;
    
    // Subtle breathing animation based on volume
    float breathe = sin(u_time * 2.0) * 0.005 * u_volumeIntensity;
    pos *= 1.0 + breathe;
    
    // Extra movement when singing
    if (u_isSinging) {
        float bounce = abs(sin(u_time * 8.0)) * 0.01;
        pos.y += bounce;
    }
    
    v_texCoord = a_texCoord;
    v_position = pos;
    
    gl_Position = vec4(pos, 0.0, 1.0);
}
