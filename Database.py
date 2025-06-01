#!/usr/bin/env python3
"""
__authors__    = ["Blaze Sanders"]
__email__      = ["dev@blazesanders.com"]
__license__    = "MIT"
__status__     = "Development"
__deprecated__ = "False"
__version__    = "2025.0"
__doc__        = "Manage SQLite database and store non-Personally Identifiable Information for DMuffler application"
"""

# Disable PyLint linting messages
# https://pypi.org/project/pylint/
# pylint: disable=line-too-long
# pylint: disable=invalid-name

## Standard Python libraries
import sqlite3                                  # SQlite Database
from datetime import datetime, time, timedelta 	# Manipulate calendar dates & time objects https://docs.python.org/3/library/datetime.html
from time import sleep                          # Pause program execution
import os                                       # Get filename information like directoty and file path
import csv                                      # Manipulate .CSV files for data reporting
import json                                     # Use to serialize a list of list and insert into TEXT column of SQLite database
from typing import Optional                     # TODO Give function argument an optional

## 3rd party libraries
import pytz 					                # World Timezone Definitions  https://pypi.org/project/pytz/
from pytz import timezone                       # Sync data write time to database no matter where server is located https://pypi.org/project/pytz/

## Internally developed modules
import GlobalConstants as GC

"""
    conn = sqlite3.connect('DMufflerLocal.db')
    cursor = conn.cursor()

    table = GC.DATABASE_TABLE_NAMES[GC.USERS_TABLE]
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (\
                     id INTEGER PRIMARY KEY AUTOINCREMENT,\
                     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                     first_name TEXT DEFAULT JOHN)")

    table = GC.DATABASE_TABLE_NAMES[GC.VEHICLES_TABLE]
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (\
                     id INTEGER PRIMARY KEY AUTOINCREMENT,\
                     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                     vin TEXT DEFAULT 12345678901234567),\
                     make TEXT DEFAULT TESLA,\
                     model TEXT DEFAULT Y,\
                     color TEXT DEFAULT RED")

    table = GC.DATABASE_TABLE_NAMES[GC.ENGINE_SOUNDS]
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (\
                     id INTEGER PRIMARY KEY AUTOINCREMENT,\
                     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                     wav_filename TEXT DEFAULT MC_LAREN_F1)")

    conn.commit()

    # query = fINSERT INTO {GC.DATABASE_TABLE_NAMES[GC.VEHICLES_TABLE]} (timestamp, vin) VALUES (?, ?)

    # cursor.execute(query, (now, vin))
    # conn.commit()

    Common Table Constraints
    - `PRIMARY KEY`: Uniquely identifies each record
    - `AUTOINCREMENT`: Automatically increases value for new records
    - `NOT NULL`: Column cannot contain NULL values
    - `UNIQUE`: All values in column must be different
    - `DEFAULT`: Provides a default value
    - `CHECK`: Ensures values meet specified condition
    - `FOREIGN KEY`: Links to primary key in another table
    """


class Database:

    def __init__(self, dbName: str):
        """ Constructor to initialize an Database object
        """
        # Connect to the database (create if it doesn't exist)
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()

        # Create ? (?) tables in dbName.db to run DMuffler application without internet
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {GC.DATABASE_TABLE_NAMES[GC.USERS_TABLE]} (id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT DEFAULT JOHN, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {GC.DATABASE_TABLE_NAMES[GC.VEHICLES_TABLE]}  (id INTEGER PRIMARY KEY, totalWeeklyWattHours INTEGER, currentCostPerWh REAL, weekNumber TEXT)''')
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {GC.DATABASE_TABLE_NAMES[GC.ENGINE_SOUNDS_TABLE]} (id INTEGER PRIMARY KEY, filename TEXT, cost_in_cents INTEGER, timestamp TEXT)''')

        # Create debuging logg
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS DebugLoggingTable (id INTEGER PRIMARY KEY, logMessage TEXT)''')

        # Confifure graph database at .db file creation
        self.setup_engine_sounds_tables()

        # Commit the five tables to database
        self.conn.commit()


    def setup_engine_sounds_tables(self):
        """ Prepopulate EngineSoundTable 6 free engine sounds

        """
        for asset in GC.VEHICLE_ASSETS:
            baseAudioFilename = asset.name  # Using the vehicle's name as the identifier
            now = datetime.now().isoformat() #2025-01-30T13:13:13.123456
            self.insert_engine_sounds_table(baseAudioFilename, 0, now)


    def insert_engine_sounds_table(self, baseAudioFilename: str, cost: int, now: str):
        """ Insert or update the Engine Sounds SQLite table with base audio (.wav) filenames

        Args:
            baseAudioFilename (str): CONSTANT from GlobalConstants.py

        Returns:
            int: Database index id of last row inserted
        """
        lastDatabaseIndexInserted = -1

        results, isEmpty, isValid = self.get_engine_sounds(baseAudioFilename)
        if GC.DEBUG_STATEMENTS_ON: print(f"Tuple returned was: {(results, isEmpty, isValid)}")

        try:
            if results:
                idPrimaryKeyToUpdate = results[0][2]
                self.cursor.execute("UPDATE EngineSoundsTable SET baseAudioFilename = ? WHERE id = ?", (baseAudioFilename, idPrimaryKeyToUpdate))
            else:
                self.cursor.execute("INSERT INTO EngineSoundsTable (filename, cost_in_cents, timestamp) VALUES (?, ?, ?)", (baseAudioFilename, cost, now))

        except TypeError:
            print("Error occured while inserting data...")

        lastDatabaseIndexInserted = self.cursor.lastrowid

        self.commit_changes()

        return lastDatabaseIndexInserted


    def get_engine_sounds(self, baseAudioFilename:str):
        """ Get filename from EngineSoundsTable SQLite table

        Args:
            baseAudioFilename (str): See EngineSoundsDict in GlobalConstants.py

        Returns:
            tuple: Tuple of results, isEmpty, isValid
        """
        isEmpty = False
        isValid = True


        try:
            if delta < 7:
                sql_query = """
                    SELECT timestamp, totalDailyWattHours, id
                    FROM DailyEnergyTable
                    WHERE id >= (SELECT id FROM DailyEnergyTable WHERE timestamp = ?)
                    AND id <= (SELECT id FROM DailyEnergyTable WHERE timestamp = ?)
                """

                self.cursor.execute(sql_query, (baseAudioFilename,))
                result = self.cursor.fetchall()
                if len(result) == 0:
                    isEmpty = True
                    print("Got no results!")
                return result, isEmpty, isValid
            else:
                sql_query = """
                    SELECT *
                    FROM EngineSoundsTable
                    WHERE baseAudioFilename = baseAudioFilename
                    AND id <= (SELECT id FROM DailyEnergyTable WHERE timestamp = ?)+6
                """

                self.cursor.execute(sql_query, (start_date,start_date))
                result = self.cursor.fetchall()
                if len(result) == 0:
                    isEmpty = True
                    print("Got no results!")

                return result, isEmpty, isValid

        except IndexError:
            if GC.DEBUG_STATEMENTS_ON: self.insert_debug_logging_table("INSIDE INDEX ERROR")
            return None, None, False

        except sqlite3.OperationalError:
            if GC.DEBUG_STATEMENTS_ON: self.insert_debug_logging_table(f"INSIDE OPERATIONAL ERROR")
            return None, None, False


    def commit_changes(self):
        """ Commit data inserted into a table to the *.db database file
        """
        self.conn.commit()


    def close_database(self):
        """ Close database to enable another sqlite3 instance to query a *.db database
        """
        self.conn.close()


    def get_date_time(self) -> datetime:
        """ Get date and time in Marianna, FL timezone, independent of location on server running code

        Returns:
            Datetime:
        """
        tz = pytz.timezone('America/Chicago')
        zulu = pytz.timezone('UTC')
        now = datetime.now(tz)
        if now.dst() == timedelta(0):
            now = datetime.now(zulu) - timedelta(hours=6)
            if GC.DEBUG_STATEMENTS_ON: print('Standard Time')

        else:
            now = datetime.now(zulu) - timedelta(hours=5)
            if GC.DEBUG_STATEMENTS_ON: print('Daylight Savings')

        return now


    def insert_debug_logging_table(self, logLevel: int, debugText: str):
        """ Insert debugging text in database for later review

        Args:
            debugText (str): "ERROR: " or "WARNING: " + text message to log
        """
        if logLevel == GC.ERROR_LEVEL_LOG:
            debugText = "ERROR: " + debugText
        elif logLevel == GC.WARNING_LEVEL_LOG:
            debugText = "WARNING: " + debugText

        self.cursor.execute("INSERT INTO DebugLoggingTable (logMessage) VALUES (?)", (debugText,))
        self.commit_changes()


    def query_table(self, tableName: str, searchTerm: str = None, row: Optional[int]= None, column: Optional[int]= None) -> tuple:
        """ Return every row of a table from a *.db database

        Args:
            tableName (String): Name of table in database to query
            row (Interger): Optional row from tuple to return
            column (Interger): Optional column from tuple to return

        Returns:
            result: A list of tuples from a table, where each row in table is a tuple of length n
            isEmpty: Returns True if table is empty, and False otherwise
            isValid: Returns True if table name exists in EnergyReport.db, and False otherwise

        """

        if searchTerm is None:
            sqlStatement = f"SELECT * FROM {tableName}"
        else:
            sqlStatement = f"SELECT * FROM {tableName} WHERE timestamp = ?"  #f"SELECT * FROM {tableName} WHERE content LIKE ?, ('%' + {str(searchTerm)} + '%',)" #self.cursor.execute("SELECT * FROM DatasetTable WHERE content LIKE ?", ('%' + str(searchTerm) + '%',))

        self.cursor.execute(sqlStatement, (searchTerm, ))


        isEmpty = False
        isValid = True
        result = self.cursor.fetchall()[0]

        if GC.DEBUG_STATEMENTS_ON: print("-------------------------")

        if len(result) == 0:
            isEmpty = True

        try:
            if row == None and column == None:
                return result, isEmpty, isValid
            elif column == None:
                return result[row-1], isEmpty, isValid
            else:
                if column == GC.IMAGE_URL_COLUMN_NUMBER:
                    return json.loads(result[row-1][column]), isEmpty, isValid
                else:
                    return result[row-1][column], isEmpty, isValid

        except IndexError:
            if GC.DEBUG_STATEMENTS_ON: self.insert_debug_logging_table("INSIDE INDEX ERROR")
            return None, None, False

        except sqlite3.OperationalError:
            if GC.DEBUG_STATEMENTS_ON: self.insert_debug_logging_table(f"INSIDE OPERATIONAL ERROR")
            return None, None, False


    def is_date_between(self, startDatetimeObj, endDatetimeObj, dateToCheck) -> bool:
        """ Check if a date is between two other dates

        Args:
            startDatetimeObj (datetime): Start date
            endDatetimeObj (datetime): End date
            dateToCheck (datetime): Date to check
        """
        return startDatetimeObj <= dateToCheck <= endDatetimeObj


if __name__ == "__main__":
    print("Testing DMuffler Database.py")

    db = Database("TestDMuffler.db")

    """
    db.example_tables()
    db.update_graph_table('2024-01-01', GC.RADIO_BUTTON_VALUES[0])
    db.update_graph_table('2024-01-01', GC.RADIO_BUTTON_VALUES[0])

    date = db.get_date_time()
    isoDateDay = date.isoformat()[0:10]

    results = db.query_table("DailyEnergyTable", isoDateDay)
    if GC.DEBUG_STATEMENTS_ON: print(results)


    results = db.query_table("DailyEnergyTable", "2024-01-01")
    if GC.DEBUG_STATEMENTS_ON: print(results)

    db.export_table_to_csv(["DailyEnergyTable", "WeeklyEnergyTable", "MonthlyEnergyTable", "WeekGraphTable", "MonthGraphTable", "DebugLoggingTable"])

    insertErrors = db.insert_check_in_table(1001)
    print(insertErrors)
    checkOutErrors = db.insert_check_out_table(1001)
    print(insertErrors)
    """

    db.close_database()
