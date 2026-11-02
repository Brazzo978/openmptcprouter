#!/usr/bin/env python3
"""Apply the tracked startup fix only to the pinned LuCI checkout, idempotently."""
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
row=json.loads((ROOT/'source-lock-3k.json').read_text())['upstream']['luci']
source=ROOT/row['path']
actual=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
if actual != row['commit']:
    raise SystemExit('LuCI startup fix refused: source HEAD differs from the lock')
patch=ROOT/'patches/luci-features-startup-retry.patch'
base=['patch','--batch','-p1','--input',str(patch)]
reverse=subprocess.run(base+['--dry-run','--reverse'],cwd=source,capture_output=True,text=True)
if reverse.returncode==0:
    print('3K LuCI startup fix already present')
else:
    subprocess.run(base+['--dry-run','--forward'],cwd=source,check=True)
    subprocess.run(base+['--forward'],cwd=source,check=True)
    print('3K LuCI startup fix applied to pinned source')
