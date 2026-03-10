#include "gui.hpp"
#include "data.hpp"
#include "pathfinding.hpp"
#include <algorithm>
#include <imgui.h>
#include <imgui_texture.hpp>
#include <implot.h>
#include <mutex>
#include <vector>

namespace gui {

  static std::vector<data::Route> routes;
  static ImGui::Texture map_texture;
  static ImGui::Texture map_overlay;

  ImGui::Texture build_hitcount_overlay(const std::vector<data::Route>& routes, const ImGui::Texture& map_texture) {
    std::vector<size_t> hit_count(map_texture.GetWidth() * map_texture.GetHeight(), 0);
    for (const auto& route : routes) {
      for (size_t i = 0; i < route.points.size() - 1; i++) {
        const auto sensor1 = route.points.at(i).sensor;
        const auto sensor2 = route.points.at(i + 1).sensor;
        const auto path = pathfinding::a_star(data::sensor_location_map.at(sensor1), data::sensor_location_map.at(sensor2), map_texture);
        for (const auto point : path) {
          const size_t x = static_cast<size_t>(std::round(point.x * map_texture.GetWidth()));
          const size_t y = static_cast<size_t>(std::round(point.y * map_texture.GetHeight()));
          hit_count.at(y * map_texture.GetWidth() + x)++;
        }
      }

      // add last point manually
      const auto point = data::sensor_location_map.at(route.points.back().sensor);
      const size_t x = static_cast<size_t>(std::round(point.x * map_texture.GetWidth()));
      const size_t y = static_cast<size_t>(std::round(point.y * map_texture.GetHeight()));
      hit_count.at(y * map_texture.GetWidth() + x)++;
    }

    const size_t max_hit_count = *std::max_element(hit_count.cbegin(), hit_count.cend());

    std::vector<stbi_uc> data(map_texture.GetWidth() * map_texture.GetHeight() * 4, 0);
    ImGui::Texture map_overlay(map_texture.GetWidth(), map_texture.GetHeight(), 4, data.data());

    for (size_t y = 0; y < map_overlay.GetHeight(); y++) {
      for (size_t x = 0; x < map_overlay.GetWidth(); x++) {
        const size_t index = y * map_overlay.GetWidth() + x;
        const float t = hit_count.at(index) / static_cast<float>(max_hit_count);

        if (t == 0.0f) continue;

        map_overlay.at(x, y, 0) = 255;
        map_overlay.at(x, y, 3) = static_cast<stbi_uc>(255 * t);
      }
    }
    map_overlay.Sync();

    return map_overlay;
  }

  void init() {
    routes = data::Route::Load("./sensors.csv");
    map_texture = ImGui::Texture("./map.bmp");
    map_overlay = build_hitcount_overlay(routes, map_texture);
  }

  void Map() {
    if (ImGui::Begin("Map")) {
      if (ImPlot::BeginPlot("Map", ImVec2(-1, -1), ImPlotFlags_NoTitle | ImPlotFlags_Equal)) {
        ImPlot::SetupAxis(ImAxis_X1, "X");
        ImPlot::SetupAxis(ImAxis_Y1, "Y", ImPlotAxisFlags_Invert);

        // Map
        ImPlot::PlotImage("Map", map_texture.GetID(), ImPlotPoint(0, 1), ImPlotPoint(1, 0));

        // Overlay
        ImPlot::PlotImage("Path", map_overlay.GetID(), ImPlotPoint(0, 1), ImPlotPoint(1, 0), ImVec2(0, 0), ImVec2(1, 1), ImVec4(1, 0, 0, 1));

        // Sensor labels
        ImPlot::PushStyleColor(ImPlotCol_InlayText, ImVec4(0.5, 1, 0.5, 1));
        for (const auto [sensor, sensor_name] : data::sensor_name_map) {
          ImVec2 position = data::sensor_location_map.at(sensor);
          ImPlot::PlotText(sensor_name, position.x + 0.5 / map_texture.GetWidth(), position.y - 1.5 / map_texture.GetHeight());
        }
        ImPlot::PopStyleColor();
      }
      ImPlot::EndPlot();
    }
    ImGui::End();
  }

  void render() {
    static std::once_flag init_flag{};
    std::call_once(init_flag, init);

    Map();
  }

} // namespace gui
