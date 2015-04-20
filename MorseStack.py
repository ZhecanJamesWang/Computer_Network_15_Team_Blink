"""
15 Spring. Computer Network. Lab 9
 - last updated 4/20/2015
"""

#help debugging (print out each steps or silent)
def print_details(X, *T, **D):
    print(X, *T, **D)

#sender blinking period
blink_duration = .01

#receiver oversampling ratio
oversampling_ratio = 4


import random
import socket as s

import time
import RPi.GPIO as GPIO

#----------------------------------------------------------------------------------#
# #Preparation for Rasberry pi#
class Safeguards:
    def __enter__(self):
        return self
    def __exit__(self,*rabc):
        GPIO.cleanup()
        print("Safe exit succeeded")
        return not any(rabc)

def sending_prepare_pin(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin,GPIO.OUT)

def receiving_prepare_pin(pin):
    GPIO.setmode(GPIO.BCM)  
    GPIO.setup(pin,GPIO.IN)

def turn_high(pin):
    GPIO.output(pin,GPIO.HIGH)

def turn_low(pin):
    GPIO.output(pin,GPIO.LOW)

def delay(duration):
    time.sleep(duration) 

def read_pin(pin):
    return GPIO.input(pin)

#----------------------------------------------------------------------------------#
#physical layer implementation

#sending and receiving pulsed
def send(bit):
    pin_signal = 17
    pin_status = 23
    receiving_prepare_pin(pin_status)
    while True:
        if read_pin(pin_status):
            wait_time = random.randrange(10,20)
            print_details(" Layer1. The Channel is Occupied, wait for " + str(wait_time))
            delay(wait_time)
        else:
            print_details(" Layer1. start to send signals")
            sending_prepare_pin(pin_signal)
            sending_prepare_pin(pin_status)
            turn_high(pin_status)
            for i in bit:
                if i=="1":
                    #print_details("1")
                    turn_high(pin_signal)
                    delay(blink_duration)
                if i=="0":
                    #print_details("0")
                    turn_low(pin_signal)
                    delay(blink_duration)
            turn_low(pin_status)
            receiving_prepare_pin(pin_status)
            receiving_prepare_pin(pin_signal)
            print_details(" Layer1. sending ended")
            return

def receive(blink=1000,duration=.5,pin=17):
    pulse=""
    receiver_duration = 1.0 * blink_duration / oversampling_ratio
    receiving_prepare_pin(pin)
    sequential_one = 0
    sequential_zero = 14 * oversampling_ratio
    
    pulse_temp = [0 for _ in range(blink * oversampling_ratio)]
    j=0
    while True:
        if read_pin(pin):
            if sequential_zero != 0:
                if sequential_zero < 2 * oversampling_ratio:
                    pulse_temp[j] = 1
##                    print_details("0")
                elif sequential_zero < 5 * oversampling_ratio:
                    pulse_temp[j] = 2
##                    print_details("000")
                else:
                    pulse_temp[j] = 3
##                    print_details("0000000")
                sequential_zero = 0
                j=j+1
            sequential_one+=1
            delay(receiver_duration)
        else:
            if sequential_one != 0:
                if sequential_one < 2 * oversampling_ratio:
                    pulse_temp[j] = 5
##                    print_details("1")
                else:
                    pulse_temp[j] = 6
##                    print_details("111")
                sequential_one = 0
                j=j+1
            if sequential_zero == 13 * oversampling_ratio:
                pulse_temp[j] = 3
                pulse_temp[j+1] = 9
                print_details(" Layer1. receive function ended")
                break
            sequential_zero+=1
            delay(receiver_duration)
    for i in range(j+1):
        if pulse_temp[i] == 1:
            pulse+="0"
        elif pulse_temp[i] == 2:
            pulse+="000"
        elif pulse_temp[i] == 3:
            pulse+="0000000"
        elif pulse_temp[i] == 5:
            pulse+="1"
        elif pulse_temp[i] == 6:
            pulse+="111"
        elif pulse_temp[i] == 9:
            break
    #print(pulse)
    return pulse

#converting between sentence and morse code using mother_layer class and functions
class mother_layer:
    def __init__(self,function,inverse):
        self.descend=function
        self.ascend=inverse

#receiving dictionary
dict_m2l={".*-":"A","-*.*.*.":"B","-*.*-*.":"C","-*.*.":"D",".":"E",".*.*-*.":"F","-*-*.":"G",".*.*.*.":"H",".*.":"I",".*-*-*-":"J","-*.*-":"K",".*-*.*.":"L","-*-":"M","-*.":"N","-*-*-":"O",".*-*-*.":"P","-*-*.*-":"Q",".*-*.":"R",".*.*.":"S","-":"T",".*.*-":"U",".*.*.*-":"V",".*-*-":"W","-*.*.*-":"X","-*.*-*-":"Y","-*-*.*.":"Z",".*-*-*-*-":"1",".*.*-*-*-":"2",".*.*.*-*-":"3",".*.*.*.*-":"4",".*.*.*.*.":"5","-*.*.*.*.":"6","-*-*.*.*.":"7","-*-*-*.*.":"8","-*-*-*-*.":"9","-*-*-*-*-":"0","*******":" "}
#sending dictionary
dict_l2m={"@":"*","A":".*-","B":"-*.*.*.","C":"-*.*-*.","D":"-*.*.","E":".","F":".*.*-*.","G":"-*-*.","H":".*.*.*.","I":".*.","J":".*-*-*-","K":"-*.*-","L":".*-*.*.","M":"-*-","N":"-*.","O":"-*-*-","P":".*-*-*.","Q":"-*-*.*-","R":".*-*.","S":".*.*.","T":"-","U":".*.*-","V":".*.*.*-","W":".*-*-","X":"-*.*.*-","Y":"-*.*-*-","Z":"-*-*.*.","1":".*-*-*-*-","2":".*.*-*-*-","3":".*.*.*-*-","4":".*.*.*.*-","5":".*.*.*.*.","6":"-*.*.*.*.","7":"-*-*.*.*.","8":"-*-*-*.*.","9":"-*-*-*-*.","0":"-*-*-*-*-"," ":"*******"}   

#words and letter_layer
class words_letter_layer(mother_layer):
    def __init__(self):
        super().__init__(words2letter,letter2word)

def words2letter(words):
    words = words.upper()
    letter = words.replace(" ", "@")
    return letter

def letter2word(letter):
    word=""
    for item in letter:
        for i in item:
            try:
                word=word+dict_m2l[i]
            except:
                pass
        word=word+" "
    return word

#letter and morse code layer#
class letter_morse_layer(mother_layer):
    """docstring for ClassName"""
    def __init__(self):
        super().__init__(letter2morse,morse2letter)

def letter2morse(letter):
    morse=""
    for i in letter:
        morse=morse+dict_l2m[i]
        morse=morse+"***"
    return morse

def morse2letter(morse):
    letter=[]
    sentence=morse.split("*******")
    for word in sentence:
        word=word.split("***")
        letter.append(word)     
    return letter

#morse code and pulse layer#
class morse_pulse_layer(mother_layer):
    """docstring for ClassName"""
    def __init__(self):
        super().__init__(morse2pulse,pulse2morse)

def morse2pulse(morse):
    global dict_m2p
    dict_m2p = {".":"1","-":"111","*":"0"}
    bit=""
    for i in morse:
        bit=bit+dict_m2p[i]
    return bit

def pulse2morse(pulse): 
    pulse=str(pulse)
    pulse=pulse.lstrip("0")
    morse=""
    for i in pulse:
        if i=="1":
            morse+="."
        if i=="0":
            morse+="*"
    morse=morse.replace("...","-")
    return morse

#----------------------------------------------------------------------------------#
#data link layer implementation
def add_mac(words, src_mac, dst_mac):
    macheader=src_mac+dst_mac
    words=macheader+words
    return words

def demac(message, mac):
    scr_mac = message[0:2]
    dst_mac = message[2:4]
    new_message = message[4:]
    if dst_mac != mac:
        print_details(" Layer2. MAC address not matched")
    return new_message

#----------------------------------------------------------------------------------#
#network layer implementation
dic_ip_mac={'DA':'MA','DB':'MB','DC':'MC', 'DR':'MR'}
def router_ip_to_mac(ip_addr):
    try:
        mac_addr = dic_ip_mac[ip_addr]
    except:
        print_details(" Layer3. router_ip_to_mac: cannot find matched ip")
        return 0
    return mac_addr

def router_add_mac(message, dst_mac):
    message=dst_mac+message
    message='MR'+message
    return message

def router_deip(message):
    src_ip=message[0:2]
    dst_ip=message[2:4]
    new_dst_mac = router_ip_to_mac(dst_ip)
    payload=message[4:]
    new_message = router_add_mac(message, new_dst_mac)
    return new_message

def add_ip(message, src_ip, dst_ip, next_protocol):
    # message formate DB (first two) = destination
    cksum = calc_ip_checksum(src_ip, dst_ip, next_protocol)
    ip_header = src_ip + dst_ip + next_protocol + cksum
    print_details(" Layer3. add_ip: ip_header is " + ip_header)
    message = ip_header + message
    return message

def deip(message, ip):
    src_ip=message[0:2]
    dst_ip=message[2:4]
    next_p = message[4]
    cksum = message[5:9]
    payload=message[9:]
    if dst_ip!=ip:
        print_details(" Layer3. deip: IP address not matched")
    if cksum != calc_ip_checksum(src_ip, dst_ip, next_p):
        print_details(" Layer3. deip: checksum wrong")
    return payload, src_ip, dst_ip

#previous version of checksum
"""
def dec_to_bin(x):
    return bin(x)[2:]

def b_int(bstring):
    return int(bstring, 2)

def dec_to_hex(x):
    return hex(b_int(x))[2:]

def calc_ip_checksum(src_ip, dst_ip, next_p):
    message = src_ip + dst_ip + next_p
    temps=""
    for c in message:
        temps+=str(dec_to_bin(ord(c)))
    temps1, temps2, temps3 = b_int(temps[-16:]), b_int(temps[-32:-16]), b_int(temps[:-32])
    tempsum = dec_to_bin(temps1 + temps2 + temps3)
    if len(str(tempsum))==17:
        tempsum= dec_to_bin(int(str(tempsum[0]),2) + int(str(tempsum[1:]),2))
        tempsum=(16-len(str(tempsum)))*'0'+str(tempsum)

    tempsum = list(str(tempsum))
    temps=""
    for i in range(len(tempsum)):
        temps += "1" if tempsum[i]=="0" else "0"
    
    temps4, temps5, temps6, temps7 = dec_to_hex(temps[0:4]), dec_to_hex(temps[4:8]), dec_to_hex(temps[8:12]), dec_to_hex(temps[12:16])
    checksum = str(temps4) + str(temps5) + str(temps6) + str(temps7)

    return checksum

"""
def calc_ip_checksum(sourceip, desip, nextProtocol):
    header = bytearray(sourceip+desip+nextProtocol,encoding="UTF-8")
    decsum = 0
    for item in header:
        decsum += int(item)
    binsumflip = bin(decsum)[2:]
    binsumflip = "0" * (16-len(binsumflip)) + binsumflip
    binsum = ""
    for char in binsumflip:
        if char == "0":
            binsum+= "1"
        else:
            binsum+= "0"
    return(hex(int(binsum,2))[2:].upper())

#----------------------------------------------------------------------------------#
#transportation layer implementation
def add_udp(message, src_port, dst_port):
    udp_header = str(src_port) + str(dst_port)
    message = udp_header + message
    return message

def de_udp(message, port):
    src_port = message[0:2]
    dst_port = message[2:4]
    payload = message[4:]
    if dst_port != str(port):
        print_details(" Layer4. de_udp: port is not matched")
    return payload, src_port, dst_port

#----------------------------------------------------------------------------------#
class mother_stack:
    """
    A template for a bijection stack which can be used to
    encode or decode messages. To use it, pass it a list
    of stack layers with common interfaces.
    """

    def __init__(self, layers):
        self.layers = layers

    def encode(self, message, src_mac, src_ip, src_port, dst_mac, dst_ip, dst_port):
        print_details(" Layer4. Before transport layer: " + message)
        message=add_udp(message, src_port, dst_port)
        next_protocol = 'A'
        print_details(" Layer3. Before network layer: " + message)
        message=add_ip(message, src_ip, dst_ip, next_protocol)
        print_details(" Layer2. Before data link layer: " + message)
        message=add_mac(message, src_mac, dst_mac)
        print_details(" Layer1. Before physical layer: " + message)
        for layer in self.layers:
            message = layer.descend(message)
        return message

    def decode(self, message, mac, ip, port):
        for layer in reversed(self.layers):
            message = layer.ascend(message)
        print_details(" Layer1. After physical layer: " + message)
        message=demac(message, mac)
        print_details(" Layer2. After data link layer: " + message)
        message,src_ip, dst_ip=deip(message, ip)
        print_details(" Layer3. After network layer: " + message)
        message, src_port, dst_port = de_udp(message, port)
        print_details(" Layer4. After transport layer: " + message)
        return message, src_ip, dst_ip, src_port, dst_port

    def router(self, message):
        for layer in reversed(self.layers):
            message = layer.ascend(message)
        print_details(" Layer1. After physical layer: " + message)
        message=demac(message, 'MR')
        print_details(" Layer2. After data link layer: " + message)
        message=router_deip(message)
        print_details(" Layer1. Before physical layer: " + message)
        for layer in self.layers:
            message = layer.descend(message)
        return message

class stack(mother_stack):
    def __init__(self):
        super().__init__([
            words_letter_layer(),
            letter_morse_layer(),
            morse_pulse_layer()])

#----------------------------------------------------------------------------------#
class Socket_stack():
    dict_ip2LANip = {"192.168.68.65":"DA","192.168.68.66":"DB","192.168.68.67":"DC"}
    dict_LANip2ip = {v:k for (k,v) in dict_ip2LANip.items()}
    dict_LANip2mac = {"DA":"MA","DB":"MB","DC":"MC"}
    dict_port42 = {}
    dict_port24 = {}
    sock_stack_addr = ("127.0.0.1", 1000)

    def __init__(self):
        self.stack = stack()
        self.socket, self.AF_INET, self.SOCK_DGRAM, self.timeout = s.socket, s.AF_INET, s.SOCK_DGRAM, s.timeout
        self.sock = s.socket(self.AF_INET, self.SOCK_DGRAM)
        self.sock.bind(self.sock_stack_addr)
        self.sock.settimeout(2.0)
        while True:
            try:
                bytearray_cap_msg, self.sock_app_addr = self.sock.recvfrom(1024)
                cap_msg = bytearray_cap_msg.decode()
                print_details(cap_msg)
                self.cmd, self.src_ip, self.src_port, self.dst_ip, self.dst_port, self.msg = self.decapsulate(cap_msg)
                if self.cmd == "SENDTO":
                    self.send_stack()
                elif self.cmd == "BIND":
                    self.bind_stack()
                elif self.cmd == "RECVFROM":
                    self.receive_stack()
            except self.timeout:
                print(".",end="")
                continue
    
    def __exit__(self, *args):
        self.sock.close()
        return self
    
    def send_stack(self):
        print_details(" Socket_stack. send_stack running")
        try:
            self.src_LANip = self.dict_ip2LANip[self.src_ip]
            self.src_mac = self.dict_LANip2mac[self.src_LANip]
        except:
            raise ValueError(" Socket. sendto: src_ip, src_mac wrong")
        try:
            self.dst_LANip = self.dict_ip2LANip[self.dst_ip]
            self.dst_mac = self.dict_LANip2mac[self.dst_LANip]
        except:
            l = self.dst_ip.split(".")
            if len(l[3]) == 1 and "0" <= l[3] and "9" >= l[3]:
                self.dst_LANip = chr(int(l[2])) + l[3]
            else:
                self.dst_LANip = chr(int(l[2])) + chr(int(l[3]))
            self.dst_mac = 'MR'
        #Updating ports to be right length
        self.port_checking(self.src_port)
        self.port_checking(self.dst_port)

        print_details(" Socket. sendto: src/dst details: ", self.src_mac, self.src_LANip, self.src_port, self.dst_mac, self.dst_LANip, self.dst_port)
        encoded = self.stack.encode(self.msg, self.src_mac, self.src_LANip, self.src_port, self.dst_mac, self.dst_LANip, self.dst_port)
        print_details(" Layer0. Sending pulses : " + encoded)
        send(encoded)
        return int(len(encoded)/8)

    def bind_stack(self):
        print_details(" Socket_stack. bind_stack running")
        try:
            self.src_LANip = self.dict_ip2LANip[self.src_ip]
            self.src_mac = self.dict_LANip2mac[self.src_LANip]
            
        except:
            raise ValueError(" Socket. sendto: src_ip, src_mac wrong")
        print_details(" Socket_stack. bind_stack: socket binded at", self.src_mac, self.src_LANip, self.src_port)

    def receive_stack(self):
        print_details(" Socket_stack. receive_stack running")
        receiving_pulse = receive()
        #receiving_pulse = "111011100010111000111011100010111000111010100010111000111010100010111000101110001110111011101010001110111011101010001110101110100010101011101110001010101110111000111011101110111011100010101110111011100011101110111011101110001010101000100010111010100010111010100011101110111000"
        print_details(" Layer0. received pulse: ", receiving_pulse)
        decoded, src_ip, dst_ip, src_port, dst_port = self.stack.decode(receiving_pulse, self.src_mac, self.src_LANip, self.src_port)
        dst_port = self.port_checking(dst_port)

        print_details("Received messeage: " + decoded)
        try:
            sender_LANip = self.dict_LANip2ip[src_ip]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
        except:
            if len(src_ip[1]) == 1 and "0" <= src_ip[1] and "9" >= src_ip[1]:
                sender_LANip = "192.168."+str(ord(src_ip[0])) + "." + src_ip[1]
            else:
                sender_LANip ="192.168."+str(ord(src_ip[0]))+"."+str(ord(src_ip[1]))
            
        cap_msg = self.capsulate("RECVFROM", sender_LANip, src_port," "," ",decoded)
        bytearray_cap_msg = bytearray(cap_msg,encoding="UTF-8")
        bytes_sent = self.sock.sendto(bytearray_cap_msg, self.sock_app_addr)

    def capsulate(self, cmd, src_ip, src_port, dst_ip, dst_port, msg):
        cap_msg = "@C" + cmd + "@SIP" + src_ip + "@SP" + str(src_port) + "@DIP" + dst_ip + "@DP" + str(dst_port) + "@M" + msg
        return cap_msg

    def decapsulate(self, cap_msg):
        cmd_index = cap_msg.index("@C")
        src_ip_index = cap_msg.index("@SIP")
        src_port_index = cap_msg.index("@SP")
        dst_ip_index = cap_msg.index("@DIP")
        dst_port_index = cap_msg.index("@DP")
        msg_index = cap_msg.index("@M")

        cmd = cap_msg[(cmd_index+2):src_ip_index]
        src_ip = cap_msg[(src_ip_index+4):src_port_index]
        src_port = cap_msg[(src_port_index+3):dst_ip_index]
        dst_ip = cap_msg[(dst_ip_index+4):dst_port_index]
        dst_port = cap_msg[(dst_port_index+3):msg_index]
        msg = cap_msg[(msg_index+2):]
        return cmd, src_ip, src_port, dst_ip, dst_port, msg

    def port_checking(self,port):
        port4 = port if len(str(port)) == 4 else str(1000+int(port))
        port2 = port if len(str(port)) == 2 else str(int(port) - 1000)

        #Check if port (2 digit, 4 digit) saved in dictionary, if not add it
        if port2 not in self.dict_port24:
            self.dict_port24[port2] = port4
        if port4 not in self.dict_port42:
            self.dict_port42[port4] = port2

        port_return = self.dict_port42[port4] if len(str(port)) == 4 else self.dict_port24[port2]

        return port_return


#----------------------------------------------------------------------------------#


if __name__ == "__main__":
    with Safeguards():
        s_s = Socket_stack()
