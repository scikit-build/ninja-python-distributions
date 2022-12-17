cmake_minimum_required(VERSION 3.15)

project(NinjaPythonDistributions)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_MODULE_PATH})

# Options
option(BUILD_VERBOSE "Display additional information while building (e.g download progress, ...)" OFF)
option(RUN_NINJA_TEST "Run Ninja test suite" ON)
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
message(STATUS "  RUN_NINJA_TEST            : ${RUN_NINJA_TEST}")
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
set(Ninja_BINARY_DIR ${CMAKE_BINARY_DIR}/Ninja-build)
# cache arguments
set(_cache_args )
foreach(var_name IN ITEMS
  CMAKE_BUILD_TYPE
  CMAKE_TOOLCHAIN_FILE
  CMAKE_BUILD_PARALLEL_LEVEL
  CMAKE_JOB_POOLS
  CMAKE_JOB_POOL_COMPILE
  CMAKE_JOB_POOL_LINK
  CMAKE_OSX_DEPLOYMENT_TARGET
  CMAKE_OSX_ARCHITECTURES
  CMAKE_OSX_SYSROOT
  )
  if(DEFINED ${var_name})
    list(APPEND _cache_args -D${var_name}:STRING=${${var_name}})
    message(STATUS "SuperBuild - ${var_name}: ${${var_name}}")
  endif()
endforeach()

# _cache_args should not be empty
list(APPEND _cache_args -DNINJA_SUPERBUILD:BOOL=true)
ExternalProject_add(build_ninja
  SOURCE_DIR ${Ninja_SOURCE_DIR}
  BINARY_DIR ${Ninja_BINARY_DIR}
  DOWNLOAD_COMMAND ""
  UPDATE_COMMAND ""
  BUILD_ALWAYS 1
  USES_TERMINAL_CONFIGURE 1
  USES_TERMINAL_BUILD 1
  INSTALL_COMMAND ""
  CMAKE_CACHE_ARGS ${_cache_args}
  DEPENDS
    download_ninja_source
  )
set(ninja_executable ${Ninja_BINARY_DIR}/ninja${CMAKE_EXECUTABLE_SUFFIX})
set(NINJA_BUILD_LAST_STEP "build")

# This should not be stripped or tested if cross-compiling on Windows
if(CMAKE_CROSS_COMPILE OR NOT DEFINED ENV{DIST_EXTRA_CONFIG})
  find_program(STRIP_EXECUTABLE strip)
  if(STRIP_EXECUTABLE)
    ExternalProject_Add_Step(build_ninja strip_executables
      DEPENDEES ${NINJA_BUILD_LAST_STEP}
      COMMENT "Stripping CMake executables"
      COMMAND ${STRIP_EXECUTABLE} ${ninja_executable}
      USES_TERMINAL 1
      )
    set(NINJA_BUILD_LAST_STEP "strip_executables")
  endif()

  if(RUN_NINJA_TEST)
    ExternalProject_Add_Step(build_ninja run_ninja_test_suite
      DEPENDEES ${NINJA_BUILD_LAST_STEP}
      COMMENT "Running Ninja test suite"
      COMMAND ${Ninja_BINARY_DIR}/ninja_test${CMAKE_EXECUTABLE_SUFFIX}
      WORKING_DIRECTORY ${Ninja_BINARY_DIR}
      USES_TERMINAL 1
      )
    set(NINJA_BUILD_LAST_STEP "run_ninja_test_suite")
  endif()
endif()

install(FILES ${Ninja_SOURCE_DIR}/misc/ninja_syntax.py DESTINATION src/ninja)
install(PROGRAMS ${ninja_executable} DESTINATION src/ninja/data/bin)
