import sys
import time
import string
from threading import Thread

class _CloudConnection():
    class PollThread(Thread):
        def __init__(self, cloud):
            self.cloud = cloud
            super().__init__()
        def run(self):
            t = 0
            while 1:
                if t > 9:  # Max 10 cloud vars
                    for name in self.cloud.all_vars.copy():
                        self.cloud.get(name)  # Force update known variables
                        time.sleep(.5)
                    time.sleep(1)
                try:
                    self.cloud.get_event()
                except BlockingIOError:
                    pass
                t += 1
    def __init__(self, c):
        self.all_vars = {}
        self.c = c
        self.evfix = None
    def async_vars_update(self):
        """Makes all_vars change in real time. (breaks mainloop)"""
        self.PollThread(self).start()
    def get_event(self):
        """Non-blocking poll_event"""
        self.c.setblocking(0)
        try:
            res = self.poll_event()
        except BlockingIOError:
            self.c.setblocking(1)
            raise
        self.c.setblocking(1)
        return res
    def poll_event(self):
        """Polls for an event.
Use inheritence and mainloop() instead."""
        if self.evfix is not None:
            ret = self.evfix
            self.evfix = None
            #print(ret)
            return ret
        c = self.c
        ev = recv_till_slash(c)
        if ev == "set":
            name = recv_till_slash(c)
            val  = recv_till_slash(c)

            #print(name, "|", val)
            val2 = val
            smallest_i = None
            for char in string.ascii_letters:
                if char in val2:
                    i = val2.index(char)
                    if smallest_i is None:
                        smallest_i = i
                    if i < smallest_i:
                        smallest_i = i
            if smallest_i is not None:
                # New event[?]
                ev2   = val[smallest_i:]
                val   = val[:smallest_i]
                name2 = recv_till_slash(c)
                v     = recv_till_slash(c)
                self.evfix = {"type": val2, "name": name2, "val": v}
            else:
                self.all_vars.update({name: val})             # Update the local var log
            #print({"type": "set", "name": name, "val": val})
            return {"type": "set", "name": name, "val": val}  # Return the event
        print("unknown event", ev, file=sys.stderr)
        # recv_till_slash(c)
        return self.poll_event()
    def ev_set(self, name, value):
        print(name, ":", value, file=sys.stderr)
    def set(self, name, value):
        self.c.send(b"set\\"+name.encode("latin1")+b"\\"+value.encode("latin1"))
    def get(self, name):
        """Force the server to broadcast a `set` event with the updated variable value.
A little ambigious but without an event queue i can't do much better then that."""
        self.c.sendall(b"get\\"+name.encode("latin1"))
        self.poll_event()
        
    def mainloop(self):
        while 1:
            ev = self.poll_event()
            if ev["type"] == "set":
                self.ev_set(ev["name"], ev["val"])

class CloudConnection(_CloudConnection):
    def __init__(self, c):
        super().__init__(c)
        self.async_vars_update()
    def mainloop(self):
        raise Exception("mainloop() supported in EventCloudConnection only.")
    def ev_set(self, *_):
        pass

def recv_till_slash(c):
    x = b""
    while 1:
        if len(x) > 0:
            if x[-1] == 92: break
        x += c.recv(1)
    # print(x.decode("latin1"), end="")
    return x[:-1].decode("latin1")
