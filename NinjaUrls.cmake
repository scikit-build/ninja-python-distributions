
#-----------------------------------------------------------------------------
# Ninja sources
set(unix_source_url       "https://github.com/kitware/ninja/archive/v1.8.2.g3bbbe.kitware.dyndep-1.jobserver-1.tar.gz")
set(unix_source_sha256    "121c432cec32c8aea730a71a256a81442ac8446c6f0e7652ea3121da9e0d482d")

set(windows_source_url    "https://github.com/kitware/ninja/archive/v1.8.2.g3bbbe.kitware.dyndep-1.jobserver-1.zip")
set(windows_source_sha256 "01a2bb09bb2f6e6c0e4c9634e0491ad137fde80c3e99de581ee311401d07976a")

if(MSVC AND (MSVC_VERSION EQUAL 1600 OR MSVC_VERSION LESS 1600))
  # Fix compilation using "Microsoft Visual C++ Compiler for Python 2.7" or "Visual Studio 2010"
  set(windows_source_url    "https://github.com/jcfr/ninja/archive/kitware-staged-features-support-vs2008-vs2010.zip")
  set(windows_source_sha256 "d64d6ae2eaeed28832e9a9c28901b01f9d070d3f440346e585f68d490447f262")
endif()

#-----------------------------------------------------------------------------
# Ninja binaries
set(linux32_binary_url    "NA")  # Linux 32-bit binaries not available
set(linux32_binary_sha256 "NA")

set(linux64_binary_url    "https://github.com/Kitware/ninja/releases/download/v1.8.2.g3bbbe.kitware.dyndep-1.jobserver-1/ninja-1.8.2.g3bbbe.kitware.dyndep-1.jobserver-1_x86_64-linux-gnu.tar.gz")
set(linux64_binary_sha256 "d0c1c112edbbee421509540764086a2aeaba72d9f552f31423390f8cd254d332")

set(macosx_binary_url    "https://github.com/Kitware/ninja/releases/download/v1.8.2.g3bbbe.kitware.dyndep-1.jobserver-1/ninja-1.8.2.g3bbbe.kitware.dyndep-1.jobserver-1_x86_64-apple-darwin.tar.gz")
set(macosx_binary_sha256 "d71dfa6ec1c15fca4c559ef5d8e7170639e791d499a742eb814e104e82352338")

set(win32_binary_url    "NA")  # Windows 32-bit binaries not available
set(win32_binary_sha256 "NA")

set(win64_binary_url    "https://github.com/Kitware/ninja/releases/download/v1.8.2.g3bbbe.kitware.dyndep-1.jobserver-1/ninja-1.8.2.g3bbbe.kitware.dyndep-1.jobserver-1_i686-pc-windows-msvc.zip")
set(win64_binary_sha256 "665581a875ffa16bcb410972fd8cb419035ce66cf4760b55ba8a57774b2afa61")
