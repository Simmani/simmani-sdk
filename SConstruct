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
        'git remote add simmani https://github.com/Simmani/esp-tests.git ; '
        'git fetch simmani && '
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

def _write_commands(target, binary, command):
    with open(target, 'w') as _f, open(command, 'r') as _c:
        _f.write('#!/bin/sh\n')
        _f.write('cd /root\n')
        for line in _c:
            args = line[:line.rfind(' >')]
            _f.write('echo "Run: ./%s %s"\n' % (binary, args))
            _f.write('./%s %s\n' % (binary, args))
        _f.write('poweroff\n')
    os.chmod(target, os.stat(target).st_mode | stat.S_IEXEC)

WriteCommands = ActionFactory(
    _write_commands,
    lambda target, binary, command:
    'WriteCommands("%s", "%s", "%s")' % (target, binary, command))

def _linux_srcs(target, source, env):
    return target, source + reduce(add, [
        [
            os.path.join(dirpath, f)
            for f in filenames if os.path.splitext(f)[1] in ['.c', '.S']
        ]
        for dirpath, _, filenames in os.walk(
            os.path.join(env['LINUX_DIR'], 'arch', 'riscv'))
    ])

def _linux_actions(source, target, env, for_signature):
    build = os.path.abspath(os.path.join(
        env['RISCV_PK_DIR'], 'build-%s' % target[0].name))
    return [
        # buildroot config
        Copy(os.path.join(env['BUILDROOT_DIR'], '.config'), source[0].abspath),
        ' '.join(['make', '-C', env['BUILDROOT_DIR'], 'oldconfig']),
        # Build buildroot
        Delete(os.path.join(env['BUILDROOT_DIR'], 'output', 'target', 'root')),
        ' '.join(['make', '-C', env['BUILDROOT_DIR'], '-j1']),
        # linux config
        Copy(os.path.join(env['LINUX_DIR'], '.config'),
             os.path.join(env['BASE_DIR'], 'linux-config')),
        ' '.join(['make', '-C', env['LINUX_DIR'], 'ARCH=riscv', 'oldconfig']),
        # Build linux
        ' '.join(['make', '-C', env['LINUX_DIR'], '-j', 'ARCH=riscv', 'vmlinux']),
        # Build bbl
        Delete(build),
        Mkdir(build),
        ' '.join([
            'cd', build, '&&',
            '../configure',
            '--prefix=' + env['ENV']['RISCV'],
            '--host=riscv64-unknown-elf',
            '--with-payload=' + os.path.join(env['LINUX_DIR'], 'vmlinux'),
        ]),
        ' '.join(['cd', build, '&&', 'make'])
    ] + ([
        Mkdir(target[0].dir.abspath)
    ] if os.path.isdir(target[0].dir.abspath) else []) + [
        Copy(target[0].abspath, os.path.join(build, 'bbl'))
    ]

def build_bblvmlinux(env, suffix, overlay_dir, overlay_files):
    buildroot_config = env.Command(
        os.path.join(env['OUTPUT_DIR'], 'buildroot-config-' + suffix),
        os.path.join(env['BASE_DIR'], 'buildroot-config'),
        ChangeOverlay('$TARGET', '$SOURCE', overlay_dir))
    env.Depends(buildroot_config, overlay_files)
    bblvmlinux = env.Linux(
        os.path.join(env['OUTPUT_DIR'], 'bblvmlinux-' + suffix),
        buildroot_config)
    env.Depends(bblvmlinux, overlay_files)
    env.SideEffect('#bblvmlinux', bblvmlinux)
    return bblvmlinux

def setup():
    variables = Variables('config.py', ARGUMENTS)
    variables.AddVariables(
        ('SPEC2006_DIR', 'Directory path for SPEC2006', ''),
        ('SPEC2017_DIR', 'Directory path for SPEC2017', ''))
    overlay_dir = os.path.abspath('overlays')
    output_dir = os.path.abspath('outputs')
    env = Environment(
        variables=variables,
        ENV=os.environ,
        BASE_DIR=os.path.abspath(os.path.curdir),
        BUILDROOT_DIR=os.path.abspath('buildroot'),
        LINUX_DIR=os.path.abspath('linux'),
        RISCV_PK_DIR=os.path.abspath('riscv-pk'),
        OVERLAY_DIR=overlay_dir,
        OUTPUT_DIR=output_dir,
        WRITE_INIT=WriteInit,
        WRITE_COMMANDS=WriteCommands,
        BUILD_BBLVMLINUX=build_bblvmlinux,
        BUILDERS={
            'Tools': Builder(
                generator=_tool_actions),
            'Linux': Builder(
                generator=_linux_actions,
                emitter=_linux_srcs),
            'Spike': Builder(
                action=' '.join([
                    os.path.join(os.environ['RISCV'], 'bin', 'spike'),
                    '--isa=rv64imafd',
                    '--extension=hwacha',
                    '$SOURCE.abspath', '>',
                    os.path.join(output_dir, '${SOURCE.file}.out')
                ]))
        })

    return env

def main():
    env = setup()
    env.Alias('riscv-tools', env.Tools(
        '#riscv-tools', os.path.join('resources', 'build-riscv-tools.sh')))
    env.SConscript(os.path.join('custom', 'SConscript'), exports='env')
    env.SConscript(os.path.join('spec2006', 'SConscript'), exports='env')
    env.SConscript(os.path.join('spec2017', 'SConscript'), exports='env')
    env.Alias('clean', env.Command('#clean-linux', None, [
        ' '.join(['make', '-C', env['BUILDROOT_DIR'], 'clean']),
        ' '.join(['make', '-C', env['LINUX_DIR'], 'clean'])
    ]))
    env.Clean('all', [
        env['OVERLAY_DIR'], env['OUTPUT_DIR']
    ] + Glob(os.path.join('riscv-pk', 'build*')))

if __name__ == 'SCons.Script':
    main()
