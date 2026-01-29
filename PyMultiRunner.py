# Author: MinhNguyen2412
from __future__ import annotations
from collections import deque
from typing import List, Tuple
from rich.live import Live
from rich.panel import Panel
from rich.columns import Columns
from rich.console import Group, Console
from rich.syntax import Syntax
from rich.text import Text
console = Console()
def clear_():
    __import__('os').system('cls' if __import__('os').name == 'nt' else 'clear')
TIMEOUT_SECONDS = 300
MAX_BUF_LINES = 2000
PROMPT_RE = __import__('re').compile('(enter|file|path|name|input|y/n|yes/no|choose|select|press).*[:?]\\s*$|>>>\\s|^\\.\\.\\.\\s', __import__('re').IGNORECASE)
cmd = '#' * 42
if len(__import__('sys').argv) > 1:
    TARGET = __import__('sys').argv[1]
else:
    while True:
        clear_()
        print(cmd)
        try:
            file_list = [f for f in __import__('os').listdir(__import__('os').getcwd()) if f.endswith(('.pyc', '.py', '.exe'))]
        except OSError:
            file_list = []
        for i, file_name in enumerate(file_list, start=1):
            print(f'[ {file_name} ]', end=' ')
            if i % 3 == 0:
                print()
        print('\n' + cmd)
        __file__ = input(f'[+] [NHẬP FILE]: ')
        if __import__('os').path.isfile(__file__):
            TARGET = __file__
            break
        else:
            input('[!] [KHÔNG TÌM THẤY FILE!]')
            continue
found = {}
path_dirs = __import__('os').environ.get('PATH', '').split(':')
for dir_path in path_dirs:
    if not __import__('os').path.isdir(dir_path):
        continue
    try:
        files = __import__('os').listdir(dir_path)
    except OSError:
        continue
    for name in files:
        if not name.startswith('python'):
            continue
        full = __import__('os').path.join(dir_path, name)
        if not __import__('os').access(full, __import__('os').X_OK):
            continue
        if full in found:
            continue
        if 'config' in name or 'm' in name.split('.')[-1]:
            continue
        try:
            out = __import__('subprocess').check_output([full, '--version'], stderr=__import__('subprocess').STDOUT, text=True, timeout=1).strip()
            parts = out.split(' ')[1].split('.')
            ver_short = f'{parts[0]}.{parts[1]}'
            if ver_short not in found.values():
                found[full] = ver_short
        except:
            pass
DATA_CONVERT = {'config': {**found}}
STATUS = {i: 0 for i in range(len(DATA_CONVERT['config']))}
while True:
    clear_()
    print(' ' * 9 + '--> MENU VERSION <--')
    print(cmd)
    items = list(DATA_CONVERT['config'].items())
    for i, (path, ver) in enumerate(items):
        st_text = f"{__import__('colorama').Fore.GREEN}Enabled{__import__('colorama').Style.RESET_ALL}" if STATUS[i] else f"{__import__('colorama').Fore.RED}Disabled{__import__('colorama').Style.RESET_ALL}"
        print(f' {i + 1}. [--->{ver:^10}<---] [{st_text}]')
    print('-' * 42)
    print(' R. START RUNNING..')
    print(' K. EXIT TOOL')
    print(cmd)
    inp = input('[+] [CHOOSE]: ').strip().upper()
    if inp == 'R':
        selected = [items[i] for i in range(len(items)) if STATUS[i]]
        if not selected:
            input('[!] [ERROR: EMPTY DATA LIST]')
        else:
            INTERPRETERS = [(f'Py {v}', k) for k, v in selected]
            break
    elif inp == 'K':
        __import__('sys').exit()
    else:
        try:
            idx = int(inp) - 1
            if 0 <= idx < len(items):
                STATUS[idx] = 1 - STATUS[idx]
        except:
            pass

def start_process_with_pty(exe: str, target: str):
    master_fd, slave_fd = __import__('os').openpty()
    cmd_list = [exe, '-u', '-i', target]
    proc = __import__('subprocess').Popen(cmd_list, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, close_fds=True, preexec_fn=__import__('os').setsid)
    __import__('os').close(slave_fd)
    return (master_fd, proc)

def reader_thread(master_fd: int, buffer: deque, stop_event: __import__('threading').Event):
    while not stop_event.is_set():
        try:
            r, _, _ = __import__('select').select([master_fd], [], [], 0.1)
            if master_fd in r:
                data = __import__('os').read(master_fd, 4096)
                if not data:
                    break
                text = data.decode(errors='replace')
                if buffer:
                    last_line = buffer.pop()
                    text = last_line + text
                lines = text.splitlines(keepends=True)
                buffer.extend(lines)
                while len(buffer) > MAX_BUF_LINES:
                    buffer.popleft()
        except OSError:
            break

def make_panel(name, exe, buf, rc, err, elapsed, interactive, focused, panel_height):
    header = f'[b]{name}[/]'
    VISIBLE_LINES = max(1, panel_height - 4)
    if not buf:
        content_text = ''
        last_line_check = ''
    else:
        lines = list(buf)
        last_line_check = lines[-1]
        if len(lines) > VISIBLE_LINES:
            lines = lines[-VISIBLE_LINES:]
        content_text = ''.join(lines)
    in_shell = False
    if last_line_check and ('>>>' in last_line_check or '...' in last_line_check):
        in_shell = True
    content = Syntax(content_text, 'python', line_numbers=False, word_wrap=True)
    info = Text()
    if rc is not None:
        info.append(f'Exit: {rc} ', style='bold')
    if err:
        info.append(f'Err ', style='bold red')
    if elapsed:
        info.append(f'{round(elapsed, 1)}s ', style='dim')
    if in_shell:
        info.append('(SHELL MODE)', style='bold green blink')
    elif interactive:
        info.append('(running)', style='blue dim')
    body = Group(info, Panel(content, title='output', padding=(0, 0), border_style='dim'))
    border = 'green' if in_shell else 'red' if rc is not None else 'bright_blue' if focused else 'yellow'
    return Panel(body, title=f"{header} {('[√]' if focused else '')}", border_style=border, height=panel_height)

def main():
    if __import__('os').name == 'nt':
        print('Requires Linux/macOS.')
        return
    masters, buffers, procs, stops, rcs, errs, starts = ([], [], [], [], [], [], [])
    for name, exe in INTERPRETERS:
        if not __import__('shutil').which(exe):
            masters.append(None)
            buffers.append(deque())
            procs.append(None)
            stops.append(None)
            rcs.append(None)
            errs.append(f'Not found: {exe}')
            starts.append(None)
            continue
        buf = deque()
        stop = __import__('threading').Event()
        try:
            fd, proc = start_process_with_pty(exe, TARGET)
            t = __import__('threading').Thread(target=reader_thread, args=(fd, buf, stop), daemon=True)
            t.start()
            masters.append((fd, proc))
            buffers.append(buf)
            procs.append(proc)
            stops.append(stop)
            rcs.append(None)
            errs.append(None)
            starts.append(__import__('time').time())
        except Exception as e:
            masters.append(None)
            buffers.append(deque())
            procs.append(None)
            stops.append(None)
            rcs.append(None)
            errs.append(str(e))
            starts.append(None)
    old_tty = __import__('termios').tcgetattr(__import__('sys').stdin.fileno())
    __import__('tty').setcbreak(__import__('sys').stdin.fileno())
    focused = 0
    raw_mode = False
    current_input = ''
    last_esc = False
    awaiting = None
    last_trigger_line = {}
    try:
        with Live(screen=True, refresh_per_second=20) as live:
            while True:
                term_w, term_h = console.size
                MIN_WIDTH = 45
                cols_per_row = max(1, term_w // MIN_WIDTH)
                required_rows = __import__('math').ceil(len(INTERPRETERS) / cols_per_row)
                footer_space = 6
                available_height = max(10, term_h - footer_space)
                dynamic_height = available_height // required_rows
                for i, proc in enumerate(procs):
                    if proc and rcs[i] is None:
                        ret = proc.poll()
                        if ret is not None:
                            rcs[i] = ret
                            stops[i].set()
                for i, buf in enumerate(buffers):
                    if buf and rcs[i] is None:
                        last = buf[-1]
                        if PROMPT_RE.search(last):
                            if last_trigger_line.get(i) != last:
                                last_trigger_line[i] = last
                                focused = i
                                if '>>>' not in last and '...' not in last:
                                    awaiting = i
                                elif awaiting == i:
                                    awaiting = None
                panels = []
                display_order = [focused] + [x for x in range(len(INTERPRETERS)) if x != focused]
                for i in display_order:
                    name, exe = INTERPRETERS[i]
                    is_focused = focused == i
                    elapsed = __import__('time').time() - starts[i] if starts[i] and rcs[i] is None else None
                    panels.append(make_panel(name, exe, buffers[i], rcs[i], errs[i], elapsed, masters[i] is not None, is_focused, panel_height=dynamic_height))
                footer = Text()
                footer.append(' | Alt+1..4 switch | ')
                footer.append('Ctrl-T send ALL', style='bold yellow')
                footer.append(' | ')
                footer.append('Ctrl-O cmd', style='bold cyan')
                footer.append(' | ')
                footer.append('Ctrl-C exit', style='bold red')
                footer.append(f' | RAW: {raw_mode} | Focused: {INTERPRETERS[focused][0]}\n')
                footer.append(f'Input: {current_input}' + (' (RAW)' if raw_mode else ''))
                layout = Group(Columns(panels, equal=True, expand=True), Panel(footer, title='Controls'))
                live.update(layout)
                rlist, _, _ = __import__('select').select([__import__('sys').stdin], [], [], 0.05)
                if not rlist:
                    continue
                data_in = __import__('os').read(__import__('sys').stdin.fileno(), 1024)
                for b in data_in:
                    if b == 27:
                        last_esc = True
                        continue
                    if last_esc:
                        last_esc = False
                        if 49 <= b <= 57:
                            idx = b - 49
                            if idx < len(INTERPRETERS):
                                focused = idx
                                awaiting = None
                        continue
                    if b == 3:
                        raise KeyboardInterrupt
                    if b == 20:
                        for m in masters:
                            if m:
                                __import__('os').write(m[0], (current_input + '\n').encode())
                        current_input = ''
                        awaiting = None
                        continue
                    if b == 15:
                        __import__('termios').tcsetattr(__import__('sys').stdin.fileno(), __import__('termios').TCSADRAIN, old_tty)
                        try:
                            cmd_in = input('\n[CMD] (q/r/1-9): ').strip().lower()
                        except:
                            cmd_in = ''
                        __import__('tty').setcbreak(__import__('sys').stdin.fileno())
                        if cmd_in == 'q':
                            raise KeyboardInterrupt
                        if cmd_in == 'r':
                            raw_mode = not raw_mode
                        if cmd_in.isdigit():
                            focused = int(cmd_in) - 1
                        continue
                    tgt = awaiting if awaiting is not None else focused
                    if tgt < len(masters) and masters[tgt]:
                        if raw_mode:
                            __import__('os').write(masters[tgt][0], bytes([b]))
                        elif b in (10, 13):
                            __import__('os').write(masters[tgt][0], (current_input + '\n').encode())
                            current_input = ''
                            awaiting = None
                        elif b in (127, 8):
                            current_input = current_input[:-1]
                        else:
                            current_input += chr(b)
    except KeyboardInterrupt:
        pass
    finally:
        __import__('termios').tcsetattr(__import__('sys').stdin.fileno(), __import__('termios').TCSADRAIN, old_tty)
        for m in masters:
            if m:
                try:
                    __import__('os').close(m[0])
                    m[1].terminate()
                except:
                    pass
if __name__ == '__main__':
    main()
