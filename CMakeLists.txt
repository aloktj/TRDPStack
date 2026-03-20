cmake_minimum_required(VERSION 3.20)

project(TRDPStack C)

include(GNUInstallDirs)
include(CTest)
find_package(Threads REQUIRED)

option(TRDP_MD_SUPPORT "Enable Message Data support" ON)
option(TRDP_SOA_SUPPORT "Enable service-oriented API support" OFF)
option(TRDP_TSN_SUPPORT "Enable TSN support" OFF)
option(TRDP_PD_UNICAST_SUPPORT "Enable PD unicast support" OFF)
option(TRDP_HIGH_PERF_INDEXED "Enable indexed high-performance PD mode" OFF)
option(TRDP_HIGH_PERF_BASE2 "Use base-2 high-performance indexing" OFF)
option(TRDP_BUILD_EXAMPLES "Build example applications" ON)
option(TRDP_BUILD_TESTS "Build test applications" ON)
option(TRDP_BUILD_XML_TOOLS "Build XML-based tools requiring trdpap" ON)
option(TRDP_BUILD_MARSHALLING_TESTS "Build marshalling tests requiring trdpap" ON)
option(TRDP_ENABLE_DEBUG "Build with DEBUG instead of NO_DEBUG" OFF)

if(NOT CMAKE_C_COMPILER_ID STREQUAL "GNU")
    message(WARNING "This CMake conversion is tuned for GCC-compatible toolchains; current compiler is ${CMAKE_C_COMPILER_ID}.")
endif()

set(TRDP_COMMON_SOURCES
    src/common/trdp_pdcom.c
    src/common/trdp_utils.c
    src/common/tlp_if.c
    src/common/tlc_if.c
    src/common/trdp_stats.c
    src/vos/common/vos_utils.c
    src/vos/common/vos_mem.c
    src/vos/posix/vos_sock.c
    src/vos/posix/vos_thread.c
    src/vos/posix/vos_shared_mem.c
)

set(TRDP_OPTIONAL_SOURCES
    src/common/trdp_xml.c
    src/common/tau_xml.c
    src/common/tau_marshall.c
    src/common/tau_dnr.c
    src/common/tau_tti.c
    src/common/tau_ctrl.c
)

if(TRDP_MD_SUPPORT)
    list(APPEND TRDP_COMMON_SOURCES
        src/common/trdp_mdcom.c
        src/common/tlm_if.c
    )
endif()

if(TRDP_SOA_SUPPORT)
    list(APPEND TRDP_OPTIONAL_SOURCES src/common/tau_so_if.c)
endif()

if(TRDP_TSN_SUPPORT)
    list(APPEND TRDP_COMMON_SOURCES src/vos/posix/vos_sockTSN.c)
endif()

if(TRDP_HIGH_PERF_INDEXED)
    list(APPEND TRDP_COMMON_SOURCES src/common/trdp_pdindex.c)
endif()

set(TRDP_PUBLIC_INCLUDES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/api
    ${CMAKE_CURRENT_SOURCE_DIR}/src/vos/api
)

set(TRDP_PRIVATE_INCLUDES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/common
    ${CMAKE_CURRENT_SOURCE_DIR}/src/vos/posix
)

set(TRDP_COMPILE_DEFS
    LINUX
    POSIX
    HAS_UUID
)

if(TRDP_MD_SUPPORT)
    list(APPEND TRDP_COMPILE_DEFS MD_SUPPORT=1)
else()
    list(APPEND TRDP_COMPILE_DEFS MD_SUPPORT=0)
endif()

if(TRDP_SOA_SUPPORT)
    list(APPEND TRDP_COMPILE_DEFS SOA_SUPPORT)
endif()

if(TRDP_TSN_SUPPORT)
    list(APPEND TRDP_COMPILE_DEFS TSN_SUPPORT RT_THREADS)
endif()

if(TRDP_PD_UNICAST_SUPPORT)
    list(APPEND TRDP_COMPILE_DEFS PD_UNICAST_SUPPORT)
endif()

if(TRDP_HIGH_PERF_INDEXED)
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
    -Wno-int-to-void-pointer-cast
    -Wno-self-assign
    -fstrength-reduce
    -fno-builtin
    -fsigned-char
    -fPIC
    -D_GNU_SOURCE
)

add_library(trdp STATIC ${TRDP_COMMON_SOURCES})
add_library(TRDP::trdp ALIAS trdp)

target_include_directories(trdp
    PUBLIC ${TRDP_PUBLIC_INCLUDES}
    PRIVATE ${TRDP_PRIVATE_INCLUDES}
)

target_compile_definitions(trdp PUBLIC ${TRDP_COMPILE_DEFS})
target_compile_options(trdp PRIVATE ${TRDP_COMPILE_OPTIONS})
target_link_libraries(trdp PUBLIC Threads::Threads uuid rt)

target_compile_features(trdp PRIVATE c_std_99)
set_target_properties(trdp PROPERTIES OUTPUT_NAME trdp)

add_library(trdpap STATIC ${TRDP_COMMON_SOURCES} ${TRDP_OPTIONAL_SOURCES})
add_library(TRDP::trdpap ALIAS trdpap)

target_include_directories(trdpap
    PUBLIC ${TRDP_PUBLIC_INCLUDES}
    PRIVATE ${TRDP_PRIVATE_INCLUDES}
)

target_compile_definitions(trdpap PUBLIC ${TRDP_COMPILE_DEFS})
target_compile_options(trdpap PRIVATE ${TRDP_COMPILE_OPTIONS})
target_link_libraries(trdpap PUBLIC Threads::Threads uuid rt)
target_compile_features(trdpap PRIVATE c_std_99)
set_target_properties(trdpap PROPERTIES OUTPUT_NAME trdpap)

function(trdp_add_executable target source lib)
    add_executable(${target} ${source})
    target_include_directories(${target} PRIVATE ${TRDP_PUBLIC_INCLUDES} ${TRDP_PRIVATE_INCLUDES})
    target_compile_definitions(${target} PRIVATE ${TRDP_COMPILE_DEFS})
    target_compile_options(${target} PRIVATE ${TRDP_COMPILE_OPTIONS})
    target_link_libraries(${target} PRIVATE ${lib})
    target_compile_features(${target} PRIVATE c_std_99)
endfunction()

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

if(BUILD_TESTING AND TARGET test_marshalling)
    add_test(NAME marshalling_selftest COMMAND test_marshalling)
endif()

install(TARGETS trdp trdpap
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(FILES
    src/api/trdp_if_light.h
    src/api/trdp_types.h
    src/api/iec61375-2-3.h
    src/vos/api/vos_sock.h
    src/vos/api/vos_types.h
    src/vos/api/vos_thread.h
    src/vos/api/vos_mem.h
    src/vos/api/vos_shared_mem.h
    src/vos/api/vos_utils.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/trdp
)
