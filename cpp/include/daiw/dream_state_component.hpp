/**
 * DAiW Dream State Component - OpenGL Visualization
 *
 * Real-time shader-based visualization for the Dream State mode.
 * Uses JUCE's OpenGL integration with custom GLSL shaders.
 */

#pragma once

#include <juce_opengl/juce_opengl.h>
#include <juce_gui_basics/juce_gui_basics.h>

#include <memory>
#include <atomic>

namespace daiw {
namespace gui {

/**
 * DreamStateComponent - OpenGL-rendered visualization.
 *
 * Displays animated shader effects that respond to audio analysis
 * and emotional intent parameters.
 */
class DreamStateComponent : public juce::Component,
                            public juce::OpenGLRenderer {
public:
    DreamStateComponent() {
        // Attach OpenGL context
        openGLContext.setRenderer(this);
        openGLContext.attachTo(*this);
        openGLContext.setContinuousRepainting(true);
    }

    ~DreamStateComponent() override {
        openGLContext.detach();
    }

    // =========================================================================
    // OpenGLRenderer Interface
    // =========================================================================

    void newOpenGLContextCreated() override {
        // Compile shaders
        createShaders();
    }

    void renderOpenGL() override {
        // 1. Calculate the animation frame time
        float time = static_cast<float>(juce::Time::getMillisecondCounter()) / 1000.0f;

        // 2. Clear background
        juce::OpenGLHelpers::clear(juce::Colours::black);

        // 3. SAFETY: Execute on GL thread
        if (shaderProgram != nullptr && shaderProgram->getLastError().isEmpty()) {

            // 4. Activate Shader
            shaderProgram->use();

            // 5. Update Uniforms
            if (timeUniform != nullptr)
                timeUniform->set(time);

            if (resolutionUniform != nullptr)
                resolutionUniform->set(static_cast<float>(getWidth()),
                                       static_cast<float>(getHeight()));

            if (intensityUniform != nullptr)
                intensityUniform->set(intensity_.load());

            if (emotionUniform != nullptr)
                emotionUniform->set(emotionValue_.load());

            // 6. Draw fullscreen quad
            drawQuad();
        }
    }

    void openGLContextClosing() override {
        shaderProgram.reset();
    }

    // =========================================================================
    // Control Interface
    // =========================================================================

    /**
     * Set visualization intensity (0.0 - 1.0).
     */
    void setIntensity(float intensity) {
        intensity_.store(juce::jlimit(0.0f, 1.0f, intensity));
    }

    /**
     * Set emotion value for color/movement mapping.
     * -1.0 = sad/cold, 0.0 = neutral, 1.0 = happy/warm
     */
    void setEmotionValue(float value) {
        emotionValue_.store(juce::jlimit(-1.0f, 1.0f, value));
    }

    /**
     * Trigger a pulse effect (e.g., on beat).
     */
    void pulse() {
        pulseTime_.store(static_cast<float>(juce::Time::getMillisecondCounter()) / 1000.0f);
    }

private:
    void createShaders() {
        // Vertex shader - simple fullscreen quad
        const char* vertexShader = R"(
            #version 330 core
            layout (location = 0) in vec2 aPos;
            out vec2 fragCoord;

            void main() {
                fragCoord = aPos * 0.5 + 0.5;
                gl_Position = vec4(aPos, 0.0, 1.0);
            }
        )";

        // Fragment shader - Dream State visualization
        const char* fragmentShader = R"(
            #version 330 core
            in vec2 fragCoord;
            out vec4 FragColor;

            uniform float uTime;
            uniform vec2 uResolution;
            uniform float uIntensity;
            uniform float uEmotion;

            // Simplex noise function
            vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
            vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
            vec3 permute(vec3 x) { return mod289(((x*34.0)+1.0)*x); }

            float snoise(vec2 v) {
                const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                                   -0.577350269189626, 0.024390243902439);
                vec2 i  = floor(v + dot(v, C.yy));
                vec2 x0 = v -   i + dot(i, C.xx);
                vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
                vec4 x12 = x0.xyxy + C.xxzz;
                x12.xy -= i1;
                i = mod289(i);
                vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0))
                                        + i.x + vec3(0.0, i1.x, 1.0));
                vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
                                        dot(x12.zw,x12.zw)), 0.0);
                m = m*m; m = m*m;
                vec3 x = 2.0 * fract(p * C.www) - 1.0;
                vec3 h = abs(x) - 0.5;
                vec3 ox = floor(x + 0.5);
                vec3 a0 = x - ox;
                m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);
                vec3 g;
                g.x  = a0.x  * x0.x  + h.x  * x0.y;
                g.yz = a0.yz * x12.xz + h.yz * x12.yw;
                return 130.0 * dot(m, g);
            }

            void main() {
                vec2 uv = fragCoord;
                vec2 p = uv * 2.0 - 1.0;
                p.x *= uResolution.x / uResolution.y;

                // Time-based animation
                float t = uTime * 0.3;

                // Layered noise
                float n1 = snoise(p * 2.0 + t) * 0.5;
                float n2 = snoise(p * 4.0 - t * 0.5) * 0.25;
                float n3 = snoise(p * 8.0 + t * 0.25) * 0.125;
                float noise = n1 + n2 + n3;

                // Color based on emotion
                vec3 coldColor = vec3(0.1, 0.2, 0.4);   // Blue/sad
                vec3 warmColor = vec3(0.4, 0.2, 0.1);   // Orange/warm
                vec3 neutralColor = vec3(0.2, 0.15, 0.3); // Purple/neutral

                vec3 baseColor;
                if (uEmotion < 0.0) {
                    baseColor = mix(neutralColor, coldColor, -uEmotion);
                } else {
                    baseColor = mix(neutralColor, warmColor, uEmotion);
                }

                // Apply noise and intensity
                vec3 color = baseColor + noise * 0.3 * uIntensity;

                // Vignette
                float vignette = 1.0 - length(p) * 0.5;
                color *= vignette;

                // Glow effect
                float glow = sin(uTime * 2.0) * 0.1 + 0.9;
                color *= glow * uIntensity;

                FragColor = vec4(color, 1.0);
            }
        )";

        shaderProgram = std::make_unique<juce::OpenGLShaderProgram>(openGLContext);

        if (!shaderProgram->addVertexShader(vertexShader) ||
            !shaderProgram->addFragmentShader(fragmentShader) ||
            !shaderProgram->link()) {
            DBG("Shader compilation error: " << shaderProgram->getLastError());
            return;
        }

        // Get uniform locations
        timeUniform = std::make_unique<juce::OpenGLShaderProgram::Uniform>(
            *shaderProgram, "uTime");
        resolutionUniform = std::make_unique<juce::OpenGLShaderProgram::Uniform>(
            *shaderProgram, "uResolution");
        intensityUniform = std::make_unique<juce::OpenGLShaderProgram::Uniform>(
            *shaderProgram, "uIntensity");
        emotionUniform = std::make_unique<juce::OpenGLShaderProgram::Uniform>(
            *shaderProgram, "uEmotion");
    }

    void drawQuad() {
        // Simple fullscreen quad
        static const float vertices[] = {
            -1.0f, -1.0f,
             1.0f, -1.0f,
             1.0f,  1.0f,
            -1.0f,  1.0f
        };

        static const unsigned int indices[] = { 0, 1, 2, 2, 3, 0 };

        // Draw using immediate mode (for simplicity)
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, vertices);
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, indices);
        glDisableVertexAttribArray(0);
    }

    juce::OpenGLContext openGLContext;
    std::unique_ptr<juce::OpenGLShaderProgram> shaderProgram;

    std::unique_ptr<juce::OpenGLShaderProgram::Uniform> timeUniform;
    std::unique_ptr<juce::OpenGLShaderProgram::Uniform> resolutionUniform;
    std::unique_ptr<juce::OpenGLShaderProgram::Uniform> intensityUniform;
    std::unique_ptr<juce::OpenGLShaderProgram::Uniform> emotionUniform;

    std::atomic<float> intensity_{0.8f};
    std::atomic<float> emotionValue_{0.0f};
    std::atomic<float> pulseTime_{0.0f};

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(DreamStateComponent)
};

} // namespace gui
} // namespace daiw
