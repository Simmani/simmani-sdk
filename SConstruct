import os
import stat
from operator import add
from functools import reduce
from SCons.Action import ActionFactory

def _tool_actions(source, target, env, for_signature):
    def build_project(project, flags=None):
        build = os.path.join('esp-tools', project, 'build')
        return ([
            Mkdir(build)
        ] if not os.path.isdir(build) else []) + [
            ' '.join([
                'cd', build, '&&', '../configure',
                '--prefix=%s' % env['ENV']['RISCV']
            ] + (flags if flags else [])),
            ' '.join(['make', '-C', build]),
            ' '.join(['make', '-C', build, 'install'])
        ]
    return ([
        'git clone https://github.com/ucb-bar/esp-tools.git'
    ] if not os.path.isdir('esp-tools') else []) + [
        'cd esp-tools && git submodule update --init',
        'cd esp-tools/riscv-gnu-toolchain && '
        'git submodule init && '
        'git submodule update riscv-binutils-gdb && '
        'git submodule update riscv-gcc && '
        'git submodule update riscv-glibc && '
        'git submodule update riscv-newlib && '
        'git submodule update riscv-dejagnu',
        'cd esp-tools/riscv-gnu-toolchain/riscv-gcc && '
        'git checkout be9abee2aaa919ad8530336569d17b5a60049717',
        'cd esp-tools/riscv-tests && '
        'git remote add donggyu https://github.com/donggyukim/esp-tests.git ; '
        'git fetch donggyu && '
        'git checkout large-input && '
        'git submodule update --init '
    ] + \
    build_project('riscv-fesvr') + \
    build_project('riscv-isa-sim', ['--with-fesvr=%s' % env['ENV']['RISCV']]) + \
    build_project('riscv-gnu-toolchain', ['--with-arch=rv64imafd']) + \
    build_project('riscv-pk', ['--host=riscv64-unknown-elf']) + \
    build_project('riscv-tests', ['--prefix=%s/riscv64-unknown-elf' % env['ENV']['RISCV']]) + [
        ' '.join(['make', '-C', os.path.join('esp-tools', 'riscv-gnu-toolchain', 'build'), 'linux'])
    ]

def _change_overlay(target, source, overlay):
    with open(target, 'w') as _t, open(source, 'r') as _s:
        for line in _s:
            if 'BR2_ROOTFS_OVERLAY' in line:
                _t.write('BR2_ROOTFS_OVERLAY="%s"\n' % os.path.abspath(overlay))
            else:
                _t.write(line)

ChangeOverlay = ActionFactory(
    _change_overlay,
    lambda target, source, overlay:
    'ChangeOverlay("%s", "%s", %s")' % (target, source, overlay))

def _write_init(target, text):
    with open(target, 'w') as _f:
        _f.write(text)
    os.chmod(target, os.stat(target).st_mode | stat.S_IEXEC)

WriteInit = ActionFactory(
    _write_init,
    lambda target, text: 'WriteInit("%s", "%s")' % (target, text))

def _init_d_tgts(target, source, env):
    return target + [
        os.path.join(env['OVERLAY'], 'etc', 'init.d', 'rcS'),
        os.path.join(env['OVERLAY'], 'etc', 'init.d', 'rcK')
    ], source

def _overlay_actions(source, target, env, for_signature):
    init_d = os.path.join(env['OVERLAY'], 'etc', 'init.d')
    return [
        Delete(init_d),
        Mkdir(init_d),
        WriteInit(os.path.join(init_d, 'rcS'), env['rcS']),
        WriteInit(os.path.join(init_d, 'rcK'), '\n'.join([
            '#!/bin/sh', '# Do nothing']))
    ] + reduce(add, [
        ([
            Mkdir(t.dir.abspath)
        ] if os.path.isdir(t.dir.abspath) else []) + [
            Copy(t.abspath, s.abspath)
        ]
        for t, s in zip(target, source)
    ])

def _linux_srcs(target, source, env):
    return target, source + reduce(add, [
        [
            os.path.join(dirpath, f)
            for f in filenames if os.path.splitext(f)[1] in ['.c', '.S']
        ]
        for dirpath, _, filenames in os.walk(
            os.path.join('linux', 'arch', 'riscv'))
    ])

def _linux_actions(source, target, env, for_signature):
    buildroot_dir = os.path.abspath('buildroot')
    linux_dir = os.path.abspath('linux')
    build = os.path.abspath(os.path.join(
        'riscv-pk', 'build-%s' % target[0].name))
    return [
        # buildroot config
        Copy(os.path.join('buildroot', '.config'), source[0].abspath),
        ' '.join(['make', '-C', buildroot_dir, 'oldconfig']),
        # Build buildroot
        Delete(os.path.join('buildroot', 'output', 'target', 'root')),
        ' '.join(['make', '-C', buildroot_dir, '-j1']),
        # linux config
        Copy(os.path.join(linux_dir, '.config'), os.path.abspath('linux-config')),
        ' '.join(['make', '-C', linux_dir, 'ARCH=riscv', 'oldconfig']),
        # Build linux
        ' '.join(['make', '-C', linux_dir, '-j', 'ARCH=riscv', 'vmlinux']),
        # Build bbl
        Delete(build),
        Mkdir(build),
        ' '.join([
            'cd', build, '&&',
            '../configure',
            '--prefix=' + env['ENV']['RISCV'],
            '--host=riscv64-unknown-elf',
            '--with-payload=' + os.path.join(linux_dir, 'vmlinux'),
        ]),
        ' '.join(['cd', build, '&&', 'make'])
    ] + ([
        Mkdir(target[0].dir.abspath)
    ] if os.path.isdir(target[0].dir.abspath) else []) + [
        Copy(target[0].abspath, os.path.join(build, 'bbl'))
    ]

def setup():
    variables = Variables('config.py', ARGUMENTS)
    variables.AddVariables(
        ('SPEC2006_DIR', 'Directory path for SPEC2006', ''))
    overlay_dir = os.path.abspath('overlays')
    output_dir = os.path.abspath('outputs')
    env = Environment(
        variables=variables,
        ENV=os.environ,
        OVERLAY_DIR=overlay_dir,
        OUTPUT_DIR=output_dir,
        WRITE_INIT=WriteInit,
        BUILDERS={
            'Tools': Builder(
                generator=_tool_actions),
            'Overlay': Builder(
                generator=_overlay_actions,
                emitter=_init_d_tgts),
            'Linux': Builder(
                generator=_linux_actions,
                emitter=_linux_srcs),
            'Spike': Builder(
                action=' '.join([
                    'spike',
                    '--isa=rv64gc',
                    '--extension=hwacha',
                    '$SOURCE.abspath', '>',
                    os.path.join(output_dir, '${SOURCE.file}.out')
                ]))
        })

    return env

def build_bblvmlinux(env, suffix, overlay_dir, overlay_files):
    buildroot_config = env.Command(
        os.path.join(env['OUTPUT_DIR'], 'buildroot-config-' + suffix),
        'buildroot-config',
        ChangeOverlay('$TARGET', '$SOURCE', overlay_dir))
    env.Depends(buildroot_config, overlay_files)
    bblvmlinux = env.Linux(
        os.path.join('outputs', 'bblvmlinux-' + suffix),
        buildroot_config)
    env.SideEffect('#bblvmlinux', bblvmlinux)
    return bblvmlinux

def build_hello(env):
    env.VariantDir(os.path.join('hello', 'hello'), 'hello', duplicate=0)
    env['CC'] = os.path.join(env['ENV']['RISCV'], 'bin', 'riscv64-unknown-elf-gcc')
    hello = env.Program(os.path.join('hello', 'hello', 'hello.c'))
    overlay_dir = os.path.join(env['OVERLAY_DIR'], 'hello')
    overlay_files = env.Overlay(
        [
            os.path.join(overlay_dir, 'root', t.name)
            for t in hello
        ],
        hello,
        OVERLAY=overlay_dir,
        rcS='\n'.join(['#!/bin/sh', '/root/hello', 'poweroff']))
    env.Alias('hello', build_bblvmlinux(env, 'hello', overlay_dir, overlay_files))

def build_spec2006(env):
    spec2006 = env.SConscript(
        os.path.join('spec2006', 'SConscript'), exports='env')
    for suite, input_type in spec2006:
        for benchmark, binary in spec2006[suite, input_type]:
            bblvmlinux = build_bblvmlinux(
                env,
                '%s.%s' % (benchmark, input_type),
                os.path.abspath(os.path.join(binary.dir.abspath, '..')),
                [binary.abspath])
            env.Alias(
                'build-spec2006%s-%s' % (suite, input_type), bblvmlinux)
            env.Alias(
                'run-spec2006%s-%s' % (suite, input_type),
                env.Spike('#run-%s.%s' % (benchmark, input_type), bblvmlinux))

def main():
    env = setup()
    env.Alias('riscv-tools', env.Tools('#riscv-tools', None))
    build_hello(env.Clone())
    build_spec2006(env)

if __name__ == 'SCons.Script':
    main()
