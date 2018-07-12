import socket
import random

class irbis64():
    """
    Класс для подключения к серверу САБ ИРБИС64
"""
    proc_id = random.randint(11111111,99999999)
    command_num = 1

    def __init__(self,
                 host='127.0.0.1',
                 port=6666,
                 arm='C',
                 login='1',
                 password='1'):
        self.host = host
        self.port = port
        self.arm = arm
        self.login = login
        self.password = password



    ##################################
    #  Функция регистрации на сервере
    ##################################
    def reg(self):
        paramlist = ('A',
                     self.arm,
                     'A',
                     str(self.proc_id),
                     str(self.command_num),
                     '',
                     '',
                     '',
                     '',
                     '',
                     self.login,
                     self.password)
        packet = '\n'.join(paramlist)
        packet = str(len(packet)) + '\n' + packet  
        answer = self.send(packet)
        ###########################
        #Особенность регистрации - разбор ответа в кодировке cp1251
        ###########################
        answer = answer.decode('cp1251')
        answer = answer.split("\r\n")
        status = answer[10]
        return str(status)


    ##################################
    #  Функция разрегистрации на сервере
    ##################################
    def unreg(self):
        paramlist = ('B',
                     self.arm,
                     'B',
                     str(self.proc_id),
                     str(self.command_num),
                     '',
                     '',
                     '',
                     '',
                     '',
                     self.login)
        packet = '\n'.join(paramlist)
        packet = str(len(packet)) + '\n' + packet  
        answer = self.send(packet)
        answer = answer.decode('utf8')
        answer = answer.split("\r\n")
        status = answer[10]
        return str(status)


    ##################################
    #  Функция отправки команд на сервер
    ##################################
    def send(self,packet):
        sock = socket.socket()
        sock.connect((self.host, self.port))
        sock.send(packet.encode())
        tmp = b''
        data = b''
        ################################
        tmp = sock.recv(1024)
        while sock:
            if not tmp:
                sock.close()
                break
            else:
                data += tmp
                tmp = sock.recv(1024)
        #########################     
        sock.close()
        self.command_num += 1
        return data


    ##################################
    #  Функция поиска запискей в базе
    ##################################
    def search(self,
               db_name,
               search_exp,
               num_records,
               first_record,
               formatpft):
        paramlist = ('K',
                     self.arm,
                     'K',
                     str(self.proc_id),
                     str(self.command_num),
                     '',
                     '',
                     '',
                     '',
                     '',
                     db_name,
                     search_exp,
                     str(num_records),
                     str(first_record),
                     formatpft,
                     '',
                     '',
                     '')
        packet = '\n'.join(paramlist)
        packet = str(len(packet)) + '\n' + packet  
        answer = self.send(packet)
        answer = answer.decode('utf8')
        answer = answer.split("\r\n")

        status = answer[10]
        count = answer[11]
        result = []
        i = 12
        rec = ''
        mfn = ''
        while i < len(answer):
            if len(answer[i])>0:
                tmp = answer[i] 
                tmp = tmp.split('#', maxsplit=1)
                result.append ({'mfn' : tmp[0], 'rec' : tmp[1]})
            i += 1
                
        return {'status' : status, 'count' : count, 'result' : result}


