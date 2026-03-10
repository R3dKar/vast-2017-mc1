#pragma once

#include <imgui.h>
#include <imgui_texture.hpp>
#include <vector>

namespace pathfinding {
  std::vector<ImVec2> a_star(ImVec2 start, ImVec2 end, const ImGui::Texture& image);
}
