cmake_minimum_required(VERSION 3.15)

project(NinjaPythonDistributions)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_MODULE_PATH})

# Verify that the Ninja source directory is available
if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/ninja-upstream/CMakeLists.txt")
  if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/.git")
    set(_details "Make sure to initialize submodules: git submodule update --init --recursive.")
  else()
    set(_details "Source distribution appears to be incomplete or invalid.")
  endif()
  message(FATAL_ERROR "Missing ninja-upstream sources at [${CMAKE_CURRENT_SOURCE_DIR}/ninja-upstream]. ${_details}")
endif()

# Options
option(RUN_NINJA_TEST "Run Ninja test suite" OFF)

message(STATUS "************************************")
message(STATUS "Ninja Python Distribution")
message(STATUS "")
message(STATUS "  RUN_NINJA_TEST : ${RUN_NINJA_TEST}")
message(STATUS "************************************")

set(BUILD_TESTING ${RUN_NINJA_TEST} CACHE INTERNAL "")

add_subdirectory(ninja-upstream)

if(RUN_NINJA_TEST)
  add_custom_target(
    run_ninja_test ALL "$<TARGET_FILE:ninja_test>" ${TEST_OPTS}
    DEPENDS ninja_test
    WORKING_DIRECTORY "$<TARGET_FILE_DIR:ninja_test>"
  )
endif()

install(TARGETS ninja COMPONENT python DESTINATION "${SKBUILD_SCRIPTS_DIR}")
install(FILES "${ninja_SOURCE_DIR}/misc/ninja_syntax.py" COMPONENT python DESTINATION ninja)
