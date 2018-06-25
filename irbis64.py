import socket
import random

port = 6666
host = '127.0.0.1'

login = '1'
password = '1'
arm = 'C'
proc_id = random.randint(11111111,99999999)
command_num = 1


##################################
#  Функция регистрации на сервере
##################################
def reg(login, password):
    paramlist = ('A', arm, 'A', str(proc_id), str(command_num), '', '', '', '', '', login, password)
    packet = '\n'.join(paramlist)
    packet = str(len(packet)) + '\n' + packet  
    answer = send(packet)
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
def unreg(login,password):
    paramlist = ('B', arm, 'B', str(proc_id), str(command_num), '', '', '', '', '', login)
    packet = '\n'.join(paramlist)
    packet = str(len(packet)) + '\n' + packet  
    answer = send(packet)
    answer = answer.decode('utf8')
    answer = answer.split("\r\n")
    status = answer[10]
    return str(status)


##################################
#  Функция отправки команд на сервер
##################################
def send(packet):
    global command_num
    sock = socket.socket()
    sock.connect((host, port))
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
    command_num = command_num + 1
    return data


##################################
#  Функция поиска запискей в базе
##################################
def search(db_name, search_exp, num_records, first_record, formatpft):
    paramlist = ('K', arm, 'K', str(proc_id), str(command_num), '', '', '', '', '',db_name, search_exp, str(num_records), str(first_record), formatpft, '', '', '')
    packet = '\n'.join(paramlist)
    packet = str(len(packet)) + '\n' + packet  
    answer = send(packet)
    #answer = answer.decode('cp1251')
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


#Регистрация на сервере Ирбиса
retval = reg(login,password)
print('Результаты регистрации на сервере - ' + retval)
#Поиск книг в базе
retval = search('ibis','HD=$',10,1,'@brief')
#Вывод на печать результатов поиска
if (int(retval['status']) == 0):
    i = 0
    while i < len(retval['result']):
        print('Книга №' + str(i) + ': ' + '(mfn=' + retval['result'][i]['mfn'] +  ') ' + retval['result'][i]['rec']) 
        i += 1
        
#print('Выполнение поиска - ' + retval)
retval = unreg(login,password)
print('Результаты разрегистрации на сервере - ' + retval)
#Разрегистрация на сервере Ирбиса
