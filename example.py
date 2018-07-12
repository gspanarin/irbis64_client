from irbis64_class import irbis64

irbis = irbis64()
irbis.reg()
retval = irbis.search('ibis','HD=$',10,1,'@brief')
print(retval)
irbis.unreg()
