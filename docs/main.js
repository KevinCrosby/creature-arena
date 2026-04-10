'use strict';

/* ------------------------------------------------------------------ */
/* Game file list (copied to docs/game/ by CI)                        */
/* ------------------------------------------------------------------ */
const GAME_FILES = [
  'achievements.py', 'battle.py', 'breeding.py', 'collection.py',
  'creature.py', 'data.py', 'display.py', 'evolution.py', 'items.py',
  'main.py', 'pokedex.py', 'replay.py', 'save_manager.py', 'story.py',
  'tournament.py', 'trading.py', 'weather.py',
];

/* ------------------------------------------------------------------ */
/* SharedArrayBuffer for synchronous input                            */
/* Layout: [0..3]=state(Int32) [4..7]=length(Int32) [8..]=data(Uint8) */
/* ------------------------------------------------------------------ */
const INPUT_BUF = 4096;
let sharedBuffer, inputState, inputLength, inputData;

/* ------------------------------------------------------------------ */
/* Terminal                                                            */
/* ------------------------------------------------------------------ */
const term = new Terminal({
  cursorBlink: true,
  fontSize: 14,
  fontFamily: '"Fira Code","Cascadia Code",Menlo,monospace',
  theme: {
    background:  '#1a1a2e',  foreground:    '#e0e0e0',
    cursor:      '#50fa7b',  cursorAccent:  '#1a1a2e',
    selectionBackground: '#44475a80',
    black:   '#1a1a2e', red:     '#ff5555', green:   '#50fa7b',
    yellow:  '#f1fa8c', blue:    '#6272a4', magenta: '#ff79c6',
    cyan:    '#8be9fd', white:   '#f8f8f2',
    brightBlack:  '#44475a', brightRed:     '#ff6e6e',
    brightGreen:  '#69ff94', brightYellow:  '#ffffa5',
    brightBlue:   '#d6acff', brightMagenta: '#ff92df',
    brightCyan:   '#a4ffff', brightWhite:   '#ffffff',
  },
  scrollback: 5000,
  convertEol: true,
});

const fitAddon = new FitAddon.FitAddon();
term.loadAddon(fitAddon);
term.open(document.getElementById('terminal'));
fitAddon.fit();
window.addEventListener('resize', () => fitAddon.fit());

/* ------------------------------------------------------------------ */
/* Keyboard / paste → shared buffer                                   */
/* ------------------------------------------------------------------ */
let currentLine = '';
let waitingForInput = false;

function submitLine() {
  const enc = new TextEncoder().encode(currentLine);
  inputData.set(enc);
  Atomics.store(inputLength, 0, enc.length);
  Atomics.store(inputState,  0, 1);          // READY
  Atomics.notify(inputState, 0);
  currentLine = '';
  waitingForInput = false;
}

term.onData((data) => {
  if (!waitingForInput) return;
  for (const ch of data) {
    if (ch === '\r') {                        // Enter
      term.write('\r\n');
      submitLine();
      return;
    }
    if (ch === '\x7f' || ch === '\b') {       // Backspace
      if (currentLine.length) {
        currentLine = currentLine.slice(0, -1);
        term.write('\b \b');
      }
      continue;
    }
    if (ch >= ' ') {                          // printable
      currentLine += ch;
      term.write(ch);
    }
  }
});

/* ------------------------------------------------------------------ */
/* Web Worker messages                                                 */
/* ------------------------------------------------------------------ */
const worker     = new Worker('worker.js');
const overlayEl  = document.getElementById('loading-overlay');
const loadTxtEl  = document.getElementById('loading-text');

worker.onmessage = ({ data }) => {
  switch (data.type) {
    case 'stdout':
    case 'stderr':
      term.write(data.text);
      break;
    case 'input':
      waitingForInput = true;
      break;
    case 'loading':
      if (loadTxtEl) loadTxtEl.textContent = data.text;
      term.write('\x1b[33m' + data.text + '\x1b[0m\r\n');
      break;
    case 'ready':
      if (overlayEl) overlayEl.classList.add('hidden');
      break;
    case 'error':
      if (overlayEl) overlayEl.classList.add('hidden');
      term.write('\x1b[31m❌ ' + data.text + '\x1b[0m\r\n\r\n');
      term.write('Run it locally instead:\r\n');
      term.write('  git clone https://github.com/KevinCrosby/creature-arena\r\n');
      term.write('  cd creature-arena && python3 main.py\r\n');
      break;
    case 'exit':
      term.write('\r\n\x1b[36mGame ended. Refresh to play again!\x1b[0m\r\n');
      waitingForInput = false;
      break;
  }
};

/* ------------------------------------------------------------------ */
/* Boot                                                                */
/* ------------------------------------------------------------------ */
if (typeof SharedArrayBuffer === 'undefined') {
  if (overlayEl) overlayEl.classList.add('hidden');
  term.write('\x1b[33m⏳ Enabling cross-origin isolation…\x1b[0m\r\n');
  term.write('If this message persists after a refresh, your browser may\r\n');
  term.write('not support SharedArrayBuffer. Play locally instead:\r\n\r\n');
  term.write('  git clone https://github.com/KevinCrosby/creature-arena\r\n');
  term.write('  cd creature-arena && python3 main.py\r\n');
} else {
  sharedBuffer = new SharedArrayBuffer(8 + INPUT_BUF);
  inputState   = new Int32Array(sharedBuffer, 0, 1);
  inputLength  = new Int32Array(sharedBuffer, 4, 1);
  inputData    = new Uint8Array(sharedBuffer, 8);
  worker.postMessage({ type: 'init', sharedBuffer, gameFiles: GAME_FILES });
}
