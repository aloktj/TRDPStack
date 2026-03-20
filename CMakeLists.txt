cmake_minimum_required(VERSION 3.20)

project(TRDPStack VERSION 0.1.0 LANGUAGES C)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)
include(CTest)

set(TRDP_VOS_BACKEND "posix" CACHE STRING "Select the VOS backend to build (posix or custom)")
set_property(CACHE TRDP_VOS_BACKEND PROPERTY STRINGS posix custom)

option(TRDP_MD_SUPPORT "Enable Message Data support" ON)
option(TRDP_SOA_SUPPORT "Enable service-oriented API support" OFF)
option(TRDP_TSN_SUPPORT "Enable TSN support" OFF)
option(TRDP_PD_UNICAST_SUPPORT "Enable PD unicast support" OFF)
option(TRDP_HIGH_PERF_INDEXED "Enable indexed high-performance PD mode" OFF)
option(TRDP_HIGH_PERF_BASE2 "Use base-2 high-performance indexing" OFF)
option(TRDP_BUILD_EXAMPLES "Build example applications" OFF)
option(TRDP_BUILD_TESTS "Build test applications" OFF)
option(TRDP_BUILD_XML_TOOLS "Build XML-based tools requiring trdpap" OFF)
option(TRDP_BUILD_MARSHALLING_TESTS "Build marshalling tests requiring trdpap" OFF)
option(TRDP_ENABLE_DEBUG "Build with DEBUG instead of NO_DEBUG" OFF)
option(TRDP_ENABLE_PIC "Build targets with position independent code" ON)

if(NOT CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    message(WARNING "This CMake build is tuned for GCC-compatible toolchains; current compiler is ${CMAKE_C_COMPILER_ID}.")
endif()

set(TRDP_COMMON_SOURCES
    src/common/trdp_pdcom.c
    src/common/trdp_utils.c
    src/common/tlp_if.c
    src/common/tlc_if.c
    src/common/trdp_stats.c
    src/vos/common/vos_utils.c
    src/vos/common/vos_mem.c
)

set(TRDP_OPTIONAL_SOURCES
    src/common/trdp_xml.c
    src/common/tau_xml.c
    src/common/tau_marshall.c
    src/common/tau_dnr.c
    src/common/tau_tti.c
    src/common/tau_ctrl.c
)

set(TRDP_BUILD_PUBLIC_INCLUDES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/api
    ${CMAKE_CURRENT_SOURCE_DIR}/src/vos/api
)

set(TRDP_PRIVATE_INCLUDES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/common
)

set(TRDP_COMPILE_DEFS)
set(TRDP_SYSTEM_LIBS)
set(TRDP_THREADS_REQUIRED OFF)

if(TRDP_VOS_BACKEND STREQUAL "posix")
    list(APPEND TRDP_COMMON_SOURCES
        src/vos/posix/vos_sock.c
        src/vos/posix/vos_thread.c
        src/vos/posix/vos_shared_mem.c
    )
    list(APPEND TRDP_PRIVATE_INCLUDES ${CMAKE_CURRENT_SOURCE_DIR}/src/vos/posix)
    list(APPEND TRDP_COMPILE_DEFS LINUX POSIX HAS_UUID)
    list(APPEND TRDP_SYSTEM_LIBS uuid rt)
    set(TRDP_THREADS_REQUIRED ON)
elseif(TRDP_VOS_BACKEND STREQUAL "custom")
    list(APPEND TRDP_COMPILE_DEFS TRDP_CUSTOM_VOS)
    list(APPEND TRDP_PRIVATE_INCLUDES ${CMAKE_CURRENT_SOURCE_DIR}/src/vos/custom)
    set(TRDP_ENABLE_PIC OFF CACHE BOOL "Build targets with position independent code" FORCE)
else()
    message(FATAL_ERROR "Unsupported TRDP_VOS_BACKEND='${TRDP_VOS_BACKEND}'. Supported values: posix, custom")
endif()

if(TRDP_MD_SUPPORT)
    list(APPEND TRDP_COMMON_SOURCES
        src/common/trdp_mdcom.c
        src/common/tlm_if.c
    )
    list(APPEND TRDP_COMPILE_DEFS MD_SUPPORT=1)
else()
    list(APPEND TRDP_COMPILE_DEFS MD_SUPPORT=0)
endif()

if(TRDP_SOA_SUPPORT)
    list(APPEND TRDP_OPTIONAL_SOURCES src/common/tau_so_if.c)
    list(APPEND TRDP_COMPILE_DEFS SOA_SUPPORT)
endif()

if(TRDP_TSN_SUPPORT)
    if(NOT TRDP_VOS_BACKEND STREQUAL "posix")
        message(FATAL_ERROR "TRDP_TSN_SUPPORT currently requires TRDP_VOS_BACKEND=posix")
    endif()
    list(APPEND TRDP_COMMON_SOURCES src/vos/posix/vos_sockTSN.c)
    list(APPEND TRDP_COMPILE_DEFS TSN_SUPPORT RT_THREADS)
endif()

if(TRDP_PD_UNICAST_SUPPORT)
    list(APPEND TRDP_COMPILE_DEFS PD_UNICAST_SUPPORT)
endif()

if(TRDP_HIGH_PERF_INDEXED)
    list(APPEND TRDP_COMMON_SOURCES src/common/trdp_pdindex.c)
    list(APPEND TRDP_COMPILE_DEFS HIGH_PERF_INDEXED)
endif()

if(TRDP_HIGH_PERF_BASE2)
    list(APPEND TRDP_COMPILE_DEFS HIGH_PERF_BASE2)
endif()

if(TRDP_ENABLE_DEBUG)
    list(APPEND TRDP_COMPILE_DEFS DEBUG)
else()
    list(APPEND TRDP_COMPILE_DEFS NO_DEBUG)
endif()

set(TRDP_COMPILE_OPTIONS
    -Wall
    -Wno-unknown-pragmas
    -Wno-format
    -Wno-unused-label
    -Wno-unused-function
)

if(TRDP_VOS_BACKEND STREQUAL "posix")
    list(APPEND TRDP_COMPILE_OPTIONS
        -fstrength-reduce
        -fno-builtin
        -fsigned-char
        -D_GNU_SOURCE
    )
endif()

if(TRDP_THREADS_REQUIRED)
    find_package(Threads REQUIRED)
endif()

function(trdp_configure_target target_name)
    target_include_directories(${target_name}
        PUBLIC
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/api>
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/vos/api>
            $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}/trdp/api>
            $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}/trdp/vos/api>
        PRIVATE
            ${TRDP_PRIVATE_INCLUDES}
    )
    target_compile_definitions(${target_name} PUBLIC ${TRDP_COMPILE_DEFS})
    target_compile_options(${target_name} PRIVATE ${TRDP_COMPILE_OPTIONS})
    target_compile_features(${target_name} PRIVATE c_std_99)
    set_target_properties(${target_name} PROPERTIES
        POSITION_INDEPENDENT_CODE ${TRDP_ENABLE_PIC}
    )

    if(TRDP_THREADS_REQUIRED)
        target_link_libraries(${target_name} PUBLIC Threads::Threads)
    endif()

    if(TRDP_SYSTEM_LIBS)
        target_link_libraries(${target_name} PUBLIC ${TRDP_SYSTEM_LIBS})
    endif()
endfunction()

add_library(trdp STATIC ${TRDP_COMMON_SOURCES})
add_library(TRDP::trdp ALIAS trdp)
set_target_properties(trdp PROPERTIES OUTPUT_NAME trdp EXPORT_NAME trdp)
trdp_configure_target(trdp)

add_library(trdpap STATIC ${TRDP_COMMON_SOURCES} ${TRDP_OPTIONAL_SOURCES})
add_library(TRDP::trdpap ALIAS trdpap)
set_target_properties(trdpap PROPERTIES OUTPUT_NAME trdpap EXPORT_NAME trdpap)
trdp_configure_target(trdpap)

function(trdp_add_executable target source lib)
    add_executable(${target} ${source})
    target_include_directories(${target} PRIVATE ${TRDP_BUILD_PUBLIC_INCLUDES} ${TRDP_PRIVATE_INCLUDES})
    target_compile_definitions(${target} PRIVATE ${TRDP_COMPILE_DEFS})
    target_compile_options(${target} PRIVATE ${TRDP_COMPILE_OPTIONS})
    target_compile_features(${target} PRIVATE c_std_99)
    target_link_libraries(${target} PRIVATE ${lib})
endfunction()

if(TRDP_VOS_BACKEND STREQUAL "posix")
    if(TRDP_BUILD_EXAMPLES)
        trdp_add_executable(echoCallback example/echoCallback.c trdp)
        trdp_add_executable(receivePolling example/echoPolling.c trdp)
        trdp_add_executable(sendHello example/sendHello.c trdp)
        trdp_add_executable(receiveHello example/receiveHello.c trdp)
        trdp_add_executable(sendData example/sendData.c trdp)
        trdp_add_executable(sourceFiltering example/sourceFilter/sourceFiltering.c trdp)
    endif()

    if(TRDP_BUILD_TESTS)
        trdp_add_executable(getStats test/diverse/getStats.c trdp)
        trdp_add_executable(test_mdSingle test/diverse/test_mdSingle.c trdp)
        trdp_add_executable(inaugTest test/diverse/inaugTest.c trdp)
        trdp_add_executable(trdp-pd-test test/pdpatterns/trdp-pd-test.c trdp)
        trdp_add_executable(pd_responder test/diverse/pd_responder.c trdp)
        trdp_add_executable(testSub test/diverse/subTest.c trdp)
        trdp_add_executable(trdp-md-test test/mdpatterns/trdp-md-test.c trdp)
        trdp_add_executable(trdp-md-test-fast test/mdpatterns/trdp-md-test-fast.c trdp)
        trdp_add_executable(trdp-md-reptestcaller test/mdpatterns/rep-testcaller.c trdp)
        trdp_add_executable(trdp-md-reptestreplier test/mdpatterns/rep-testreplier.c trdp)
    endif()

    if(TRDP_BUILD_XML_TOOLS)
        trdp_add_executable(trdp-xmlprint-test test/xml/trdp-xmlprint-test.c trdpap)
        trdp_add_executable(trdp-xmlpd-test test/xml/trdp-xmlpd-test.c trdpap)
    endif()

    if(TRDP_BUILD_MARSHALLING_TESTS)
        trdp_add_executable(test_marshalling test/marshalling/test_marshalling.c trdpap)
    endif()
endif()

if(BUILD_TESTING AND TARGET test_marshalling)
    add_test(NAME marshalling_selftest COMMAND test_marshalling)
endif()

install(TARGETS trdp trdpap
    EXPORT TRDPStackTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(DIRECTORY src/api/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/trdp/api FILES_MATCHING PATTERN "*.h")
install(DIRECTORY src/vos/api/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/trdp/vos/api FILES_MATCHING PATTERN "*.h")

install(EXPORT TRDPStackTargets
    FILE TRDPStackTargets.cmake
    NAMESPACE TRDP::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/TRDPStack
)

configure_package_config_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/TRDPStackConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/TRDPStackConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/TRDPStack
)

write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/TRDPStackConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/TRDPStackConfig.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/TRDPStackConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/TRDPStack
)
