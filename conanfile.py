from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy
import os


class TrdpStackConan(ConanFile):
    name = "trdpstack"
    version = "0.1.0"
    package_type = "static-library"
    license = "MPL-2.0"
    url = "https://example.invalid/TRDPStack"
    description = "TCNOpen TRDP prototype stack packaged for CMake/Conan consumers"
    topics = ("trdp", "railway", "fieldbus", "stm32", "cmake", "conan")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "vos_backend": ["posix", "custom"],
        "md_support": [True, False],
        "soa_support": [True, False],
        "tsn_support": [True, False],
        "pd_unicast_support": [True, False],
        "high_perf_indexed": [True, False],
        "high_perf_base2": [True, False],
        "enable_debug": [True, False],
        "enable_pic": [True, False],
    }
    default_options = {
        "vos_backend": "posix",
        "md_support": True,
        "soa_support": False,
        "tsn_support": False,
        "pd_unicast_support": False,
        "high_perf_indexed": False,
        "high_perf_base2": False,
        "enable_debug": False,
        "enable_pic": True,
    }
    exports_sources = (
        "CMakeLists.txt",
        "cmake/*",
        "src/*",
        "example/*",
        "test/*",
        ".gitignore",
        "readme.txt",
    )

    def layout(self):
        cmake_layout(self)

    def validate(self):
        if self.options.tsn_support and self.options.vos_backend != "posix":
            raise ConanInvalidConfiguration("TSN support currently requires vos_backend=posix.")
        if self.options.vos_backend == "posix" and str(self.settings.os) not in {"Linux", "Macos", "FreeBSD"}:
            raise ConanInvalidConfiguration(
                "The posix backend is intended for POSIX-like hosts. Use vos_backend=custom for embedded targets such as STM32."
            )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TRDP_VOS_BACKEND"] = str(self.options.vos_backend)
        tc.variables["TRDP_MD_SUPPORT"] = self.options.md_support
        tc.variables["TRDP_SOA_SUPPORT"] = self.options.soa_support
        tc.variables["TRDP_TSN_SUPPORT"] = self.options.tsn_support
        tc.variables["TRDP_PD_UNICAST_SUPPORT"] = self.options.pd_unicast_support
        tc.variables["TRDP_HIGH_PERF_INDEXED"] = self.options.high_perf_indexed
        tc.variables["TRDP_HIGH_PERF_BASE2"] = self.options.high_perf_base2
        tc.variables["TRDP_ENABLE_DEBUG"] = self.options.enable_debug
        tc.variables["TRDP_ENABLE_PIC"] = self.options.enable_pic
        tc.variables["TRDP_BUILD_EXAMPLES"] = False
        tc.variables["TRDP_BUILD_TESTS"] = False
        tc.variables["TRDP_BUILD_XML_TOOLS"] = False
        tc.variables["TRDP_BUILD_MARSHALLING_TESTS"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "readme.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TRDPStack")

        common_includes = [
            os.path.join("include", "trdp", "api"),
            os.path.join("include", "trdp", "vos", "api"),
        ]

        trdp = self.cpp_info.components["trdp"]
        trdp.set_property("cmake_target_name", "TRDP::trdp")
        trdp.libs = ["trdp"]
        trdp.includedirs = common_includes
        trdp.defines = [f"MD_SUPPORT={1 if self.options.md_support else 0}"]

        trdpap = self.cpp_info.components["trdpap"]
        trdpap.set_property("cmake_target_name", "TRDP::trdpap")
        trdpap.libs = ["trdpap"]
        trdpap.includedirs = common_includes
        trdpap.defines = [f"MD_SUPPORT={1 if self.options.md_support else 0}"]

        if self.options.soa_support:
            trdp.defines.append("SOA_SUPPORT")
            trdpap.defines.append("SOA_SUPPORT")
        if self.options.tsn_support:
            trdp.defines.extend(["TSN_SUPPORT", "RT_THREADS"])
            trdpap.defines.extend(["TSN_SUPPORT", "RT_THREADS"])
        if self.options.pd_unicast_support:
            trdp.defines.append("PD_UNICAST_SUPPORT")
            trdpap.defines.append("PD_UNICAST_SUPPORT")
        if self.options.high_perf_indexed:
            trdp.defines.append("HIGH_PERF_INDEXED")
            trdpap.defines.append("HIGH_PERF_INDEXED")
        if self.options.high_perf_base2:
            trdp.defines.append("HIGH_PERF_BASE2")
            trdpap.defines.append("HIGH_PERF_BASE2")
        if self.options.enable_debug:
            trdp.defines.append("DEBUG")
            trdpap.defines.append("DEBUG")
        else:
            trdp.defines.append("NO_DEBUG")
            trdpap.defines.append("NO_DEBUG")

        if self.options.vos_backend == "posix":
            posix_defines = ["LINUX", "POSIX", "HAS_UUID"]
            trdp.defines.extend(posix_defines)
            trdpap.defines.extend(posix_defines)
            trdp.system_libs = ["pthread", "uuid", "rt"]
            trdpap.system_libs = ["pthread", "uuid", "rt"]
        else:
            trdp.defines.append("TRDP_CUSTOM_VOS")
            trdpap.defines.append("TRDP_CUSTOM_VOS")
