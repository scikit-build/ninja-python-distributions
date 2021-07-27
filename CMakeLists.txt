cmake_minimum_required(VERSION 3.6)

project(NinjaPythonDistributions)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_MODULE_PATH})

# Options
option(BUILD_VERBOSE "Display additional information while building (e.g download progress, ...)" OFF)
set(ARCHIVE_DOWNLOAD_DIR "${CMAKE_BINARY_DIR}" CACHE PATH "Directory where to download archives")

include(NinjaUrls)

#-----------------------------------------------------------------------------
# Which archives ?
#-----------------------------------------------------------------------------
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

#-----------------------------------------------------------------------------
# Summary
#-----------------------------------------------------------------------------
message(STATUS "*********************************************")
message(STATUS "Ninja Python Distribution")
message(STATUS "")
message(STATUS "  BUILD_VERBOSE             : ${BUILD_VERBOSE}")
message(STATUS "")
message(STATUS "  ARCHIVE_DOWNLOAD_DIR      : ${ARCHIVE_DOWNLOAD_DIR}")
message(STATUS "")
message(STATUS "    src_archive             : ${src_archive}")
message(STATUS "    <src_archive>_url       : ${${src_archive}_url}")
message(STATUS "    <src_archive>_sha256    : ${${src_archive}_sha256}")
message(STATUS "*********************************************")

#-----------------------------------------------------------------------------
include(ExternalProject)

set(ep_download_no_progress_args)
if(NOT BUILD_VERBOSE)
  set(ep_download_no_progress_args
    DOWNLOAD_NO_PROGRESS 1
    )
endif()

#-----------------------------------------------------------------------------
# Download source
#-----------------------------------------------------------------------------
if(NOT DEFINED Ninja_SOURCE_DIR)
  set(Ninja_SOURCE_DIR "${CMAKE_SOURCE_DIR}/Ninja-src")

  # Download selected source archive
  ExternalProject_add(download_ninja_source
    SOURCE_DIR ${Ninja_SOURCE_DIR}
    URL ${${src_archive}_url}
    URL_HASH SHA256=${${src_archive}_sha256}
    DOWNLOAD_DIR ${ARCHIVE_DOWNLOAD_DIR}
    USES_TERMINAL_DOWNLOAD 1
    CONFIGURE_COMMAND ""
    BUILD_COMMAND ""
    BUILD_IN_SOURCE 1
    INSTALL_COMMAND ""
    ${ep_download_no_progress_args}
    )
  message(STATUS "download_ninja_source - URL: ${${src_archive}_url}")
elseif(NOT EXISTS ${Ninja_SOURCE_DIR})
  message(FATAL_ERROR "Ninja_SOURCE_DIR is set to a nonexistent directory")
endif()

#-----------------------------------------------------------------------------
# Build from source
#-----------------------------------------------------------------------------
if(UNIX AND NOT APPLE)
  # We're more likely to build from sources from PyPI on UNIX
  # In order to relax the constraint on CMake version,
  # use the python bootstrap script rather than the CMake build (requires 3.15+)

  # Dependencies
  find_package(PythonInterp REQUIRED)

  set(ninja_executable ${Ninja_SOURCE_DIR}/ninja${CMAKE_EXECUTABLE_SUFFIX})
  set(bootstrap_command ${PYTHON_EXECUTABLE} configure.py --bootstrap)
  # Explicitly defining _BSD_SOURCE is required to support building the wheel on Alpine. See issue  #22
  set(bootstrap_command ${CMAKE_COMMAND} -E env CXXFLAGS=-D_BSD_SOURCE ${bootstrap_command})
  add_custom_command(
    COMMAND ${bootstrap_command}
    OUTPUT ${ninja_executable}
    WORKING_DIRECTORY ${Ninja_SOURCE_DIR}
    )
  add_custom_target(build_ninja ALL
    DEPENDS download_ninja_source ${ninja_executable}
    )
else()
  set(Ninja_BINARY_DIR ${CMAKE_BINARY_DIR}/Ninja-build)
  ExternalProject_add(build_ninja
    SOURCE_DIR ${Ninja_SOURCE_DIR}
    BINARY_DIR ${Ninja_BINARY_DIR}
    DOWNLOAD_COMMAND ""
    UPDATE_COMMAND ""
    BUILD_ALWAYS 1
    USES_TERMINAL_CONFIGURE 1
    USES_TERMINAL_BUILD 1
    INSTALL_COMMAND ""
    DEPENDS
      download_ninja_source
    )
  set(ninja_executable ${Ninja_BINARY_DIR}/ninja${CMAKE_EXECUTABLE_SUFFIX})
endif()

find_program(STRIP_EXECUTABLE strip)
if(STRIP_EXECUTABLE)
  add_custom_target(strip_ninja_executable ALL
    COMMAND ${STRIP_EXECUTABLE} ${ninja_executable}
    WORKING_DIRECTORY ${Ninja_SOURCE_DIR}
    COMMENT "Stripping ninja executable"
    )
  add_dependencies(strip_ninja_executable build_ninja)
endif()

install(FILES ${Ninja_SOURCE_DIR}/misc/ninja_syntax.py DESTINATION src/ninja)
install(PROGRAMS ${ninja_executable} DESTINATION src/ninja/data/bin)
