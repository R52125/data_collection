import random
import time
import requests
import sys
import getopt

class OrderDetail:
    def __init__(self, consumerId=0, itemId=0, itemCategory=0, amout=0 ,money=0):
        self.consumerId = consumerId
        self.itemId = itemId
        self.itemCategory = itemCategory
        self.amout = amout
        self.money = money
    def trans2Http(self, rowkey:int):
        list = []
        data = dict()
        data['headers'] = {
            'key':"%06d"%int(rowkey)+'-Order Detail',
        }
        body = {
            'consumerId':self.consumerId,
            'itemId':self.itemId,
            'itemCategory':self.itemCategory,
            'amout':self.amout,
            'money':self.money
        }
        data['body'] = str(body)
        return [data]

class Transaction:
    def __init__(self, createTime=None, paymentTime=None, deliveryTime=None, completeTime=None):
        self.createTime = createTime
        self.paymentTime = paymentTime
        self.deliveryTime = deliveryTime
        self.completeTime = completeTime

    def trans2Http(self, rowkey):
        list = []
        data = dict()
        data['headers'] = {
            'key':"%06d"%int(rowkey)+'-Transaction',
        }
        body = dict()
        if self.createTime:
            body['createTime'] = self.createTime
        if self.paymentTime:
            body['paymentTime'] = self.paymentTime
        if self.deliveryTime:
            body['deliveryTime'] = self.deliveryTime
        if self.completeTime:
            body['completeTime'] = self.completeTime
        data['body'] = str(body)
        return [data]

def generatorOrderDetail() ->OrderDetail:
    consumerId = random.randint(1,1e7)
    itemId = random.randint(1,1e7)
    itemCategory = random.randint(1,1e4)
    amout = random.randint(1,1e2)
    money = random.randint(1,1e3*amout)/10
    data = OrderDetail(consumerId, itemId, itemCategory, amout, money)
    return data

def transTime(x):
    return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x)))

def generatorTransaction(saveId, a):
    transaction = None
    t1, t2 = None, None
    if saveId[a][0] == 0:
        a1 = (2020, 1, 1, 0, 0, 0, 0, 0, 0)
        a2 = (2020, 5, 1, 0, 0, 0, 0, 0, 0)
        start = time.mktime(a1)
        end = time.mktime(a2)
        t1 = random.randint(start, end)
        t2 = t1 + random.randint(100,3600)
        saveId[a] = (1, t2)
        transaction = Transaction(transTime(t1),transTime(t2),None,None)
    elif saveId[a][0]==1:
        t1 = saveId[a][1] + random.randint(1000, 10000000)
        saveId[a] = (2, t1)
        transaction = Transaction(None,None,transTime(t1),None)
    else:
        t1 = saveId[a][1] + random.randint(1000, 10000000)
        del saveId[a]
        transaction = Transaction(None,None,None,transTime(t1))
    return transaction

def generator():
    saveId = dict()
    total = 0
    random.seed(19960106)
    while True:
        if total>100000:
            return
        if len(saveId)==0:
            t = 0
        else:
            t = random.randint(0,3)
        if t==0:
            orderDetail = generatorOrderDetail()
            rowkey = str(total)
            yield orderDetail.trans2Http(rowkey)
            saveId[rowkey] = (0,-1)
            total += 1
        else:
            a = random.sample(saveId.keys(),1)[0]
            transaction = generatorTransaction(saveId, a)
            yield transaction.trans2Http(a)
        time.sleep(random.randint(0,30)/10)

def getHostnamePort():
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"h:p:")
    except:
        print("Error")
        return None, None
    host_name, port = None, None
    for opt, arg in opts:
        if opt in ['-h']:
            host_name = arg
        elif opt in ['-p']:
            port = arg
    return host_name, port

if __name__=="__main__":
    host_name, port = getHostnamePort()
    if (not host_name) or (not port):
        print("Error")
        exit(0)
    print(host_name, port)
    f = generator()
    while True:
        try:
            plain_data = next(f)
            print(str(plain_data))
            res = requests.post(url="http://"+host_name+":"+port, json=plain_data)
        except StopIteration:
            break
    print("It's over!")


