#pragma once

#include <chrono>
#include <functional>
#include <imgui.h>
#include <optional>
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

  extern const std::unordered_map<Sensor, const char*> sensor_name_map;

  extern const std::unordered_map<std::string_view, Sensor> name_sensor_map;

  extern const std::unordered_map<Sensor, ImVec2> sensor_location_map;

  struct RoutePoint {
    Sensor sensor;
    std::chrono::system_clock::time_point timestamp;

    RoutePoint(const std::string& sensor, const std::string& timestamp);
  };

  struct Route {
    std::string car_id;
    std::string car_type;
    std::vector<RoutePoint> points;

    static std::vector<Route> Load(const char* filename, std::optional<std::function<bool(const Route&)>> filter = std::nullopt);
  };

  std::unordered_map<std::string, std::vector<std::string>> read_clusters(const char* filename);
} // namespace data
