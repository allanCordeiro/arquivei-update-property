import os
import sqlite3
from shutil import copyfile
from datetime import datetime


class DbNfse:
    def __init__(self):
        if not os.path.isfile('db/db_localdb.db'):
            copyfile('db/bkp_localdb.db', 'db/db_localdb.db')

        self.__db_name = 'db/db_localdb.db'

    def insert_documents(self, data):
        query = "INSERT INTO nfses (nfsehash, persiststatus, dtcreation) VALUES(?,?,?);"
        try:
            db = sqlite3.connect(self.__db_name)
            cur = db.cursor()
            cur.executemany(query, data)
            db.commit()
        except Exception as err:
            db.rollback()
            raise Exception(err)
        finally:
            db.close()

    def get_pendent_documents(self):
        query = "SELECT id, nfsehash FROM nfses WHERE persiststatus = 0;"
        try:
            db = sqlite3.connect(self.__db_name)
            cur = db.cursor()
            rows = cur.execute(query).fetchall()
            return rows
        except Exception as err:
            raise Exception(err)
        finally:
            db.close()

    def update_document(self, id_nfse):
        timestamp = datetime.now()
        dt_execution = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        query = "UPDATE nfses SET persiststatus = 1, dtexecution = ? WHERE id = ?;"
        try:
            db = sqlite3.connect(self.__db_name)
            cur = db.cursor()
            cur.execute(query, (dt_execution, id_nfse))
            db.commit()
        except Exception as err:
            db.rollback()
            raise Exception(err)
        finally:
            db.close()

    def update_cursor(self, current_cursor):
        query = "UPDATE cursor SET current_cursor = ? WHERE id = 1;"
        try:
            db = sqlite3.connect(self.__db_name)
            cur = db.cursor()
            cur.execute(query, (current_cursor,))
            db.commit()
        except Exception as err:
            db.rollback()
            raise Exception(err)
        finally:
            db.close()

    def get_cursor(self):
        query = "SELECT current_cursor FROM cursor WHERE id = 1;"
        try:
            db = sqlite3.connect(self.__db_name)
            cur = db.cursor()
            row = cur.execute(query).fetchone()
            cursor = row[0]
            if cursor is None:
                return 1
            return cursor
        except Exception as err:
            raise Exception(err)
        finally:
            db.close()
