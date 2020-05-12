# _*_ coding:utf-8 _*_
# Author: zizle
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_table():
    db_path = os.path.join(BASE_DIR, 'dawn/tupdate.db')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS `table_update_config`("
                   "`id` INTEGER PRIMARY KEY AUTOINCREMENT,"
                   "`update_time` VARCHAR(32) DEFAULT NULL,"
                   "`variety_name` VARCHAR(128) NOT NULL,"
                   "`variety_id` INTEGER NOT NULL,"
                   "`group_name` VARCHAR(128) NOT NULL,"
                   "`group_id` INTEGER NOT NULL,"
                   "`file_folder` VARCHAR (1024) NOT NULL"
                   ");")
    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    create_table()

