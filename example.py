from irbis64_class import irbis64, irbis64_rec

##################################
# Пример функции поиска записей в базе
##################################
def search_record(irbis):
    retval = irbis.search('ibis','HD=$',10,1,'@brief')
    if int(retval["status"]) == 0:
        print('Всего найдено: ' + retval['count'])
        nom = 1
        for item in retval["result"]:
            print('{0}. {1} (MFN={2})'.format(nom,item["rec"],item["mfn"]))
            nom += 1
    else:
        print('error')

##################################
# Пример функции чтения записи по заданному номеру MFN
##################################
def read_record(irbis):
    retval = irbis.read_record('ibis',1)
    print(retval)
         

##################################
# Пример функции создания записи и сохранения ее в базу
##################################
def creat_and_save_record(irbis):
    rec = irbis64_rec()
    rec.add_field(920,'PAZK')
    rec.add_field(900,'^Ta^B05')
    rec.add_field(102,'UA')
    rec.add_field(101,'ukr')
    rec.add_field(999,'00000')
    rec.add_field(700,'^AЛеся^GУкраїнка')
    rec.add_field(200,'^AЛісова Пісня')
    rec.add_field(210,'^D2018^CХарків')

    result = irbis.save_record('mcc', rec)
    
    if result > 0:
        print('OK')
    else:
        print('ERROR')


    
irbis = irbis64()
irbis.host = '127.0.0.1'
irbis.port = 6666
#Установка отладочного режима:
#На экран будут выводиться все пакеты
#irbis.debug = True

#Регистрация на сервере САБ ИРБИС64
irbis.reg()

#Поиск записи по запросу на языке Ирбис
#search_record(irbis)
#Чтение записи в базе по ее номеру (MFN)
#read_record(irbis)
#Создание новой записи и сохранение ее в базу данных
#creat_and_save_record(irbis)
#Чтение параметров ини-файла АРМа пользователя
#print(irbis.ini.get('MAIN', 'DBNNAMECAT'))

#разрегистрация на сервере САБ ИРБИС64
irbis.unreg()

