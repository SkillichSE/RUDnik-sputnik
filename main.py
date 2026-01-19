#  ______              _______              _    _   ____
# |  ____|     /\     |__   __|     /\     | |  | | |  __|      /\
# | |__       /  \       | |       /  \    | |__| | | |_       /  \
# |  __|     / /\ \      | |      / /\ \   |  __  | |  _ \    / /\ \
# | |____   / /  \ \     | |     / ____ \  | |  | | | |_) |  / ____ \
# |______| /_/    \_\    |_|    /_/    \_\ |_|  |_| |____/  /_/    \_\

import sys
import asyncio
from PyQt5 import QtWidgets, uic
from qasync import QEventLoop, asyncSlot
from ai_logic import ai_answer  

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.sendAI.clicked.connect(self.on_send)
        self.quest.returnPressed.connect(self.on_send)

    @asyncSlot()
    async def on_send(self):
        user_text = self.quest.text()
        if not user_text.strip():
            return

        self.Answ.append(f"<b>Вы:</b> {user_text}")
        self.quest.clear()

        answer = await ai_answer(user_text)
        self.Answ.append(f"<b>ИИ:</b> {answer}")
        self.Answ.append("")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()
