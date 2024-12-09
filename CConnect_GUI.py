import tkinter as tk
from tkinter import *
from tkinter import ttk
from CServer_BL import *

BTN_IMAGE = BTN2_IMAGE
FONT = "Calibri"
FONT_BUTTON = (FONT,40)

# events
NEW_CONNECTION: int = 1
CLOSE_CONNECTION: int = 2
class CServerGUI(CServerBL):

    def __init__(self, host, port):
        super().__init__(host,port)

        # Attributes
        self._server_thread = None

        self._root = None
        self._canvas = None
        self._img_bg = None
        self._img_btn = None

        self._entry_IP = None
        self._entry_Port = None
        self._entry_Received = None
        self._entry_Send = None

        self._btn_start = None
        self._btn_stop = None

        self.tree = None

        # GUI initialization
        self.create_ui()

    def create_ui(self):

        self._root = tk.Tk()
        self._root.title("Server GUI")

        # Load bg image
        self._img_bg = PhotoImage(file=BG_IMAGE)
        img_width = self._img_bg.width()
        img_height = self._img_bg.height()

        # Set size of the application window = image size
        self._root.geometry(f'{img_width}x{img_height}')
        self._root.resizable(True,True)

        # Create a canvas to cover the entire window
        self._canvas = tk.Canvas(self._root)
        self._canvas.config(width=img_width,height=img_height)
        self._canvas.pack(fill='both',expand=True)
        self._canvas.create_image(0,0,anchor="nw",image=self._img_bg)

        # Add labels, the same as.. add text on canvas
        self._canvas.create_text(400,80,text='Server',font=('Calibri',60),fill='#000000')
        self._canvas.create_text(100,190,text='IP:',font=FONT_BUTTON,fill='#000000',anchor='w')
        self._canvas.create_text(100,240,text='Port:',font=FONT_BUTTON,fill='#000000',anchor='w')
        self._canvas.create_text(100,290,text='Send:',font=FONT_BUTTON,fill='#000000',anchor='w')
        self._canvas.create_text(100,340,text='Received:',font=FONT_BUTTON,fill='#000000',anchor='w')

        # Load button image
        self._img_btn = PhotoImage(file=BTN_IMAGE)
        img_btn_w = self._img_btn.width()
        img_btn_h = self._img_btn.height()

        # Button "Start"
        self._btn_start = tk.Button(self._canvas,text="Start",font=FONT_BUTTON,fg="#808080",compound="center",
                                    width=img_btn_w,height=img_btn_h,image=self._img_btn,bd=0,
                                    command=self.on_click_start)
        self._btn_start.place(x=800,y=420)

        # Button "Stop"
        self._btn_stop = tk.Button(self._canvas,text="Stop",font=FONT_BUTTON,fg="#808080",compound="center",
                                   width=img_btn_w,height=img_btn_h,image=self._img_btn,bd=0,
                                   command=self.on_click_stop,state="disabled")
        self._btn_stop.place(x=800,y=500)

        # Create Entry boxes
        self._entry_IP = tk.Entry(self._canvas, font=('Calibri',26), fg='#000000')
        self._entry_IP.insert(0,'127.0.0.1')
        self._entry_IP.place(x=320,y=168)

        self._entry_Port = tk.Entry(self._canvas,font=('Calibri',26),fg='#000000')
        self._entry_Port.insert(0,"8822")
        self._entry_Port.place(x=320,y=218)

        self._entry_Send = tk.Entry(self._canvas,font=('Calibri',26),fg='#000000')
        self._entry_Send.insert(0,"text message")
        self._entry_Send.place(x=320,y=268)

        self._entry_Received = tk.Entry(self._canvas,font=('Calibri',26),fg='#000000')
        self._entry_Received.insert(0,"...")
        self._entry_Received.place(x=320,y=318)

        self.tree = ttk.Treeview(self._canvas, columns=("IP", "Address"), show="headings")
        self.tree.heading("IP", text="IP")
        self.tree.heading("Address", text="Address")
        self.tree.place(x=800, y=150)

    def run(self):
        self._root.mainloop()

    def on_click_start(self):
        self._entry_IP.config(state="disabled")
        self._entry_Port.config(state="disabled")
        self._btn_start.config(state="disabled")
        self._btn_stop.config(state="normal")

        self._server_thread = threading.Thread(target=self.start_server)
        self._server_thread.start()

    def on_click_stop(self):
        self._entry_IP.config(state="normal")
        self._entry_Port.config(state="normal")
        self._btn_start.config(state="normal")
        self._btn_stop.config(state="disabled")

        self.stop_server()

    def fire_event(self, enum_event: int, client_handle):
        if enum_event == NEW_CONNECTION:
            data = client_handle.address
            self.tree.insert('', tk.END, value=data)
        if enum_event == CLOSE_CONNECTION:

            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                if values and str(client_handle._address[1] in [str(value).lower() for value in values]):
                    self.tree.delete(item)


if __name__ == "__main__":
    server = CServerGUI(CLIENT_HOST, PORT)
    server.run()


