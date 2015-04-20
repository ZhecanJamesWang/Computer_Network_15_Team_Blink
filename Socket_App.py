"""
15 Spring. Computer Network. Lab 9. Socket_App
 - last updated 4/20/2015
"""

import CN_Sockets as s

#help debugging (print out each steps or silent)
def print_details(X, *T, **D):
    print(X, *T, **D)
    pass

sock_stack_addr = ("127.0.0.1", 1000)

AF_INET = s.AF_INET
SOCK_DGRAM = s.SOCK_DGRAM
timeout = s.timeout

class socket():
    def __init__(self, p_family=AF_INET, p_type=SOCK_DGRAM, proto=0, fileno=None):
        self.p_family=p_family
        self.p_type=p_type
        self.src_ip = '0'
        self.AF_INET, self.SOCK_DGRAM = s.AF_INET, s.SOCK_DGRAM
        self.sock = s.socket(AF_INET, SOCK_DGRAM)

    def __exit__(self,argException,argString,argTraceback):
        if argException is KeyboardInterrupt:
            print (argString)
            self.sock.close()   # return socket resources on ctl-c keyboard interrupt
            return True

    def __enter__(self):
        return self

    def bind(self,addr):
        print_details(" Socket_app. bind running")

        self.addr = addr
        self.src_ip=self.addr[0]
        self.src_port=self.addr[1]
        self.sock_app_addr = ("127.0.0.1", self.src_port)
        self.sock.bind(self.sock_app_addr)
        temp_cap_msg = self.capsulate("BIND", self.src_ip, self.src_port, " "," "," ")
        print_details(" app. bind: bind to", self.src_ip, self.src_port)
        bytes_sent = self.sock.sendto(bytearray(temp_cap_msg, encoding="UTF-8"), sock_stack_addr)

    def sendto(self, bytearray_msg, dst_addr):
        if self.src_ip == '0':
            self.src_ip = input("Your IP Address: ")
            self.src_port=input("Your Port Number: ")
       
        self.sock_app_addr = ("127.0.0.1", self.src_port)

        print_details(" Socket_app. sendto running")
        dst_ip = dst_addr[0]
        dst_port = dst_addr[1]
        msg = bytearray_msg.decode()
        cap_msg = self.capsulate("SENDTO", self.src_ip, self.src_port, dst_ip, dst_port, msg)
        bytearray_cap_msg = bytearray(cap_msg, encoding="UTF-8")
        print_details(" Socket_app. sendto: cap_msg is: ", cap_msg)
        bytes_sent = self.sock.sendto(bytearray_cap_msg, sock_stack_addr)
        return len(msg)

    def recvfrom(self, b_size):
        print_details(" Socket_app. recvfrom running")
        temp_cap_msg = self.capsulate("RECVFROM"," "," "," "," "," ")
        bytes_sent = self.sock.sendto(bytearray(temp_cap_msg, encoding="UTF-8"), sock_stack_addr)
        self.b_size = b_size
        bytearray_cap_msg, recv_addr = self.sock.recvfrom(b_size)
        cap_msg = bytearray_cap_msg.decode()
        print_details(" Socket_app. recvfrom: cap_msg is", cap_msg)
        r_cmd, r_src_ip, r_src_port, r_dst_ip, r_dst_port, r_msg = self.decapsulate(cap_msg)
        if r_cmd != "RECVFROM":
            print_details(" Socket_app_recvfrom. cmd not matched")
        return bytearray(r_msg, encoding="UTF-8"), (r_src_ip, r_src_port)

    def settimeout(self, timeout):
        if (timeout < 0): raise ValueError('timeout must be nonnegative!')
        self._timeout = timeout

    def gettimeout(self):
        return self._timout

    def capsulate(self, cmd, src_ip, src_port, dst_ip, dst_port, msg):
        cap_msg = "@C" + cmd + "@SIP" + src_ip + "@SP" + str(src_port) + "@DIP" + dst_ip + "@DP" + str(dst_port) + "@M" + msg.upper()
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

if __name__ == "__main__":
    import time
    with socket() as s:
        s.bind(("192.168.68.65", 5280))
        while True:
            print(".")
            time.sleep(2)
