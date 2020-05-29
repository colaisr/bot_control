import configparser
import sqlite3
from _datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini')
DATABASE = "scheduler_db.sqlite"


def orders_table_exist(c):
    # get the count of tables with the name
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Orders' ''')

    # if the count is 1, then table exists
    if c.fetchone()[0] == 1:
        return True
    else:
        return False


def create_interactions(c):
    # Create table
    c.execute('''CREATE TABLE Interactions
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                     Started TIMESTAMP,
                     Ended TIMESTAMP,
                     OrderID int NOT NULL ,
                     UserFirst TEXT,
                     UserLast TEXT,
                     UserUser,
                     UserTeId int,
                     FOREIGN KEY(OrderID) REFERENCES Orders(OrderID)
                     )''')


def create_orders(c):
    # Create table
    c.execute('''CREATE TABLE Orders
                     (OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
                     Created TIMESTAMP,
                     Name TEXT,
                     Phone TEXT,
                     Date TEXT,
                     Hours TEXT,
                     Minutes TEXT
                     )''')


def validate_user(user):
    if user.first_name == None:
        user.first_name = ""
    if user.last_name == None:
        user.last_name = ""
    if user.username == None:
        user.last_name = ""
    if user.id == None:
        user.last_name = ""
    return user


def validate_order(order):
    if order.name is None:
        order.name = ""
    if order.phone is None:
        order.phone = ""
    if order.date is None:
        order.date = ""
    if order.hours is None:
        order.hours = ""
    if order.minutes is None:
        order.minutes = ""
    return order


def update_stat(order, user, new_record=False, close_record=False):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    naive_dt = datetime.now()
    if not orders_table_exist(c):
        create_interactions(c)
        create_orders(c)

    if new_record:
        # add order

        c.execute("INSERT INTO Orders (Created,Name,Phone,Date,Hours,Minutes) VALUES (?,?,?,?,?,?)",
                  (naive_dt, order.name, order.phone, order.date, order.hours, order.minutes))
        last_order = c.lastrowid

        user = validate_user(user)
        c.execute(
            "INSERT INTO Interactions (Started,Ended,OrderId,UserFirst,UserLast,UserUser,UserTeId) VALUES (?,?,?,?,?,?,?)",
            (naive_dt, "Null", last_order, user.first_name, user.last_name, user.username, user.id))
    else:
        # updating
        # get last interaction for user
        c.execute(
            "SELECT * FROM Interactions WHERE UserTeId = ? ORDER BY ID DESC LIMIT 1 ",
            (user.id,))

        i = c.fetchone()
        interact_id = i[0]
        order_id = i[3]

        # update Order
        c.execute("UPDATE Orders SET Name=?,Phone=?,Date=?,Hours=?,Minutes=? WHERE OrderId = ?",
                  (order.name, order.phone, order.date, order.hours, order.minutes, order_id))

    if close_record:
        # updating
        # get last interaction for user
        c.execute(
            "SELECT * FROM Interactions WHERE UserTeId = ? ORDER BY ID DESC LIMIT 1 ",
            (user.id,))

        i = c.fetchone()
        interact_id = i[0]
        order_id = i[3]

        # update Order
        c.execute("UPDATE Orders SET Name=?,Phone=?,Date=?,Hours=?,Minutes=? WHERE OrderId = ?",
                  (order.name, order.phone, order.date, order.hours, order.minutes, order_id))

        # update Interaction
        c.execute("UPDATE Interactions SET Ended=? WHERE ID = ?",
                  (naive_dt, interact_id))

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

    pass
