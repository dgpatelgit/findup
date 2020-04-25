import logging
import os
import sqlite3


class DB:
    def __init__(self):
        """
        Important contructor that opens database connection and also creates
        required tables if db is created for the first time.
        """
        self.clog = logging.getLogger("CORE.DB")

        # Create db folder if not exists.
        dbFolder = "./db"
        os.makedirs(name=dbFolder, exist_ok=True)

        # Opens / creates a new database file.
        dbFile = "{dbFolder}/findup.db".format(dbFolder=dbFolder)
        self.conn = sqlite3.connect(dbFile)

    def createDbs(self):
        # Create scan table if not exists.
        query = '''
            CREATE TABLE IF NOT EXISTS "scan" (
                "id"                    INTEGER PRIMARY KEY AUTOINCREMENT,
                "name"                  VARCHAR(50),
                "root_path"             TEXT,
                "state"                 INTEGER,
                "folder_count"          INTEGER,
                "file_count"            INTEGER,
                "total_size_in_bytes"   INTEGER,
                "created_timestamp"     INTEGER,
                "modified_timestamp"	INTEGER
            );
        '''
        self.execInsert(query, None, True)

        query = '''
            CREATE TABLE IF NOT EXISTS "fsobject" (
                "id"                    INTEGER PRIMARY KEY AUTOINCREMENT,
                "scan_id"               INTEGER,
                "parent_id"             INTEGER,
                "type"                  INTEGER,
                "full_path"             TEXT,
                "state"                 INTEGER,
                "size_in_bytes"         INTEGER,
                "content_hash"          TEXT,
                "created_timestamp"     INTEGER,
                "modified_timestamp"	INTEGER
            );
        '''
        self.execInsert(query, None, True)

    def execInsert(self, query, params, commit_immediately):
        """
        Execute a insert query with filter params
        :param query:  Sqlite insert query.
        :param params: Params as a collection, if its None, then only query will be executed.
        :param commit_immediately: If True, query will be commit to DB after execution, if False, query will be executed without commit. Caller must ensure to call commit() function once done with all insertions.
        :return: Last inserted Id.
        """

        self.clog.info("Executing insert query: {query} params: {params}".format(
            query=query, params=params))

        cur = self.conn.cursor()
        if params is not None:
            cur.execute(query, params)
        else:
            cur.execute(query)

        if commit_immediately:
            self.conn.commit()

        return cur.lastrowid

    def execDelete(self, query, params, commit_immediately):
        """
        Execute a delete query with filter params
        :param query:  Sqlite delete query.
        :param params: Params as a collection, if its None, then only query will be executed.
        :param commit_immediately: If True, query will be commit to DB after execution, if False, query will be executed without commit. Caller must ensure to call commit() function once done with all insertions.
        :return: Nothing.
        """
        self.clog.info("Executing delete query: {query} params: {params}".format(
            query=query, params=params))

        cur = self.conn.cursor()
        if params is not None:
            cur.execute(query, params)
        else:
            cur.execute(query)

        if commit_immediately:
            self.conn.commit()

    def commit(self):
        """
        Commit the executed queries into database file.
        :return: Nothing.
        """
        self.conn.commit()

    def fetchAll(self, query, params):
        """
        Fetches all the rows as per query and params.
        If params is None, its is ignored.
        :return: Collection of tuple of rows matching query
        """
        self.clog.info("Executing select query: {query}".format(query=query))

        cur = self.conn.cursor()
        if params is not None:
            cur.execute(query, params)
        else:
            cur.execute(query)

        return cur.fetchall()

