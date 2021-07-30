from cpt.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager()

    def add_arch(arch: str):
        settings = {
            'os': 'Emscripten',
            'arch': arch,
            'compiler': 'clang',
            'compiler.version': '13.0',
            'compiler.libcxx': 'libc++',
        }
        builder.add(settings=settings)

    add_arch('arm.js')
    add_arch('wasm')

    builder.run()
