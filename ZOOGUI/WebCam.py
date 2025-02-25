import tkinter
import requests, numpy, threading
from PIL import Image, ImageTk
from io import BytesIO

class WebCam:
    def Run(self):
        self.url = ["192.168.231.23", "192.168.231.24"]
        self.nurl = len(self.url)

        self.win = tkinter.Tk()
        self.win.title("Remote View")
        self.win.resizable(width=False, height=False)

        self.var = tkinter.IntVar()
        self.var.set(0)
        self.rbtn = [0] * self.nurl
        for xd in range(self.nurl):
            self.rbtn[xd] = tkinter.Radiobutton(self.win, value=xd, variable=self.var, text="WebCam%d : %s"%(xd, self.url[xd]))
            self.rbtn[xd].grid(row=1, column=xd, pady=5)

        self.canvas = tkinter.Canvas(self.win, width=640, height=480, bg="white")
        self.canvas.grid(row=2, column=0, columnspan=self.nurl)

#        self.btn_run_kamo = tkinter.Button(self.win, text="Run KAMO View", command=self.RunKamo)
#        self.btn_run_kamo.grid(row=3, column=0, columnspan=self.nurl, pady=5)

        self.win.after(100, self.Update)
        self.win.mainloop()

    def Update(self):
        global tkimg
        req = requests.get("http://%s/cgi-bin/camera?resolution=640"%self.url[self.var.get()])
        img = Image.open(BytesIO(req.content))
        tkimg = ImageTk.PhotoImage(img)
        self.canvas.create_image(320, 240, image=tkimg)
        self.win.after(100, self.Update)

    def RunKamo(self):
        import htmlview
        htmlwork = threading.Thread(target=htmlview.Run)
        htmlwork.start()

    def Close():
        self.win.destory()

if __name__ == "__main__":
    webcam = WebCam()
    camwork = threading.Thread(target=webcam.Run)
    camwork.start()
