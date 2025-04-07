class ManagerServerData:
    def __init__(self, startMsg):
        self.connectedCompsState = {
            "orbital": False,
            "cyber": False,
            "operational": False,
        }
        data = startMsg["data"]
        self.tle = data["tle"]
        self.attacks = data["attacks"]
        self.time = data["time"]
        self.night_probability = data["night_probability"]

        self.min = data["min"]
        self.max = data["max"]
