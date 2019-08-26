import atexit
import scratch
import socket
import time
import traceback

s = None

def wait_till_ready(cloud):
    """Waits until we have received values for all 4 important variables"""
    while cloud.all_vars.get("recv") == None or cloud.all_vars.get("new_recv") == None or\
          cloud.all_vars.get("send") == None or cloud.all_vars.get("new_send") == None:
        time.sleep(.1)


def send(cloud, what):
    time.sleep(1)
    cloud.set("recv", "1" + encode(what))
    count = 0
    while cloud.all_vars["recv"] != ("1" + encode(what)):
        print("[send()] 1", cloud.all_vars["new_recv"])
        time.sleep(1)
        count += 1
        if count > 30:
            raise TimeoutError()
    time.sleep(0.2)
    cloud.set("new_recv", "1")
    time.sleep(1)
    count = 0
    while cloud.all_vars["new_recv"] != "0":
        print("[send()] 2", cloud.all_vars["new_recv"])
        time.sleep(1)
        count += 1
        if count > 30:
            raise TimeoutError()

def recv(cloud):
    count = 0
    while cloud.all_vars["new_send"] != "1":
        time.sleep(1)
        count += 1
        if count > 30:
            raise TimeoutError()
    time.sleep(1)
    cloud.set("new_send", "0")
    time.sleep(1)
    count = 0
    while cloud.all_vars["new_send"] != "0":
        cloud.set("new_send", "0")
        time.sleep(.5)
        count += 1
        if count > 60:
            raise TimeoutError()
    return decode(cloud.all_vars["send"][1:])

def decode(x):
    global charset
    y = ""
    i = 0
    while i < len(x):
        y += charset[int(x[i]+x[i+1])]
        i += 2
    return y

def encode(x):
    global charset
    y = ""
    for i in x.lower():
        try:
            y += str(charset.index(i)).zfill(2)
        except:
            print(i)
            raise
    return y

def close():
    global s
    s.shutdown(socket.SHUT_RDWR)
    s.close()

atexit.register(close)

x = scratch.CloudConnection()

s = x.c  # readibility 100

charset = "\0qwertyuiopasdfghjklzxcvbnm0123456789# '.,[]!?*+-/"

databases = {
    "main": {
        "can_access": ["robowiko123", "*"],
        "tables": {
            "users": {
                "column_names": ["primary", "Username", "ID", "Comment"],
                "values": [
                    ["0", "Robowiko123", "2634267", "A great account [admin]"],
                    ["1", "100Tests", "906981", "pretty sure no one has this name on scratch if you have please comment"],
                    ["2", "ILikeDragons", "62417", "It's true!"]
                ]
            },
            "multiplication": {
                "column_names": ["*", "1", "2", "3", "4"],
                "values": [
                    ["1", "1", "2", "3", "4"],
                    ["2", "2", "4", "6", "8"],
                    ["3", "3", "6", "9", "12"],
                    ["4", "4", "8", "12", "16"],
                ]
            }
        }
    }
}

cloud = x

wait_till_ready(cloud)
print("Ready.")

while 1:
    try:
        x = recv(cloud)
        print("Got", x)
        if x == "hi":
            send(cloud, "username")
            username = recv(cloud)
            print("Username:", username)
            send(cloud, "database")
            database_name = recv(cloud)
            print("Database name:", database_name)
            if database_name not in databases:
                send(cloud, "#1 Database doesn't exist.")
                send(cloud, "bye")
                print("Database doesn't exist.")
                continue
            elif (username not in databases[database_name]["can_access"]) and ("*" not in databases[database_name]["can_access"]):
                send(cloud, "#2 Permission denied.")
                send(cloud, "bye")
                print("Permission denied.")
                continue
            send(cloud, "#0 OK.")
            send(cloud, "action")
            action = recv(cloud)
            cmd = action.split(" ")
            print(cmd)
            if cmd[0] == "list":
                if cmd[1] == "table":
                    t = " ".join(cmd[2:])
                    print("list table", t)
                    table = databases[database_name]["tables"].get(t, None)
                    if table is None:
                        send(cloud, "#3 Table doesn't exist.")
                        send(cloud, "bye")
                        continue
                    send(cloud, "#0 OK.")
                    send(cloud, ",".join(table["column_names"]))
                    for row in table["values"]:
                        send(cloud, ",".join(row))
                    send(cloud, "bye")
                    continue
                elif cmd[1] == "tables":
                    send(cloud, "#0 OK.")
                    send(cloud, ",".join([i for i in databases[database_name]["tables"]]))
                    send(cloud, "bye")
                    continue
                else:
                    send(cloud, "#4 Unknown command.")
                    send(cloud, "bye")
            else:
                send(cloud, "#4 Unknown command.")
                send(cloud, "bye")
    except:
        traceback.print_exc()
        print("Still running!")
