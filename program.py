#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from mainclass import MainBase

def readData(fname):
    inpdata = ""
    with open(fname , 'r') as f:
        i = 1
        for line in f:
            inpdata += line
    inpdata = inpdata.rstrip('\n')

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
  
    money = Mbase.calculateAmount(saleList, shoppingList, checkObj)
    print money
    return

def main(argv=None):

    readData(argv[1])
    
if __name__ == "__main__":
    sys.exit(main(sys.argv))
