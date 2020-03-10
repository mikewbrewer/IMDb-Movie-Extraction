import mysql.connector

from clear_table import clear_table
from extract import extract
from to_excel import toExcel
from password import PASSWORD



if __name__ == '__main__':
    # if run on it's own, this connects the script to the database
    mydb = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        passwd = PASSWORD,
        database = 'pythondatabase',
        auth_plugin = 'mysql_native_password'
    )
    my_cursor = mydb.cursor()

    clear_table(my_cursor)

    # extract movies from IMDb
    extract(my_cursor, mydb)

    # write the table to an excel file
    toExcel(my_cursor, mydb)
