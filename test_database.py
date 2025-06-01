import sys
from unittest.mock import MagicMock, patch, call
import unittest
from datetime import datetime, timedelta

mock_gc_for_sys = MagicMock()
import GlobalConstants as RealGC

mock_gc_for_sys.VEHICLE_ASSETS = [
    RealGC.VehicleAsset("SOUND_ID_1", "Sound One", "img1.png", "sound1.wav"),
    RealGC.VehicleAsset("SOUND_ID_2", "Sound Two", "img2.png", "sound2.wav"),
]
mock_gc_for_sys.DATABASE_TABLE_NAMES = RealGC.DATABASE_TABLE_NAMES
mock_gc_for_sys.USERS_TABLE = RealGC.USERS_TABLE
mock_gc_for_sys.VEHICLES_TABLE = RealGC.VEHICLES_TABLE
mock_gc_for_sys.ENGINE_SOUNDS_TABLE = RealGC.ENGINE_SOUNDS_TABLE
mock_gc_for_sys.DEBUG_STATEMENTS_ON = False
mock_gc_for_sys.ERROR_LEVEL_LOG = RealGC.ERROR_LEVEL_LOG
mock_gc_for_sys.WARNING_LEVEL_LOG = RealGC.WARNING_LEVEL_LOG
mock_gc_for_sys.IMAGE_URL_COLUMN_NUMBER = 3

sys.modules['GlobalConstants'] = mock_gc_for_sys

from Database import Database
import sqlite3

class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db_name = ":memory:"
        self.db = Database(self.db_name)

    def tearDown(self):
        self.db.close_database()

    def test_01_init_creates_tables(self):
        tables_to_check = [
            mock_gc_for_sys.DATABASE_TABLE_NAMES[mock_gc_for_sys.USERS_TABLE],
            mock_gc_for_sys.DATABASE_TABLE_NAMES[mock_gc_for_sys.VEHICLES_TABLE],
            mock_gc_for_sys.DATABASE_TABLE_NAMES[mock_gc_for_sys.ENGINE_SOUNDS_TABLE],
            "DebugLoggingTable"
        ]
        for table_name in tables_to_check:
            with self.subTest(table=table_name):
                try:
                    self.db.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    self.db.cursor.fetchone()
                except sqlite3.OperationalError as e:
                    self.fail(f"Table {table_name} was not created or query failed: {e}")

        engine_sounds_table_name = mock_gc_for_sys.DATABASE_TABLE_NAMES[mock_gc_for_sys.ENGINE_SOUNDS_TABLE]
        self.db.cursor.execute(f"SELECT COUNT(*) FROM {engine_sounds_table_name}")
        count = self.db.cursor.fetchone()[0]
        self.assertEqual(count, len(mock_gc_for_sys.VEHICLE_ASSETS))

    def test_02_setup_engine_sounds_tables(self):
        engine_sounds_table = mock_gc_for_sys.DATABASE_TABLE_NAMES[mock_gc_for_sys.ENGINE_SOUNDS_TABLE]
        self.db.cursor.execute(f"DELETE FROM {engine_sounds_table}")
        self.db.commit_changes()
        self.db.setup_engine_sounds_tables()
        self.db.cursor.execute(f"SELECT COUNT(*) FROM {engine_sounds_table}")
        count = self.db.cursor.fetchone()[0]
        self.assertEqual(count, len(mock_gc_for_sys.VEHICLE_ASSETS))

    def test_03_insert_engine_sounds_table_new_sound(self):
        filename = "NewSound.wav"
        cost = 100
        timestamp_now = datetime.now().isoformat()
        engine_sounds_table = mock_gc_for_sys.DATABASE_TABLE_NAMES[mock_gc_for_sys.ENGINE_SOUNDS_TABLE]
        self.db.cursor.execute(f"DELETE FROM {engine_sounds_table} WHERE filename = ?", (filename,))
        self.db.commit_changes()
        with patch.object(self.db, 'get_engine_sounds', return_value=(None, True, True)) as mock_get_sound:
            last_id = self.db.insert_engine_sounds_table(filename, cost, timestamp_now)
        mock_get_sound.assert_called_once_with(filename)
        self.assertIsNotNone(last_id)
        self.db.cursor.execute(f"SELECT filename, cost_in_cents, timestamp FROM {engine_sounds_table} WHERE filename = ?", (filename,))
        row = self.db.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], filename)
        self.assertEqual(row[1], cost)
        self.assertEqual(row[2], timestamp_now)

    @patch('Database.datetime')
    @patch('Database.pytz.timezone')
    def test_04_get_date_time(self, mock_pytz_timezone, mock_datetime_module_in_db):
        mock_std_dt_now_local = datetime(2023, 1, 15, 12, 0, 0)
        mock_std_dt_zulu_equiv = datetime(2023, 1, 15, 18, 0, 0)

        mock_chicago_tz_std = MagicMock(name="ChicagoMockSTD")
        mock_chicago_tz_std.dst.return_value = timedelta(0)
        mock_utc_tz = MagicMock(name="UTCMock")

        def timezone_side_effect_std(tz_name):
            if tz_name == 'America/Chicago': return mock_chicago_tz_std
            elif tz_name == 'UTC': return mock_utc_tz
            return MagicMock(name=f"UnexpectedTZMockSTD_{tz_name}")
        mock_pytz_timezone.side_effect = timezone_side_effect_std

        def now_side_effect_std(tz=None):
            # print(f"DEBUG STD: datetime.now called with tz='{str(tz)}' (id: {id(tz)}) vs mock_utc_tz (id: {id(mock_utc_tz)})")
            if tz is mock_utc_tz:
                # print(f"DEBUG STD: Matched mock_utc_tz, returning {mock_std_dt_zulu_equiv}")
                return mock_std_dt_zulu_equiv
            elif tz is mock_chicago_tz_std:
                # print(f"DEBUG STD: Matched mock_chicago_tz_std, returning {mock_std_dt_now_local}")
                return mock_std_dt_now_local
            # print(f"DEBUG STD: No match, returning very old date")
            return datetime(1970,1,1) # Return an obviously wrong date for unexpected calls
        mock_datetime_module_in_db.now.side_effect = now_side_effect_std

        dt_obj_std = self.db.get_date_time()
        self.assertIsInstance(dt_obj_std, datetime)
        self.assertEqual(dt_obj_std, mock_std_dt_zulu_equiv - timedelta(hours=6))

        mock_pytz_timezone.reset_mock(side_effect=True)
        mock_datetime_module_in_db.reset_mock(side_effect=True)
        mock_datetime_module_in_db.now.side_effect = None

        mock_dst_dt_now_local = datetime(2023, 6, 15, 12, 0, 0)
        mock_dst_dt_zulu_equiv = datetime(2023, 6, 15, 17, 0, 0)

        mock_chicago_tz_dst = MagicMock(name="ChicagoMockDST")
        mock_chicago_tz_dst.dst.return_value = timedelta(hours=1)

        def timezone_side_effect_dst(tz_name):
            if tz_name == 'America/Chicago': return mock_chicago_tz_dst
            elif tz_name == 'UTC': return mock_utc_tz
            return MagicMock(name=f"UnexpectedTZMockDST_{tz_name}")
        mock_pytz_timezone.side_effect = timezone_side_effect_dst

        def now_side_effect_dst(tz=None):
            if tz is mock_chicago_tz_dst: return mock_dst_dt_now_local
            elif tz is mock_utc_tz: return mock_dst_dt_zulu_equiv
            return datetime(1970,1,1)
        mock_datetime_module_in_db.now.side_effect = now_side_effect_dst

        dt_obj_dst = self.db.get_date_time()
        self.assertIsInstance(dt_obj_dst, datetime)
        self.assertEqual(dt_obj_dst, mock_dst_dt_zulu_equiv - timedelta(hours=5))

    def test_05_insert_debug_logging_table(self):
        self.db.insert_debug_logging_table(mock_gc_for_sys.ERROR_LEVEL_LOG, "Test error message")
        self.db.insert_debug_logging_table(mock_gc_for_sys.WARNING_LEVEL_LOG, "Test warning message")
        self.db.insert_debug_logging_table(3, "Test other message")
        self.db.cursor.execute("SELECT logMessage FROM DebugLoggingTable ORDER BY id")
        rows = self.db.cursor.fetchall()
        logs = [row[0] for row in rows]
        expected_logs = ["ERROR: Test error message", "WARNING: Test warning message", "Test other message"]
        self.assertEqual(logs, expected_logs)

    def test_06_is_date_between(self):
        start = datetime(2023, 1, 10); end = datetime(2023, 1, 20)
        self.assertTrue(self.db.is_date_between(start, end, datetime(2023, 1, 15)))
        self.assertTrue(self.db.is_date_between(start, end, start))
        self.assertTrue(self.db.is_date_between(start, end, end))
        self.assertFalse(self.db.is_date_between(start, end, datetime(2023, 1, 9)))
        self.assertFalse(self.db.is_date_between(start, end, datetime(2023, 1, 21)))

    def test_07_commit_and_close(self):
        original_conn = self.db.conn
        self.db.conn = MagicMock(spec=sqlite3.Connection)

        self.db.commit_changes()
        self.db.conn.commit.assert_called_once()

        self.db.close_database()
        self.db.conn.close.assert_called_once()

        self.db.conn = original_conn

if __name__ == '__main__':
    unittest.main()
