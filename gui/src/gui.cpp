#include "gui.hpp"
#include "data.hpp"
#include <imgui.h>
#include <imgui_texture.hpp>
#include <implot.h>
#include <mutex>

namespace gui {

  static std::vector<data::Route> routes;
  static ImGui::Texture map_texture;

  void init() {
    routes = data::Route::Load(R"(D:\Projects\vast-2017-mc1\data\sensors.csv)");
    map_texture = ImGui::Texture(R"(D:\Projects\vast-2017-mc1\data\map.bmp)");
  }

  void Map() {
    if (ImGui::Begin("Map")) {
      if (ImPlot::BeginPlot("Map", ImVec2(-1, -1), ImPlotFlags_NoTitle | ImPlotFlags_Equal)) {
        ImPlot::SetupAxis(ImAxis_X1, "X");
        ImPlot::SetupAxis(ImAxis_Y1, "Y", ImPlotAxisFlags_Invert);

        ImPlot::PlotImage("Map", map_texture.GetID(), ImPlotPoint(0, 0), ImPlotPoint(1, 1));
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
