from pywinauto import application
from pywinauto import timings
import time
import os

app = application.Application()
app.start("C:/KiwoomFlash3/bin/nkministarter.exe")

title = "번개3 Login"
dlg = timings.WaitUntilPasses(20, 0.5, lambda: app.window_(title=title))

pass_ctrl = dlg.Edit2
pass_ctrl.SetFocus()
pass_ctrl.TypeKeys('tmdtn12')

pass_ctrl = dlg.Edit3
pass_ctrl.SetFocus()
pass_ctrl.TypeKeys('rlatmdtn1!')

btn_ctrl = dlg.Button0
btn_ctrl.Click()

time.sleep(50)
os.system("taskkill /im nkmini.exe")
