import sqlite3


class DBHandler:
    def __init__(self, table_name=None, column_name=None):
        self.db_path = "./socket_client.db"

        if table_name is not None:
            self.table_name = table_name
        else:
            self.table_name = "socket_client"
        if column_name is not None:
            self.column_name = column_name
        else:
            self.column_name = "client_secret_key"
        try:
            self.connection_instance = sqlite3.connect(self.db_path)

        except Exception as err:
            print(err.message)

    def get_table_row_count(self):
        try:
            query = "select count(*) from {}".format(self.table_name)
            return int(self.connection_instance.execute(query).fetchone()[0])

        except Exception as err:
            print(err.message)

    def get_whitelist_ip_count(self):
        try:
            query = "select count(*) from whitelist"
            return int(self.connection_instance.execute(query).fetchone()[0])
        except Exception as err:
            print(err.message)


    def get_client_data(self):
        try:
            row_count = self.get_table_row_count()
            if row_count == 0:
                return None
            elif row_count == 1:
                query = "select {} from {}".format(self.column_name,
                                                   self.table_name)
                return str(self.connection_instance.execute(query).fetchone()[0])

        except Exception as err:
            print(err.message)

    def set_client_data(self, secret_key):
        row_count = self.get_table_row_count()

        try:
            if row_count == 0:
                query = "insert into {}({}) values('{}')".format(self.table_name,
                                                                 self.column_name,
                                                                 secret_key)
                cursor = self.connection_instance.execute(query)
                if cursor.rowcount == 1:
                    self.connection_instance.commit()
                    return True
                else:
                    return False

        except Exception as err:
            print(err.message)

    def delete_client_data(self):
        try:
            query = "delete from {}".format(self.table_name)
            self.connection_instance.execute(query)
            self.connection_instance.commit()
            return True
        except Exception as err:
            print(err.message)

    def whitelist_entry_db(self, ipaddress=None, timestamp=None):
        try:
            if ipaddress is not None and timestamp is not None:
                insert_query = "insert into whitelist(ip, timestamp) values({}, {})".format(
                    ipaddress,
                    timestamp
                )
                if self.get_whitelist_ip_count() == 0:
                    self.connection_instance.execute(insert_query)
                    self.connection_instance.commit()
                    return True
                else:
                    return False
        except Exception as err:
            print(err)
            return False
