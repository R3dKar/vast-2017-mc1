#pragma once

#include "data.hpp"
#include <imgui.h>
#include <imgui_texture.hpp>
#include <vector>

namespace pathfinding {
  std::vector<ImVec2> a_star(ImVec2 start, ImVec2 end, const ImGui::Texture& image);
  const std::vector<ImVec2>& find_path(data::Sensor start, data::Sensor end, const ImGui::Texture& image);
} // namespace pathfinding
