#pragma once

#include <GLFW/glfw3.h>
#include <cstdint>
#include <imgui.h>
#include <stb_image.h>
#include <vector>

namespace ImGui {
  class Texture {
  public:
    Texture() = default;
    Texture(const char* filename);
    Texture(size_t width, size_t height, size_t channels, const stbi_uc* pixels);

    Texture(const Texture& other);
    Texture(Texture&& other) noexcept;

    Texture& operator=(const Texture& other);
    Texture& operator=(Texture&& other) noexcept;

    ~Texture();

    void Sync();

    stbi_uc& at(size_t x, size_t y, size_t channel);
    const stbi_uc& at(size_t x, size_t y, size_t channel) const;

    size_t GetWidth() const;
    size_t GetHeight() const;
    ImVec2 GetSize() const;
    void* GetID();

  private:
    void CreateTexture();
    void ReleaseGLTexture();
    void Dispose();

    GLuint m_texture = 0;
    std::vector<stbi_uc> m_pixels{};
    size_t m_width = 0;
    size_t m_height = 0;
    size_t m_channels = 0;
  };
} // namespace ImGui
