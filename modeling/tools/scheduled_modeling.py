"""One-shot modeling jobs, real quota monitoring, persistent progress and one writer."""
from __future__ import annotations
import argparse, ctypes, datetime, json, msvcrt, os, pathlib, queue, socket, subprocess, time
from codex_rpc import CodexRPC

ROOT=pathlib.Path(__file__).resolve().parents[2]
WORK=ROOT/'modeling'
LOG=WORK/'automation'
LOG.mkdir(exist_ok=True)
STATE=LOG/'scheduler_state.json'
EVENTS=LOG/'worker-events.jsonl'

def log(kind, data):
    with EVENTS.open('a',encoding='utf-8') as f:
        f.write(json.dumps({'time':datetime.datetime.now().astimezone().isoformat(),'kind':kind,'data':data},ensure_ascii=False)+'\n')

def state_write(state):
    STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')

def quota(rpc):
    data=rpc.request('account/rateLimits/read')
    bucket=data.get('rateLimitsByLimitId',{}).get('codex') or data['rateLimits']
    window=next((bucket.get(x) for x in ('primary','secondary') if (bucket.get(x) or {}).get('windowDurationMins')==300),None)
    if window is None:raise RuntimeError('No authoritative 300-minute quota window available')
    log('quota',window)
    return window

def checkpoint():
    # Use the installed official add-on bridge only to preserve this project's file.
    code="import bpy, pathlib\np=pathlib.Path(bpy.data.filepath) if bpy.data.filepath else None\nroot=pathlib.Path("+repr(str(WORK))+ ")\nif p is not None and root in p.parents:\n bpy.ops.wm.save_as_mainfile(filepath=str(p))\n result={'saved':str(p)}\nelse:\n result={'saved':None,'reason':'No active modeling project file'}"
    try:
        with socket.create_connection(('127.0.0.1',9876),timeout=15) as s:
            s.settimeout(300)
            s.sendall((json.dumps({'type':'execute','code':code,'strict_json':True})+'\0').encode())
            response=b''
            while b'\0' not in response:
                part=s.recv(65536)
                if not part:break
                response+=part
            log('checkpoint',json.loads(response.split(b'\0')[0]))
    except Exception as exc:log('checkpoint_error',str(exc))

PROMPT='''继续用户授权的OpenMicroKbd精细可交互模型任务。工作目录是 {root}。
首先读取 modeling/资料整理.md、建模计划.md、工作日志.md、progress.json。按计划使用已配置的官方 Blender MCP 工具制作；所有 Blender 场景操作通过 MCP。用源CAD/PCB/实拍而不是臆测。先生成并实际查看源CAD多视角参考，再制作正式资产。
当前是{phase}次定时执行。完成接下来的一个完整资产批次：建模、保存、渲染、使用view_image实际审看、不合格返工再次审看，更新文件进度。每个小步骤保存，单次调用不要超过安全可恢复的工作量。不要仅做计划或以回复代替制作。模型有13独立可按键、带旋转/按压的旋钮、双轴/按压摇杆、触摸区域、13+8灯、可识别内部电子件、真实材质和可控解构层级，包含实际可用交互面板和示范动画。不要用扁平占位物冒充精细完成品。内部元件允许适度简化。
保存 modeling/assets/MacroPad.blend、增量checkpoint和渲染到 modeling/renders；不会覆盖别的用户文件。不要提交/推送仓库，不要发送外部消息。保留原始资料。
每批结束更新progress.json的completed_batches、next_action、known_issues、render_paths、visual_reviews、complete和audit_complete，并写工作日志。只有重开.blend并完成全部逐项视觉与交互验证后才能complete=true。
如果模型已complete=true：本次专门重新打开保存的文件进行独立全量验收，实际检查13键、旋钮、摇杆、LED、解构复位、内部、资源打包和全部视角；修复发现的问题后重新渲染。全部通过才将audit_complete=true并写验收报告。
本地执行器监控真实5小时额度，≤6%将提醒保存，≤5%会中断当前turn。不要消耗重置券。不要派生子智能体。完成一批后返回实际结果，执行器会继续下一批。'''

def run(phase, preflight=False):
    lock=(LOG/'writer.lock').open('a+b')
    lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:
        if phase=='second':(LOG/'second-request.json').write_text(json.dumps({'requested':time.time()}))
        log('existing_writer',{'phase':phase,'action':'queued second-phase request'})
        return
    rpc=None
    state=json.loads(STATE.read_text(encoding='utf-8-sig')) if STATE.exists() else {}
    try:
        rpc=CodexRPC(str(ROOT))
        q=quota(rpc)
        if preflight:
            print(json.dumps({'cli_ready':True,'remaining_percent':100-q['usedPercent'],'reset_at':q['resetsAt'],'root':str(ROOT)},ensure_ascii=False));return
        if q['usedPercent']>=95:
            state.update(status='stopped_at_quota',phase=phase,quota=q);state_write(state);return
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
        try:
            with socket.create_connection(('localhost',9876),timeout=2):pass
        except OSError:
            startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
            subprocess.Popen(['D:/blender.exe'],startupinfo=startup)
            for _ in range(30):
                time.sleep(1)
                try:
                    with socket.create_connection(('localhost',9876),timeout=1):break
                except OSError:continue
            else:raise RuntimeError('Blender MCP could not start')
        if state.get('thread_id'):
            rpc.request('thread/resume',{'threadId':state['thread_id'],'cwd':str(ROOT)},timeout=120)
        else:
            started=rpc.request('thread/start',{'cwd':str(ROOT),'approvalPolicy':'never','sandbox':'danger-full-access'},timeout=120)
            state['thread_id']=started['thread']['id']
        state.pop('error',None)
        state.update(status='running',phase=phase,runner_pid=os.getpid(),server_pid=rpc.proc.pid)
        state_write(state)
        while True:
            progress=json.loads((WORK/'progress.json').read_text(encoding='utf-8-sig'))
            signal=LOG/'second-request.json'
            if signal.exists():phase='second';signal.unlink();state['phase']=phase
            if phase=='first' and progress.get('complete'):break
            q=quota(rpc)
            if q['usedPercent']>=95:state['status']='stopped_at_quota';break
            text=PROMPT.format(root=ROOT,phase='第一' if phase=='first' else '第二')
            turn=rpc.request('turn/start',{'threadId':state['thread_id'],'input':[{'type':'text','text':text}]},timeout=120)
            turn_id=turn['turn']['id'];state.update(turn_id=turn_id,status='running');state_write(state)
            last_check=time.monotonic();warned=False;finished=False;turn_status=None
            while not finished:
                messages=rpc.events;rpc.events=[]
                try:messages.append(rpc.incoming.get(timeout=1))
                except queue.Empty:pass
                for msg in messages:
                    method=msg.get('method','')
                    if method in ('turn/completed','item/completed','error','item/started'):log(method,msg.get('params'))
                    if method=='turn/completed' and msg.get('params',{}).get('turn',{}).get('id')==turn_id:
                        finished=True;turn_status=msg['params']['turn'].get('status')
                    if 'id' in msg and 'method' in msg:
                        # No unattended authorization expansion or invented user answer.
                        raise RuntimeError('Worker requested user interaction: '+method)
                if not finished and time.monotonic()-last_check>=20:
                    q=quota(rpc);last_check=time.monotonic()
                    if q['usedPercent']>=95:
                        rpc.request('turn/interrupt',{'threadId':state['thread_id'],'turnId':turn_id})
                        checkpoint();state.update(status='stopped_at_quota',quota=q);state_write(state);return
                    if q['usedPercent']>=94 and not warned:
                        try:rpc.request('turn/steer',{'threadId':state['thread_id'],'expectedTurnId':turn_id,'input':[{'type':'text','text':'额度剩余约6%，立即保存当前.blend和progress.json、日志，停止新制作并结束本turn。'}]})
                        except Exception as exc:log('steer_error',str(exc))
                        warned=True
                    if rpc.proc.poll() is not None:raise RuntimeError('Worker app-server exited')
            state['last_turn_status']=turn_status;state_write(state)
            if turn_status!='completed':raise RuntimeError('Modeling turn did not complete: '+str(turn_status))
            progress=json.loads((WORK/'progress.json').read_text(encoding='utf-8-sig'))
            if phase=='second' and progress.get('complete') and progress.get('audit_complete'):break
        state['status']='completed' if progress.get('complete') else state.get('status','stopped')
        state_write(state)
    except Exception as exc:
        if rpc and state.get('turn_id'):
            try:rpc.request('turn/interrupt',{'threadId':state['thread_id'],'turnId':state['turn_id']})
            except Exception:pass
        checkpoint();state.update(status='error',error=str(exc));state_write(state);log('runner_error',str(exc))
        raise
    finally:
        if rpc:rpc.close()
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        lock.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['first','second']);p.add_argument('--preflight',action='store_true')
    a=p.parse_args();run(a.phase,a.preflight)
