import os
import  ftp
import sqlite3, clear
from lxml import etree

from profiling import time_of_function


if __name__ == "__main__":

    clear.clean_dir('moskva')


    clear.clean_dir('moskva\\unziped')
    years = ['_2018', '_2019']
    for year in years:
        print(year)


        ftp.download_files(year)

    xml_files = os.listdir(os.path.join(r"moskva", r"unziped"))
    #conn = sqlite3.connect(":memory:")  # или :memory: чтобы сохранить в RAM
    try:
        os.remove('1.db')
    except Exception:
        print ("Cannot delete db")

    conn = sqlite3.connect("1.db")  # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()

    conn.execute("""CREATE TABLE purchase(`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, timestamp text, customer text, customer_inn text, lot_name text, lot_currency text, lot_initsum text, lot_initsum_int float)""")
    conn.execute("""CREATE TABLE offers(`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, purchase_id INTEGER, supplier_name text, supplier_inn text, offer_price text, offer_currency text, offer_win text, offer_accepted text, offer_price_int float)""")

    for xml_file in xml_files:
        xml_file = os.path.join(r"moskva", r"unziped", xml_file)
        print("XML:",xml_file)

        try:
            tree = etree.parse(xml_file)
        except Exception:
            continue
        #for i in tree.findall('.//'):
        #    print (i)

        LotApplications = tree.find('//{http://zakupki.gov.ru/223fz/purchase/1}protocolLotApplications')

        # Информация о заказе
        purchaseProtocolData = tree.find('{http://zakupki.gov.ru/223fz/purchase/1}body').\
            find('{http://zakupki.gov.ru/223fz/purchase/1}item').\
            find('{http://zakupki.gov.ru/223fz/purchase/1}purchaseProtocolData')

        timestamp = purchaseProtocolData.find('{http://zakupki.gov.ru/223fz/purchase/1}createDateTime').text

        customer_name = purchaseProtocolData.find('{http://zakupki.gov.ru/223fz/purchase/1}customer').\
            find("{http://zakupki.gov.ru/223fz/types/1}mainInfo").\
            find('{http://zakupki.gov.ru/223fz/types/1}fullName').text

        customer_inn = purchaseProtocolData.find('{http://zakupki.gov.ru/223fz/purchase/1}customer'). \
            find("{http://zakupki.gov.ru/223fz/types/1}mainInfo"). \
            find('{http://zakupki.gov.ru/223fz/types/1}inn').text



        # SELECT id FROM mytable WHERE rowid=last_insert_rowid();

        protocolLotApplications = purchaseProtocolData.find('{http://zakupki.gov.ru/223fz/purchase/1}lotApplicationsList').\
            find("{http://zakupki.gov.ru/223fz/purchase/1}protocolLotApplications")

        lot = protocolLotApplications.find('{http://zakupki.gov.ru/223fz/purchase/1}lot')
        lot_name = lot.find('{http://zakupki.gov.ru/223fz/purchase/1}subject').text

        try:
            lot_currency = lot.find('{http://zakupki.gov.ru/223fz/purchase/1}currency').\
                find('{http://zakupki.gov.ru/223fz/types/1}code').text
        except Exception:
            lot_currency = ''

        try:
            lot_initsum = lot.find('{http://zakupki.gov.ru/223fz/purchase/1}initialSum').text

            #print(lot_initsum)
            lot_initsum_int = float(lot_initsum)
            #print (lot_initsum_int)
        except Exception:
            lot_initsum = ''
            lot_initsum_int = 0
        try:
            init_sum = lot.find('{http://zakupki.gov.ru/223fz/purchase/1}initialSum').text
        except Exception:
            init_sum = ''

        conn.execute("INSERT INTO purchase(timestamp, customer, customer_inn, lot_name, lot_currency, lot_initsum, lot_initsum_int) VALUES(?,?,?,?,?,?, ?)",
                       (timestamp, customer_name, customer_inn, lot_name, lot_currency, init_sum, lot_initsum_int))
        conn.commit()

        cursor = conn.execute("SELECT id FROM purchase WHERE rowid=last_insert_rowid();")
        #print(cursor)
        for row in cursor:
            purchase_id = row[0]


        offers = protocolLotApplications.findall('{http://zakupki.gov.ru/223fz/purchase/1}application')


        for offer in offers:
            try:
                supplier_name = offer.find('{http://zakupki.gov.ru/223fz/purchase/1}supplierInfo').\
                    find('{http://zakupki.gov.ru/223fz/types/1}name').text
                supplier_inn = offer.find('{http://zakupki.gov.ru/223fz/purchase/1}supplierInfo'). \
                    find('{http://zakupki.gov.ru/223fz/types/1}inn').text
            except Exception:
                supplier_name = 'Noname'
                supplier_inn = 'Noname'

            try:
                offer_price = offer.find('{http://zakupki.gov.ru/223fz/purchase/1}price').text
                offer_price_int = float(offer_price)


            except Exception:
                offer_price = 'None'
                offer_price_int = 0



            try:
                offer_currency = offer.find('{http://zakupki.gov.ru/223fz/purchase/1}currency').\
                    find('{http://zakupki.gov.ru/223fz/types/1}code').text
            except Exception:
                offer_currency = 'None'
            try:
                offer_win = offer.find('{http://zakupki.gov.ru/223fz/purchase/1}winnerIndication').text
            except Exception:
                offer_win = ''

            try:
                offer_accepted = offer.find('{http://zakupki.gov.ru/223fz/purchase/1}accepted').text
            except Exception:
                offer_accepted = ''

            #print (supplier_name, supplier_inn, offer_price, offer_currency, offer_win, offer_accepted)

            conn.execute("INSERT INTO offers(purchase_id, supplier_name, supplier_inn, offer_price, offer_currency, offer_win, offer_accepted, offer_price_int) VALUES(?, ?,?,?,?,?,?,?)",
                (purchase_id, supplier_name, supplier_inn, offer_price, offer_currency, offer_win, offer_accepted, offer_price_int))
            conn.commit()




    conn.close()