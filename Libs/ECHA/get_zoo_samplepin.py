import ECHA.ESAloaderAPI as ESAloaderAPI


if __name__ == '__main__':
    zoo_id = 12
    esa = ESAloaderAPI.ESAloaderAPI(zoo_id)

    esa.getSamplePin()


