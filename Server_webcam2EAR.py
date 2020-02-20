from socket import *
import time
import pymysql

HOST = ''
PORT = 8009
BUFSIZE = 1024
ADDR = (HOST,PORT)

# DB connection
conn = pymysql.connect(host='localhost', user='root', password='juneomysql', db='mysql', charset='utf8')
curs = conn.cursor()

#### set webcam2 ON DB
sql = "update Command SET Webcam2 = 'ON'"
curs.execute(sql)
conn.commit()
conn.close()

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(ADDR)
print('Webcam2EAR Server launched..')

server_socket.listen(1)
print('Waiting connection..')

client_socket, addr = server_socket.accept()
print('Connected by: ', str(addr))
###wait for client dlib loading
print('wait 5 sec')
time.sleep(5)

while True: # Server loop; webcam2 off, alert on
    # DB connection
    conn = pymysql.connect(host='localhost', user='root', password='juneomysql', db='mysql', charset='utf8')
    curs = conn.cursor()
    
    ### Read Data
    sql = "select Webcam2 from Command"
    curs.execute(sql)
    dbdata = curs.fetchall()
    str_dbdata = ''.join(dbdata[0])
    
    ### check Webcam2 Data
    print('Webcam2 Check:', str_dbdata) 

    ### Send message OFF/ON 
    if 'OFF' in str_dbdata:
        client_socket.send('Webcam2 OFF'.encode('utf-8'))
        print('\nWebcam2 OFF and Shut down\n')
        
        nothing1 = client_socket.recv(BUFSIZE) #n1 n2

    elif 'ON' in str_dbdata:
        client_socket.send('Webcam2 ON'.encode('utf-8'))    
        
        time.sleep(0.1)
        print('\nWebcam2 ON and Detecting\n')

        sql = "select Registration2 from Command"
        curs.execute(sql)
        regis2 = curs.fetchall()
        str_regis = ''.join(regis2[0])

        print('Registration2 Check:', str_regis)
        #time.sleep(0.6) #n 
        nothing2 = client_socket.recv(BUFSIZE)

        if str_regis != 'OFF':
            client_socket.send('EAR update'.encode('utf-8'))
            print('Calculating New drivers EAR')
            ###value socket receiver
            new_earcal=client_socket.recv(BUFSIZE) #recv 1
            value=new_earcal.decode('utf-8')
            print('Received EAR: ', value)
            ###SET DB EAR value
            sql = "UPDATE User U INNER JOIN Command C ON U.NAME = C.REGISTRATION2 SET U.EAR =" + value + "WHERE U.NAME = C.REGISTRATION2"
            curs.execute(sql)
            conn.commit()
            print('updated your EAR')
            ###SET DB Regist OFF
            sql = "update Command SET Registration2 = 'OFF'"
            curs.execute(sql)
            conn.commit()

        elif str_regis == 'OFF': ##detecting drowsiness part
            client_socket.send('OFF'.encode('utf-8')) #send regis OFF
            print('Driver confirmed')
            #time.sleep(0.3)
            nothing3=client_socket.recv(BUFSIZE) #n3
            sql = "select Name from Driver"
            curs.execute(sql)
            name = curs.fetchall()
            drivername = ''.join(name[0])
            
            if drivername == 'OFF':
                EAR_load = '0.05'
                print('Driver OFF')
                client_socket.send(EAR_load.encode('utf-8')) #send regis 0.05
            
            elif drivername == '':
                EAR_load = '0.05'
                print('Driver null')
                client_socket.send(EAR_load.encode('utf-8'))
                          
            else:    
                sql = "select EAR from User WHERE Name = '"+drivername+"'"
                curs.execute(sql)
                EARdb = curs.fetchall() #if not in EARdb EAR_load= 0.05 in
                print(EARdb)
                EAR_load = ''.join(EARdb[0]) 
                print('Driver EAR: ', EAR_load)
                client_socket.send(EAR_load.encode('utf-8')) #send regis EAR
            
            ### Write Data to ALERT (wait)
            #send
            clientdata = client_socket.recv(BUFSIZE)
            
            if 'Normal' in clientdata.decode('utf-8'):
                print('1 Normal Driver Condition')
                client_socket.send('1st 2nd'.encode('utf-8')) #n4
                clientdata = client_socket.recv(BUFSIZE)
                if 'Alert(DWS)' in clientdata.decode('utf-8'):
                    sql="update Command SET Alert = 'ON'"
                    curs.execute(sql)
                    conn.commit()
                    print('*******Alert(DWS); Set Alert ON in DB*******')
                elif 'Normal' in clientdata.decode('utf-8'):
                    print('2 Normal Driver Condition')
    conn.close()
    ###
    
client_socket.close()
server_socket.close()
print('[System] Server close..')


