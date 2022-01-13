import logging

import paramiko
import psycopg2


class postgresUtil:

    def execQueryPS(query, server):
        try:
            conn = psycopg2.connect(
                host=server,
                database="dndb",
                user="postgres",
                port='5432',
                password="s9etcq89WThKreA8j9he")
            cursor = conn.cursor()
            print(f'executing query={query} on postgress db on server{server}')
            cursor.execute(query)
            records = cursor.fetchall()
            print('result=')
            for row in records:
                print(row)
            return records
        except Exception as e:
            print(str(e))
        finally:
            # closing database connection.
            if conn:
                cursor.close()
                conn.close()
                print("PostgreSQL connection is closed")


    def updateTable(query, server):
        try:
            conn = psycopg2.connect(
                host=server,
                database="dndb",
                user="postgres",
                port='5432',
                password="s9etcq89WThKreA8j9he")
            cursor = conn.cursor()
            print(f'executing query={query} on postgress db on server {server}')
            cursor.execute(query)
            conn.commit()
            count = cursor.rowcount
            print(count, "Record Updated successfully ")
        except (Exception, psycopg2.Error) as error:
            print("Error in update operation", error)
        finally:
            # closing database connection.
            if conn:
                cursor.close()
                conn.close()
                print("PostgreSQL connection is closed")


