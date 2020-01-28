from socket import *
import time
import pymysql

HOST = ''
PORT = 8008
BUFSIZE = 1024
ADDR = (HOST,PORT)


server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(ADDR)
print('Server launched..')

server_socket.listen(1)
print('Waiting connection..')

client_socket, addr = server_socket.accept()
print('Connected by: ', str(addr))
            
### DB connection
conn = pymysql.connect(host='localhost', user='root', password='juneo', 
    db='mysql', charset='utf8')
curs = conn.cursor()
### set webcam2 on 
sql="update Command SET Webcam2 = 'ON'"


while True: # Server loop; webcam2 off, alert on

   
    ### Read Data
    sql ="select Webcam2 from Command"
    curs.execute(sql)
    dbdata = curs.fetchall()
    print(data2)

    if 'OFF' in dbdata:
        message = 'Webcam2 OFF'
        message = message.encode('utf-8')
        server_socket.send(message)
    elif 'ON' in dbdata:
        message = 'Webcam2 ON'
        message = message.encode('utf-8')
        server_socket.send(message)    
    

    ### Update Data 
    clientdata = client_socket.recv(BUFSIZE)
        
    if 'Alert(DWS)' in clientdata.decode('utf-8'):
        sql="update Command SET Alert = 'ON'"
        print('Alert(DWS); Set Alert ON in DB')
    elif 'Normal' in clientdata.decode('utf-8'):
        print('Normal')
        
           
    time.sleep(0.5)
    
    if not data:
        break



