#  ______              _______              _    _   ____
# |  ____|     /\     |__   __|     /\     | |  | | |  __|      /\
# | |__       /  \       | |       /  \    | |__| | | |_       /  \
# |  __|     / /\ \      | |      / /\ \   |  __  | |  _ \    / /\ \
# | |____   / /  \ \     | |     / ____ \  | |  | | | |_) |  / ____ \
# |______| /_/    \_\    |_|    /_/    \_\ |_|  |_| |____/  /_/    \_\

import sys
import asyncio
from datetime import datetime, timezone
from PyQt5 import QtWidgets, uic
from qasync import QEventLoop, asyncSlot
from ai_logic import ai_answer
from tle_loader import save_tle, dataset_sat, parse_tle_fields
from sgp4_core import simulate


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)

        # --- AI ---
        self.sendAI.clicked.connect(self.on_send)
        self.quest.returnPressed.connect(self.on_send)
        self.Answ.setReadOnly(True)

        # --- Console / Commands ---
        self.consoleTextEdit.setReadOnly(True)
        self.command_buffer = []
        self.sendCommandButton.clicked.connect(self.add_command_to_console)
        self.sendPackButton.clicked.connect(self.send_command_pack)
        self.commandLineEdit.returnPressed.connect(self.add_command_to_console)

        # --- SGP4 ---
        self.consoleTextEdit.append("[SYSTEM] Console ready\n")
        save_tle()
        self.consoleTextEdit.append("✔ TLE database loaded")

    # --- AI Slot ---
    @asyncSlot()
    async def on_send(self):
        user_text = self.quest.text().strip()
        if not user_text:
            return

        self.Answ.append(f"<b>Вы:</b> {user_text}")
        self.quest.clear()

        answer = await ai_answer(user_text)
        self.Answ.append(f"<b>ИИ:</b> {answer}\n")

    # --- Command Handling ---
    def add_command_to_console(self):
        command = self.commandLineEdit.text().strip()
        if not command:
            return

        self.consoleTextEdit.append(f"> {command}")
        self.commandLineEdit.clear()

        if command.lower().startswith("sat "):
            try:
                sat_number = int(command.split()[1])
            except (IndexError, ValueError):
                self.consoleTextEdit.append("❌ Invalid satellite number")
                return
            asyncio.create_task(self.load_satellite_async(sat_number))
        else:
            self.command_buffer.append(command)

    def send_command_pack(self):
        if not self.command_buffer:
            self.consoleTextEdit.append("[INFO] No commands to send\n")
            return

        self.consoleTextEdit.append("[PACK] Sending command pack...")
        for cmd in self.command_buffer:
            self.consoleTextEdit.append(f"[SENT] {cmd}")
        self.consoleTextEdit.append("[PACK] Done\n")
        self.command_buffer.clear()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()

