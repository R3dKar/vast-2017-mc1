#include "imgui_texture.hpp"
#define STB_IMAGE_IMPLEMENTATION
#include <stb_image.h>

ImGui::Texture::Texture(const char* filename) {
  int width, height, channels;
  stbi_set_flip_vertically_on_load(true);
  stbi_uc* data = stbi_load(filename, &width, &height, &channels, 0);

  m_width = width;
  m_height = height;
  m_channels = channels;
  m_pixels.assign(data, data + m_width * m_height * m_channels);
  stbi_image_free(data);

  CreateTexture();
}

ImGui::Texture::Texture(size_t width, size_t height, size_t channels, const stbi_uc* pixels)
    : m_width(width), m_height(height), m_channels(channels), m_pixels(pixels, pixels + width * height * channels) {
  CreateTexture();
}

ImGui::Texture::Texture(const ImGui::Texture& other) : ImGui::Texture(other.m_width, other.m_height, other.m_channels, other.m_pixels.data()) {
}

ImGui::Texture::Texture(ImGui::Texture&& other) noexcept {
  std::swap(m_width, other.m_width);
  std::swap(m_height, other.m_height);
  std::swap(m_channels, other.m_channels);
  std::swap(m_pixels, other.m_pixels);
  std::swap(m_texture, other.m_texture);
}

ImGui::Texture& ImGui::Texture::operator=(const ImGui::Texture& other) {
  if (&other != this) {
    Dispose();
    m_width = other.m_width;
    m_height = other.m_height;
    m_channels = other.m_channels;
    m_pixels = other.m_pixels;
    CreateTexture();
  }

  return *this;
}

ImGui::Texture& ImGui::Texture::operator=(ImGui::Texture&& other) noexcept {
  if (&other != this) {
    std::swap(m_width, other.m_width);
    std::swap(m_height, other.m_height);
    std::swap(m_channels, other.m_channels);
    std::swap(m_pixels, other.m_pixels);
    std::swap(m_texture, other.m_texture);
  }

  return *this;
}

void ImGui::Texture::CreateTexture() {
  glGenTextures(1, &m_texture);
  glBindTexture(GL_TEXTURE_2D, m_texture);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
  glPixelStorei(GL_UNPACK_ROW_LENGTH, 0);

  GLenum format;
  switch (m_channels) {
  case 4:
    format = GL_RGBA;
    break;
  case 3:
    format = GL_RGB;
    break;
  case 1:
    format = GL_RED;
    break;
  }

  glTexImage2D(GL_TEXTURE_2D, 0, format, static_cast<GLint>(m_width), static_cast<GLint>(m_height), 0, format, GL_UNSIGNED_BYTE, m_pixels.data());
}

void ImGui::Texture::ReleaseGLTexture() {
  if (m_texture == 0) return;
  glDeleteTextures(1, &m_texture);
  m_texture = 0;
}

void ImGui::Texture::Dispose() {
  if (m_texture == 0) return;

  ReleaseGLTexture();
  m_width = 0;
  m_height = 0;
  m_channels = 0;
  m_pixels.clear();
}

ImGui::Texture::~Texture() {
  Dispose();
}

void ImGui::Texture::Sync() {
  ReleaseGLTexture();
  CreateTexture();
}

stbi_uc& ImGui::Texture::at(size_t x, size_t y, size_t channel) {
  return m_pixels.at((y * m_width + x) * m_channels + channel);
}

const stbi_uc& ImGui::Texture::at(size_t x, size_t y, size_t channel) const {
  return m_pixels.at((y * m_width + x) * m_channels + channel);
}

size_t ImGui::Texture::GetWidth() const {
  return m_width;
}

size_t ImGui::Texture::GetHeight() const {
  return m_height;
}

ImVec2 ImGui::Texture::GetSize() const {
  return ImVec2(static_cast<float>(m_width), static_cast<float>(m_height));
}

void* ImGui::Texture::GetID() {
  return reinterpret_cast<void*>(static_cast<intptr_t>(m_texture));
}
