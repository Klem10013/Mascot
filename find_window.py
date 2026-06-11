from Xlib import display, X
from Xlib.ext import record
from Xlib import protocol

d = display.Display()
root = d.screen().root

# Subscribe to window change events on root
root.change_attributes(event_mask=(
    X.SubstructureNotifyMask |   # window created/destroyed
    X.PropertyChangeMask         # window properties changed
))

self_id = None

def listen_for_window_changes(mascot):
    global self_id
    print("Listening for window changes...")
    while True:
        event = d.next_event()
        if event.type == X.CreateNotify and self_id == None:
            self_id = event.window.id
            continue
        if event.type == X.DestroyNotify:
            mascot.delete_window(event.window.id)
        if event.type == X.ConfigureNotify and event.window.id != self_id:
            mascot.check_if_inside(event.window.id, event.x,event.y,event.width,event.height,self_id)


def get_all_windows_pos():
    tree = root.query_tree()
    all_windows = {}  # id -> (x,y,width,height)

    #This for loop return all the windows for the back to the front of the screen
    for _, window in enumerate(tree.children):
        try:
            geo = window.get_geometry()
            if geo.width > 50 and geo.height > 50 and geo.x > 0:
                all_windows[window.id] = ((geo.x,geo.y,geo.width,geo.height))
        except Exception:
            pass  # some windows may be inaccessible
    return all_windows