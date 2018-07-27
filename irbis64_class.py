import socket
import random
import configparser

class irbis64():
    """
    Класс для подключения к серверу САБ ИРБИС64
"""
    proc_id = random.randint(11111111,99999999)
    command_num = 1
    debug = False
    ini = configparser.ConfigParser()
    error = ''
    
    def __init__(self,
                 host = '127.0.0.1',
                 port = 5555,
                 arm = 'C',
                 login = '1',
                 password = '1'):
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
        if int(status) == 0:
            tmp = '\n'.join(answer[12:])
            self.ini.read_string(tmp)
        else:
            self.error = 'REG_ERROR: ' + status
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
        if self.debug:
            print('==========================')
            print(packet)
            print('==========================')

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
        if self.debug:
            print(data)
            print('==========================')
        
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




    ##################################
    #  Функция чтения записи по заданной базе и МФН
    ##################################
    def read_record(self,
                    db_name,
                    mfn,
                    lock = 0):
        """
"""
        paramlist = ('C',
                     self.arm,
                     'C',
                     str(self.proc_id),
                     str(self.command_num),
                     '',
                     '',
                     '',
                     '',
                     '',
                     db_name,
                     str(mfn),
                     str(lock))
        packet = '\n'.join(paramlist)
        packet = str(len(packet.encode('utf8'))) + '\n' + packet  
        answer = self.send(packet)
        answer = answer.decode('utf8')
        answer = answer.split("\r\n")

        #Это статус выполнения запроса
        status = int(answer[10])
        if status == 0:
            tmp = answer[11]
            mfn = tmp[:tmp.find('#')]
            #Это статус текущей записи
            stat = tmp[tmp.find('#') + 1:]

            tmp = answer[12]
            ver = tmp[tmp.find('#') + 1:]
            fields = list()
            i = 13
            while i < len(answer):
                if len(answer[i])>0:
                    tmp = answer[i]
                    fieldnum = tmp[:tmp.find('#')]
                    fieldval = tmp[tmp.find('#') + 1:]

                    fields.append ({'fieldnum' : fieldnum, 'fieldval' : fieldval})
                i += 1
                    
            return {'mfn' : mfn, 'status' : stat, 'ver': ver, 'fields' : fields}      
        else:
            return {'error' :'status = ' + status}




    ##################################
    #  Функция сохранения записи в базу САБ ИРБИС64
    ##################################
    def save_record(self, db_name, rec, Lock = 0, IfUpdate = 1):
        """
    Db_name – имя БД
    Lock – блокировать ли запись. 1 – блокировать, 0 – не блокировать.
    IfUpdate – актуализировать ли запись. 1 – актуализировать, 0 – не актуализировать
"""
        str_rec = '{0}#{1}{3}0#{2}'.format(rec.mfn, rec.status, rec.version, chr(31)+chr(30))
        for f in rec.fields:
            str_rec += '{0}{1}#{2}'.format(chr(31)+chr(30), f['fieldnum'], f['fieldval'])
        str_rec += chr(31)+chr(30)

        paramlist = ('D',
                     self.arm,
                     'D',
                     str(self.proc_id),
                     str(self.command_num),
                     self.password,
                     self.login,
                     '',
                     '',
                     '',
                     db_name,
                     str(Lock),
                     str(IfUpdate),
                     str_rec)
        packet = '\n'.join(paramlist)
        packet = str(len(packet.encode('utf-8'))) + '\n' + packet  
        answer = self.send(packet)
        answer = answer.decode('utf8')
        answer = answer.split("\r\n")
 
        try:
            if int(answer[10]) > 0:
                return int(answer[10])
            else:
                return -1 #Ошибка
        except:
            return -1 #ошибка




class irbis64_rec():
    """
    Класс ЗАПИСЬ САБ ИРБИС64
"""
    
    def __init__(self,
                 mfn = 0,
                 status = 0,
                 version = 0,
                 fields = list()):
        self.mfn = mfn
        self.status = status
        self.version = version
        self.fields = fields

    ##################################
    #  Функция добавления поля в запись
    ##################################
    def add_field(self,fieldnum,fieldval):
        self.fields.append({'fieldnum' : fieldnum, 'fieldval' : fieldval})

    ##################################
    #  Функция добавления поля в запись
    ##################################
    def clear_field(self):
        self.fields.clear()

    ##################################
    #  Функция вывода информации о записи
    ##################################
    def rec_info(self):
        s = 'mfn = ' + str(self.mfn) + '\n'
        s += 'status = ' + str(self.status) + '\n'
        s += 'version = ' + str(self.version) + '\n'
        s += 'fields : \n'
        for f in self.fields:
            s += '\t#{0}: {1}'.format(f['fieldnum'],f['fieldval']) + '\n'
        return s
        
