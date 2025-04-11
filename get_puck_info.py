import Zoo
if __name__ == "__main__":
    zoo=Zoo.Zoo()
    zoo.connect()
    puck_list=zoo.getSampleInformation()

    for puck in puck_list:
        print(puck, end=' ')
