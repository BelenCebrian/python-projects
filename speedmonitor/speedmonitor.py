#!/usr/bin/python3
# coding: utf-8

import speedtest
import datetime, time
import csv, os, sys

s = speedtest.Speedtest()

# cambiamos al directorio para que los ficheros se generen en la ruta correcta
# https://unix.stackexchange.com/questions/334800/python-script-output-in-the-wrong-directory-when-called-from-cron
os.chdir(sys.path[0]) 

def threads():
    servers = []  # servers = [1234] (specific server)
    threads = 2 
    # threads = None (no threads test)

    s.get_servers(servers)
    s.get_best_server()
    s.download(threads=threads)
    s.upload(threads=threads)
    s.results.share()

    results_dict = s.results.dict()
    print(results_dict)

def normal_mode():
    #print("\nn", sys.version)
    #print(os.getcwd())
    #print("method2!!")
    
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    time_now = datetime.datetime.now().strftime("%H:%M")

    filename = 'data_'+today+'.csv'
    #print(filename)
    file_exists = os.path.isfile(filename)

    with open(filename, 'a+', newline='') as csvfile:
        fields = ['time', 'download', 'upload', 'ping']
        writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=fields )

        server = s.get_best_server()
        ping = round(s.results.ping, 2)

        if not file_exists:
            writer.writeheader()

        download = round((round(s.download()) / 1048576), 2)
        upload = round((round(s.upload()) / 1048576), 2)

        #writer.writerow({time_now, download, upload})

        writer.writerow({ 
            'time': time_now,
            'download': download, 
            'upload': upload,
            'ping': ping
        })

        #print(f"time: {time_now}, download: {download} Mb/s, upload: {upload} Mb/s, ping: {ping} ms")
        #time.sleep(60*5) # delay

if __name__ == "__main__":
    normal_mode()
