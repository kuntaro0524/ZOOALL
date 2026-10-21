import sys,math,numpy,os
import Zoo
import datetime
import ZooNavigator
import ZooMyException
import socket
import MyDate
import logging
import logging.config
import subprocess
import PuckExchanger
import PuckConfig
import ZooResume
import argparse
import BLFactory
from configparser import ConfigParser, ExtendedInterpolation

# Get information from beamline.ini file.
config = ConfigParser(interpolation=ExtendedInterpolation())
config_path = "%s/beamline.ini" % os.environ['ZOOCONFIGPATH']
config.read(config_path)

zoologdir = config.get("dirs", "zoologdir")
beamline = config.get("beamline", "beamline")
blanc_address = config.get("server", "blanc_address")
logging_conf = config.get("files", "logging_conf")

if __name__ == "__main__":
    # isDebug
    isSkipNoPins = False

    # Logging setting
    d = MyDate.MyDate()
    time_str = d.getNowMyFormat(option="date")
    logname = "%s/zoo_%s.log" % (zoologdir, time_str)

    # logging_config
    logging_config = {
    "version": 1,
    "formatters": {
        "f1": {
            "format": "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "f1",
            "stream": "ext://sys.stdout",
        },
        "fileHandler": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "f1",
            "filename": logname,  # 動的に設定
        },
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["consoleHandler", "fileHandler"],
        }
    },
    }

    logging.config.dictConfig(logging_config)
    logger = logging.getLogger('ZOO')
    logger.info("Start ZOO")

    # Initialize BLFactory
    blf = BLFactory.BLFactory()
    blf.initDevice()

    zoo=Zoo.Zoo()
    zoo.connect()

    # Command line. 'plan' is the measurement configure file (meas_file,time_limit).
    parser = argparse.ArgumentParser(description="ZOO with puck exchanger: one CSV after another.")
    parser.add_argument("plan", help="CSV with columns meas_file,time_limit (e.g. 12h, 90m, 2s=2 shifts).")
    parser.add_argument("--resume", action="store_true",
                        help="Continue after a stop: use the previous zoo_*.db of each CSV (done pins are not measured again).")
    cmd_args = parser.parse_args()

    # Read measurement configure file
    pe_config = PuckConfig.PuckConfig(cmd_args.plan)
    puck_dict = pe_config.readConfig()
    print(PuckConfig.summarize(puck_dict))

    # Resume plan: only reads/updates the previous zoo_*.db files. No hardware access.
    resume_plans = {}
    if cmd_args.resume:
        for meas_info in puck_dict:
            csv_file = meas_info['meas_file']
            if csv_file.endswith("csv"):
                resume_plans[csv_file] = ZooResume.plan_resume(csv_file)
                print(ZooResume.describe(csv_file, resume_plans[csv_file]))

    # Puck exchanger preparation
    pe = PuckExchanger.PuckExchanger(zoo)

    if cmd_args.resume:
        # The pin may remain on the goniometer when the previous run stopped.
        try:
            zoo.dismountCurrentPin()
        except ZooMyException.MyException as e:
            logger.error("Cannot dismount the current pin: %s" % e)
            print("ERROR: ゴニオのpinを外せません（%s）。SPACEの状態を確認・復旧してから再開してください。" % e)
            sys.exit(2)

    total_pins = 0
    # Currently only CSV files
    for meas_info in puck_dict:
        # Initializing
        input_file=meas_info['meas_file']
        # This can be obtained a certain value in [hours]
        time_hour=meas_info['time_limit_hour']

        #logger.info("Start processing %s" % input_file)
        if input_file.rfind("csv") != -1:
            resume_plan = resume_plans.get(input_file)
            if resume_plan is not None:
                if resume_plan["finished"]:
                    logger.info("All pins of %s have been processed. Skipped." % input_file)
                    continue
                # Pucks of the unfinished pins only. Finished ones are returned to PE.
                pe.checkCurrentPucksAndMount(input_file, planned=resume_plan["planned"])
                navi = ZooNavigator.ZooNavigator(blf, input_file, is_renew_db=False)
                navi.setTimeLimit(time_hour)
                print("TimeLimit=%s"%time_hour)
                n_pins = navi.goAround(resume_plan["db"])
            else:
                pe.checkCurrentPucksAndMount(input_file)
                navi = ZooNavigator.ZooNavigator(blf, input_file, is_renew_db=True)
                navi.setTimeLimit(time_hour)
                print("TimeLimit=%s"%time_hour)
                n_pins = navi.goAround()
        elif input_file.rfind("db") != -1:
            print("Currently, DB restart function is not available. Wait for the next release!")
            sys.exit()
            # esa_csv = "dummy.csv"
            # navi=ZooNavigator.ZooNavigator(zoo,ms,esa_csv,is_renew_db=False)
            # n_pins = navi.goAround(input_file)
        total_pins += n_pins
        # The final pin should be unmounted before changing CSV file.
        zoo.dismountCurrentPin()
        # SPACE cleaning after 1 CSV file
        zoo.cleaning()

    if total_pins == 0 and isSkipNoPins:
        logger.info("ZOO did not process any pins")
    else:
        logger.info("Start cleaning after the measurements")
        # Dismount the last pin on the goniometer
        zoo.dismountCurrentPin()
        # Dismount all pucks in SPACE
        pe.unmountAllpucksFromSPACE()
        # SPACE cleaning
        zoo.cleaning()

    zoo.disconnect()