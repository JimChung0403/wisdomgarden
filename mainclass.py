#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
from datetime import datetime


_PRODUCT_DISCOUNT_MAP_ = {
    "0" : 1,
    "1" : 1,
    "2" : 1,
    "3" : 1
    }

_PRODUCTTPYE_ = {
    "電子" : "0",
    "食品" : "1",
    "日用品" : "2",
    "酒類" : "3"
    }

_PRODUCT_MAP_ = {
    "ipad" : _PRODUCTTPYE_["電子"],
    "iphone" : _PRODUCTTPYE_["電子"],
    "螢幕" : _PRODUCTTPYE_["電子"],
    "筆記型電腦" : _PRODUCTTPYE_["電子"],
    "鍵盤" : _PRODUCTTPYE_["電子"],
    "麵包" : _PRODUCTTPYE_["食品"],
    "餅乾" : _PRODUCTTPYE_["食品"],
    "蛋糕" : _PRODUCTTPYE_["食品"],
    "牛肉" : _PRODUCTTPYE_["食品"],
    "魚" : _PRODUCTTPYE_["食品"],
    "蔬菜" : _PRODUCTTPYE_["食品"],
    "餐巾紙" : _PRODUCTTPYE_["日用品"],
    "收納箱" : _PRODUCTTPYE_["日用品"],
    "咖啡杯" : _PRODUCTTPYE_["日用品"],
    "雨傘" : _PRODUCTTPYE_["日用品"],
    "啤酒" : _PRODUCTTPYE_["酒類"],
    "白酒" : _PRODUCTTPYE_["酒類"],
    "伏特加" : _PRODUCTTPYE_["酒類"]
    }


class MainBase(object):
    _errno = _checkoutamount = 0
    _product_map = _product_type = _product_discount_map = {}
    _checkoutamount = 0

    def __init__(self):
        try:
            self._errno = 0
            self._product_map = _PRODUCT_MAP_
            self._product_type = _PRODUCTTPYE_
            self._product_discount_map = _PRODUCT_DISCOUNT_MAP_
            self._checkoutamount = 0.0
        except:
            self._errno = -1
        return

    @property
    def errno(self):
            return self._errno

    def __del__(self):
        self._errno = 0
        return
    
    def __getPricebysale__(self, amount, dc):
        return amount * float(dc)

    def __getDiscounts__(self, salelist, checkdate):
        if len(salelist) == 0:
            return 1
        sale = salelist[0]
        rbdate = datetime.strptime(sale["date"], "%Y.%m.%d")
        ccdate = datetime.strptime(checkdate, "%Y.%m.%d")
        return self._product_discount_map[sale["producttype"]] if( rbdate >= ccdate ) else 1

    def __getValuefromPattern__(self, s, ptn):
        return re.search(ptn, s).group(0)

    # get saleInfo from partI
    def getSalebysaleData(self, data):
        salList = []
        salObj = {}
        arrData = data.split('\n')

        for d in arrData:
            salObj = {}
            arrsal = d.split('|')
            if len(arrsal) < 3:
                continue
            salObj["date"] = arrsal[0]
            salObj["producttype"] = self._product_type[arrsal[2]]
            salObj["discount"]  = self._product_discount_map[self._product_type[arrsal[2]]] = arrsal[1]
            salList.append(salObj)
        return salList
       
 
    # get shoppingInfo from partII
    def getShoppingbyshoppingData(self, data):
        sppList = []
        sppObj = {}
        arrData = data.split('\n')
        for d in arrData:
            sppObj = {}
            try:
                sppObj["num"] = self.__getValuefromPattern__(d, '[\d][^*]*')
                sppObj["producy"] = self.__getValuefromPattern__(d, '(?<=\*)[^:]*')
                sppObj["cost"] = self.__getValuefromPattern__(d, '(?<=:)[.\w]+')
                sppObj["totalcost"] = int(sppObj["num"]) * float(sppObj["cost"])
                sppObj["producttype"] = _PRODUCT_MAP_[sppObj["producy"]]
                sppList.append(sppObj)
            except:
                print '資料格式錯誤或沒有販售該產品(%s)'%sppObj["producy"]

        return sppList

    # get checkoutInfo from partIII
    def getCheckInfobycheckData(self, data):
        couponList = []
        couponObj = {}
        checkInfo = {
            "couponlist" : couponList
        } 
        
        arrData = data.split('\n',1)
        checkInfo["checkdate"] = arrData[0]

        try:
            arrCoupon = arrData[1].split('\n')
            for d in arrCoupon:
                couponObj = {}
                if len(d.strip()) == 0:
                    continue
                arrcp = d.split(' ')
                couponObj["period"] = arrcp[0]
                couponObj["condition"] = arrcp[1]
                couponObj["tradein"]   = arrcp[2]
                couponList.append(couponObj)
        except:
            pass
        
        checkInfo["couponlist"] = couponList
        return checkInfo

    #Checkout amount calculated
    def calculateAmount(self, salelist, shoppinglist, checkobj):
        
        for s in shoppinglist:
            #print s
            filsale = filter(lambda x: x["producttype"] == s["producttype"], salelist)
            rebate = self.__getDiscounts__(filsale, checkobj["checkdate"])
            #print rebate
            samount = self.__getPricebysale__( s["totalcost"], rebate)
            self._checkoutamount += samount


        #print self._checkoutamount
        for c in checkobj["couponlist"]:
            cpdate = datetime.strptime(c["period"], "%Y.%m.%d")
            ccdate = datetime.strptime(checkobj["checkdate"], "%Y.%m.%d")
            if int(c["condition"]) <= self._checkoutamount:
                self._checkoutamount -= float(c["tradein"]) if cpdate>=ccdate else self._checkoutamount
                #print self._checkoutamount

        return self._checkoutamount

def main(argv=None):

    inpdata = """2015.11.5|0.7|電子
2015.11.15|0.7|食品

1*ipad:2399.00
12*啤酒:25.00
1*螢幕1:1799.00

2015.11.11
2016.3.2 1000 200
2016.3.6 1000 700
    """


    arrInpData = inpdata.split('\n\n')
    saleData = arrInpData[0]
    shoppingData = arrInpData[1]
    checkData = arrInpData[2]

    Mbase = MainBase()
    if Mbase.errno != 0:
        print "Faild to init MainBase object"
        return
    
    saleList = Mbase.getSalebysaleData(saleData)
    shoppingList = Mbase.getShoppingbyshoppingData(shoppingData)
    checkObj = Mbase.getCheckInfobycheckData(checkData)

    #print saleList
    #print shoppingList
    #print checkObj

    #return
    money = Mbase.calculateAmount(saleList, shoppingList, checkObj)
    print money

if __name__ == "__main__":
    sys.exit(main(sys.argv))

