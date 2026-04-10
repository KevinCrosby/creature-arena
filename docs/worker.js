'use strict';

/* ------------------------------------------------------------------ */
/* Pyodide Web Worker — runs the Python game                          */
/* ------------------------------------------------------------------ */
const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.26.2/full/';

let inputState, inputLength, inputData;

/* -- JS functions exposed to Python via `import js` -- */

globalThis.postOutput = (text) => {
  self.postMessage({ type: 'stdout', text });
};

globalThis.requestInput = () => {
  self.postMessage({ type: 'input' });
  Atomics.store(inputState, 0, 0);           // reset → WAITING
  Atomics.wait(inputState, 0, 0);            // block until not 0
  const len = Atomics.load(inputLength, 0);
  return new TextDecoder().decode(inputData.slice(0, len));
};

const _sleepBuf = new Int32Array(new SharedArrayBuffer(4));
globalThis.webSleep = (ms) => {
  if (ms > 0) Atomics.wait(_sleepBuf, 0, 0, ms);
};

/* ------------------------------------------------------------------ */
/* Boot                                                                */
/* ------------------------------------------------------------------ */
self.onmessage = async (event) => {
  if (event.data.type !== 'init') return;

  const { sharedBuffer, gameFiles } = event.data;
  inputState  = new Int32Array(sharedBuffer, 0, 1);
  inputLength = new Int32Array(sharedBuffer, 4, 1);
  inputData   = new Uint8Array(sharedBuffer, 8);

  try {
    /* 1 — load Pyodide */
    self.postMessage({ type: 'loading', text: '📦 Loading Python runtime…' });
    importScripts(PYODIDE_URL + 'pyodide.js');

    const pyodide = await loadPyodide({
      indexURL: PYODIDE_URL,
      stdout: (line) => self.postMessage({ type: 'stdout', text: line + '\n' }),
      stderr: (line) => self.postMessage({ type: 'stderr', text: line + '\n' }),
    });

    /* 2 — prepare virtual filesystem */
    pyodide.FS.mkdir('/game');
    pyodide.FS.mkdir('/game/saves');
    pyodide.FS.mkdir('/game/replays');

    /* 3 — fetch game sources */
    self.postMessage({ type: 'loading', text: '📁 Loading game files…' });
    const files = await Promise.all(
      gameFiles.map(async (f) => {
        const r = await fetch('game/' + f);
        if (!r.ok) throw new Error('Failed to load ' + f + ' (' + r.status + ')');
        return { name: f, text: await r.text() };
      })
    );
    for (const f of files) pyodide.FS.writeFile('/game/' + f.name, f.text);

    /* 4 — mock colorama */
    pyodide.FS.mkdir('/game/colorama');
    pyodide.FS.writeFile('/game/colorama/__init__.py', COLORAMA_MOCK);

    /* 5 — patch Python I/O */
    self.postMessage({ type: 'loading', text: '🎮 Starting game…' });
    await pyodide.runPythonAsync(PYTHON_SETUP);
    self.postMessage({ type: 'ready' });

    /* 6 — run! */
    await pyodide.runPythonAsync(PYTHON_RUN);
    self.postMessage({ type: 'exit' });

  } catch (err) {
    self.postMessage({ type: 'error', text: String(err) });
  }
};

/* ------------------------------------------------------------------ */
/* Inline assets                                                       */
/* ------------------------------------------------------------------ */

const COLORAMA_MOCK = `\
"""Colorama mock — raw ANSI codes for xterm.js."""

class Fore:
    BLACK   = '\\033[30m'
    RED     = '\\033[31m'
    GREEN   = '\\033[32m'
    YELLOW  = '\\033[33m'
    BLUE    = '\\033[34m'
    MAGENTA = '\\033[35m'
    CYAN    = '\\033[36m'
    WHITE   = '\\033[37m'
    RESET   = '\\033[39m'
    LIGHTBLACK_EX   = '\\033[90m'
    LIGHTRED_EX     = '\\033[91m'
    LIGHTGREEN_EX   = '\\033[92m'
    LIGHTYELLOW_EX  = '\\033[93m'
    LIGHTBLUE_EX    = '\\033[94m'
    LIGHTMAGENTA_EX = '\\033[95m'
    LIGHTCYAN_EX    = '\\033[96m'
    LIGHTWHITE_EX   = '\\033[97m'

class Back:
    BLACK   = '\\033[40m'
    RED     = '\\033[41m'
    GREEN   = '\\033[42m'
    YELLOW  = '\\033[43m'
    BLUE    = '\\033[44m'
    MAGENTA = '\\033[45m'
    CYAN    = '\\033[46m'
    WHITE   = '\\033[47m'
    RESET   = '\\033[49m'

class Style:
    DIM       = '\\033[2m'
    NORMAL    = '\\033[22m'
    BRIGHT    = '\\033[1m'
    RESET_ALL = '\\033[0m'

def init(**kwargs):
    pass
`;

const PYTHON_SETUP = `
import sys, os, builtins, time
import js

sys.path.insert(0, '/game')
os.chdir('/game')
os.environ['HOME'] = '/game'

# ---- stdout / stderr ----
class _WebStream:
    encoding = 'utf-8'
    errors   = 'replace'
    def write(self, text):
        if text:
            js.postOutput(str(text))
        return len(text) if text else 0
    def flush(self):
        pass
    def isatty(self):
        return True
    def readable(self):
        return False
    def writable(self):
        return True
    def fileno(self):
        raise OSError('not a real file descriptor')

sys.stdout = _WebStream()
sys.stderr = _WebStream()

# ---- input() ----
def _web_input(prompt=''):
    if prompt:
        sys.stdout.write(str(prompt))
        sys.stdout.flush()
    return str(js.requestInput())

builtins.input = _web_input

# ---- time.sleep ----
def _web_sleep(seconds):
    ms = int(float(seconds) * 1000)
    if ms > 0:
        js.webSleep(ms)

time.sleep = _web_sleep

# ---- terminal helpers ----
os.get_terminal_size = lambda fd=None: os.terminal_size((80, 24))
`;

const PYTHON_RUN = `
try:
    from main import main
    main()
except SystemExit:
    pass
except KeyboardInterrupt:
    pass
except Exception as exc:
    import traceback
    print(f"\\n\\033[31mGame error: {exc}\\033[0m")
    traceback.print_exc()
`;
