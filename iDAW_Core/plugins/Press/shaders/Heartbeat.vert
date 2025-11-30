/**
 * Heartbeat.vert - Vertex Shader for The Press visualization
 */

#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoord;

out vec2 fragTexCoord;

uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;

void main() {
    fragTexCoord = texCoord;
    gl_Position = projectionMatrix * viewMatrix * vec4(position, 1.0);
}
