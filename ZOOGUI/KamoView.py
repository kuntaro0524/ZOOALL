import htmlview, threading

if __name__ == "__main__":
    htmlwork = threading.Thread(target=htmlview.Run)
    htmlwork.start()

