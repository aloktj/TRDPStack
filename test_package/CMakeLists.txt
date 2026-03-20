cmake_minimum_required(VERSION 3.20)
project(test_package C)

include(CTest)
enable_testing()

find_package(TRDPStack CONFIG REQUIRED COMPONENTS trdp trdpap)

add_executable(test_package src/test_package.c)
target_link_libraries(test_package PRIVATE TRDP::trdp TRDP::trdpap)
add_test(NAME test_package COMMAND test_package)
