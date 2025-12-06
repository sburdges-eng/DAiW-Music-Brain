/**
 * Graphite.vert - Vertex Shader for The Pencil visualization
 * 
 * Simple pass-through vertex shader for graphite effect.
 */

#version 330 core

// Attributes
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoord;

// Outputs
out vec2 fragTexCoord;

// Uniforms
uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;

void main() {
    fragTexCoord = texCoord;
    gl_Position = projectionMatrix * viewMatrix * vec4(position, 1.0);
}
