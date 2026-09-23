# -*- coding: utf-8 -*-
"""
打包 com.qweather.widget fpk（与服务端解包器兼容的格式）
用法: python build_fp.py
产物: com.qweather.widget-<version>-x86.fpk
"""
import io
import os
import tarfile
import hashlib
import gzip

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'fpk')
APP_DIR = os.path.join(SRC, 'app')

SKIP_NAMES = {'__pycache__'}
SKIP_SUFFIX = ('.pyc', '.pyo')


def should_skip(name):
    if name in SKIP_NAMES:
        return True
    if name.endswith(SKIP_SUFFIX):
        return True
    return False


def build_app_tgz():
    """app.tgz：目录条目(DIRTYPE, 带尾斜杠)先于其内容，否则服务端解包成 0 字节文件"""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz', compresslevel=6) as tar:
        base = APP_DIR
        entries = []  # (relpath_with_slash_for_dirs, abspath, isdir)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if not should_skip(d))
            filenames = sorted(f for f in filenames if not should_skip(f))
            rel_dir = os.path.relpath(dirpath, base).replace(os.sep, '/')
            for d in dirnames:
                ap = os.path.join(dirpath, d)
                rel = d if rel_dir == '.' else rel_dir + '/' + d
                entries.append((rel + '/', ap, True))
            for f in filenames:
                ap = os.path.join(dirpath, f)
                rel = f if rel_dir == '.' else rel_dir + '/' + f
                entries.append((rel, ap, False))

        # 目录必须先于其下内容
        entries.sort(key=lambda e: (not e[2], e[0]))
        for arc, ap, isdir in entries:
            ti = tarfile.TarInfo(arc)
            if isdir:
                ti.type = tarfile.DIRTYPE
                ti.mode = 0o755
                ti.mtime = 0
                tar.addfile(ti)
            else:
                with open(ap, 'rb') as fh:
                    data = fh.read()
                ti.type = tarfile.REGTYPE
                ti.size = len(data)
                ti.mode = 0o755 if os.access(ap, os.X_OK) else 0o644
                ti.mtime = 0
                tar.addfile(ti, io.BytesIO(data))
    return buf.getvalue()


def parse_source_manifest(path):
    fields = []
    with open(path, 'rb') as f:
        raw = f.read().decode('utf-8')
    for line in raw.replace('\r\n', '\n').split('\n'):
        line = line.strip()
        if not line or line.startswith(';') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        fields.append((k.strip(), v.strip()))
    return fields


def build_manifest(fields, checksum):
    # 去掉源中可能存在的 checksum，追加新的
    fields = [(k, v) for k, v in fields if k != 'checksum']
    fields.append(('checksum', checksum))
    out = io.BytesIO()
    for k, v in fields:
        line = k.ljust(27) + '= ' + v
        out.write(line.encode('utf-8') + b'\r\n')
    return out.getvalue()


def add_regular(tar, arc, data, mode=0o644):
    ti = tarfile.TarInfo(arc)
    ti.type = tarfile.REGTYPE
    ti.size = len(data)
    ti.mode = mode
    ti.mtime = 0
    tar.addfile(ti, io.BytesIO(data))


def main():
    app_tgz = build_app_tgz()
    checksum = hashlib.md5(app_tgz).hexdigest()
    fields = parse_source_manifest(os.path.join(SRC, 'manifest'))
    version = dict(fields)['version']
    manifest = build_manifest(fields, checksum)

    def read(rel):
        with open(os.path.join(SRC, rel), 'rb') as f:
            return f.read()

    out_path = os.path.join(ROOT, f'com.qweather.widget-{version}-x86.fpk')
    with tarfile.open(out_path, 'w:gz', compresslevel=6) as tar:
        add_regular(tar, 'app.tgz', app_tgz)
        for name in sorted(os.listdir(os.path.join(SRC, 'cmd'))):
            add_regular(tar, f'cmd/{name}', read(f'cmd/{name}'), 0o755)
        for name in sorted(os.listdir(os.path.join(SRC, 'config'))):
            add_regular(tar, f'config/{name}', read(f'config/{name}'))
        add_regular(tar, 'ICON.PNG', read('ICON.PNG'))
        add_regular(tar, 'ICON_256.PNG', read('ICON_256.PNG'))
        add_regular(tar, 'manifest', manifest)
        wpath = os.path.join(SRC, 'wizard')
        for name in sorted(os.listdir(wpath)):
            add_regular(tar, f'wizard/{name}', read(f'wizard/{name}'), 0o755)

    print(f'built: {out_path} ({os.path.getsize(out_path)} bytes)')
    print(f'app.tgz md5: {checksum}')

    # 自检：重新解开确认目录条目
    with tarfile.open(out_path, 'r:gz') as t:
        inner = t.extractfile('app.tgz').read()
    with tarfile.open(fileobj=io.BytesIO(inner)) as t:
        bad = [m.name for m in t.getmembers()
               if m.isdir() and m.type != tarfile.DIRTYPE]
        assert not bad, bad
    print('self-check OK')


if __name__ == '__main__':
    main()
