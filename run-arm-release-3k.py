#!/usr/bin/env python3
"""Build the pinned 3K ARM matrix sequentially, with persistent status and artifacts."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ORDER = ["armsr_armv8", "rockchip_armv8", "bcm27xx_bcm2711", "bcm27xx_bcm2712",
         "mediatek_filogic", "bcm27xx_bcm2710", "bcm27xx_bcm2709",
         "mvebu_cortexa53", "mvebu_cortexa9", "mediatek_mt7622", "mediatek_mt7623",
         "ipq40xx_generic", "ipq806x_generic", "qualcommax_ipq807x", "sunxi_cortexa7"]
PREFERRED = {"armsr_armv8": "armsr64", "rockchip_armv8": "r4s",
             "mediatek_filogic": "bpi-r3", "mvebu_cortexa9": "wrt3200acm"}
def require(ok, message):
    if not ok:
        raise RuntimeError(message)
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()
def run(args, cwd, log, env=None):
    with log.open("ab") as f:
        return subprocess.run(args, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                              stdout=f, stderr=subprocess.STDOUT).returncode
def matrix(root):
    groups={}
    names=json.loads((root/"source-lock-3k.json").read_text())["supported_targets"]
    for target in names:
        if target=="x86_64":
            continue
        require(re.fullmatch("[a-z0-9][a-z0-9_-]*", target), "invalid target")
        template=root/("config-"+target)
        devices=re.findall(r"^CONFIG_TARGET_([^=\n]+_DEVICE_[^=\n]+)=y$",template.read_text(),re.M)
        require(len(devices)==1, "exactly one device required: "+target)
        key=devices[0].split("_DEVICE_")[0]
        groups.setdefault(key,[]).append({"target":target,"device":devices[0]})
    require(len(groups)==15 and sum(map(len,groups.values()))==44, "ARM matrix changed; review it")
    require(set(groups)==set(ORDER), "unexpected platform")
    return groups


def verify_completed_artifacts(record):
    out=Path(record["artifact_directory"]).resolve(strict=True)
    proof=json.loads((out/"artifact-manifest.json").read_text())
    require(proof.get("passed") and proof.get("static_checks_only"),"completed artifact proof missing")
    for item in proof["files"]:
        path=out/item["path"]
        require(path.resolve().is_relative_to(out) and path.is_file(),"completed artifact path missing or unsafe")
        require(path.stat().st_size==item["size"] and sha(path)==item["sha256"],"completed artifact hash mismatch: "+str(path))
    require(bool(proof["files"]),"empty completed artifact manifest")

def overlay_untracked_files(source):
    names=subprocess.check_output(["git","ls-files","--others","--exclude-standard","-z"],cwd=source).split(b"\0")
    files=[]
    for raw in names:
        if not raw:
            continue
        path=source/os.fsdecode(raw)
        if path.is_symlink():
            files.append({"path":os.fsdecode(raw),"symlink":os.readlink(path)})
        else:
            require(path.is_file(),"untracked source input missing")
            files.append({"path":os.fsdecode(raw),"size":path.stat().st_size,"sha256":sha(path)})
    return files


def retire_completed_kernels(root, source, job, groups, state, active):
    cache_root=(source/"build_dir").resolve()
    compressor=source/"staging_dir/host/bin/zstd"
    if not compressor.is_file():
        return
    archive_root=job/"cache-archives"
    archive_root.mkdir(mode=0o700,exist_ok=True)
    for platform,rows in groups.items():
        if platform==active or not all(state["targets"].get(row["target"],{}).get("phase")=="built_static_checks_passed" for row in rows):
            continue
        directories=list(cache_root.glob("target-*/linux-"+platform))
        if directories:
            for row in rows:
                verify_completed_artifacts(state["targets"][row["target"]])
        for directory in directories:
            require(directory.is_dir() and not directory.is_symlink() and directory.resolve().is_relative_to(cache_root),"unsafe cache archive path")
            archive=archive_root/(directory.parent.name+"--"+directory.name+".tar.zst")
            partial=archive.with_suffix(archive.suffix+".partial")
            require(not archive.exists() and not partial.exists(),"inspect existing kernel cache archive before retry")
            log=archive_root/(directory.parent.name+"--"+platform+".log")
            try:
                with log.open("wb") as output:
                    subprocess.run(["tar","--use-compress-program="+str(compressor)+" -T2 -3","-cf",str(partial),"-C",str(directory.parent),directory.name],stdout=output,stderr=subprocess.STDOUT,check=True)
                    subprocess.run([str(compressor),"--test",str(partial)],stdout=output,stderr=subprocess.STDOUT,check=True)
                    subprocess.run(["tar","--use-compress-program="+str(compressor),"-tf",str(partial)],stdout=subprocess.DEVNULL,stderr=output,check=True)
                    subprocess.run(["tar","--use-compress-program="+str(compressor),"--compare","-f",str(partial),"-C",str(directory.parent)],stdout=output,stderr=subprocess.STDOUT,check=True)
                partial.replace(archive)
                proof={"platform":platform,"archive":str(archive),"sha256":sha(archive),"size":archive.stat().st_size,"original_directory":str(directory),"verified_archive":True}
                record=archive.with_suffix(archive.suffix+".json")
                record.write_text(json.dumps(proof,indent=2)+"\n")
                require(directory.resolve().is_relative_to(cache_root) and not directory.is_symlink(),"cache path changed")
                shutil.rmtree(directory)
                proof["cache_removed_after_archive_verification"]=True
                record.write_text(json.dumps(proof,indent=2)+"\n")
            except Exception:
                if partial.exists():
                    partial.unlink()
                raise

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--job",type=Path,required=True)
    p.add_argument("--jobs",type=int,default=18)
    p.add_argument("--adopt-first-exit",type=Path)
    p.add_argument("--list",action="store_true")
    p.add_argument("--retry-failed",action="store_true")
    a=p.parse_args()
    root=a.root.resolve(strict=True)
    source=root/"shared-arm/6.18/source"
    require(source.is_dir() and (source/".git").exists(), "shared pinned OpenWrt source missing")
    require(1<=a.jobs<=20, "jobs must be 1..20")
    groups=matrix(root)
    if a.list:
        print(json.dumps(groups,indent=2));return
    job=a.job.resolve()
    job.mkdir(parents=True,exist_ok=True)
    require(job!=root and not job.is_relative_to(source), "job directory must be outside source")
    lock=(job/"queue.lock").open("w")
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    (job/"queue.pid").write_text(str(os.getpid())+"\n")
    status_file=job/"status.json"
    root_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
    lock_data=json.loads((root/"source-lock-3k.json").read_text())
    require(not subprocess.check_output(["git","status","--porcelain","--untracked-files=all"],cwd=root,text=True).strip(), "root changes must be committed or explicitly ignored")
    require(subprocess.check_output(["git","rev-parse","HEAD"],cwd=source,text=True).strip()==lock_data["upstream"]["openwrt"]["commit"], "OpenWrt source pin changed")
    state=json.loads(status_file.read_text()) if status_file.exists() else {
        "release":"v0.64.2-3K-arm","boards":44,"platform_groups":15,
        "build_root_commit":root_commit,
        "openwrt_commit":lock_data["upstream"]["openwrt"]["commit"],
        "feed_commit":json.loads((root/"source-lock-3k.json").read_text())["client_feed_release"]["commit"],
        "targets":{}}
    require(state["build_root_commit"]==root_commit and state["feed_commit"]==lock_data["client_feed_release"]["commit"], "resume provenance changed; use a new job directory")
    def save():
        state["updated_utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
        temp=job/"status.json.tmp";temp.write_text(json.dumps(state,indent=2)+"\n")
        temp.replace(status_file)
    state["phase"]="running";save()
    env=dict(os.environ,FORCE_UNSAFE_CONFIGURE="1",OMR_JOBS=str(a.jobs))
    queue=[]
    for platform in ORDER:
        preferred=PREFERRED.get(platform)
        queue.extend((platform,[row]) for row in sorted(groups[platform],key=lambda x:(x["target"]!=preferred,x["target"])))
    require(len(queue)==44,"44 independent board builds required")
    for key,rows in queue:
        representative=rows[0]["target"]
        previous=state["targets"].get(representative,{})
        if previous.get("phase")=="built_static_checks_passed" or (previous.get("phase")=="failed" and not a.retry_failed):
            continue
        record={"phase":"preparing","boards":[x["target"] for x in rows],"representative":representative,
                "started_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
        record["platform"]=key
        state["current"]=representative;state["targets"][representative]=record;save()
        out=job/"artifacts"/representative;out.mkdir(parents=True,exist_ok=True)
        log=job/(representative+".log")
        try:
            retire_completed_kernels(root,source,job,groups,state,key)
            require(shutil.disk_usage(root).free >= 15*1024**3, "less than 15 GiB free; stopping before disk exhaustion")
            adopted=representative=="armsr64" and a.adopt_first_exit is not None
            if adopted:
                a.adopt_first_exit=a.adopt_first_exit.resolve()
                require(a.adopt_first_exit.parent==job,"adopted build must belong to this job")
                adopted_config_sha=sha(source/".config")
                require("CONFIG_TARGET_armsr_armv8_DEVICE_generic=y" in (source/".config").read_text(),"adopted build target changed")
            if adopted:
                record["phase"]="building";record["log"]=str(job/"armsr64-build.log");record["adopted_config_sha256"]=adopted_config_sha;save()
                while not a.adopt_first_exit.exists():
                    time.sleep(15);save()
                require(a.adopt_first_exit.read_text().strip()=="0","initial ARM64 build failed; see armsr64-build.log")
                require(sha(source/".config")==adopted_config_sha,"adopted build configuration changed")
            else:
                env["OMR_TARGET"]=representative
                require(run(["./run-build-3k.sh","prepare"],root,log,env)==0,
                        "preparation failed; inspect "+str(log))
                # Isolate binary outputs to prevent stale images/APKs from another board.
                # The source, toolchains and downloaded sources are reused sequentially.
                binary=job/"binary-output"/representative
                binary.mkdir(parents=True,exist_ok=True)
                with (source/".config").open("a") as f:
                    f.write('\nCONFIG_BINARY_FOLDER="'+str(binary)+'"\n')
                require(run(["make","defconfig"],source,log,env)==0,"group defconfig failed")
                resolved=(source/".config").read_text()
                require('CONFIG_BINARY_FOLDER="'+str(binary)+'"' in resolved.splitlines(),"isolated binary output path missing after defconfig")
                for row in rows:
                    require("CONFIG_TARGET_"+row["device"]+"=y" in resolved,
                            "device absent from pinned OpenWrt: "+row["target"])
                require(run(["./validate-3k-config.sh",str(source),representative],root,log,env)==0,
                        "3K group configuration validation failed")
                record["phase"]="building";record["log"]=str(log);save()
                require(run(["make","-j"+str(a.jobs)],source,log,env)==0,"strict firmware build failed")
            resolved=(source/".config").read_text()
            architecture=re.search(r'^CONFIG_TARGET_ARCH_PACKAGES="([^"]+)"$',resolved,re.M).group(1)
            board,subtarget=key.split("_",1)
            arch_parts=architecture.split("_",2)
            build_arch="_".join(arch_parts[:2])+("+"+arch_parts[2] if len(arch_parts)==3 else "")
            binary_match=re.search(r'^CONFIG_BINARY_FOLDER="([^"]+)"$',resolved,re.M)
            output_root=Path(binary_match.group(1)) if binary_match else source/"bin"
            if not adopted:
                require(output_root==job/"binary-output"/representative,"isolated binary output path changed during build")
            output=output_root/"targets"/board/subtarget
            require(output.is_dir(),"target output directory missing")
            profiles=json.loads((output/"profiles.json").read_text())["profiles"]
            for row in rows:
                device=row["device"].split("_DEVICE_",1)[1]
                require(device in profiles and bool(profiles[device].get("images")),
                        "firmware images missing for "+row["target"])
                for image in profiles[device]["images"]:
                    path=output/image["name"]
                    require(path.is_file() and path.stat().st_size>0,"profile image file missing: "+image["name"])
                    if image.get("sha256"):
                        require(sha(path)==image["sha256"],"profile image hash mismatch: "+image["name"])

            roots=list((source/"build_dir").glob("target-"+build_arch+"_*/root-"+board))
            require(len(roots)==1,"one installed root filesystem expected")
            installed=roots[0]
            required=["usr/bin/speedtest","usr/bin/btop","usr/sbin/mqvpn",
                      "usr/libexec/omr-diagnostic-log","etc/init.d/omr-diagnostic-log",
                      "usr/share/omr/diagnostic.lua",
                      "www/luci-static/resources/view/openmptcprouter/wizard.js",
                      "www/luci-static/resources/view/mptcp/mptcp_monitor.js",
                      "www/luci-static/resources/view/mptcp/multipath.js"]
            for path in required:
                require((installed/path).is_file(),"required installed file missing: "+path)
            machine=183 if architecture.startswith("aarch64_") else 40
            for path in ("usr/bin/speedtest","usr/bin/btop","usr/sbin/mqvpn"):
                with (installed/path).open("rb") as binary_file:
                    data=binary_file.read(20)
                require(data[:4]==b"\x7fELF" and data[5]==1 and int.from_bytes(data[18:20],"little")==machine,
                        "wrong executable architecture: "+path)
            schedulers=sorted((installed/"usr/share/bpf/scheduler").glob("mptcp_bpf_*.o"))
            require(len(schedulers)==8,"eight compiled BPF schedulers required")
            kernels=list((source/"build_dir").glob("target-"+build_arch+"_*/linux-"+key+"/linux-6.18.39/.config"))
            require(len(kernels)==1,"built kernel config missing")
            kernel=kernels[0].read_text()
            controls=["BBR","BBR1","BBR2","NANQINLANG","CUBIC"]+[
                "NANBBR"+version+"_"+variant for version in ("1","2","3")
                for variant in ("LIGHT","DEF","AGGR","VAR")]
            for control in controls:
                require("CONFIG_TCP_CONG_"+control+"=y" in kernel,"kernel congestion control missing: "+control)
            require('CONFIG_DEFAULT_TCP_CONG="bbr"' in kernel,"kernel default must be BBRv3")
            symbols=subprocess.check_output(["readelf","--symbols",str(kernels[0].parent/"vmlinux")],text=True)
            require(any(line.split() and line.split()[-1]=="tcp_reno" for line in symbols.splitlines()),"built-in Reno symbol missing")
            for manifest in output.glob("*.manifest"):
                packages={line.split()[0] for line in manifest.read_text().splitlines() if line.split()}
                require(not any(re.search(r"(modemmanager|luci-i18n-|(^|[-_])(mbim|qmi|ncm|wwan)([-_]|$)|^mlvpn$)",name,re.I) for name in packages),"banned package in installed image manifest")

            shutil.copytree(output,out/"firmware",dirs_exist_ok=True)
            package_source=output_root/"packages"/architecture
            require(package_source.is_dir(),"APK repositories missing")
            shutil.copytree(package_source,out/"packages",dirs_exist_ok=True)
            keys=installed/"etc/apk/keys"
            for path in keys.iterdir():
                data=path.read_bytes()
                require(b"PUBLIC KEY" in data and b"PRIVATE" not in data,"public signing keys only")
            shutil.copytree(keys,out/"public-keys",dirs_exist_ok=True)
            shutil.copyfile(source/".config",out/"build.config")
            shutil.copyfile(kernels[0],out/"kernel.config")
            files=[{"path":p.relative_to(out).as_posix(),"size":p.stat().st_size,"sha256":sha(p)}
                   for p in sorted(out.rglob("*")) if p.is_file() and p.name!="artifact-manifest.json"]
            proof={"passed":True,"static_checks_only":True,"hardware_boot_tested":False,
                   "platform":key,"architecture":architecture,"boards":record["boards"],
                   "build_root_commit":state["build_root_commit"],"openwrt_commit":state["openwrt_commit"],"feed_commit":state["feed_commit"],
                   "congestion_controls":len(controls)+1,"reno_builtin_symbol_verified":True,"bpf_schedulers":8,"source_lock":lock_data,"openwrt_overlay_diff_sha256":hashlib.sha256(subprocess.check_output(["git","diff","--binary","HEAD"],cwd=source)).hexdigest(),"untracked_openwrt_source_inputs":overlay_untracked_files(source),"files":files}
            (out/"artifact-manifest.json").write_text(json.dumps(proof,indent=2)+"\n")
            # Keep the verified release copy and remove only identical binary-output duplicates.
            duplicate_files=0
            for item in files:
                relative=Path(item["path"])
                if relative.parts[0]=="firmware":
                    original=output/Path(*relative.parts[1:])
                elif relative.parts[0]=="packages":
                    original=package_source/Path(*relative.parts[1:])
                else:
                    continue
                if original.is_file():
                    require(original.stat().st_size==item["size"] and sha(original)==item["sha256"],"output duplicate differs from verified artifact")
                    original.unlink()
                    duplicate_files+=1
            record["verified_output_duplicates_removed"]=duplicate_files
            record.update(phase="built_static_checks_passed",architecture=architecture,files=len(files),
                          artifact_directory=str(out),hardware_boot_tested=False)
        except Exception as exc:
            record.update(phase="failed",error=str(exc))
            print(representative+": "+str(exc),flush=True)
        record["finished_utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime());save()
    state["phase"]="build_queue_finished"
    state["built_boards"]=sum(x.get("phase")=="built_static_checks_passed" for x in state["targets"].values())
    state["failed_boards"]=sum(x.get("phase")=="failed" for x in state["targets"].values())
    state["ready_to_publish"]=False
    state["next_step"]="Review failures, verify installed UI/source parity, run available ARM64 boot tests, then package and publish"
    save()
    print(json.dumps({"built_boards":state["built_boards"],"failed_boards":state["failed_boards"],
                      "ready_to_publish":False}),flush=True)
if __name__=="__main__":
    main()
