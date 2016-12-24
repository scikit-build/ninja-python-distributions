cmake_minimum_required(VERSION 3.6)

project(NinjaPythonDistributions)

# Options
set(_build_from_source_default ON)
if((WIN32 AND CMAKE_SIZEOF_VOID_P EQUAL 8) OR APPLE)
  set(_build_from_source_default OFF)
endif()
option(BUILD_FROM_SOURCE "Build Ninja from source" ${_build_from_source_default})
option(BUILD_VERBOSE "Display additional information while building (e.g download progress, ...)" OFF)
set(ARCHIVE_DOWNLOAD_DIR "${CMAKE_BINARY_DIR}" CACHE PATH "Directory where to download archives")

# Dependencies
find_package(PythonInterp REQUIRED)

# Ninja sources
set(unix_source_url       "https://github.com/ninja-build/ninja/archive/v1.7.2.tar.gz")
set(unix_source_sha256    "2edda0a5421ace3cf428309211270772dd35a91af60c96f93f90df6bc41b16d9")

set(windows_source_url    "https://github.com/ninja-build/ninja/archive/v1.7.2.zip")
set(windows_source_sha256 "6645230ae6cea71d095fa3b8992a30a58d967a65c931a779f07cbb62eaa39698")

# Ninja binaries
set(linux32_binary_url    "NA")  # Linux 32-bit binaries not available
set(linux32_binary_sha256 "NA")

set(linux64_binary_url    "https://github.com/ninja-build/ninja/releases/download/v1.7.2/ninja-linux.zip")
set(linux64_binary_sha256 "38fa8cfb9c1632a5cdf7a32fe1a7c5aa89e96c1d492c28624f4cc018e68458b9")

set(macosx_binary_url    "https://github.com/ninja-build/ninja/releases/download/v1.7.2/ninja-mac.zip")
set(macosx_binary_sha256 "dd29df5d1a92f1216659c3752311286da5350896b94f8963bb8e0877e0f1de04")

set(win32_binary_url    "NA")  # Windows 32-bit binaries not available
set(win32_binary_sha256 "NA")

set(win64_binary_url    "https://github.com/ninja-build/ninja/releases/download/v1.7.2/ninja-win.zip")
set(win64_binary_sha256 "95b36a597d33c1fe672829cfe47b5ab34b3a1a4c6bf628e5d150b6075df4ef50")


message(STATUS "*********************************************")
message(STATUS "Build Ninja from source: ${BUILD_FROM_SOURCE}")
message(STATUS "*********************************************")

#-----------------------------------------------------------------------------
# Which archives ?

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

set(binary_archive "linux32_binary")
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
  set(binary_archive "linux64_binary")
endif()
if(APPLE)
  set(binary_archive "macosx_binary")
endif()
if(WIN32)
  set(binary_archive "win32_binary")
  if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    set(binary_archive "win64_binary")
  endif()
endif()
check_archive_var("${binary_archive}")

#-----------------------------------------------------------------------------
include(ExternalProject)

set(ep_download_no_progress_args)
if(NOT BUILD_VERBOSE)
  set(ep_download_no_progress_args
    DOWNLOAD_NO_PROGRESS 1
    )
endif()

#
# Always expect the sources (needed for `sdist`)
#
if(NOT DEFINED Ninja_SOURCE_DIR)
  set(Ninja_SOURCE_DIR "${CMAKE_SOURCE_DIR}/src")

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

if(BUILD_FROM_SOURCE)

  set(ninja_executable ${Ninja_SOURCE_DIR}/ninja${CMAKE_EXECUTABLE_SUFFIX})
  add_custom_command(
    COMMAND ${PYTHON_EXECUTABLE} configure.py --bootstrap
    OUTPUT ${ninja_executable}
    WORKING_DIRECTORY ${Ninja_SOURCE_DIR}
    )
  add_custom_target(build_ninja ALL
    DEPENDS ${ninja_executable}
    )
  add_dependencies(build_ninja download_ninja_source)

  find_program(STRIP_EXECUTABLE strip)
  if(STRIP_EXECUTABLE)
    add_custom_target(strip_ninja_executable ALL
      COMMAND ${STRIP_EXECUTABLE} ${ninja_executable}
      WORKING_DIRECTORY ${Ninja_SOURCE_DIR}
      COMMENT "Stripping ninja executable"
      )
    add_dependencies(strip_ninja_executable build_ninja)
  endif()

else()

  if(${binary_archive}_sha256 STREQUAL "NA")
    message(FATAL_ERROR "Pre-built archives not available for '${binary_archive}'. Consider setting BUILD_FROM_SOURCE to ON.")
  endif()
  # Download selected binary archive
  ExternalProject_add(download_ninja_binary
    SOURCE_DIR ${CMAKE_BINARY_DIR}/bin
    URL ${${binary_archive}_url}
    URL_HASH SHA256=${${binary_archive}_sha256}
    DOWNLOAD_DIR ${ARCHIVE_DOWNLOAD_DIR}
    USES_TERMINAL_DOWNLOAD 1
    CONFIGURE_COMMAND ""
    BUILD_COMMAND ""
    BUILD_IN_SOURCE 1
    INSTALL_COMMAND ""
    ${ep_download_no_progress_args}
    )
  message(STATUS "download_ninja_binary - URL: ${${binary_archive}_url}")
  set(ninja_executable ${CMAKE_BINARY_DIR}/bin/ninja${CMAKE_EXECUTABLE_SUFFIX})

endif()

install(FILES ${Ninja_SOURCE_DIR}/misc/ninja_syntax.py DESTINATION ninja)
install(PROGRAMS ${ninja_executable} DESTINATION ninja/data/bin)

