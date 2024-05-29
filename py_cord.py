import multiprocessing
import socket
import struct
import pickle
import time

# Q: Question , A: Acknowledge , Ab - Abort , C - Commit , R- request for previous log Rb- Reply backedup data
# 're'- restarted the server
class Operations:
    def __init__(self,process_ID,simulation,current_value,state= None):
        self.MCAST_GRP = '224.1.1.1'
        self.MCAST_PORT = 6005
        self.PROCESS_ID = process_ID
        self.responses = [0,0,0]
        self.current_value = current_value
        self.future_value = current_value
        self.simulation = simulation
        self.checker = 0
        self.state = state
        if simulation ==1:
            print('---------------CASE ONE: WHERE NO NODE FAILS---------------')
        elif simulation ==2:
            print('---------------CASE TWO: PARTICIPANT ONE FAIL---------------')
        elif simulation == 3 and state == None:
            print('----------------CASE THREE: COORDINATOR  FAILS AFTER SENDING CAN COMMIT MESSAGE---------------')
        elif simulation == 4 and state==None:
            print('----------------CASE FOUR: COORDINATOR FAILS AFTER SENDING COMMIT MESSAGE---------------')



    def sender(self,data = None):
              MULTICAST_TTL = 2
              sock_ref1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
              sock_ref1.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
              if self.PROCESS_ID == 'coordinator' and data == None and self.state == None:
                      opt = 'N'
                      if self.simulation == 1 or self.simulation == 2 or self.simulation==4:
                          opt = 'Y'
                      if opt == 'Y':
                          data = {
                              "data": 'message from administrator want to commit?',
                              "message_type": 'Q',
                              "process_id": str(self.PROCESS_ID),
                          }
                          self.responses = [0,0,0]
                          data = pickle.dumps(data)
                          sock_ref1.sendto(data, (self.MCAST_GRP, self.MCAST_PORT))
              elif self.PROCESS_ID == 'coordinator' and data == None and self.state == 're':
                  opt = 'N'
                  if self.simulation == 3 or self.simulation==4:
                      opt = 'Y'
                  if opt == 'Y':
                      data = {
                          "data": 'message from administrator requesting backup data',
                          "message_type": 'R',
                          "process_id": str(self.PROCESS_ID),
                      }
                      self.responses = [0, 0, 0]
                      data = pickle.dumps(data)
                      sock_ref1.sendto(data, (self.MCAST_GRP, self.MCAST_PORT))

              else:
                  if data!=None:
                      data = pickle.dumps(data)
                      sock_ref1.sendto(data, (self.MCAST_GRP, self.MCAST_PORT))

              if data !=None:
                  print(pickle.loads(data))




    def receiver(self):
              sock_ref2= socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
              sock_ref2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
              sock_ref2.bind((self.MCAST_GRP, self.MCAST_PORT))
              mreqs = struct.pack("=4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)
              sock_ref2.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreqs)
              while True:
                    if self.simulation == 2 and self.checker == 2 and self.PROCESS_ID == 'coordinator':
                        time.sleep(10)
                        if self.checker == 2:
                            data_to_be_sent = {
                              "data": 'message from coordinator Abort the transaction',
                              "message_type": 'Ab',
                              "message": "abort",
                              "process_id": str(self.PROCESS_ID),
                            }
                            print(' OPERATION ABORTED CURRENT PERMANENT COMMITED VALUE  :', self.current_value)
                            self.responses = [0, 0, 0]
                            self.sender(data_to_be_sent)
                            time.sleep(20)
                    data ,address = sock_ref2.recvfrom(10240)
                    data = pickle.loads(data)
                    message_type = data['message_type']
                    message_from = data["process_id"]
                    if message_from != 'coordinator' and message_type == 'Ac' and self.PROCESS_ID =='coordinator':
                        self.checker +=1
                    if message_from !='coordinator' and int(message_from) != self.PROCESS_ID:
                        print(data)
                    if message_type == 'Q' and message_from == 'coordinator' and self.PROCESS_ID != 'coordinator':
                        opt = 'N'
                        if self.simulation == 1 or self.simulation == 2 or self.simulation==4:
                            opt = 'Y'
                        if opt == 'Y':
                            self.future_value = self.current_value + 1
                            print('Current value       :',self.current_value)
                            print('Calculated value     :',self.future_value)
                        data_to_be_sent = {
                                  "data": 'message from participant want to commit/NO?',
                                  "message_type": 'Ac',
                                  "message":'Y',
                                  "process_id": str(self.PROCESS_ID),
                              }
                        self.sender(data_to_be_sent)
                    elif (message_type == 'C' or message_type == 'Ab') and self.PROCESS_ID != 'coordinator':
                        if message_type == 'C':
                            self.current_value = self.future_value
                            print('VALUE COMMITED PERMANENTLY AND VALUE IS     :',self.current_value)
                        else:
                            if self.PROCESS_ID == 0 and self.simulation == 3:
                                print('*******SUB SIMULATION  I HAVE RECOVERED AFTER SENDING READY MESSAGE AND RECOVERING DATA******')
                            print(' OPERATION ABORTED CURRENT PERMANENT COMMITED VALUE  :',self.current_value)


                    elif message_type == 'Ac' and self.PROCESS_ID == 'coordinator':
                        self.responses[int(message_from)] = data["message"]
                        if 0 not in self.responses:
                            if 'N' not in self.responses:
                                data_to_be_sent = {
                                    "data": 'message from coordinator commit the transaction',
                                    "message_type": 'C',
                                    "message": "commit",
                                    "process_id": str(self.PROCESS_ID),
                                }
                                self.current_value +=1
                                if self.simulation !=4:
                                    print('VALUE COMMITED PERMANENTLY AND VALUE IS     :', self.current_value)
                            else:
                                data_to_be_sent = {
                                    "data": 'message from coordinator Abort the transaction',
                                    "message_type": 'Ab',
                                    "message": "abort",
                                    "process_id": str(self.PROCESS_ID),
                                }
                                print(' OPERATION ABORTED CURRENT PERMANENT COMMITED VALUE  :', self.current_value)
                            self.responses = [0,0,0]
                            self.sender(data_to_be_sent)
                    elif message_type == 'R' and self.PROCESS_ID == 1:
                        data_to_be_sent = {
                            "data": 'sending backup data from participant to coordinator',
                            "message_type": 'Rb',
                            "message": self.current_value,
                            "process_id": str(self.PROCESS_ID),
                        }
                        self.sender(data_to_be_sent)
                    elif message_type == 'Rb' and self.PROCESS_ID == 'coordinator':
                        data_to_be_sent = {
                            "data": 'message from coordinator commit the transaction',
                            "message_type": 'C',
                            "message": "commit",
                            "process_id": str(self.PROCESS_ID),
                        }
                        self.current_value = int(data['message'])
                        print('VALUE COMMITED PERMANENTLY AND VALUE IS     :', self.current_value)
                        if self.simulation != 4:
                            self.sender(data_to_be_sent)


if __name__ == '__main__':
   # SIMULATING CASE ONE
    object = Operations('coordinator',1,0)
    process1 = multiprocessing.Process(target=object.sender, args=( ))
    process2 = multiprocessing.Process(target=object.receiver, args=())
    process2.start()
    process1.start()
    process1.join(timeout=50)
    process2.join(timeout=50)
    process1.terminate()
    process2.terminate()

    # SIMULATING CASE TWO
    time.sleep(10)

    object = Operations('coordinator', 2,1)
    process1 = multiprocessing.Process(target=object.sender, args=( ))
    process2 = multiprocessing.Process(target=object.receiver, args=())
    process2.start()
    process1.start()
    process1.join(timeout=50)
    process2.join(timeout=50)
    process1.terminate()
    process2.terminate()



    # SIMULATING CASE THREE

    # Coordinator starts and stops after 20 units of time

    object = Operations('coordinator', 3, 1)
    process1 = multiprocessing.Process(target=object.sender, args=( ))
    process2 = multiprocessing.Process(target=object.receiver, args=())
    process2.start()
    process1.start()
    process1.join(timeout=20)
    process2.join(timeout=20)
    process1.terminate()
    process2.terminate()

    # Coordinator restarts immediately

    object = Operations('coordinator', 3, 1,'re')
    process1 = multiprocessing.Process(target=object.sender, args=( ))
    process2 = multiprocessing.Process(target=object.receiver, args=())
    process2.start()
    process1.start()
    process1.join(timeout=20)
    process2.join(timeout=20)
    process1.terminate()
    process2.terminate()

    time.sleep(35)

   #SIMULATING CASE FOUR
   # coordinator sends can commit, commit transaction messages and then fails
    object = Operations('coordinator', 4, 2)
    process1 = multiprocessing.Process(target=object.sender, args=( ))
    process2 = multiprocessing.Process(target=object.receiver, args=())
    process2.start()
    process1.start()
    process1.join(timeout=30)
    process2.join(timeout=30)
    process1.terminate()
    process2.terminate()


    # Coordinator recovers and starts requesting participants for the backup


    object = Operations('coordinator', 4, 2, 're')
    process1 = multiprocessing.Process(target=object.sender, args=( ))
    process2 = multiprocessing.Process(target=object.receiver, args=())
    process2.start()
    process1.start()
    process1.join(timeout=50)
    process2.join(timeout=50)
    process1.terminate()
    process2.terminate()






