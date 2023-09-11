import logging
import logging.config

logname = "ZOO_today.log"
logging.config.fileConfig('logging.conf', defaults={'logfile_name':logname})
logger = logging.getLogger('ZOO')

logger.debug('1. This is debug.')
logger.info('2. This is info.')
logger.warning('3. This is warning.')
logger.error('4. This is error.')
logger.critical('5. This is critical.')
