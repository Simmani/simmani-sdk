import os
import stat
from operator import add
from functools import reduce
from SCons.Action import ActionFactory

def _change_overlay(target, source, overlay):
    with open(target, 'w') as _t, open(source, 'r') as _s:
        for line in _s:
            if 'BR2_ROOTFS_OVERLAY' in line:
                _t.write('BR2_ROOTFS_OVERLAY="../%s"\n' % overlay)
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
    lambda target, text: 'WriteText("%s", "%s")' % (target, text))

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
        [
            Mkdir(t.dir.abspath),
            Copy(t.abspath, s.abspath),
        ]
        for t, s in zip(target, source)
    ])

def _bbl_actions(source, target, env, for_signature):
    build = os.path.join('riscv-pk', 'build-' + env['SUFFIX'])
    return [
        Delete(build),
        Mkdir(build),
        ' '.join([
            'cd', build, '&&',
            '../configure',
            '--prefix=' + env['ENV']['RISCV'],
            '--host=riscv64-unknown-elf',
            '--with-payload=' + source[0].abspath
        ]),
        ' '.join([
            'cd', build, '&&', 'make'
        ]),
        Copy(target[0].abspath, os.path.join(build, 'bbl'))
    ]

def init():
    return Environment(
        ENV=os.environ,
        BUILDERS={
            'Overlay': Builder(
                generator=_overlay_actions,
                emitter=_init_d_tgts),
            'BBL': Builder(
                generator=_bbl_actions)
        })

def build_linux(env, suffix, overlay_dir, overlay_files):
    # Config
    buildroot_config = env.Command(
        os.path.join('buildroot', '.config'),
        'buildroot-config',
        ChangeOverlay('$TARGET', '$SOURCE', overlay_dir))

    buildroot_oldconfig = env.Command(
        os.path.join('buildroot', '.config.old'),
        buildroot_config,
        ' '.join(['make', '-C', 'buildroot', 'oldconfig']))

    linux_config = env.Command(
        os.path.join('linux', '.config'),
        'linux-config',
        Copy('$TARGET', '$SOURCE'))

    linux_oldconfig = env.Command(
        os.path.join('linux', '.config.old'),
        linux_config,
        ' '.join(['make', '-C', 'linux', 'ARCH=riscv', 'oldconfig']))

    # Build
    initramfs = env.Command(
        os.path.join('buildroot', 'output', 'images', 'rootfs.cpio'),
        [buildroot_oldconfig] + overlay_files,
        ' '.join(['make', '-C', 'buildroot', '-j1']))
    env.SideEffect('#build', initramfs)

    vmlinux = env.Command(
        os.path.join('linux', 'vmlinux'),
        linux_oldconfig + initramfs,
        ' '.join(['make', '-C', '$TARGET.dir', '-j', 'ARCH=riscv', '$TARGET.file']))
    env.SideEffect('#build', vmlinux)

    if not os.path.exists('outputs'):
        Execute(Mkdir('outputs'))
    bblvmlinux = env.BBL(
        os.path.join('outputs', 'bblvmlinux-' + suffix), vmlinux, SUFFIX=suffix)
    env.SideEffect('#build', bblvmlinux)
    return bblvmlinux

def build_hello(env):
    env.VariantDir(os.path.join('hello', 'hello'), 'hello', duplicate=0)
    env['CC'] = os.path.join(env['ENV']['RISCV'], 'bin', 'riscv64-unknown-elf-gcc')
    hello = env.Program(os.path.join('hello', 'hello', 'hello.c'))
    overlay_dir = os.path.join('overlays', 'hello') 
    overlay_files = env.Overlay(
        [
            os.path.join(overlay_dir, 'root', t.name)
            for t in hello
        ],
        hello,
        OVERLAY=overlay_dir,
        rcS='\n'.join(['#!/bin/sh', '/root/hello', 'poweroff']))
    env.Alias('hello', build_linux(env, 'hello', overlay_dir, overlay_files))

def main():
    env = init()
    build_hello(env.Clone())

if __name__ == 'SCons.Script':
    main()
