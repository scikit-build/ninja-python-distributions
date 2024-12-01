cmake_minimum_required(VERSION 3.15)

project(NinjaPythonDistributions)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_MODULE_PATH})

# Options
option(RUN_NINJA_TEST "Run Ninja test suite" OFF)

message(STATUS "************************************")
message(STATUS "Ninja Python Distribution")
message(STATUS "")
message(STATUS "  RUN_NINJA_TEST : ${RUN_NINJA_TEST}")
message(STATUS "************************************")

include(FetchContent)
FetchContent_Declare(
  ninja
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/ninja-upstream
)
FetchContent_MakeAvailable(ninja)

if(RUN_NINJA_TEST)
  add_custom_target(
    run_ninja_test ALL "$<TARGET_FILE:ninja_test>"
    DEPENDS ninja_test
    WORKING_DIRECTORY "$<TARGET_FILE_DIR:ninja_test>"
  )
endif()

install(TARGETS ninja COMPONENT python DESTINATION "${SKBUILD_SCRIPTS_DIR}")
install(FILES "${ninja_SOURCE_DIR}/misc/ninja_syntax.py" COMPONENT python DESTINATION ninja)
