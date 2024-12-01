cmake_minimum_required(VERSION 3.15)

project(NinjaPythonDistributions)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_MODULE_PATH})

# Options
option(BUILD_VERBOSE "Display additional information while building (e.g download progress, ...)" OFF)
option(RUN_NINJA_TEST "Run Ninja test suite" ON)

message(STATUS "************************************")
message(STATUS "Ninja Python Distribution")
message(STATUS "")
message(STATUS "  BUILD_VERBOSE  : ${BUILD_VERBOSE}")
message(STATUS "  RUN_NINJA_TEST : ${RUN_NINJA_TEST}")
message(STATUS "************************************")

include(FetchContent)
FetchContent_Declare(
  ninja
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/ninja-upstream
)
FetchContent_MakeAvailable(ninja)

install(TARGETS ninja COMPONENT python DESTINATION "${SKBUILD_SCRIPTS_DIR}")
install(FILES "${ninja_SOURCE_DIR}/misc/ninja_syntax.py" COMPONENT python DESTINATION ninja)
