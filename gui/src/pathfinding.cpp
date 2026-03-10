#include "pathfinding.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <optional>
#include <queue>

namespace {
  struct Point {
    int x, y;

    bool operator==(const Point& other) const {
      return x == other.x && y == other.y;
    }
  };

  struct Node {
    Point pos;
    float g = 0, h = 0, f = 0;
    std::optional<Point> parent;

    bool operator>(const Node& other) const {
      return f > other.f;
    }
  };

  float heuristic(Point point1, Point point2) {
    return static_cast<float>(std::abs(point1.x - point2.x) + std::abs(point1.y - point2.y));
  }
} // namespace

std::vector<ImVec2> pathfinding::a_star(ImVec2 start, ImVec2 end, const ImGui::Texture& image) {
  if (start.x == end.x && start.y == end.y) return {start};
  if (start.x < 0 || start.x >= 1 || start.y < 0 || start.y >= 1) return {};
  if (end.x < 0 || end.x >= 1 || end.y < 0 || end.y >= 1) return {};

  Point start_point;
  start_point.x = static_cast<int>(std::round(start.x * image.GetWidth()));
  start_point.y = static_cast<int>(std::round(start.y * image.GetHeight()));

  Point end_point;
  end_point.x = static_cast<int>(std::round(end.x * image.GetWidth()));
  end_point.y = static_cast<int>(std::round(end.y * image.GetHeight()));

  const auto is_path = [&](Point point) -> bool {
    for (size_t ch = 0; ch < image.GetChannels(); ch++) {
      if (image.at(point.x, point.y, ch) == 255) return true;
    }
    return false;
  };

  if (!is_path(start_point) || !is_path(end_point)) return {};

  const std::array<Point, 4> directions{{{1, 0}, {-1, 0}, {0, -1}, {0, 1}}};

  std::vector<::Node> open_set{};
  std::vector<::Node> closed_set{};
  std::priority_queue<::Node, std::vector<Node>, std::greater<::Node>> queue{};

  ::Node start_node{start_point, 0, 0, 0};
  queue.push(start_node);
  open_set.emplace_back(start_node);

  while (!queue.empty()) {
    ::Node current = queue.top();
    queue.pop();

    open_set.erase(std::remove_if(open_set.begin(), open_set.end(), [&](const ::Node& n) { return n.pos == current.pos; }), open_set.end());

    if (current.pos == end_point) {
      std::vector<ImVec2> path{};
      Point at = current.parent.value();
      while (at != start_point) {
        path.emplace_back(static_cast<float>(at.x) / image.GetWidth(), static_cast<float>(at.y) / image.GetWidth());
        auto it = std::find_if(closed_set.begin(), closed_set.end(), [&](const ::Node& n) { return n.pos == at; });
        if (it != closed_set.end() && it->parent.has_value())
          at = it->parent.value();
        else
          return {};
      }
      path.emplace_back(start);
      std::reverse(path.begin(), path.end());
      return path;
    }

    closed_set.emplace_back(current);

    for (const auto& dir : directions) {
      Point next_point{current.pos.x + dir.x, current.pos.y + dir.y};
      if (next_point.x < 0 || next_point.x >= image.GetWidth()) continue;
      if (next_point.y < 0 || next_point.y >= image.GetHeight()) continue;
      if (!is_path(next_point)) continue;
      if (std::find_if(closed_set.begin(), closed_set.end(), [&](const ::Node& n) { return n.pos == next_point; }) != closed_set.end()) continue;

      float g_new = current.g + 1;
      float h_new = ::heuristic(next_point, end_point);
      float f_new = g_new + h_new;

      auto open_it = std::find_if(open_set.begin(), open_set.end(), [&](const ::Node& n) { return n.pos == next_point; });

      if (open_it == open_set.end()) {
        ::Node neighbor{next_point, g_new, h_new, f_new, current.pos};
        open_set.emplace_back(neighbor);
        queue.push(neighbor);
      } else if (g_new < open_it->g) {
        open_it->g = g_new;
        open_it->h = h_new;
        open_it->f = f_new;
        open_it->parent = current.pos;
        queue.push(*open_it);
      }
    }
  }

  return {};
}
