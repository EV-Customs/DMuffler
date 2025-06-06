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
Example of proper SQL table creation with foreign key constraints:

    conn = sqlite3.connect('DMufflerLocal.db')
    cursor = conn.cursor()

    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON")

    # Create vehicles table first (since it will be referenced by users)
    table = GC.DATABASE_TABLE_NAMES[GC.VEHICLES_TABLE]
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (\
                     id INTEGER PRIMARY KEY AUTOINCREMENT,\
                     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                     first_name TEXT DEFAULT 'JOHN',\
                     vehicle_id INTEGER,
                     FOREIGN KEY (vehicle_id) REFERENCES Vehicles(id)")

    table = GC.DATABASE_TABLE_NAMES[GC.VEHICLES_TABLE]
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (\
                     id INTEGER PRIMARY KEY AUTOINCREMENT,\
                     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                     vin TEXT DEFAULT '12345678901234567'),\
                     make TEXT DEFAULT 'Tesla',\
                     model TEXT DEFAULT 'Model Y',\
                     color TEXT DEFAULT 'E')

    table = GC.DATABASE_TABLE_NAMES[GC.ENGINE_SOUNDS]
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} (\
                     id INTEGER PRIMARY KEY AUTOINCREMENT,\
                     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                     wav_filename TEXT DEFAULT 'MC_LAREN_F1',\
                     cost_in_cents INTEGER DEFAULT 0)")

    conn.commit()

    # Example of inserting a vehicle and linking it to a user
    # First insert the vehicle
    vehicle_query = f"INSERT INTO {GC.DATABASE_TABLE_NAMES[GC.VEHICLES_TABLE]} (vin, make, model, color) VALUES (?, ?, ?, ?)"
    cursor.execute(vehicle_query, ('ABC123456789', 'TESLA', 'Model 3', 'Blue'))
    vehicle_id = cursor.lastrowid

    # Then insert the user with a reference to the vehicle
    user_query = f"INSERT INTO {GC.DATABASE_TABLE_NAMES[GC.USERS_TABLE]} (first_name, vehicle_id) VALUES (?, ?)"
    cursor.execute(user_query, ('Alice', vehicle_id))

    conn.commit()

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

        # Enable foreign key support
        self.cursor.execute("PRAGMA foreign_keys = ON")

        # Create tables with proper relationships in dbName.db to run DMuffler application without internet
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {GC.DATABASE_TABLE_NAMES[GC.VEHICLES_TABLE]} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            vin TEXT DEFAULT '12345678901234567',
            make TEXT DEFAULT 'TESLA',
            model TEXT DEFAULT 'Y',
            color TEXT DEFAULT 'RED'
        )''')

        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {GC.DATABASE_TABLE_NAMES[GC.USERS_TABLE]} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            first_name TEXT DEFAULT 'JOHN',
            vehicle_id INTEGER,
            FOREIGN KEY (vehicle_id) REFERENCES {GC.DATABASE_TABLE_NAMES[GC.VEHICLES_TABLE]}(id)
        )''')

        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {GC.DATABASE_TABLE_NAMES[GC.ENGINE_SOUNDS_TABLE]} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            filename TEXT DEFAULT 'MC_LAREN_F1',
            cost_in_cents INTEGER DEFAULT 0
        )''')

        # Create debuging logg
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS DebugLoggingTable (id INTEGER PRIMARY KEY, logMessage TEXT)''')

        # Confifure graph database at .db file creation
        self.setup_engine_sounds_tables()

        # Commit the five tables to database
        self.conn.commit()


    def setup_engine_sounds_tables(self):
        """ Prepopulate EngineSoundTable with free engine sounds from VEHICLE_ASSETS
        """
        try:
            # Use VEHICLE_ASSETS to populate the engine sounds table
            for asset in GC.VEHICLE_ASSETS:
                now = datetime.now().isoformat() #2025-01-30T13:13:13.123456
                # Use the engineSoundID as the filename identifier
                self.insert_engine_sounds_table(asset.sound, 0, now)
        except Exception as e:
            print(f"Error in setup_engine_sounds_tables: {e}")


    def insert_engine_sounds_table(self, baseAudioFilename: str, cost: int, now: str):
        """ Insert or update the Engine Sounds SQLite table with base audio (.wav) filenames

        Args:
            baseAudioFilename (str): CONSTANT from GlobalConstants.py
            cost (int): Cost of the engine sound in cents (0 for free sounds)
            now (str): Timestamp string for this record

        Returns:
            int: Database index id of last row inserted
        """
        lastDatabaseIndexInserted = -1

        results, isEmpty, isValid = self.get_engine_sounds(baseAudioFilename)
        if GC.DEBUG_STATEMENTS_ON: print(f"Tuple returned was: {(results, isEmpty, isValid)}")

        try:
            # Get the table name from constants
            table_name = GC.DATABASE_TABLE_NAMES[GC.ENGINE_SOUNDS_TABLE]

            if results:
                # If record exists, update it
                # First element in result tuple is the ID (based on our SELECT in get_engine_sounds)
                idPrimaryKeyToUpdate = results[0][0]
                self.cursor.execute(f"UPDATE {table_name} SET filename = ?, cost_in_cents = ? WHERE id = ?",
                                   (baseAudioFilename, cost, idPrimaryKeyToUpdate))
            else:
                # If no record exists, insert a new one
                self.cursor.execute(f"INSERT INTO {table_name} (filename, cost_in_cents, timestamp) VALUES (?, ?, ?)",
                                   (baseAudioFilename, cost, now))

        except TypeError as e:
            print(f"Error occurred while inserting data: {e}")

        lastDatabaseIndexInserted = self.cursor.lastrowid

        self.commit_changes()

        return lastDatabaseIndexInserted


    def get_engine_sounds(self, baseAudioFilename:str):
        """ Get engine sound record from ENGINE_SOUNDS_TABLE using the filename

        Args:
            baseAudioFilename (str): Filename of the engine sound to look up

        Returns:
            tuple: Tuple of (results, isEmpty, isValid)
                - results: List of matching records as tuples
                - isEmpty: True if no matching records found
                - isValid: True if query executed successfully
        """
        isEmpty = False
        isValid = True

        try:
            # Use the correct table name from GlobalConstants
            table_name = GC.DATABASE_TABLE_NAMES[GC.ENGINE_SOUNDS_TABLE]

            # Search by filename
            sql_query = f"""
                SELECT id, timestamp, filename, cost_in_cents
                FROM {table_name}
                WHERE filename = ?
            """

            self.cursor.execute(sql_query, (baseAudioFilename,))
            result = self.cursor.fetchall()

            # Check if any results were found
            if len(result) == 0:
                isEmpty = True
                if GC.DEBUG_STATEMENTS_ON:
                    print(f"No engine sound found with filename: {baseAudioFilename}")

            return result, isEmpty, isValid

        except IndexError as e:
            if GC.DEBUG_STATEMENTS_ON:
                self.insert_debug_logging_table(GC.ERROR_LEVEL_LOG, f"Index error in get_engine_sounds: {str(e)}")
            return None, None, False

        except sqlite3.OperationalError as e:
            if GC.DEBUG_STATEMENTS_ON:
                self.insert_debug_logging_table(GC.ERROR_LEVEL_LOG, f"SQL error in get_engine_sounds: {str(e)}")
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


    def insert_debug_logging_table(self, logLevel=None, debugText=None):
        """ Insert debugging text in database for later review

        Args:
            logLevel (int, optional): Error level (GC.ERROR_LEVEL_LOG or GC.WARNING_LEVEL_LOG)
            debugText (str, optional): Text message to log
        """
        # Handle both old and new function signature
        if debugText is None and logLevel is not None:
            # Old usage: single parameter is the debug text
            debugText = str(logLevel)
            logLevel = None

        message = debugText
        if logLevel == GC.ERROR_LEVEL_LOG:
            message = "ERROR: " + message
        elif logLevel == GC.WARNING_LEVEL_LOG:
            message = "WARNING: " + message

        self.cursor.execute("INSERT INTO DebugLoggingTable (logMessage) VALUES (?)", (message,))
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
            if GC.DEBUG_STATEMENTS_ON: self.insert_debug_logging_table(GC.ERROR_LEVEL_LOG, "INSIDE INDEX ERROR")
            return None, None, False

        except sqlite3.OperationalError:
            if GC.DEBUG_STATEMENTS_ON: self.insert_debug_logging_table(GC.ERROR_LEVEL_LOG, "INSIDE OPERATIONAL ERROR")
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

    # Example of adding a vehicle and linking it to a user
    try:
        # First add a vehicle - using proper string constant instead of a set
        vehicle_table = GC.DATABASE_TABLE_NAMES[GC.VEHICLES_TABLE]
        db.cursor.execute(f"INSERT INTO {vehicle_table} (vin, make, model, color) VALUES (?, ?, ?, ?)",
                         ('12345678901234567', 'TESLA', 'Model Y', 'Black'))
        vehicleId = db.cursor.lastrowid

        # Then add a user with reference to the vehicle
        db.cursor.execute(f"INSERT INTO {GC.DATABASE_TABLE_NAMES[GC.USERS_TABLE]} (first_name, vehicle_id) VALUES (?, ?)",
                         ('Alice', vehicleId))

        # Commit the changes
        db.commit_changes()

        # Add a user with reference to the vehicle
        user_table = GC.DATABASE_TABLE_NAMES[GC.USERS_TABLE]
        db.cursor.execute(f"INSERT INTO {user_table} (first_name, vehicle_id) VALUES (?, ?)",
                         ('Alice', vehicleId))

        # Query the relationship
        db.cursor.execute(f"""
            SELECT u.first_name, v.make, v.model
            FROM {user_table} u
            JOIN {vehicle_table} v ON u.vehicle_id = v.id
        """)

        # Query to verify insertion
        db.cursor.execute(f"SELECT * FROM {vehicle_table} WHERE vin = ?", ('12345678901234567',))
        results = db.cursor.fetchall()
        if GC.DEBUG_STATEMENTS_ON:
            print("Vehicle Inserted:")
            for result in results:
                print(f"ID: {result[0]}, VIN: {result[2]}, Make: {result[3]}, Model: {result[4]}, Color: {result[5]}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

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
