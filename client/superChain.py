import tkinter as tk
from tkinter import ttk
VISIABLE_X_INIT=960
VISIABLE_Y_INIT=720
INPUTBOX_LENGTH=40
COMMIT_LOG_WIDTH=100
COMMIT_LOG_HEIGHT=10
LOG_WIDTH=112
LOG_HEIGHT=20

class Window:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("SuperChain")
        # self.root.geometry(str(VISIABLE_X_INIT) + "x" + str(VISIABLE_Y_INIT))
        self.root.rowconfigure(0, weight=3)
        self.root.rowconfigure(1, weight=5)
        self._set_input_frame()
        self._set_log_frame()

    def _set_input_frame(self):
        input_frame=tk.LabelFrame(self.root,text="Input",font=("黑体",12),borderwidth=5, width=COMMIT_LOG_WIDTH)
        input_frame.grid(row=0,stick=tk.NW)
        # input_frame.grid_propagate(0)
        main_server_label=tk.Label(input_frame,text="主服务器地址")
        main_server_label.grid(row=0,column=0,sticky=tk.W)
        main_server_input=tk.Entry(input_frame,show=None,width=INPUTBOX_LENGTH)
        main_server_input.grid(row=0,column=1,sticky=tk.W)
        to_commit_log_label = tk.Label(input_frame,text="待提交日志")
        to_commit_log_label.grid(row=1,column=0,sticky=tk.W)
        to_commit_log_area=tk.Text(input_frame,width=COMMIT_LOG_WIDTH, height=COMMIT_LOG_HEIGHT)
        to_commit_log_area.grid(row=1,column=1, sticky=tk.W)
        # to_commit_log_area.insert('end', 'new material to insert', ('highlightline', 'recent', 'warning'))
        # to_commit_log_area.insert("2.0","this is a begin test piece.\n")
        # end = to_commit_log_area.index("end")
        # to_commit_log_area.insert(f"{end}","这是一段测试数据")
        # 打开日志文件
        open_log_button = tk.Button(input_frame, text="打开日志文件", border=5, borderwidth=5)
        open_log_button.grid(row=2, column=0, sticky=tk.NW)
        # 提交
        submit_button = tk.Button(input_frame, text="提交",border=5, borderwidth=5)
        submit_button.grid(row=2, column=1, sticky=tk.NW)

    def _set_log_frame(self):
        log_frame = tk.LabelFrame(self.root,text="Log",font=("黑体",12),borderwidth=5,width=LOG_WIDTH)
        log_frame.grid(row=1,stick=tk.NW)
        log_area=tk.Text(log_frame, width=LOG_WIDTH, height=LOG_HEIGHT)
        log_area.grid(row=0,column=0, sticky=tk.NW)

    def run(self):
        self.root.mainloop()

if __name__=="__main__":
    window = Window()
    window.run()