import mysql.connector
import pandas as pd

from password import PASSWORD



# reads the info from the database and then exports to excel
def toExcel(_cursor, _db):
    df = pd.read_sql('SELECT * FROM movies', con=_db)
    df.to_excel(r'C:\Users\Michael\Desktop\Coding Practice\mySQL\IMDb_SQL\movies.xlsx', index = None, header = True)



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

    toExcel(my_cursor, mydb)
