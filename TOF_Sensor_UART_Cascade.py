#!/usr/bin/env python3

'''
#############################################################
# Project:  TOF Time Of Flight Laser Range Sensors          #
#           in UART cascade mode with 5 sensors chained.   #
# Short Range Distance: 12mm to 2.16m 
# Accuracy: +- 1cm, Resolution: 1mm   
# Wavelwngth: 940nm (Class1 standard compliant), FOV 15 ~27°
# Communication interface: UART 3.3V TTL
# Cascade support: UART up to 8 sensors
# Power consumption: 290mW, 5V, 58mA
# 
# DRINKOTEC Swiss Bevrage, Company 1266 Duillier -CH                                                #
#############################################################
'''

#coding: UTF-8
import RPi.GPIO as GPIO
import serial 
import time
import chardet
import sys

TOF_length = 16
TOF_header=(87,0,255)
TOF_system_time = 0
TOF_distance = 0
TOF_status = 0
TOF_signal = 0
TOF_check = 0

ser = serial.Serial('/dev/ttyAMA0',921600) #115200)
ser.flushInput()
ser.flushOutput()


NBR_SENSORS = 5
sensor_distance = [5000]*NBR_SENSORS  # Sensor distance set to max distance measurement 5m or 5000mm

# Request commands to query sensors
request_sensors = [

    [0x57,0x10,0xff,0xff,0x01, 0xff, 0xff, 0x64], 
    [0x57,0x10,0xff,0xff,0x02, 0xff, 0xff, 0x65], 
    [0x57,0x10,0xff,0xff,0x03, 0xff, 0xff, 0x66],
    [0x57,0x10,0xff,0xff,0x04, 0xff, 0xff, 0x67],
    [0x57,0x10,0xff,0xff,0x05, 0xff, 0xff, 0x68]
    
 ]


def verifyCheckSum(data):
    TOF_check = 0
    
    for c in data:
        TOF_check += int(c)
        
    TOF_check=TOF_check%256
    
    return TOF_check
    

def send_Req(ser, i):
    try:
        ser.flushInput() #reset_input_buffer()  # Flush input buffer, discarding all its contents.
        ser.write(bytes(request_sensors[i])) #[0x57,0x10,0xff,0xff,0x02, 0xff, 0xff, 0x65]))
        ser.flush() # it is buffering. required to get the data out *now*
        print("Message sent: " + str(request_sensors[i]) )
    except Exception as e:
        print("Error : No Serial RS232.")
        sys.exit(0) 



while True:
    
    for i in range(0,NBR_SENSORS):
        
        # Send query-request to sensor i
        send_Req(ser, i)
        
        start_message = False
        header = False
        data = False
        status = False
        count = 0
        buffer_mess = bytearray()
        time.sleep(0.05)
    
    
        while True:
            
            try:
                # read one byte
                byte = ser.read(1) 
                #print(self.byte)			
            except TimeoutError: 
                print("Timeout Reading RS232")
                break
            except Exception as e:
                print(e) 
                print("Error while Reading RS232")
                break
        
            if(byte==""):
                print("Empty byte - Tinmeout?")
                break
            
    
            if(data == True and count == 15):
                
                checkSum = verifyCheckSum(buffer_mess)
                
                buffer_mess.append(byte[0])
                
                if(status and int(byte[0]) == checkSum  ): 
                    print(" [+] -> Correct")
                    print( ' '.join( str(hex(int(c)))  for c in buffer_mess ) )
                    
                    print("TOF ID: "+ str(int(buffer_mess[3])))
                
                    #TOF_system_time = int(buffer_mess[4]) | int(buffer_mess[5]) <<8 | int(buffer_mess[6]) <<16 | int(buffer_mess[7]) <<24;
                    #print("TOF system time is: "+str(TOF_system_time)+'ms')
                    
                    TOF_distance = int(buffer_mess[8]) | int(buffer_mess[9])<<8 | int(buffer_mess[10])<<16
                    print("TOF distance: "+str(TOF_distance)+'mm')
                    
                    TOF_status = int(buffer_mess[11])
                    print("TOF status: "+str(TOF_status))
                    if(TOF_status == 0):
                        sensor_distance[i]=TOF_distance
                    else:
                        sensor_distance[i] = 5000
                    
                    TOF_signal = int(buffer_mess[12]) | int(buffer_mess[13])<<8;
                    print("TOF signal: "+str(TOF_signal) )
                    
                    
                else:
                    print(" [-] -> Error")
                    sensor_distance[i] = 5000
                
                break
            elif(header == True and count <= 14):
                count += 1
                data = True
                
                buffer_mess.append(byte[0])
                
                if(count==12):
                    #print("Status: {}".format(hex(ord(byte))))
                    if(byte == bytes([0x00])):
                        status = True
                
                
            elif( start_message == True and header == False and count ==1 and byte == bytes([0x00]) ):
                header = True 
                count += 1
                buffer_mess.append(byte[0])
                #print("Header 0x57 0x00")
            elif( byte == bytes([0x57])  ):
                #print("Start of Message 0x57")
                start_message = True
                count += 1
                buffer_mess.append(byte[0])
                
                
        print(sensor_distance)
        print("----------------------------------------------\n")

         
    
        
    





