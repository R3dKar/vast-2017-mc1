#include "utility.hpp"

#include <cstdio>
#include <cstdlib>
#include <ctime>

void utility::format_timestamp(double timestamp, char* buffer, size_t buffer_size, const char* format) {
  std::time_t time = static_cast<std::time_t>(timestamp);
  std::tm* timeinfo = std::gmtime(&time);
  std::strftime(buffer, buffer_size, format, timeinfo);
}

void utility::format_timespan(double timespan, char* buffer, size_t buffer_size) {
  const long long timespan_int = static_cast<long long>(timespan);

  auto division = std::lldiv(timespan_int, 7 * 24 * 60 * 60);
  const size_t weeks = division.quot;

  division = std::lldiv(division.rem, 24 * 60 * 60);
  const size_t days = division.quot;

  division = std::lldiv(division.rem, 60 * 60);
  const size_t hours = division.quot;

  division = std::lldiv(division.rem, 60);
  const size_t minutes = division.quot;
  const size_t seconds = division.rem;

  if (weeks > 0) {
    std::snprintf(buffer, buffer_size, "%zuw %zud %02zu:%02zu:%02zu", weeks, days, hours, minutes, seconds);
    return;
  } else if (days > 0) {
    std::snprintf(buffer, buffer_size, "%zud %02zu:%02zu:%02zu", days, hours, minutes, seconds);
    return;
  } else {
    std::snprintf(buffer, buffer_size, "%02zu:%02zu:%02zu", hours, minutes, seconds);
    return;
  }
}
