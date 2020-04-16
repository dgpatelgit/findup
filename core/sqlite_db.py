import logging
import sqlite3

class DB:
    def __init__(self):
        self.clog = logging.getLogger("CORE.DB")
        self.conn = None

        try:
            dbFile = "./db/findup.db"
            self.conn = sqlite3.connect(dbFile)
        except Exception as ex:
            self.clog.error("Exception occured: %s\ndb file: %s", ex, dbFile)

    def execInsert(self, query, params, commit_immediately):
        """
        Execute a insert query with filter params
        :param query:  Sqlite insert query.
        :param params: Params as a collection, if its None, then only query will be executed.
        :param commit_immediately: If True, query will be commit to DB after execution, if False, query will be executed without commit. Caller must ensure to call commit() function once done with all insertions.
        :return: Last inserted Id.
        """
        
        #sql = 'INSERT INTO scan(id, name, root_path, created_timestamp, modified_timestamp) VALUES (?, ?, ?, ?, ?)'
        cur = self.conn.cursor()
        cur.execute(query, params)

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

