import requests
from datetime import datetime, timedelta

class WebSocketBSS:

    def __init__(self):
        self.isInit = False
        self.api_url = "http://localhost:10302/command"
        self.headers = {
            "Content-Type": "application/json"
        }

    def beamstopper(self, switch):
        if switch == "on":
            command = {
                "command":"bss_function",
                "function":"BeamStop.insert",
                "param":""
            }

        elif switch == "off":
            command = {
                "command":"bss_function",
                "function":"BeamStop.remove",
                "param":""
            }

        response = requests.post(self.api_url, headers=self.headers, json=command)
        return response.json()
    
    def collimator(self, switch):
        if switch == "on":
            command = {
                "command":"bss_function",
                "function":"Collimator.insert",
                "param":""
            }
        elif switch == "off":
            command = {
                "command":"bss_function",
                "function":"Collimator.remove",
                "param":""
            }
        
        response = requests.post(self.api_url, headers=self.headers, json=command)
        return response.json()

    def light(self, switch):
        if switch == "on":
            command = {
                "command":"bss_function",
                "function":"BackLight.on",
                "param":""
            }
        elif switch == "off":
            command = {
                "command":"bss_function",
                "function":"BackLight.off",
                "param":""
            }
        
        response = requests.post(self.api_url, headers=self.headers, json=command)
        return response.json()

    def intensityMonitor(self, switch):
        if switch == "on":
            command = {
                "command":"bss_function",
                "function":"IntensityMonitor.on",
                "param":""
            }

        elif switch == "off":
            command = {
                "command":"bss_function",
                "function":"IntensityMonitor.off",
                "param":""
            }

        response = requests.post(self.api_url, headers=self.headers, json=command)
        return response.json()

    def cryoStage(self, switch):
        if switch == "on":
            command = {
                "command":"bss_function",
                "function":"CryoStream.on",
                "param":"0"
            }
        elif switch == "off":
            command = {
                "command":"bss_function",
                "function":"CryoStream.off",
                "param":"0"
            }
        response = requests.post(self.api_url, headers=self.headers, json=command)
        return response.json()

    def removeAtt(self, trans=1.0):
        trans_str = f"{trans:.5f}"
        print(trans_str)
        command = {
            "command":"bss_function",
            #"function":"Attenuator.set",
            "function":"Attenuator.set",
            "param": "0"
        }
        print(command)
        response = requests.post(self.api_url, headers=self.headers, json=command)
        return response.json()

    def shutter(self, switch):
        if switch == "open":
            command = {
                "command":"bss_function",
                "function":"STShutter.open",
                "param":""
            }
        elif switch == "close":
            command = {
                "command":"bss_function",
                "function":"STShutter.close",
                "param":""
            }
        response = requests.post(self.api_url, headers=self.headers, json=command)
        return response.json()

if __name__ == "__main__":
    ws = WebSocketBSS()
    #print(ws.beamstopper("off"))
    #print(ws.collimator("on"))
    #print(ws.collimator("off"))
    #print(ws.intensityMonitor("on"))
    #print(ws.intensityMonitor("off"))
    #print(ws.light("on"))
    #print(ws.light("off"))
    #print(ws.beamstopper("on"))
    #print(ws.beamstopper("off"))
    #print(ws.collimator("on"))
    #print(ws.collimator("off"))
    #print(ws.intensityMonitor("off"))
    print(ws.cryoStage("off"))
    print(ws.cryoStage("on"))
    #print(ws.removeAtt())
    #import time
    #time.sleep(5.0)
    #print(ws.shutter("open"))
    #time.sleep(5.0)
    #print(ws.shutter("close"))