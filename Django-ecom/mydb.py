import mysql.connector

database = mysql.connector.connect(
    host='localhost',
    user = '', # INSERT UR USER NAME
    password = '', #ur USER PASSWORD
    


)

# prepare a cursor object

cursorobject = database.cursor()

# create the database

cursorobject.execute("CREATE DATABASE ecommerce")
print ("all done")


# after connecting and making migrations u can delete it if u want
