""" MODULE backup.py
This module contains functions for DataFrame interactions such as CRUD
"""

import re
import os
import shutil
import pandas as pd
import configs.config as conf
from datetime import datetime

def createRecord(id: int, name: str, birthday: str):
    df = pd.DataFrame(pd.read_csv(conf.DB_PATH, delimiter=';'))
    if df.loc[df['id'] == id].empty == True:
        df.loc[len(df.index)] = [id, name, birthday]
        df.to_csv(conf.DB_PATH, sep=';', index=False)
        return 1
    else:
        return 0

def loadDB(db):
    df = pd.DataFrame(pd.read_csv(db, delimiter=';'))
    df.to_csv(conf.DB_PATH, sep=';', index=False)

def readRecords(returnType='DataFrame'):
    df = pd.DataFrame(pd.read_csv(conf.DB_PATH, delimiter=';'))
    if returnType == 'DataFrame':
        return df
    elif returnType == 'dict':
        return df.to_dict("records")

def readRecord(id: int, returnType='DataFrame'):
    """
    Parameters
    ----------
    id : int
        takes user id
    returnType : DataFrame or dict
        used for changing return record type
    """
    df = pd.DataFrame(pd.read_csv(conf.DB_PATH, delimiter=';'))
    if returnType == 'DataFrame':
        return df.loc[df['id'] == id]
    elif returnType == 'dict':
        return df.loc[df['id'] == id].to_dict("records")[0]

# TODO: change hardcoded fields to *args
def updateRecord(id: int, name: str=None, birthday: str=None):
    df = pd.DataFrame(pd.read_csv(conf.DB_PATH, delimiter=';'))
    newData = [id, name, birthday]
    df.loc[df['id'] == id] = newData
    df.to_csv(conf.DB_PATH, sep=';', index=False)

def deleteRecord(id: int):
    df = pd.DataFrame(pd.read_csv(conf.DB_PATH, delimiter=';'))
    df.drop(df[df['id'] == id].index, inplace=True)
    df.to_csv(conf.DB_PATH, sep=';', index=False)

def backupDB(dfPath: str, checkDate: bool=True):
    if checkDate:
        for filename in os.listdir("./users_backup"):
            fileDate = re.search(r"(\d+-\d+-\d+)", filename)
            if fileDate != None:
                if datetime.strptime(fileDate.group(1), "%d-%m-%Y").date() == datetime.now().date():
                    print(f"\nDatabase backup on {datetime.now().date()} already exist\n")
                    return 0
    shutil.copyfile(dfPath, (f"users_backup/users{datetime.now().day}-{datetime.now().month}-{datetime.now().year}_{datetime.now().hour}-{datetime.now().minute}-{datetime.now().second}.csv"))
    print(f"\nDatabase backup on {datetime.now().date()} complete!\n")
    return 1

