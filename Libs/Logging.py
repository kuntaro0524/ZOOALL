import logging

stream_log = logging.StreamHandler()
stream_log.setLevel(logging.DEBUG)
stream_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
file_log = logging.FileHandler(filename='log.txt')
file_log.setLevel(logging.ERROR)
file_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

logging.getLogger().addHandler(stream_log)
logging.getLogger().addHandler(file_log)
logging.getLogger().setLevel(logging.DEBUG)

logging.error('ERROR')
logging.debug('DEBUGGING')
