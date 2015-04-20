"""
15 Spring. Computer Network. network app making - 2048 game server
 - last updated 4/20/2015
"""

import Socket_App as CN_Sockets

import math
import random

class UDP_2048server(object):
    def __init__(self,IP,port):
        socket, AF_INET, SOCK_DGRAM, timeout = CN_Sockets.socket, CN_Sockets.AF_INET, CN_Sockets.SOCK_DGRAM, CN_Sockets.timeout
        with socket(AF_INET, SOCK_DGRAM) as sock:
            sock.bind((IP,port))
            sock.settimeout(2.0)
            print ("2048 Game server started on IP Address {}, port {}".format(IP,port))

            while True:
                try:
                    bytearray_msg, source_address = sock.recvfrom(1024)
                    source_IP, source_port = source_address
                    command=bytearray_msg.decode("UTF-8").strip()
                    #print("receiving message: "+bytearray_msg.decode("UTF-8"))

                    if command == 'G':
                        # reset the game
                        print("Game start")
                        olist = [[0]*4,[0]*4,[0]*4,[0]*4]
                        update = rand_add(olist)
                        olist = update[0]
                        points = 0
                        str_message=print_game(olist, points)
                    elif command == "END":
                        print("Game ends")
                        olist = [[0]*4,[0]*4,[0]*4,[0]*4]
                        points = 0
                    else:
                        print("Command: ", command)
                        olist, isInvalid, points = run_command(olist, command, points)
                        if isInvalid == 1:
                            str_message = "INVALID"
                            isInvalid = 0
                        else:
                            update = rand_add(olist)
                            if update[1] == False:
                                # if Game Over
                                points = str(points)
                                str_message="OVER "+points
                                print("***Game Over***")
                                bytearray_message = bytearray(str_message,encoding="UTF-8")
                                bytes_sent = sock.sendto(bytearray_message, source_address)
                                break
                            olist = update[0]
                            str_message = print_game(olist, points)
                    bytearray_message = bytearray(str_message,encoding="UTF-8")  
                    bytes_sent = sock.sendto(bytearray_message, source_address) 

                except timeout:
                    continue  # go wait again


def move(olist, direction, points):
    # The basic structure in this function is to move all the numbers in the matrix upward.
    # rotate() function helps to transfer other direction request cases into upward moving case.
    if direction == 'up':
        pass
    elif direction == 'down':
        olist = uptodown(olist)
    elif direction == 'right':
        olist = rotate(olist)
    elif direction == 'left':
        olist = rotate(olist)
        olist = rotate(olist)
        olist = rotate(olist)
    # The above code using rotate function to transfer the matrix into upward cases
    for j in range(4):
        mlist=olist[j]
        nlist=clean(mlist)
        i=0
        for i in range(len(nlist)-1):
            if nlist[i]==nlist[i+1]:
                nlist[i]+=nlist[i+1]
                points += int(nlist[i])
                nlist[i+1]=0
        # print ("Points:", str(points))
        nlist=clean(nlist)
        #check if every two cells have the same number. if so, adding them up.
        x=0
        for x in range(4-len(nlist)):
            nlist.append(0)
            #fullfill the rest of the space in the matrix by 0s.
        olist[j]=nlist
    if direction == 'down':
        olist = uptodown(olist)
    elif direction == 'right':
        olist = rotate(olist)
        olist = rotate(olist)
        olist = rotate(olist)
    elif direction == 'left':
        olist = rotate(olist)
    #The above code using rotate function to transfer other direction request cases back
    return olist, points

def clean(mlist):
    # This function erase all the 0s in the matrix and only leave "real" numbers there.
    nlist = []
    for item in mlist:
        if item != 0:
            nlist.append(item)
    return nlist

def uptodown(qlist):
    #This function flip the matrix upside down
    newlist=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    for i in range(len(qlist)):
        for j in range(len(qlist[i])):
            newlist[i][len(qlist)-j-1]=qlist[i][j]
    return newlist

def rotate(qlist):
    #This function  rotates the matrix in 90 degree everytime when being called.
    newlist=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    for i in range(len(qlist)):
        for j in range(len(qlist[i])):
            newlist[j][len(qlist)-i-1]=qlist[i][j]
    return newlist

def print_game(glist, points):
    #Prints the given list
    # for i in range(len(glist)):
    # print(glist[0][i],'\t',glist[1][i],'\t',glist[2][i],'\t',glist[3][i])
    message=""
    for i in range(len(glist)):
      message+=(str(glist[0][i])+" "+str(glist[1][i])+" "+str(glist[2][i])+" "+str(glist[3][i]) + " ")
      #print (glist[0][i],'\t',glist[1][i],'\t',glist[2][i],'\t',glist[3][i])
    #print('Points:',points)
    points_str=str(points)
    return message+points_str


def check_if_doubles(olist):
    #Goes through a list and checks if there is still a move left
    still_move = False
    for i in range(len(olist)):
        for j in range(1,len(olist[i])):
            if olist[i][j] == olist[i][j-1]:
                still_move = True
    #Checks columns
    templist = rotate(olist)
    for i in range(len(templist)):
        for j in range(1,len(templist[i])):
            if templist[i][j] == templist[i][j-1]:
                still_move = True
    
    return still_move


def rand_add(glist):
    #Randomly replaces a 0 with a 2 in a list
    possible_i = []
    for i in range(len(glist)):
        for j in range(len(glist[i])):
            #For each row and each column
            if glist[i][j] == 0:
                #If the space has a zero save te index
                possible_i.append((i,j))
    if len(possible_i) > 0:
        #Get random index of possible zeroes IF there are zeroes
        index = possible_i[math.floor(random.random()*len(possible_i))]
        glist[index[0]][index[1]] = 2   #Add in the next
        return glist, True
    else:
        #If no zeroes to add, see if can still make a move
        still_move = check_if_doubles(glist)
        if still_move:
            return glist, True
        else:
            return glist, False

def run_command(olist, comi, points):
    #Basic run function of user input
    isInvalid = 0
    if comi[0] == 'W':
        olist,points=move(olist,'up',points)
    elif comi[0] == 'A':
        olist,points=move(olist,'left',points)
    elif comi[0] == 'S':
        olist,points=move(olist,'down',points)
    elif comi[0] == 'D':
        olist,points=move(olist,'right',points)
    else:
        #If did not enter valid key, notify user and ask for input again
        isInvalid = 1
        return olist, isInvalid
    return olist, isInvalid, points

if __name__ == "__main__":
    UDP_2048server("192.168.68.65",40)
