"""
15 Spring. Computer Network. network app making - game 2048 client
 - last updated 4/20/2015
"""

import Socket_App as CN_Sockets

class UDP_2048client(object):

    def __init__(self,Server_Address=("192.168.68.65",40)):

        socket, AF_INET, SOCK_DGRAM = CN_Sockets.socket, CN_Sockets.AF_INET, CN_Sockets.SOCK_DGRAM
        with socket(AF_INET,SOCK_DGRAM) as sock:
            print ("2048 Game client started for 2048 Game server at IP address {} on port {}".format(Server_Address[0],Server_Address[1]))

            bytearray_message = bytearray('g',encoding="UTF-8")
            bytes_sent = sock.sendto(bytearray_message, Server_Address)
            bytearray_msg, source_address = sock.recvfrom(1024)
            source_IP, source_port = source_address

            while True:
                game = bytearray_msg.decode("UTF-8")
                game_data = game.split(' ')
                if game_data[0] == "OVER":
                    print('Game over. Your Score: ', game_data[1])
                    break
                elif game_data[0] == "INVALID":
                    print('Invalid move. Only takes keys: W A S D')
                else:
                    # Else assume have the array of matrix data (strings)
                    # 0 0 2 0 4 4 2 0 4 4 2 0 0 0 2 0 12345
                    gmatrix = [game_data[0:4], game_data[4:8], game_data[8:12],game_data[12:16]]
                    gscore = game_data[16]
                    for i in range(len(gmatrix)):
                        row = ''
                        for j in range(len(gmatrix[i])):
                            adj_len = ((6-len(gmatrix[i][j]))*' ') + gmatrix[i][j]
                            row += adj_len
                        print(row)
                    print('Score: ',gscore)
                    print('')

                str_message = input("Enter move:\n")
                if not str_message: # an return with no characters terminates the loop
                    break
                bytearray_message = bytearray(str_message,encoding="UTF-8")
                bytes_sent = sock.sendto(bytearray_message, Server_Address)
                
                bytearray_msg, source_address = sock.recvfrom(1024)
                source_IP, source_port = source_address

        print ("2048 Game client ended")
        bytearray_message = bytearray('end',encoding="UTF-8")
        bytes_sent = sock.sendto(bytearray_message, Server_Address)

if __name__ == "__main__":
    UDP_2048client()
