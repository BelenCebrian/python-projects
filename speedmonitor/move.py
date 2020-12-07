import shutil, os, sys, shlex, subprocess
from datetime import datetime, timedelta

DIRECTORY = 'Historico'

# change directory path to generate thing in the correct folder
# https://unix.stackexchange.com/questions/334800/python-script-output-in-the-wrong-directory-when-called-from-cron

os.chdir(sys.path[0]) 

#YESTERDAY
yesterday = datetime.now() - timedelta(days=1)
yesterday = yesterday.strftime("%d-%m-%Y")
#print(yesterday)

today = datetime.now().strftime("%d-%m-%Y")
graph_today = 'graph_'+today+'.jpg'
graph_yesterday = 'graph_'+yesterday+'.jpg'
csv_today = 'data_'+today+'.csv'
csv_yesterday = 'data_'+yesterday+'.csv'

#print('Gráfico ayer: {0}\nGráfico hoy: {1}'.format(graph_yesterday, graph_today))

#print('Datos ayer: {0}\nDatos hoy: {1}'.format(csv_yesterday, csv_today))

def move(thing):
    
    #print(thing)
    if os.path.isfile(thing):
        shutil.move(thing, DIRECTORY)
    else:
        message = 'ERROR al mover: '+thing
        #print(message)

        TOKEN1 = '1079377213:AAGWKiIBiAUg-Jm3litUkl9fGyjjik2YY1A' #actualizaciones
        TOKEN2 = '571258324:AAEJ_vzFgEM-9XDPkm7WakXntBlmU3Y7X6M'  #prueba-bot
        ID = "9093721"
        URm = "https://api.telegram.org/bot{}/sendMessage"
        URd = "https://api.telegram.org/bot{}/sendDocument"
        URp = "https://api.telegram.org/bot{}/sendPhoto"

        URLL = URm.format(TOKEN2)
        command = "curl -s -X POST {} -d chat_id={} -d text='{}'".format(URLL, ID, message)
        
        #print(command)
        args = shlex.split(command)
        p = subprocess.Popen(args)
        #print(args)
        #print(p)

if __name__ == "__main__":
    
    move(graph_yesterday)     
    move(csv_yesterday)  

