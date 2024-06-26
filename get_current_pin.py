import Zoo
if __name__ == "__main__":
    zoo=Zoo.Zoo()
    zoo.connect()
    puck_list=zoo.getSampleInformation()

    print zoo.getCurrentPin()
