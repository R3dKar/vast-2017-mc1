#include "gui.hpp"
#include "data.hpp"
#include "pathfinding.hpp"
#include <algorithm>
#include <fstream>
#include <imgui.h>
#include <imgui_texture.hpp>
#include <implot.h>
#include <limits>
#include <mutex>
#include <unordered_map>
#include <vector>

namespace gui {
  constexpr ImPlotColormap default_colormap = ImPlotColormap_Plasma;

  static std::vector<data::Route> routes;
  static ImGui::Texture map_texture;
  static ImGui::Texture map_overlay;

  static std::unordered_map<std::string, std::vector<size_t>> clusters{};
  static std::optional<std::string> current_cluster = std::nullopt;

  static double min_timestamp, max_timestamp, current_timestamp;
  static std::vector<uint16_t> timeline_histogram{};

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

  std::vector<uint16_t> build_timeline_histogram(const std::vector<data::Route>& routes, double& min_timestamp, double& max_timestamp) {
    min_timestamp = std::numeric_limits<double>::max();
    max_timestamp = std::numeric_limits<double>::min();

    for (const auto& route : routes) {
      min_timestamp = std::min(std::floor(route.points.front().timestamp / 3600) * 3600, min_timestamp);
      max_timestamp = std::max(std::ceil(route.points.back().timestamp / 3600) * 3600, max_timestamp);
    }

    std::vector<uint16_t> histogram(static_cast<size_t>(max_timestamp - min_timestamp) / 3600 + 1, 0);

    for (const auto& route : routes) {
      const size_t min_hour_timestamp = static_cast<size_t>(std::floor(route.points.front().timestamp / 3600));
      const size_t max_hour_timestamp = static_cast<size_t>(std::ceil(route.points.back().timestamp / 3600));
      for (size_t i = min_hour_timestamp; i <= max_hour_timestamp; i++) {
        histogram.at(i - static_cast<size_t>(min_timestamp / 3600))++;
      }
    }

    return histogram;
  }

  void render_route(const data::Route& route, double timestamp) {
    if (timestamp < route.points.front().timestamp || timestamp > route.points.back().timestamp) return;

    size_t segment_index;
    for (segment_index = 0; segment_index < route.points.size() - 1; segment_index++) {
      if (timestamp >= route.points.at(segment_index).timestamp && timestamp < route.points.at(segment_index + 1).timestamp) break;
    }

    const auto start = route.points.at(segment_index);
    const auto end = route.points.at(segment_index + 1);
    const double t = std::clamp((timestamp - start.timestamp) / (end.timestamp - start.timestamp), 0.0, 1.0);
    const auto& points = pathfinding::find_path(start.sensor, end.sensor, map_texture);
    const ImVec2 point = points.at(static_cast<size_t>(std::floor(t * (points.size() - 1))));

    ImPlot::Annotation(point.x, point.y, ImVec4(1, 0, 0, 1), ImVec2(10, 10), false, route.car_id.c_str());
  }

  void format_timestamp(double timestamp, char* buffer, size_t buffer_size, const char* format) {
    std::time_t time = static_cast<std::time_t>(timestamp);
    std::tm* timeinfo = std::gmtime(&time);
    std::strftime(buffer, buffer_size, format, timeinfo);
  }

  void update_selected_cluster() {
    if (!current_cluster.has_value()) {
      map_overlay = build_hitcount_overlay(routes, map_texture);
      timeline_histogram = build_timeline_histogram(routes, min_timestamp, max_timestamp);
      return;
    }

    std::vector<data::Route> cluster_routes{};
    for (auto index : clusters.at(current_cluster.value())) {
      cluster_routes.emplace_back(routes.at(index));
    }
    map_overlay = build_hitcount_overlay(cluster_routes, map_texture);
    timeline_histogram = build_timeline_histogram(cluster_routes, min_timestamp, max_timestamp);
  }

  void init() {
    ImPlot::GetStyle().Use24HourClock = true;
    ImPlot::GetStyle().UseISO8601 = true;

    routes = data::Route::Load("./sensors.csv");
    map_texture = ImGui::Texture("./map.bmp");
    const auto raw_clusters = data::read_clusters("./clusters.csv");

    std::unordered_map<std::string, size_t> car_id_to_route_index{};
    for (size_t i = 0; i < routes.size(); i++) {
      car_id_to_route_index[routes.at(i).car_id] = i;
    }

    for (const auto& [cluster, car_ids] : raw_clusters) {
      std::vector<size_t> indexes(car_ids.size());
      for (size_t i = 0; i < car_ids.size(); i++) {
        indexes.at(i) = car_id_to_route_index.at(car_ids.at(i));
      }
      clusters[cluster] = std::move(indexes);
    }

    update_selected_cluster();
  }

  void DataSelection() {
    static ImGuiTextFilter filter{};

    if (ImGui::Begin("Data selection")) {
      filter.Draw("Filter clusters");

      if (ImGui::BeginListBox("##cluster_listbox", ImVec2(-1, -1))) {
        if (ImGui::Selectable("All", !current_cluster.has_value())) {
          current_cluster = std::nullopt;
          update_selected_cluster();
        }

        for (const auto& [cluster, car_ids] : clusters) {
          if (!filter.PassFilter(cluster.c_str())) continue;

          const bool is_selected = current_cluster.has_value() && current_cluster.value() == cluster;
          if (ImGui::Selectable(cluster.c_str(), is_selected)) {
            current_cluster = cluster;
            update_selected_cluster();
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

        // Cars
        if (current_cluster.has_value()) {
          for (const auto& index : clusters.at(current_cluster.value())) {
            render_route(routes.at(index), current_timestamp);
          }
        } else {
          for (const auto& route : routes) {
            render_route(route, current_timestamp);
          }
        }

        ImPlot::EndPlot();
      }

      ImGui::SameLine();
      ImPlot::PushColormap(default_colormap);
      ImPlot::ColormapScale("Path hitcount", 0, 1, ImVec2(100, -1));
      ImPlot::PopColormap();
    }
    ImGui::End();
  }

  void Timeline() {
    if (ImGui::Begin("Timeline")) {
      static bool is_running = false;
      static float speed = 1;

      if (ImGui::Button((is_running) ? "Stop" : "Start")) is_running = !is_running;
      ImGui::SameLine();
      ImGui::SliderFloat("Speed", &speed, 1, 1 << 14, "%.3f", ImGuiSliderFlags_Logarithmic);

      if (is_running) {
        current_timestamp += ImGui::GetIO().DeltaTime * speed;

        if (current_timestamp >= max_timestamp) is_running = false;

        current_timestamp = std::clamp(current_timestamp, min_timestamp, max_timestamp);
      }

      if (ImPlot::BeginPlot("Timeline", ImVec2(-1, -1), ImPlotFlags_NoTitle | ImPlotFlags_NoLegend)) {
        ImPlot::SetupAxis(ImAxis_X1);
        ImPlot::SetupAxisScale(ImAxis_X1, ImPlotScale_Time);
        ImPlot::SetupAxisLimitsConstraints(ImAxis_X1, min_timestamp, max_timestamp);
        ImPlot::SetupAxis(ImAxis_Y1, "Cars in park");
        ImPlot::SetupAxisLimitsConstraints(ImAxis_Y1, 0, FLT_MAX);

        // Cars in park histogram
        const auto timeline_getter = [](int idx, void* data) { return ImPlotPoint(idx * 3600 + min_timestamp, reinterpret_cast<uint16_t*>(data)[idx]); };
        ImPlot::SetNextFillStyle(IMPLOT_AUTO_COL, 0.25f);
        ImPlot::PlotStairsG("Cars in park", timeline_getter, timeline_histogram.data(), static_cast<int>(timeline_histogram.size()), ImPlotStairsFlags_Shaded | ImPlotStairsFlags_PreStep);

        // Timeline selector
        if (ImPlot::IsPlotHovered() && ImGui::IsMouseDoubleClicked(ImGuiMouseButton_Left)) current_timestamp = ImPlot::GetPlotMousePos().x;

        ImPlot::DragLineX(0, &current_timestamp, ImVec4(1, 1, 1, 1), 2.0f);
        current_timestamp = std::clamp(current_timestamp, min_timestamp, max_timestamp);

        char date_buffer[32];
        format_timestamp(current_timestamp, date_buffer, IM_ARRAYSIZE(date_buffer), "%Y-%m-%d\n%H:%M:%S");
        ImPlot::TagX(current_timestamp, ImVec4(1, 1, 1, 1), date_buffer);

        ImPlot::EndPlot();
      }
    }
    ImGui::End();
  }

  void render() {
    static std::once_flag init_flag{};
    std::call_once(init_flag, init);

    Map();
    Timeline();
    DataSelection();
  }

} // namespace gui
