#pragma once

#include <GLFW/glfw3.h>
#include <functional>

namespace ImGui {
  class Application {
  public:
    Application(const char* window_title);
    void Run(std::function<void()> render_callback);
    ~Application();

  private:
    GLFWwindow* window;
  };
} // namespace ImGui
