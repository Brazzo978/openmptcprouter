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
def banned_image_package(name):
    # This Qualcomm kernel helper is needed by ath11k/ath12k Wi-Fi, not modem control.
    return name != "kmod-qcom-qmi-helpers" and bool(re.search(
        r"(modemmanager|luci-i18n-|^u(qmi|mbim)$|(^|[-_])(mbim|qmi|ncm|wwan)([-_]|$)|^mlvpn$)", name, re.I))
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

def maintenance_policy(catalog, groups):
    all_targets={row["target"] for rows in groups.values() for row in rows}
    require(catalog["boards"]==len(all_targets) and catalog["groups"]==
            {key:[row["target"] for row in rows] for key,rows in groups.items()},
            "catalog differs from pinned target matrix")
    policy=catalog["maintenance_policy"]
    require(policy["minimum_ram_mib"]==1024,"unexpected minimum RAM policy")
    decisions=policy["targets"]
    require(set(decisions)==all_targets,"hardware policy must classify every ARM target exactly once")
    for target,row in decisions.items():
        require(row.get("decision") in ("keep","drop","pending") and
                isinstance(row.get("reason"),str) and row["reason"].strip(),
                "invalid hardware policy decision: "+target)
        ram=row.get("ram_mib")
        require(ram is None or (type(ram) is int and ram>0) or
                (isinstance(ram,str) and re.fullmatch(r"[0-9]+(?:/[0-9]+)+",ram)),
                "invalid catalog RAM evidence: "+target)
        if row["decision"]=="keep" and ram is not None:
            options=[ram] if isinstance(ram,int) else [int(x) for x in ram.split("/")]
            require(min(options)>=policy["minimum_ram_mib"],
                    "kept target includes a sub-minimum RAM variant: "+target)
    deferred=catalog.get("deferred_targets",{})
    require(set(deferred)<=all_targets and all(isinstance(reason,str) and reason for reason in deferred.values()),
            "invalid deferred target catalog")
    candidates={target for target,row in decisions.items() if row["decision"]=="keep" and target not in deferred}
    require(catalog["build_candidates"]==len(candidates),"active build candidate count differs from hardware policy")
    return decisions,deferred,candidates

def requested_targets(targets, candidates):
    if targets is None:
        return set(candidates)
    require(len(targets)==len(set(targets)),"duplicate --targets ID")
    require(set(targets)<=candidates,
            "--targets must contain only active keep targets: "+", ".join(sorted(set(targets)-candidates)))
    return set(targets)

def policy_skip_record(target, platform, decision, previous=None):
    previous=previous or {}
    phase={"drop":"excluded_by_hardware_policy","pending":"pending_hardware_verification"}[decision["decision"]]
    record={"phase":phase,"boards":[target],"representative":target,"platform":platform,
            "reason":decision["reason"]}
    for field in ("previous_phase","previous_artifact_directory"):
        if field in previous:
            record[field]=previous[field]
    if previous.get("phase") not in (None,phase):
        record["previous_phase"]=previous["phase"]
        if previous.get("artifact_directory"):
            record["previous_artifact_directory"]=previous["artifact_directory"]
    return record

def nonbuild_record(target, platform, decision, deferred, selected, previous=None):
    previous=previous or {}
    if decision["decision"] in ("drop","pending"):
        return policy_skip_record(target,platform,decision,previous)
    if target in deferred:
        require(previous.get("phase")!="built_static_checks_passed",
                "cannot defer an already verified target")
        record={"phase":"deferred_requires_board_port","boards":[target],
                "representative":target,"platform":platform,"reason":deferred[target],
                "deferred_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
        if previous.get("error"):
            record["previous_failure"]={name:previous[name] for name in ("error","log","finished_utc") if name in previous}
        return record
    if target not in selected:
        require(previous.get("phase") in (None,"not_requested"),
                "previously processed target is outside the requested selection: "+target)
        return {"phase":"not_requested","boards":[target],
                "representative":target,"platform":platform}
    return None

def status_counts(state, expected_targets):
    require(set(state["targets"])==expected_targets,"queue status must account for every ARM target")
    statuses={"built_boards":"built_static_checks_passed","failed_boards":"failed",
              "deferred_boards":"deferred_requires_board_port",
              "excluded_boards":"excluded_by_hardware_policy",
              "pending_boards":"pending_hardware_verification","not_requested_boards":"not_requested"}
    counts={field:sum(record.get("phase")==phase for record in state["targets"].values())
            for field,phase in statuses.items()}
    require(sum(counts.values())==len(expected_targets),"queue contains unfinished or unknown target status")
    return counts


def verify_completed_artifacts(record, expected_directory=None, target=None, platform=None, state=None):
    out=Path(record["artifact_directory"]).resolve(strict=True)
    if expected_directory is not None:
        require(out==expected_directory.resolve(),"completed artifact belongs to another job or target")
    proof=json.loads((out/"artifact-manifest.json").read_text())
    require(proof.get("passed") and proof.get("static_checks_only"),"completed artifact proof missing")
    if target is not None:
        require(proof.get("boards")==[target] and proof.get("platform")==platform,
                "completed artifact belongs to another board or platform")
        for field in ("build_root_commit","openwrt_commit","feed_commit"):
            require(proof.get(field)==state.get(field),"completed artifact provenance changed: "+field)
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
    catalog=json.loads((root/"arm-targets-3k.json").read_text())
    decisions,approved_deferred,_=maintenance_policy(catalog,groups)
    archive_root=job/"cache-archives"
    archive_root.mkdir(mode=0o700,exist_ok=True)
    for platform,rows in groups.items():
        phases=[state["targets"].get(row["target"],{}).get("phase") for row in rows]
        for row in rows:
            target=row["target"]
            record=state["targets"].get(target,{})
            phase=record.get("phase")
            if phase=="deferred_requires_board_port":
                require(target in approved_deferred and decisions[target]["decision"]=="keep" and
                        record.get("reason")==approved_deferred[target],
                        "unapproved deferred status cannot authorize cache retirement")
            if phase in ("excluded_by_hardware_policy","pending_hardware_verification"):
                decision=decisions[target]
                expected={"drop":"excluded_by_hardware_policy","pending":"pending_hardware_verification"}.get(decision["decision"])
                require(phase==expected and record.get("reason")==decision["reason"],
                        "unapproved hardware skip cannot authorize cache retirement")
            if phase=="built_static_checks_passed":
                require(decisions[target]["decision"]=="keep" and target not in approved_deferred,
                        "excluded or deferred target cannot authorize cache retirement as built")
        terminal=("built_static_checks_passed","deferred_requires_board_port",
                  "excluded_by_hardware_policy","pending_hardware_verification")
        if platform==active or not all(phase in terminal for phase in phases) or "built_static_checks_passed" not in phases:
            continue
        directories=list(cache_root.glob("target-*/linux-"+platform))
        if directories:
            for row in rows:
                if state["targets"][row["target"]]["phase"]=="built_static_checks_passed":
                    target=row["target"]
                    verify_completed_artifacts(state["targets"][target],job/"artifacts"/target,
                                               target,platform,state)
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
    p.add_argument("--targets",nargs="+",metavar="OMR_TARGET",
                   help="build only these active keep IDs; all other IDs remain recorded explicitly")
    a=p.parse_args()
    root=a.root.resolve(strict=True)
    source=root/"shared-arm/6.18/source"
    require(source.is_dir() and (source/".git").exists(), "shared pinned OpenWrt source missing")
    require(1<=a.jobs<=20, "jobs must be 1..20")
    groups=matrix(root)
    catalog=json.loads((root/"arm-targets-3k.json").read_text())
    decisions,deferred,candidates=maintenance_policy(catalog,groups)
    selected=requested_targets(a.targets,candidates)
    if a.list:
        print(json.dumps({"groups":groups,"build_candidates":len(candidates),
                          "requested_targets":sorted(selected),"maintenance_policy":catalog["maintenance_policy"]},indent=2));return
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
        "requested_targets":sorted(selected),
        "targets":{}}
    require(state["build_root_commit"]==root_commit and state["feed_commit"]==lock_data["client_feed_release"]["commit"], "resume provenance changed; use a new job directory")
    require(state.get("requested_targets")==sorted(selected),"requested targets changed; use a new job directory")
    def save():
        state["updated_utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
        temp=job/"status.json.tmp";temp.write_text(json.dumps(state,indent=2)+"\n")
        temp.replace(status_file)
    state["phase"]="running";state["build_candidates"]=len(candidates);save()
    env=dict(os.environ,FORCE_UNSAFE_CONFIGURE="1",OMR_JOBS=str(a.jobs))
    queue=[]
    for platform in ORDER:
        preferred=PREFERRED.get(platform)
        queue.extend((platform,[row]) for row in sorted(groups[platform],key=lambda x:(x["target"]!=preferred,x["target"])))
    require(len(queue)==44,"44 independent board builds required")
    all_targets={row["target"] for _,rows in queue for row in rows}
    require(all_targets==set(decisions),"queue differs from hardware policy")
    # Normalize policy exclusions before any cache cleanup, including on resume.
    for key,rows in queue:
        target=rows[0]["target"]
        record=nonbuild_record(target,key,decisions[target],deferred,selected,
                               state["targets"].get(target))
        if record is not None:
            state["targets"][target]=record
    save()
    for key,rows in queue:
        representative=rows[0]["target"]
        previous=state["targets"].get(representative,{})
        if decisions[representative]["decision"] in ("drop","pending") or representative in deferred or representative not in selected:
            continue
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
                require(not any(banned_image_package(name) for name in packages),"banned package in installed image manifest")

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
                   "maintenance_policy":{"minimum_ram_mib":catalog["maintenance_policy"]["minimum_ram_mib"],
                                         "target":representative,**decisions[representative]},
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
    state.update(status_counts(state,all_targets))
    state["ready_to_publish"]=False
    state["next_step"]="Review failures, verify installed UI/source parity, run available ARM64 boot tests, then package and publish"
    save()
    print(json.dumps({"built_boards":state["built_boards"],"failed_boards":state["failed_boards"],
                      "deferred_boards":state["deferred_boards"],"excluded_boards":state["excluded_boards"],
                      "pending_boards":state["pending_boards"],"not_requested_boards":state["not_requested_boards"],
                      "ready_to_publish":False}),flush=True)
if __name__=="__main__":
    main()
