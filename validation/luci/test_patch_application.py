#!/usr/bin/env python3
"""Exercise the actual patch helper on a sparse temporary pinned Git clone."""
import argparse,json,shutil,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--luci',type=Path,default=ROOT/'feeds/6.18/luci')
args=parser.parse_args()
lock=json.loads((ROOT/'source-lock-3k.json').read_text())
sha=lock['upstream']['luci']['commit']
files=['modules/luci-base/Makefile','modules/luci-base/htdocs/luci-static/resources/luci.js']
def run(command,cwd=None,ok=True):
    p=subprocess.run(command,cwd=cwd,capture_output=True,text=True)
    if ok and p.returncode:raise AssertionError(p.stdout+p.stderr)
    return p
with tempfile.TemporaryDirectory(prefix='omr-luci-patch-') as directory:
    root=Path(directory);source=root/'feeds/luci';source.parent.mkdir()
    run(['git','clone','--shared','--no-checkout',str(args.luci.resolve()),str(source)])
    run(['git','sparse-checkout','init','--no-cone'],cwd=source)
    run(['git','sparse-checkout','set',*files],cwd=source)
    run(['git','checkout','--detach',sha],cwd=source)
    (root/'patches').mkdir()
    shutil.copyfile(ROOT/'patches/luci-features-startup-retry.patch',root/'patches/luci-features-startup-retry.patch')
    shutil.copyfile(ROOT/'apply-luci-startup-fix.py',root/'apply-luci-startup-fix.py')
    local={'upstream':{'luci':{'path':'feeds/luci','commit':sha}}}
    (root/'source-lock-3k.json').write_text(json.dumps(local))
    original={f:(source/f).read_bytes() for f in files}
    helper=[sys.executable,str(root/'apply-luci-startup-fix.py')]
    run(helper)
    assert b'firstLine' in (source/files[1]).read_bytes()
    assert b'PKG_SRC_VERSION:=26.210.61729~a3cc0e1-r1' in (source/files[0]).read_bytes()
    patched={f:(source/f).read_bytes() for f in files}
    run(helper)
    assert patched=={f:(source/f).read_bytes() for f in files},'Reapplication changed the source'
    local['upstream']['luci']['commit']='0'*40
    (root/'source-lock-3k.json').write_text(json.dumps(local))
    assert run(helper,ok=False).returncode!=0,'A different pinned HEAD must be rejected'
    local['upstream']['luci']['commit']=sha
    (root/'source-lock-3k.json').write_text(json.dumps(local))
    (source/files[0]).write_bytes(original[files[0]])
    assert run(helper,ok=False).returncode!=0,'A partially applied patch must fail closed'
    assert (source/files[1]).read_bytes()==patched[files[1]],'Failure altered the already patched JS'
print('PASS: actual helper applies on pristine pinned source, preserves repeat application, rejects HEAD drift and rejects partial application')
