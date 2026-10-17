"""Small JSON-lines client for the documented local Codex app-server protocol."""
from __future__ import annotations
import json, os, pathlib, queue, subprocess, threading, time

CLI = pathlib.Path(os.environ['APPDATA']) / 'npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe'

class CodexRPC:
    def __init__(self, cwd=None):
        self.proc = subprocess.Popen([str(CLI), 'app-server'], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding='utf-8',
            cwd=cwd, creationflags=subprocess.CREATE_NO_WINDOW)
        self.incoming = queue.Queue()
        self.events = []
        self.counter = 0
        def read():
            for line in self.proc.stdout:
                try: self.incoming.put(json.loads(line))
                except json.JSONDecodeError: pass
        threading.Thread(target=read, daemon=True).start()
        self.request('initialize', {'clientInfo':{'name':'openmicro_modeling_scheduler','version':'1.0.0'},'capabilities':{'experimentalApi':True}})
        self.send({'method':'initialized','params':{}})

    def send(self, message):
        self.proc.stdin.write(json.dumps(message, ensure_ascii=False)+'\n')
        self.proc.stdin.flush()

    def request(self, method, params=None, timeout=45):
        self.counter += 1
        request_id = self.counter
        self.send({'id':request_id,'method':method,'params':params or {}})
        deadline = time.monotonic()+timeout
        while time.monotonic()<deadline:
            message = self.incoming.get(timeout=max(.1,deadline-time.monotonic()))
            if message.get('id') == request_id and ('result' in message or 'error' in message):
                if 'error' in message: raise RuntimeError(json.dumps(message['error']))
                return message['result']
            self.events.append(message)
        raise TimeoutError(method)

    def close(self):
        if self.proc.poll() is None:
            self.proc.stdin.close()
            try: self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired: self.proc.terminate()

if __name__ == '__main__':
    rpc = CodexRPC()
    try: print(json.dumps(rpc.request('account/rateLimits/read'),ensure_ascii=False,indent=2))
    finally: rpc.close()
