#pragma once

#include <cstdint>

namespace utility {
  void format_timestamp(double timestamp, char* buffer, size_t buffer_size, const char* format = "%Y-%m-%d %H:%M:%S");

  // Format is fixed: 0w 0d 00:00:00
  void format_timespan(double timespan, char* buffer, size_t buffer_size);
} // namespace utility
