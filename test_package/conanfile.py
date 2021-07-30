from conans import ConanFile, tools, CMake
import os


class TestPackage(ConanFile):
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        test_file = os.path.join(self.build_folder, "bin", "test_package.js")
        self.run('node --version', run_environment=True)
        self.run('node %s' % test_file, run_environment=True)
