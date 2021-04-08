import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import requests, json, csv, argparse
import lxml.html
import os, sys, platform, difflib, pathlib, subprocess, re, filecmp, shlex
from datetime import datetime, timedelta
from urllib.request import urlopen
from dateutil.parser import parse
from io import open
from bs4 import BeautifulSoup as bs
import html2text
import config #TOKENs

# variables globales
TOKEN1 = config.TOKEN1  # appActualizada
TOKEN2 = config.TOKEN2  # prueba-bot
ID = config.CHAT1
VERSION = config.VERSION
MODIFICADO = config.MODIFICADO

times = []
download = []
upload = []
ping = []

today = datetime.now().strftime("%d-%m-%Y")
graph = 'graph_'+today+'.jpg'
filename = 'data_'+today+'.csv'

# cambiamos al directorio para que los ficheros se generen en la ruta correcta
# https://unix.stackexchange.com/questions/334800/python-script-output-in-the-wrong-directory-when-called-from-cron
os.chdir(sys.path[0]) 

def make_graph():
    
    #print(filename)
    file_exists = os.path.isfile(filename)

    if file_exists:
        with open(filename, 'r') as csvfile:
            plots = csv.reader(csvfile, delimiter=',')
            next(csvfile)
            for row in plots:
                times.append(str(row[0]))
                download.append(float(row[1]))
                upload.append(float(row[2]))
                ping.append(float(row[3]))

        #print("times: ", times, "\n", "download:", download, "\n", "upload:", upload, "\n", "ping:", ping, "\n" )

        # EJES
        fig, ax1 = plt.subplots()
        fig.suptitle("Velocidad de Internet ("+today+")")
        #ax = fig.add_subplot(111)

        color = 'tab:blue'
        ax1.plot(times, download, label='descarga', color='r')
        ax1.set_xlabel('Tiempo (H:M)')
        ax1.plot(times, upload, label='subida', color='b')
        ax1.set_ylabel('Velocidad (Mbps)')

        ax2 = ax1.twinx()
        color = 'tab:green'
        ax2.plot(times, ping, label='ping', color='#ADB7BD')
        ax2.set_ylabel('Ping (ms)')

        ax1.tick_params(axis='x', rotation=90)
        #fig.autofmt_xdate()   #rota HORAS y SALE eje X

        # https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot

        # legend
        legend = fig.legend(title='Leyenda', bbox_to_anchor=(0.90, 1.15), fontsize='small' )

        #ymax = max(download)
        #xpos = download.index(ymax)
        #xmax = upload[xpos]

        #ax1.annotate('descarga max', xy=(xmax, ymax), xytext=(xmax, ymax+5),
        #            arrowprops=dict(facecolor='black', shrink=0.05),
        #            )

        #style = dict(size=10, color='orange')
        #ax.text('2012-1-1', 3950, "Máxima descarga", **style)

        text = "Máximos \n -Descarga: {0}\n -Subida: {1}\n -Ping: [{2}-{3}]".format(max(download),max(upload),min(ping),max(ping))
        #print(text)
        #plt.subplots_adjust(left=0.3)
        #plt.text(50,50, text, fontsize=10)

        # SAVING
        #fig.tight_layout()
        #plt.savefig(graph) 
        plt.savefig(graph, bbox_extra_artists=(legend,), bbox_inches='tight')
        #plt.show()
    
    else:
        telegram('No se pudo guardar el gráfico')


def telegram(thing):
    graphh = r""+thing
    #Method 1: https://stackoverflow.com/questions/61463102/how-to-send-photo-via-telegram-bot-with-file-path
    #Method 2: curl + args

    URm = "https://api.telegram.org/bot{}/sendMessage"
    URd = "https://api.telegram.org/bot{}/sendDocument"
    URp = "https://api.telegram.org/bot{}/sendPhoto"
        
    if os.path.isfile(graphh):
        URLL = URp.format(TOKEN2)
        #command = "curl -s -X POST {} -d chat_id={} -d photo={}".format(URLL, ID, open(graphh, 'rb'))

        files_to_send = {
            'photo': open(graphh, 'rb')
        }

        message = ('https://api.telegram.org/bot'+ TOKEN2 + '/sendPhoto?chat_id=' + ID + 'caption=' + 'Velocidad Internet')
        send = requests.post(message, files = files_to_send)
        #print(send)

    else:
        URLL = URm.format(TOKEN2)
        command = "curl -s -X POST {} -d chat_id={} -d text='{}'".format(URLL, ID, 'Error: '+thing)
        #print(command)
        args = shlex.split(command)
        p = subprocess.Popen(args)
        #print(args)
        #print(p)

if __name__ == "__main__":
    
    make_graph()
    telegram(graph)     
