#include "gui.hpp"
#include "data.hpp"
#include "pathfinding.hpp"
#include <algorithm>
#include <fstream>
#include <imgui.h>
#include <imgui_texture.hpp>
#include <implot.h>
#include <mutex>
#include <unordered_map>
#include <vector>

namespace gui {

  static std::vector<data::Route> routes;
  static ImGui::Texture map_texture;
  static ImGui::Texture map_overlay;
  static std::unordered_map<std::string, std::vector<std::string>> clusters{};
  constexpr ImPlotColormap default_colormap = ImPlotColormap_Plasma;

  ImGui::Texture build_hitcount_overlay(const std::vector<data::Route>& routes, const ImGui::Texture& map_texture) {
    std::vector<size_t> hit_count(map_texture.GetWidth() * map_texture.GetHeight(), 0);
    for (const auto& route : routes) {
      for (size_t i = 0; i < route.points.size() - 1; i++) {
        const auto sensor1 = route.points.at(i).sensor;
        const auto sensor2 = route.points.at(i + 1).sensor;
        const auto& path = pathfinding::find_path(sensor1, sensor2, map_texture);
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

        ImVec4 color = ImPlot::SampleColormap(t, default_colormap);
        map_overlay.at(x, y, 0) = static_cast<stbi_uc>(color.x * 255);
        map_overlay.at(x, y, 1) = static_cast<stbi_uc>(color.y * 255);
        map_overlay.at(x, y, 2) = static_cast<stbi_uc>(color.z * 255);
        map_overlay.at(x, y, 3) = static_cast<stbi_uc>(color.w * 255);
      }
    }
    map_overlay.Sync();

    return map_overlay;
  }

  void init() {
    routes = data::Route::Load("./sensors.csv");
    map_texture = ImGui::Texture("./map.bmp");
    map_overlay = build_hitcount_overlay(routes, map_texture);
    clusters = data::read_clusters("./clusters.csv");
  }

  void DataSelection() {
    static std::optional<std::string> selected_cluster = std::nullopt;
    static ImGuiTextFilter filter{};

    if (ImGui::Begin("Data selection")) {
      filter.Draw("Filter clusters");

      if (ImGui::BeginListBox("##cluster_listbox", ImVec2(-1, -1))) {
        for (const auto& [cluster, car_ids] : clusters) {
          if (!filter.PassFilter(cluster.c_str())) continue;

          const bool is_selected = selected_cluster.has_value() && selected_cluster.value() == cluster;
          if (ImGui::Selectable(cluster.c_str(), is_selected)) {
            selected_cluster = cluster;
            std::vector<data::Route> cluster_routes{};
            for (const auto& car_id : car_ids) {
              cluster_routes.emplace_back(*std::find_if(routes.cbegin(), routes.cend(), [&](const auto& route) { return route.car_id == car_id; }));
            }
            map_overlay = build_hitcount_overlay(cluster_routes, map_texture);
          }
        }

        ImGui::EndListBox();
      }
    }
    ImGui::End();
  }

  void Map() {
    if (ImGui::Begin("Map")) {
      if (ImPlot::BeginPlot("Map", ImVec2(ImGui::GetContentRegionAvail().x - 100 - ImGui::GetStyle().ItemSpacing.x, -1), ImPlotFlags_NoTitle | ImPlotFlags_Equal)) {
        ImPlot::SetupAxis(ImAxis_X1, "X");
        ImPlot::SetupAxis(ImAxis_Y1, "Y", ImPlotAxisFlags_Invert);

        // Map
        ImPlot::PlotImage("Map", map_texture.GetID(), ImPlotPoint(0, 1), ImPlotPoint(1, 0));

        // Overlay
        ImPlot::PlotImage("Path", map_overlay.GetID(), ImPlotPoint(0, 1), ImPlotPoint(1, 0));

        // Sensor labels
        ImPlot::PushStyleColor(ImPlotCol_InlayText, ImVec4(0.5, 1, 0.5, 1));
        for (const auto [sensor, sensor_name] : data::sensor_name_map) {
          ImVec2 position = data::sensor_location_map.at(sensor);
          ImPlot::PlotText(sensor_name, position.x + 0.5 / map_texture.GetWidth(), position.y - 1.5 / map_texture.GetHeight());
        }
        ImPlot::PopStyleColor();
      }
      ImPlot::EndPlot();

      ImGui::SameLine();
      ImPlot::PushColormap(default_colormap);
      ImPlot::ColormapScale("Path hitcount", 0, 1, ImVec2(100, -1));
      ImPlot::PopColormap();
    }
    ImGui::End();
  }

  void render() {
    static std::once_flag init_flag{};
    std::call_once(init_flag, init);

    Map();
    DataSelection();
  }

} // namespace gui
