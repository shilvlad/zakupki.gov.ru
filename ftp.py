from ftplib import FTP
import os, shutil
import zipfile
import ftplib, clear, ftp
import xml.dom.minidom
import urllib.request



def download_files(year):
    ftp = FTP()
    HOST = 'ftp.zakupki.gov.ru'
    PORT = 21
    USER = 'fz223free'
    PASSWORD = 'fz223free'

    print(ftp.connect(HOST, PORT))
    print(ftp.login(USER, PASSWORD))

    ftp.cwd('out/published/Moskva/purchaseProtocol')

    dirs = ftp.nlst()

    clear.clean_dir('moskva')
    clear.clean_dir('moskva\\unziped')

    for a in dirs:
        if a.endswith('.zip') and year in a:
            print("Downloading file: ", a)
            local_filename = os.path.join(r"moskva", a)
            lf = open(local_filename, "wb")
            ftp.retrbinary("RETR " + a, lf.write , 8 * 1024)
            lf.close()

            zf = zipfile.ZipFile(local_filename)
            zf.extractall(os.path.join(r"moskva", r"unziped"))
            zf.close()

            #break # Для экспериментов
    ftp.close()