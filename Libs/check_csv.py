import sqlite3, csv, os, sys, copy
import MyException
import re

import ESA

if __name__ == "__main__":
    esa = ESA.ESA("test.db")
    esa.readCSV(sys.argv[1])
