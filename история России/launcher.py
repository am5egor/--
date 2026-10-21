#!/usr/bin/env python3
"""Лаунчер «Хроники Руси»: проверяет pygame, при необходимости устанавливает его и запускает игру.
Запуск: python launcher.py  (или двойной клик по start_windows.bat / start_mac_linux.command)
Если tkinter недоступен, работает консольное меню.
"""
import subprocess
import sys
import threading
from pathlib import Path

GAME = Path(__file__).resolve().with_name("chronicles_of_rus.py")
BG, FG, GOLD, PANEL = "#0f1a2e", "#e8edf5", "#e0b84f", "#182640"


def pygame_version():
    """Версия pygame или None. Проверяем в отдельном процессе, чтобы не грузить pygame в лаунчер."""
    try:
        r = subprocess.run([sys.executable, "-c", "import pygame;print(pygame.version.ver)"],
                           capture_output=True, text=True, timeout=60)
        return r.stdout.strip().splitlines()[-1] if r.returncode == 0 and r.stdout.strip() else None
    except Exception:
        return None


def install_pygame():
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pygame"],
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]


def start_game(fullscreen):
    cmd = [sys.executable, str(GAME)] + ([] if fullscreen else ["--windowed"])
    return subprocess.Popen(cmd, cwd=str(GAME.parent))


def console():
    print("ХРОНИКИ РУСИ — лаунчер")
    if not GAME.exists():
        print(f"Не найден файл игры: {GAME.name}. Положите его рядом с лаунчером.")
        return
    ver = pygame_version()
    if not ver:
        if input("pygame не установлен. Установить? [Y/n] ").strip().lower() in ("", "y", "д"):
            ok, msg = install_pygame()
            print("Готово." if ok else "Не удалось установить: " + " ".join(msg))
            ver = pygame_version()
        if not ver:
            return
    print(f"pygame {ver} найден.")
    mode = input("1 — полный экран, 2 — окно (Enter = 1): ").strip()
    start_game(mode != "2").wait()


def gui(tk):
    root = tk.Tk()
    root.title("Хроники Руси")
    root.configure(bg=BG)
    root.geometry("460x360")
    root.resizable(False, False)
    full = tk.BooleanVar(value=True)
    status = tk.StringVar(value="Проверяю pygame…")
    proc = {"p": None}

    tk.Label(root, text="ХРОНИКИ РУСИ", font=("Georgia", 28, "bold"), fg=GOLD, bg=BG).pack(pady=(26, 0))
    tk.Label(root, text="От Рюрика до наших дней", font=("Georgia", 12), fg=FG, bg=BG).pack(pady=(0, 18))
    tk.Label(root, textvariable=status, font=("Arial", 11), fg=FG, bg=BG, wraplength=400).pack(pady=(0, 10))
    tk.Checkbutton(root, text="Полный экран (в игре переключается клавишей F11)", variable=full, fg=FG, bg=BG,
                   selectcolor=PANEL, activebackground=BG, activeforeground=FG, font=("Arial", 10)).pack(pady=(0, 14))

    def btn(text, cmd, color=PANEL, fg=FG):
        b = tk.Button(root, text=text, command=cmd, font=("Arial", 13, "bold"), bg=color, fg=fg,
                      activebackground=GOLD, relief="flat", width=26, pady=6)
        b.pack(pady=4)
        return b

    play = btn("Играть", lambda: launch(), GOLD, "#1a1a1a")
    inst = btn("Установить pygame", lambda: install())
    btn("Выход", root.destroy)

    def refresh():
        def work():
            ver = pygame_version()
            ok = GAME.exists() and ver
            root.after(0, lambda: set_state(ver))
        threading.Thread(target=work, daemon=True).start()

    def set_state(ver):
        if not GAME.exists():
            status.set(f"Не найден {GAME.name}: положите его рядом с лаунчером.")
            play.config(state="disabled")
            return
        if ver:
            status.set(f"Всё готово: pygame {ver}")
            play.config(state="normal")
            inst.config(state="disabled")
        else:
            status.set("pygame не установлен. Нажмите «Установить pygame».")
            play.config(state="disabled")
            inst.config(state="normal")

    def install():
        status.set("Устанавливаю pygame, подождите…")
        inst.config(state="disabled")

        def work():
            ok, msg = install_pygame()
            ver = pygame_version()
            root.after(0, lambda: (set_state(ver), None if ver else status.set("Не удалось установить: " + " ".join(msg))))
        threading.Thread(target=work, daemon=True).start()

    def launch():
        proc["p"] = start_game(full.get())
        play.config(state="disabled")
        status.set("Игра запущена. Закройте её (Esc), чтобы вернуться.")
        poll()

    def poll():
        p = proc["p"]
        if p and p.poll() is None:
            root.after(500, poll)
        else:
            set_state(pygame_version() if p else None)
            if p:
                status.set("Игра закрыта. Можно сыграть ещё раз.")

    refresh()
    root.mainloop()


if __name__ == "__main__":
    if sys.version_info < (3, 8):
        sys.exit("Нужен Python 3.8 или новее.")
    try:
        import tkinter
    except ImportError:
        console()
    else:
        try:
            gui(tkinter)
        except tkinter.TclError:  # нет дисплея
            console()
