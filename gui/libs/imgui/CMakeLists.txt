project(imgui LANGUAGES CXX)

find_package(OpenGL REQUIRED)
add_subdirectory(glfw)

add_library(${PROJECT_NAME}) 

# imgui
target_sources(${PROJECT_NAME} PRIVATE
  imgui/imgui.cpp
  imgui/backends/imgui_impl_glfw.cpp
  imgui/backends/imgui_impl_opengl3.cpp
  imgui/imgui_draw.cpp
  imgui/imgui_widgets.cpp
  imgui/imgui_tables.cpp
  imgui_app.cpp
  imgui_texture.cpp
  imgui/imgui_demo.cpp
)
target_include_directories(${PROJECT_NAME} PUBLIC 
  ${CMAKE_CURRENT_LIST_DIR}
  imgui
  imgui/backends
)

# implot
target_sources(${PROJECT_NAME} PRIVATE
  implot/implot.cpp
  implot/implot_items.cpp
  implot/implot_demo.cpp
)
target_include_directories(${PROJECT_NAME} PUBLIC
  implot
)

target_link_libraries(${PROJECT_NAME} PRIVATE OpenGL::GL nfd::nfd PUBLIC glfw)

if (UNIX)
  target_link_libraries(${PROJECT_NAME} PRIVATE X11) 
endif()
