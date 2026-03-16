#include "gui.hpp"
#include <imgui_app.hpp>

int main() {
  ImGui::Application app("VAST 2017 MC1 Visualization");
  app.Run(gui::render);

  return 0;
}

int WinMain() {
  return main();
}
