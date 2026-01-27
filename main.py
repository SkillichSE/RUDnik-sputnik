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

    # --- SGP4 Handling ---
    async def load_satellite_async(self, sat_number):
        await asyncio.to_thread(self.load_satellite, sat_number)

    def load_satellite(self, sat_number):
        try:
            index = (sat_number - 1) * 3
            name, line1, line2 = dataset_sat(index)
        except (IndexError, ValueError):
            self.consoleTextEdit.append("❌ Satellite not found")
            return

        data = parse_tle_fields(line1, line2)

        # === TELEMETRY UI ===
        self.name_value.setText(name)
        self.num_value.setText(data["norad_id"])
        self.designator_value.setText(data["designator"])
        self.date_time_value.setText(data["epoch"])
        self.inclination_value.setText(data["inclination"])
        self.ascendation_value.setText(data["raan"])
        self.eccentricity_value.setText(data["eccentricity"])
        self.perrige_value.setText(data["perigee"])
        self.anomaly_value.setText(data["mean_anomaly"])
        self.mean_motion_value.setText(data["mean_motion"])
        self.ballistic_value.setText(data["ballistic"])
        self.dirrative_value.setText(data["derivative2"])
        self.pressure_value.setText(data["ballistic"])
        self.ephemeris_value.setText(data["ephemeris"])
        self.element_value.setText(data["element"])
        self.rottation_value.setText(data["revolution"])

        # === SGP4 ===
        self.consoleTextEdit.append("SGP-4 simulation started")
        result = simulate(
            line1,
            line2,
            datetime.now(timezone.utc),
            hours=1,
            step_min=10
        )
        for t, lat, lon, r in result:
            self.consoleTextEdit.append(f"{t} | LAT {lat:.2f} | LON {lon:.2f} | R {r:.1f} km")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()
