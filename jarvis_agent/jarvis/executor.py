"""The only module allowed to actually call tool functions.

Maps an action name (string, as emitted by the planner) to a real function.
This indirection is deliberate: the LLM only ever produces data (action name
+ args), never code, and this table is the single place that turns that data
into a real OS call.
"""
from jarvis.tools import filesystem, process, browser, input_control, system
from jarvis.logger import log_action

ACTIONS = {
    # filesystem
    "list_files": lambda args: filesystem.list_files(args["directory"]),
    "read_file": lambda args: filesystem.read_file(args["path"]),
    "write_file": lambda args: filesystem.write_file(args["path"], args["content"], args.get("append", False)),
    "delete_file": lambda args: filesystem.delete_file(args["path"]),

    # process
    "list_processes": lambda args: process.list_processes(),
    "launch_process": lambda args: process.launch_process(args["name"], args.get("args")),
    "kill_process": lambda args: process.kill_process(args["name"]),

    # browser
    "browser_navigate": lambda args: browser.browser_navigate(args["url"]),
    "browser_click": lambda args: browser.browser_click(args["selector"]),
    "browser_type": lambda args: browser.browser_type(args["selector"], args["text"]),
    "browser_read_text": lambda args: browser.browser_read_text(args.get("selector", "body")),

    # input control (disabled until config.yaml enables it)
    "mouse_click": lambda args: input_control.mouse_click(args["x"], args["y"]),
    "send_keys": lambda args: input_control.send_keys(args["text"]),
    "screenshot": lambda args: input_control.screenshot(args.get("save_path", "screenshot.png")),

    # system (disabled/stubbed per OS — see tools/system.py)
    "system_sleep": lambda args: system.system_sleep(),
    "system_shutdown": lambda args: system.system_shutdown(),
}


class UnknownAction(Exception):
    pass


def execute(action: str, args: dict):
    if action not in ACTIONS:
        log_action(action, args, "refused", "unknown action, not in executor.ACTIONS")
        raise UnknownAction(f"'{action}' has no registered tool implementation.")
    try:
        result = ACTIONS[action](args)
        log_action(action, args, "executed", str(result)[:300])
        return result
    except Exception as e:
        log_action(action, args, "error", str(e))
        raise
