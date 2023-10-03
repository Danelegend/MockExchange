import tkinter as tk

from twisted.internet import reactor

from TradeWindowLib.Connection import PublicPortClient


class GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Trade Window")
        self.window.resizable(width=False, height=False)

        self.frame = tk.Frame(master=self.window, width=400, height=400)
        self.frame.pack()

        self.tradeData = []
        self.labels = []

        self.CreateEmptyLabels()

    def start(self):
        self.window.mainloop()

    def Update(self, tradeData):
        print(tradeData.level)

        if len(self.tradeData) >= 10:
            self.tradeData.pop(0)

        self.tradeData.append(tradeData)

        for i in range(0, len(self.tradeData)):
            label = self.labels[i]
            label["text"] = str(self.tradeData["Level"]) + " " + str(self.tradeData["Volume"]) + " " + str(self.tradeData["Timestamp"])
            label["bg"] = "green"

    def CreateEmptyLabels(self):
        for i in range(0, 10):
            label = tk.Label(master=self.frame, text="", bg="white", width=100)
            label.place(x=0, y=10*i)
            label.pack()

            self.labels.append(label)


if __name__ == "__main__":
    gui = GUI()

    reactor.listenMulticast(8005, PublicPortClient(gui), listenMultiple=True)

    gui.start()

    reactor.run()
