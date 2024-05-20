cmake_minimum_required(VERSION 3.15)

project(NinjaPythonDistributions)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_MODULE_PATH})

# Options
option(BUILD_VERBOSE "Display additional information while building (e.g download progress, ...)" OFF)
option(RUN_NINJA_TEST "Run Ninja test suite" ON)
set(ARCHIVE_DOWNLOAD_DIR "${CMAKE_BINARY_DIR}" CACHE PATH "Directory where to download archives")

include(NinjaUrls)

function(check_archive_var archive_var)
  if(NOT DEFINED "${archive_var}_url")
    message(FATAL_ERROR "Failed to determine which archive to download: '${archive_var}_url' variable is not defined")
  endif()
  if(NOT DEFINED "${archive_var}_sha256")
    message(FATAL_ERROR "Could you make sure variable '${archive_var}_sha256' is defined ?")
  endif()
endfunction()

set(src_archive "unix_source")
if(WIN32)
  set(src_archive "windows_source")
endif()
check_archive_var("${src_archive}")

message(STATUS "*********************************************")
message(STATUS "Ninja Python Distribution")
message(STATUS "")
message(STATUS "  BUILD_VERBOSE             : ${BUILD_VERBOSE}")
message(STATUS "  RUN_NINJA_TEST            : ${RUN_NINJA_TEST}")
message(STATUS "")
message(STATUS "  ARCHIVE_DOWNLOAD_DIR      : ${ARCHIVE_DOWNLOAD_DIR}")
message(STATUS "")
message(STATUS "    src_archive             : ${src_archive}")
message(STATUS "    <src_archive>_url       : ${${src_archive}_url}")
message(STATUS "    <src_archive>_sha256    : ${${src_archive}_sha256}")
message(STATUS "*********************************************")

set(ep_download_no_progress_args)
if(NOT BUILD_VERBOSE)
  set(ep_download_no_progress_args
    DOWNLOAD_NO_PROGRESS 1
    )
endif()

include(FetchContent)
FetchContent_Declare(
  ninja
  URL ${${src_archive}_url}
  URL_HASH SHA256=${${src_archive}_sha256}
  DOWNLOAD_DIR ${ARCHIVE_DOWNLOAD_DIR}
  ${ep_download_no_progress_args}
)
FetchContent_MakeAvailable(ninja)

install(TARGETS ninja COMPONENT python DESTINATION "${SKBUILD_SCRIPTS_DIR}")
install(FILES "${ninja_SOURCE_DIR}/misc/ninja_syntax.py" COMPONENT python DESTINATION ninja)
