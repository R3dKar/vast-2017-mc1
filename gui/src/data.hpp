#pragma once

#include <chrono>
#include <fstream>
#include <functional>
#include <imgui.h>
#include <iomanip>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>

namespace data {
  enum class Sensor {
    Camping0,
    Camping1,
    Camping2,
    Camping3,
    Camping4,
    Camping5,
    Camping6,
    Camping7,
    Camping8,
    Entrance0,
    Entrance1,
    Entrance2,
    Entrance3,
    Entrance4,
    Gate0,
    Gate1,
    Gate2,
    Gate3,
    Gate4,
    Gate5,
    Gate6,
    Gate7,
    Gate8,
    GeneralGate0,
    GeneralGate1,
    GeneralGate2,
    GeneralGate3,
    GeneralGate4,
    GeneralGate5,
    GeneralGate6,
    GeneralGate7,
    RangerBase,
    RangerStop0,
    RangerStop1,
    RangerStop2,
    RangerStop3,
    RangerStop4,
    RangerStop5,
    RangerStop6,
    RangerStop7,
  };

  inline static const std::unordered_map<Sensor, const char*> sensor_name_map{
      {Sensor::Camping0, "camping0"},
      {Sensor::Camping1, "camping1"},
      {Sensor::Camping2, "camping2"},
      {Sensor::Camping3, "camping3"},
      {Sensor::Camping4, "camping4"},
      {Sensor::Camping5, "camping5"},
      {Sensor::Camping6, "camping6"},
      {Sensor::Camping7, "camping7"},
      {Sensor::Camping8, "camping8"},
      {Sensor::Entrance0, "entrance0"},
      {Sensor::Entrance1, "entrance1"},
      {Sensor::Entrance2, "entrance2"},
      {Sensor::Entrance3, "entrance3"},
      {Sensor::Entrance4, "entrance4"},
      {Sensor::Gate0, "gate0"},
      {Sensor::Gate1, "gate1"},
      {Sensor::Gate2, "gate2"},
      {Sensor::Gate3, "gate3"},
      {Sensor::Gate4, "gate4"},
      {Sensor::Gate5, "gate5"},
      {Sensor::Gate6, "gate6"},
      {Sensor::Gate7, "gate7"},
      {Sensor::Gate8, "gate8"},
      {Sensor::GeneralGate0, "general-gate0"},
      {Sensor::GeneralGate1, "general-gate1"},
      {Sensor::GeneralGate2, "general-gate2"},
      {Sensor::GeneralGate3, "general-gate3"},
      {Sensor::GeneralGate4, "general-gate4"},
      {Sensor::GeneralGate5, "general-gate5"},
      {Sensor::GeneralGate6, "general-gate6"},
      {Sensor::GeneralGate7, "general-gate7"},
      {Sensor::RangerBase, "ranger-base"},
      {Sensor::RangerStop0, "ranger-stop0"},
      {Sensor::RangerStop1, "ranger-stop1"},
      {Sensor::RangerStop2, "ranger-stop2"},
      {Sensor::RangerStop3, "ranger-stop3"},
      {Sensor::RangerStop4, "ranger-stop4"},
      {Sensor::RangerStop5, "ranger-stop5"},
      {Sensor::RangerStop6, "ranger-stop6"},
      {Sensor::RangerStop7, "ranger-stop7"},
  };

  inline static const std::unordered_map<std::string_view, Sensor> name_sensor_map{
      {"camping0", Sensor::Camping0},
      {"camping1", Sensor::Camping1},
      {"camping2", Sensor::Camping2},
      {"camping3", Sensor::Camping3},
      {"camping4", Sensor::Camping4},
      {"camping5", Sensor::Camping5},
      {"camping6", Sensor::Camping6},
      {"camping7", Sensor::Camping7},
      {"camping8", Sensor::Camping8},
      {"entrance0", Sensor::Entrance0},
      {"entrance1", Sensor::Entrance1},
      {"entrance2", Sensor::Entrance2},
      {"entrance3", Sensor::Entrance3},
      {"entrance4", Sensor::Entrance4},
      {"gate0", Sensor::Gate0},
      {"gate1", Sensor::Gate1},
      {"gate2", Sensor::Gate2},
      {"gate3", Sensor::Gate3},
      {"gate4", Sensor::Gate4},
      {"gate5", Sensor::Gate5},
      {"gate6", Sensor::Gate6},
      {"gate7", Sensor::Gate7},
      {"gate8", Sensor::Gate8},
      {"general-gate0", Sensor::GeneralGate0},
      {"general-gate1", Sensor::GeneralGate1},
      {"general-gate2", Sensor::GeneralGate2},
      {"general-gate3", Sensor::GeneralGate3},
      {"general-gate4", Sensor::GeneralGate4},
      {"general-gate5", Sensor::GeneralGate5},
      {"general-gate6", Sensor::GeneralGate6},
      {"general-gate7", Sensor::GeneralGate7},
      {"ranger-base", Sensor::RangerBase},
      {"ranger-stop0", Sensor::RangerStop0},
      {"ranger-stop1", Sensor::RangerStop1},
      {"ranger-stop2", Sensor::RangerStop2},
      {"ranger-stop3", Sensor::RangerStop3},
      {"ranger-stop4", Sensor::RangerStop4},
      {"ranger-stop5", Sensor::RangerStop5},
      {"ranger-stop6", Sensor::RangerStop6},
      {"ranger-stop7", Sensor::RangerStop7},
  };

  inline static const std::unordered_map<Sensor, ImVec2> sensor_location_map{
      {Sensor::Camping0, ImVec2(52 / 200.0f, 158 / 200.0f)},     {Sensor::Camping1, ImVec2(129 / 200.0f, 149 / 200.0f)},     {Sensor::Camping2, ImVec2(44 / 200.0f, 135 / 200.0f)},
      {Sensor::Camping3, ImVec2(45 / 200.0f, 131 / 200.0f)},     {Sensor::Camping4, ImVec2(48 / 200.0f, 110 / 200.0f)},      {Sensor::Camping5, ImVec2(20 / 200.0f, 78 / 200.0f)},
      {Sensor::Camping6, ImVec2(150 / 200.0f, 22 / 200.0f)},     {Sensor::Camping7, ImVec2(181 / 200.0f, 54 / 200.0f)},      {Sensor::Camping8, ImVec2(183 / 200.0f, 151 / 200.0f)},
      {Sensor::Entrance0, ImVec2(62 / 200.0f, 186 / 200.0f)},    {Sensor::Entrance1, ImVec2(17 / 200.0f, 132 / 200.0f)},     {Sensor::Entrance2, ImVec2(183 / 200.0f, 112 / 200.0f)},
      {Sensor::Entrance3, ImVec2(115 / 200.0f, 32 / 200.0f)},    {Sensor::Entrance4, ImVec2(140 / 200.0f, 15 / 200.0f)},     {Sensor::Gate0, ImVec2(63 / 200.0f, 166 / 200.0f)},
      {Sensor::Gate1, ImVec2(58 / 200.0f, 155 / 200.0f)},        {Sensor::Gate2, ImVec2(24 / 200.0f, 145 / 200.0f)},         {Sensor::Gate3, ImVec2(149 / 200.0f, 139 / 200.0f)},
      {Sensor::Gate4, ImVec2(164 / 200.0f, 85 / 200.0f)},        {Sensor::Gate5, ImVec2(131 / 200.0f, 53 / 200.0f)},         {Sensor::Gate6, ImVec2(116 / 200.0f, 48 / 200.0f)},
      {Sensor::Gate7, ImVec2(97 / 200.0f, 39 / 200.0f)},         {Sensor::Gate8, ImVec2(138 / 200.0f, 18 / 200.0f)},         {Sensor::GeneralGate0, ImVec2(110 / 200.0f, 190 / 200.0f)},
      {Sensor::GeneralGate1, ImVec2(64 / 200.0f, 174 / 200.0f)}, {Sensor::GeneralGate2, ImVec2(104 / 200.0f, 167 / 200.0f)}, {Sensor::GeneralGate3, ImVec2(186 / 200.0f, 144 / 200.0f)},
      {Sensor::GeneralGate4, ImVec2(69 / 200.0f, 101 / 200.0f)}, {Sensor::GeneralGate5, ImVec2(124 / 200.0f, 88 / 200.0f)},  {Sensor::GeneralGate6, ImVec2(136 / 200.0f, 62 / 200.0f)},
      {Sensor::GeneralGate7, ImVec2(65 / 200.0f, 55 / 200.0f)},  {Sensor::RangerBase, ImVec2(128 / 200.0f, 24 / 200.0f)},    {Sensor::RangerStop0, ImVec2(89 / 200.0f, 183 / 200.0f)},
      {Sensor::RangerStop1, ImVec2(19 / 200.0f, 175 / 200.0f)},  {Sensor::RangerStop2, ImVec2(80 / 200.0f, 164 / 200.0f)},   {Sensor::RangerStop3, ImVec2(148 / 200.0f, 154 / 200.0f)},
      {Sensor::RangerStop4, ImVec2(18 / 200.0f, 104 / 200.0f)},  {Sensor::RangerStop5, ImVec2(151 / 200.0f, 81 / 200.0f)},   {Sensor::RangerStop6, ImVec2(123 / 200.0f, 52 / 200.0f)},
      {Sensor::RangerStop7, ImVec2(100 / 200.0f, 47 / 200.0f)},
  };

  struct RoutePoint {
    Sensor sensor;
    std::chrono::system_clock::time_point timestamp;

    RoutePoint(const std::string& sensor, const std::string& timestamp) {
      this->sensor = name_sensor_map.at(sensor);

      std::tm tm_struct{};
      std::istringstream ss(timestamp);
      ss >> std::get_time(&tm_struct, "%Y-%m-%d %H:%M:%S");
      this->timestamp = std::chrono::system_clock::from_time_t(std::mktime(&tm_struct));
    }
  };

  struct Route {
    std::string car_id;
    std::string car_type;
    std::vector<RoutePoint> points;

    static std::vector<Route> Load(const char* filename, std::optional<std::function<bool(const Route&)>> filter = std::nullopt) {
      std::unordered_map<std::string, Route> routes{};

      std::ifstream csv_file(filename);
      std::string line;

      std::getline(csv_file, line); // skip headers
      while (std::getline(csv_file, line)) {
        std::vector<std::string> tokens{};

        size_t pos = 0;
        size_t next = 0;
        while ((next = line.find(',', pos)) != std::string::npos) {
          tokens.emplace_back(line.substr(pos, next - pos));
          pos = next + 1;
        }
        tokens.emplace_back(line.substr(pos));

        auto& timestamp = tokens.at(0);
        auto& car_id = tokens.at(1);
        auto& car_type = tokens.at(2);
        auto& sensor = tokens.at(3);

        if (routes.find(car_id) == routes.end()) routes.emplace(car_id, Route{car_id, car_type, {}});
        routes.at(car_id).points.emplace_back(sensor, timestamp);
      }

      std::vector<Route> result{};
      for (auto& [key, value] : routes) {
        if (filter.has_value() && !filter.value()(value)) continue;

        result.emplace_back(std::move(value));
      }
      return result;
    }
  };
} // namespace data
