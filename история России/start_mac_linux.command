#!/bin/bash
cd "$(dirname "$0")"
python3 launcher.py || { echo "Не удалось запустить. Установите Python 3.8+."; read -n 1 -s -r -p "Нажмите любую клавишу…"; }
