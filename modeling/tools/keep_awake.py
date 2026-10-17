"""Prevent automatic system sleep until the second scheduled job has started."""
import ctypes, datetime, time
deadline=datetime.datetime(2026,10,1,9,0,0)
try:
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    while datetime.datetime.now()<deadline:time.sleep(30)
finally:
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
