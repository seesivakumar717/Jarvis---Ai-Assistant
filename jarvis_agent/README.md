# JARVIS — Local Laptop Automation Agent

A local, Ollama-powered assistant that can control your own laptop: files, processes,
mouse/keyboard, browser, and (optionally) voice. It pauses and asks you before any
risky or ambiguous action instead of guessing.

## Why it's structured this way

The LLM never touches your OS directly. It only ever produces a JSON "tool call".
A separate **executor** is the only code allowed to actually do things, and every
action passes through a **risk classifier** first:

```
You (voice/text)
      |
      v
 planner.py  --(asks Ollama for a JSON action plan)-->  risk.py
                                                            |
                                        +-------------------+-------------------+
                                        |                                       |
                                   low risk                              medium/high risk
                                        |                                       |
                                        v                                       v
                                 executor.py                         confirm.py (asks you,
                                        |                             waits for yes/no)
                                        v                                       |
                                   logger.py  <----------------------- confirmed? -> executor.py
```

This means:
- You can audit exactly what it's allowed to do (`config.yaml`).
- Destructive actions (delete, send, shutdown, purchase, kill a process) always pause.
- Everything it does is logged to `logs/actions.log`.

## Setup

```bash
cd jarvis_agent
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# install and run Ollama separately: https://ollama.com
ollama pull llama3.1              # or any tool-calling-capable model you prefer

# Playwright needs its browser binaries once:
playwright install chromium
```

Edit `config.yaml` to set:
- which directories the agent is allowed to touch
- which apps/processes it's allowed to launch or kill
- which actions are low / medium / high risk
- whether voice is enabled

Run it:

```bash
python3 -m jarvis.main
```

## What's a real build vs. a stub here

Working out of the box:
- Planner → Ollama JSON tool-calling
- Risk classifier + confirm-and-wait gate
- File system tool (scoped to allowlisted dirs)
- Process tool (launch/list/kill, scoped to allowlist)
- Browser tool (Playwright: navigate, click, type, read page text)
- Action logger
- Text-mode main loop (type commands, type y/n to confirm)

Stubbed, with clear TODOs, because they depend on your hardware/OS/preferences:
- `tools/input_control.py` — mouse/keyboard simulation (pyautogui) — commented with
  exact calls to uncomment; left off by default since raw keyboard/mouse control is the
  single most dangerous capability to turn on before you trust the risk gate.
- `tools/voice.py` — STT/TTS — needs you to pick a local model (whisper.cpp / piper) and
  a mic library for your OS.
- `tools/system.py` — volume/brightness/shutdown — OS-specific calls, stubbed per OS.

## Safety notes (please actually read this)

- Everything defaults to **non-destructive and scoped**. `config.yaml` starts with a
  small allowlist of directories and apps — expand it deliberately, not all at once.
- Run this as your normal user, not as admin/root. Don't disable that to "make it easier".
- Input control (`input_control.py`) is disabled until you explicitly enable it in
  config — that's the capability most likely to do something you didn't intend if the
  risk gate has a bug.
- Nothing here phones home or needs the internet except Ollama (local) and whatever
  sites you ask the browser tool to visit.
