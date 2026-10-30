"""Historical baseline reproductions. No sockets, WANs, UCI or services are used.

Run with Linux Python (e.g. WSL). Shell dependencies and xquic calls are mocked;
the actual reviewed shell functions and C path-removal functions are extracted.
This establishes control flow, not end-to-end network availability or timings.
Source fingerprints deliberately refuse candidate sources after the fixes.
"""
import hashlib,json,os,re,subprocess,tempfile,time,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ.get('OMR3K_AUDIT_WORKSPACE',str(HERE.parents[2])))
BASE=Path(os.environ.get('OMR3K_AUDIT_OUTPUT',str(ROOT/'failover-audit-20261030')))
FEED=Path(os.environ.get('OMR3K_AUDIT_FEED',str(ROOT/'client-repo')))
MQVPN=Path(os.environ.get('OMR3K_AUDIT_MQVPN',str(ROOT/'mqvpn_engine/native-routing')))
API=FEED/'openmptcprouter/files/etc/init.d/openmptcprouter-vps'
TRACKER=FEED/'omr-tracker/files/bin/omr-tracker-server'
HOOK=FEED/'omr-tracker/files/usr/share/omr/post-tracking.d/005-mqvpn-path'
ENGINE=MQVPN/'src/mqvpn_client.c'

def shell_function(path,name):
    text=path.read_text(encoding='utf-8')
    match=re.search(r'^'+re.escape(name)+r'\(\) \{\n.*?^\}',text,re.M|re.S)
    assert match,name
    return match.group(0)

def c_function(text,name):
    match=re.search(r'\nint\n'+re.escape(name)+r'\([^;]*?\n\{',text,re.S)
    assert match,name
    start=match.start()+1; pos=match.end();depth=1
    while depth:
        if text[pos]=='{':depth+=1
        elif text[pos]=='}':depth-=1
        pos+=1
    return text[start:pos]

def run_shell(script,extra):
    with tempfile.TemporaryDirectory() as directory:
        env=dict(os.environ,TRACE=str(Path(directory)/'calls'),**extra)
        result=subprocess.run(['bash','-c',script],env=env,text=True,capture_output=True,timeout=8,check=True)
        trace=Path(env['TRACE']).read_text().splitlines() if Path(env['TRACE']).exists() else []
        return result.stdout.strip(),trace

STUBS=r'''
token=fixture-token; server=192.0.2.10; serverport=65500
valid_subnet6() { echo invalid; }
_login() { token=fixture-token; }
multipath() { printf '%s\n' "$MULTIPATH_ROWS"; }
curl() {
  local iface=auto prev='' arg
  for arg in "$@"; do
    [ "$prev" = --interface ] && iface="$arg"
    prev="$arg"
  done
  printf '%s\n' "$iface" >> "$TRACE"
  if [ "$iface" = ethB ]; then printf '%s' '{"ok":true}'; return 0; fi
  if [ "$iface" = auto ] && [ "${AUTO_RESPONSE:-}" != '' ]; then printf '%s' "$AUTO_RESPONSE"; return 0; fi
  return 28
}
sleep() { :; }
'''

class OfflineFailoverTests(unittest.TestCase):
    def api(self,rows,auto=''):
        return run_shell(STUBS+shell_function(API,'_get_json')+'\n_get_json config\n',
                         {'MULTIPATH_ROWS':rows,'AUTO_RESPONSE':auto})

    def test_api_on_wan_is_retried_after_default_failure(self):
        output,calls=self.api('ethA is deactivated\nethB is in default mode')
        self.assertEqual(json.loads(output),{'ok':True})
        self.assertEqual(calls,['auto','ethB'])

    def test_api_healthy_backup_is_not_tried(self):
        output,calls=self.api('ethA is deactivated\nethB is in backup mode')
        self.assertEqual(output,'')
        self.assertEqual(calls,['auto'])

    def test_api_healthy_subflow_mode_is_not_tried(self):
        output,calls=self.api('ethA is deactivated\nethB is in subflow mode')
        self.assertEqual(output,'')
        self.assertEqual(calls,['auto'])

    def test_api_nonempty_error_body_prevents_other_path_attempt(self):
        output,calls=self.api('ethB is in default mode','<html>503 unavailable</html>')
        self.assertIn('503 unavailable',output)
        self.assertEqual(calls,['auto'])

    def tracker(self,rows):
        text=TRACKER.read_text(encoding='utf-8')
        selection=next(x.strip() for x in text.splitlines() if x.strip().startswith('mp_default_intfs="$(multipath'))
        script=STUBS+'\n'+selection+'\n'+shell_function(TRACKER,'_check_server_intf')+'''
server_ping=false; retry=0; intervaltries=0; OMR_TRACKER_TIMEOUT=1
_check_server_intf 192.0.2.10 65500
printf '%s' "$server_ping"
'''
        return run_shell(script,{'MULTIPATH_ROWS':rows})

    def test_server_tracker_probes_normal_wan(self):
        output,calls=self.tracker('ethB is in default mode')
        self.assertEqual(output,'true')
        self.assertEqual(calls,['ethB'])

    def test_server_tracker_does_not_probe_backup_or_default_route(self):
        output,calls=self.tracker('ethA is deactivated\nethB is in backup mode')
        self.assertEqual(output,'false')
        self.assertEqual(calls,[])

    def hook(self,role):
        stubs=r'''
uci() {
 case "$*" in
  '-q get mqvpn.settings.enable') echo 1;;
  '-q get mqvpn.interface.route_via_server') echo 0;;
  '-q get openmptcprouter.wan1.vpn') echo 0;;
  '-q get network.wan1.multipath') echo "$WAN_ROLE";;
  *) return 0;;
 esac
}
pgrep() { echo 4242; }
mqvpn-path() {
 if [ "$1" = list ]; then echo '{"paths":[{"iface":"ethA"},{"iface":"ethB"}]}';
 else printf '%s\n' "$*" >> "$TRACE"; fi
}
_log() { :; }
OMR_TRACKER_DEVICE=ethA; OMR_TRACKER_INTERFACE=wan1
OMR_TRACKER_STATUS=ERROR; OMR_TRACKER_PREV_STATUS=OK
'''
        return run_shell(stubs+HOOK.read_text(encoding='utf-8'),{'WAN_ROLE':role})

    def test_tracker_removes_failed_master_path(self):
        _,calls=self.hook('master'); self.assertEqual(calls,['remove ethA'])

    def test_tracker_removes_failed_nonmaster_path(self):
        _,calls=self.hook('on'); self.assertEqual(calls,['remove ethA'])

    def test_real_c_path_removal_branches_with_mocked_xquic(self):
        text=ENGINE.read_text(encoding='utf-8')
        prelude=r'''
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <assert.h>
#define MQVPN_OK 0
#define MQVPN_ERR_INVALID_ARG -1
#define PATH_LC_CLOSED_FREE 9
#define PATH_EVENT_REMOVE_API 1
#define PATH_EVENT_PLATFORM_DROP 2
#define XQC_OK 0
#define ASSERT_TICK_THREAD(c) ((void)0)
#define LOG_I(...) ((void)0)
#define LOG_W(...) ((void)0)
typedef int64_t mqvpn_path_handle_t;
typedef int xqc_int_t;
typedef struct {int state;int live;uint64_t xqc_path_id;char name[16];} path_entry_t;
typedef struct {int cid;} fixture_conn_t;
typedef struct {void *engine;fixture_conn_t *conn;path_entry_t paths[2];} mqvpn_client_t;
typedef struct {uint64_t now_us;} path_event_ctx_t;
typedef struct {char iface[16];int reason;} mqvpn_platform_path_event_info_t;
static int conn_close,path_close,close_rc,events;
static path_entry_t *find_path_by_handle(mqvpn_client_t*c,mqvpn_path_handle_t p){return p>=0&&p<2?&c->paths[p]:NULL;}
static int path_xquic_abandon_due(path_entry_t*p){return p->live;}
static uint64_t client_now_us(mqvpn_client_t*c){(void)c;return 1;}
static void xqc_h3_conn_close(void*e,int*cid){(void)e;(void)cid;conn_close++;}
static int xqc_conn_close_path(void*e,int*cid,uint64_t p){(void)e;(void)cid;(void)p;path_close++;return close_rc;}
static void path_on_event(mqvpn_client_t*c,path_entry_t*p,int ev,path_event_ctx_t*ctx){(void)c;(void)p;(void)ev;(void)ctx;events++;}
'''
        main=r'''
int main(void){
 fixture_conn_t connection={1};mqvpn_client_t c={0};
 c.engine=&connection;c.conn=&connection;
 c.paths[0]=(path_entry_t){.live=1,.xqc_path_id=0,.name="ethA"};
 c.paths[1]=(path_entry_t){.live=1,.xqc_path_id=2,.name="ethB"};
 assert(mqvpn_client_remove_path(&c,0)==0);
 assert(conn_close==1&&path_close==0&&c.paths[1].live==1);
 printf("initial_control_remove: connection_close=%d alternative_live=%d\n",conn_close,c.paths[1].live);
 conn_close=path_close=events=0;
 assert(mqvpn_client_remove_path(&c,1)==0);
 assert(conn_close==0&&path_close==1);
 puts("secondary_control_remove_success: connection_preserved");
 conn_close=path_close=events=0;close_rc=-1;
 assert(mqvpn_client_remove_path(&c,1)==0);
 assert(conn_close==1&&path_close==1);
 puts("secondary_control_remove_error: connection_closed");
 conn_close=path_close=events=0;close_rc=0;
 assert(mqvpn_client_on_platform_path_dropped(&c,0,NULL)==0);
 assert(conn_close==0&&path_close==1);
 puts("initial_netlink_drop: only_path_close_requested");
 conn_close=path_close=events=0;close_rc=-1;
 assert(mqvpn_client_on_platform_path_dropped(&c,0,NULL)==0);
 assert(conn_close==0&&path_close==1);
 puts("netlink_close_error: return_value_ignored");
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            src=Path(directory)/'fixture.c';binary=Path(directory)/'fixture'
            src.write_text(prelude+c_function(text,'mqvpn_client_remove_path')+'\n'+c_function(text,'mqvpn_client_on_platform_path_dropped')+'\n'+main)
            subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(src),'-o',str(binary)],capture_output=True,text=True,check=True)
            output=subprocess.check_output([str(binary)],text=True)
            self.assertIn('connection_close=1 alternative_live=1',output)
            (BASE/'c-reproducer-output.txt').write_text(output,encoding='utf-8')

if __name__=='__main__':
    expected=('1be97f1b23db0d652dec6b634a053b198d9fe834913a92e9a0d7ebb2ea437675',
              '67badfd7037c070f9667d32cf42ae4c81a8beb97c51559a22920505d118c1684',
              '77c6d877589bffbe04fedc35b9a03c90e5ec6df806e751b5abec8b00ae400a83',
              '3bb09f2093de33bc1072e0a2d944aa735ad303b9b0de3def6d730ffbd929b0c8')
    if any(hashlib.sha256(p.read_bytes()).hexdigest()!=digest for p,digest in zip((API,TRACKER,HOOK,ENGINE),expected)):
        raise SystemExit('Historical baseline source mismatch. Use feed 0060b84 and pre-030 MQVPN for this reproducer; run the candidate API/real-tunnel acceptance suites for new sources (see README).')
    BASE.mkdir(parents=True,exist_ok=True)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(OfflineFailoverTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'passed':result.wasSuccessful(),'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
            'scope':'Actual shell/C functions with mocked dependencies; no network, real UCI, service restart or tunnel continuity test.',
            'sources':[{'path':os.path.relpath(p,ROOT),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (API,TRACKER,HOOK,ENGINE)],
            'checked_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    (BASE/'offline-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(not result.wasSuccessful())
