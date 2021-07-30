from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


# Adapted from https://github.com/bincrafters/conan-emsdk_installer
class EmscriptenConan(ConanFile):
    name = "emscripten-toolchain"
    description = "Emscripten is an Open Source LLVM to JavaScript compiler"
    url = "https://github.com/conan-burrito/emscripten-toolchain"
    homepage = "https://github.com/emscripten-core/emsdk"
    license = "MIT"
    settings = "os_build", "arch_build"
    short_paths = True

    def validate(self):
        if self.settings.os_build == 'Windows':
            raise ConanInvalidConfiguration("Couldn't make Windows builds work, sorry :(")

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "src")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        tools.get(**self.conan_data["sources"][self.version][str(self.settings.os_build)][str(self.settings.arch_build)],
                  destination=self._source_subfolder, strip_root=True)

    def _run(self, command):
        self.output.info(command)
        self.run(command)

    def _chmod_plus_x(self, filename):
        if self.settings.os_build in ['Macos', 'Linux']:
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def build(self):
        with tools.chdir(self._source_subfolder):
            self._do_build()

    def _exec_suffix(self, name):
        return ('%s.bat' % name) if self.settings.os_build == 'Windows' else ('./%s' % name)

    def _do_build(self):
        emsdk = self._exec_suffix('emsdk')
        if os.path.isfile("python_selector"):
            self._chmod_plus_x("python_selector")
        self._chmod_plus_x('emsdk')
        self._run('%s update' % emsdk)

        if os.path.isfile("python_selector"):
            self._chmod_plus_x("python_selector")
        self._chmod_plus_x('emsdk')

        self._run('%s list' % emsdk)
        self._run('%s install %s' % (emsdk, self.version))
        self._run('%s activate %s --embedded' % (emsdk, self.version))

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern='*', dst='.', src=self._source_subfolder)
        emsdk = self.package_folder
        emscripten = os.path.join(emsdk, 'upstream', 'emscripten')
        toolchain = os.path.join(emscripten, 'cmake', 'Modules', 'Platform', 'Emscripten.cmake')
        # allow to find conan libraries
        tools.replace_in_file(toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY BOTH)")
        tools.replace_in_file(toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE BOTH)")
        tools.replace_in_file(toolchain,
                              "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)",
                              "set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE BOTH)")

    def _define_tool_var(self, name, value):
        app_name = self._exec_suffix(value)
        path = os.path.join(self.package_folder, 'upstream', 'emscripten', app_name)
        self._chmod_plus_x(path)
        self.output.info('Creating %s environment variable: %s' % (name, path))
        return path


    def package_info(self):
        emsdk = self.package_folder
        em_config = os.path.join(emsdk, '.emscripten')
        emscripten = os.path.join(emsdk, 'upstream', 'emscripten')
        em_cache = os.path.join(emsdk, '.emscripten_cache')
        node_bin_dir = os.path.join(emsdk, next(os.walk(os.path.join(emsdk, 'node')))[1][0], 'bin')
        toolchain = os.path.join(emscripten, 'cmake', 'Modules', 'Platform', 'Emscripten.cmake')

        self.output.info('Appending PATH environment variable: %s' % emsdk)
        self.env_info.PATH.append(emsdk)

        self.output.info('Appending PATH environment variable: %s' % emscripten)
        self.env_info.PATH.append(emscripten)

        self.output.info('Appending PATH environment variable: %s' % node_bin_dir)
        self.env_info.PATH.append(node_bin_dir)

        self.output.info('Creating EMSDK environment variable: %s' % emsdk)
        self.env_info.EMSDK = emsdk

        self.output.info('Creating EMSCRIPTEN environment variable: %s' % emscripten)
        self.env_info.EMSCRIPTEN = emscripten

        self.output.info('Creating EM_CONFIG environment variable: %s' % em_config)
        self.env_info.EM_CONFIG = em_config

        self.output.info('Creating EM_CACHE environment variable: %s' % em_cache)
        self.env_info.EM_CACHE = em_cache

        self.output.info('Creating CONAN_CMAKE_TOOLCHAIN_FILE environment variable: %s' % toolchain)
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = toolchain

        self.env_info.CC = self._define_tool_var('CC', 'emcc')
        self.env_info.CXX = self._define_tool_var('CXX', 'em++')
        self.env_info.RANLIB = self._define_tool_var('RANLIB', 'emranlib')
        self.env_info.AR = self._define_tool_var('AR', 'emar')
