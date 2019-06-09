import os
import stat
from operator import add
from functools import reduce
from SCons.Action import ActionFactory

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

def _spike_action(target, source, env, for_signature):
    return ' '.join([
        os.path.join(os.environ['RISCV'], 'bin', 'spike'),
        '--isa=rv64imafd',
        '--extension=hwacha'
    ] + (['pk'] if env['SPIKE_PK'] else []) + [
        '$SOURCE.abspath'
    ] + env['SPIKE_ARGS'] + [
        '>', os.path.join(env['OUTPUT_DIR'], '${SOURCE.file}.out')
    ])

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
        SPIKE_PK=False,
        SPIKE_ARGS=[],
        BUILDERS={
            'Overlay': Builder(
                generator=_overlay_actions,
                emitter=_init_d_tgts),
            'Linux': Builder(
                generator=_linux_actions,
                emitter=_linux_srcs),
            'Spike': Builder(
                generator=_spike_action)
        })

    return env

def main():
    env = setup()
    env.SConscript(os.path.join('custom', 'SConscript'), exports='env')
    if os.path.isdir(env['SPEC2006_DIR']):
        env.SConscript(os.path.join('spec2006', 'SConscript'), exports='env')
    if os.path.isdir(env['SPEC2017_DIR']):
        env.SConscript(os.path.join('spec2017', 'SConscript'), exports='env')
    env.SConscript(os.path.join('hwacha-net', 'SConscript'), exports='env')
    env.Alias('clean', env.Command('#clean-linux', None, [
        ' '.join(['make', '-C', env['BUILDROOT_DIR'], 'clean']),
        ' '.join(['make', '-C', env['LINUX_DIR'], 'clean'])
    ]))
    env.Clean('all', [
        env['OVERLAY_DIR'], env['OUTPUT_DIR']
    ] + Glob(os.path.join('riscv-pk', 'build*')))

if __name__ == 'SCons.Script':
    main()
