#!/usr/bin/python3
# coding: utf-8
import config
import requests
import json
import argparse
import lxml.html
import os
import sys
import platform
import difflib
import pathlib
import subprocess
import re
import datetime
import filecmp
import shlex
from urllib.request import urlopen
from dateutil.parser import parse
from io import open
from bs4 import BeautifulSoup as bs
import html2text
import textwrap

# variables globales
TOKEN1 = config.TOKEN1  # appActualizada
TOKEN2 = config.TOKEN2  # prueba-bot
CHAT1 = config.CHAT1
VERSION = config.VERSION
MODIFICADO = config.MODIFICADO
FECHA = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

# Headers
H1 = config.H1
H2 = config.H2

# Ficheros
F1 = 'versiones.txt'
F2 = 'b-versiones.txt'

# cambiamos al directorio para que los ficheros se generen en la ruta correcta
# https://unix.stackexchange.com/questions/334800/python-script-output-in-the-wrong-directory-when-called-from-cron
os.chdir(sys.path[0])

# iniciamos el parser
parser = argparse.ArgumentParser()
parser.add_argument("-V", "--version",
                    help="ver version del programa", action="store_true")

# leemos argumentos desde la terminal
args = parser.parse_args()

# comprobamos argumento 'version'
if args.version:
    # "%(prog)s
    print("webmonitor.py version: ", VERSION,
          "\n\tmodificado el: ", MODIFICADO)
    exit()


def android():
    url = "https://www.android-x86.org/"
    soup = req(url)
    linea = soup.find_all('li')[0].text
    t = linea.replace(").", ")").replace(": ", " ").replace(
        "the ", "").replace("The ", "").replace(" Android-x86", "")
    dia, texto = t[:10], t[11:]
    # dia de lanzamiento como fecha, para luego cambiarle el formato
    fecha = datetime.datetime.strptime(dia, "%Y-%m-%d")
    version = "Android-x86: "+texto+" [{:%d %b. %Y}]".format(fecha)
    #f"Android-x86: {texto} {dia:%d/%m/%Y}"
    return version


def asus():

    url = "https://www.asus.com/es/Networking/RTAC68U/HelpDesk_BIOS/"
    url2 = "https://www.asus.com/support/api/product.asmx/GetPDBIOS?website=es&pdhashedid=svItyTHFccLwnprr&model=RT-AC68U&cpu=&callback=supportpdpage"
    s = requests.session()
    r = s.get(url2, headers=H1)
    limpio = (r.text.strip('supportpdpage(')).replace('S"})', 'S"}')

#    print(formato)
    datos = json.loads(limpio)
#    print(datos)
#    print(json.dumps(datos, indent=4))
#    print(json.dumps(datos, sort_keys=True, indent=4))
#    print(datos.keys()) #dict_keys(['Result', 'Status', 'Message'])

    with open("response_formato.txt", 'w') as f1, open("response_original.txt", 'w') as f2:
        print(limpio, file=f1)
        print(r.text, file=f2)

    # leemos del archivo guardado
#    with open("response_formato.json", "r") as archivo:
#        datos = json.load(archivo)

    # print(datos['Result'].keys()) #dict_keys(['Count', 'Obj'])

    firmware = datos['Result']['Obj'][0]['Files'][0]

    titulo = (datos['Result']['Obj'][0]['Files'][0]
              ['Title']).replace(" Firmware version", ":")

    version = datos['Result']['Obj'][0]['Files'][0]['Version']
    descripcion = datos['Result']['Obj'][0]['Files'][0]['Description']
    dia = datos['Result']['Obj'][0]['Files'][0]['ReleaseDate']
    fecha = datetime.datetime.strptime(dia, "%Y/%m/%d")
    tam = datos['Result']['Obj'][0]['Files'][0]['FileSize']
    enlace = datos['Result']['Obj'][0]['Files'][0]['DownloadUrl']['Global']
    # print(firmware)

    # soup = bs(descripcion, features="lxml")  #make BeautifulSoup
    # prettyHTML = soup.prettify()   #prettify the html

    desc = html2text.html2text(descripcion)
    # print('\n',titulo,'\n\t',fecha,'\t',tam,'\n\t',enlace,'\n\n',desc)
    texto = titulo+'\n\t[{:%d %b. %Y}]'.format(fecha)+'    '+tam+'\n\t'+enlace
    return texto


def calibre():
    # return soup.select("h2.release-title")[0]
    url = "https://calibre-ebook.com/whats-new"
    soup = req(url)
    version = soup.find_all('h2')[0].string
    return version.replace("Release", "Calibre").replace(",", ".")
    #ver = re.sub("[\(\[].*?[\)\]]", "", version)
    #ver = re.sub("[^\d\.]", "", ver)
    # return ver


def comprobar_ficheros(f1, f2):
    # f1: se supone el nuevo generado por bajar_fichero(versiones.txt)
    # f2: se supone el anterior (b-versiones.txt)

    #print('Comprobando versiones...')
    #telegram('Comprobando versiones...')

    file1 = pathlib.Path(f1)
    file2 = pathlib.Path(f2)

    # primero comprobamos si los ficheros son txt
    name1, ext1 = os.path.splitext(f1)
    name2, ext2 = os.path.splitext(f2)
    print('Comparando ', f1, '  y  ', f2)

    if os.path.isfile(f1):
        print('OK: ', f1, ' EXISTE!')
        if os.path.isfile(f2):
            print('OK: Existen ambos ficheros')
            comprobar_cambios(f1, f2)
            os.remove(f2)
            os.rename(f1, F2)

        else:
            # existe f1 pero no f2, renombramos f1, bajamos nuevo y comprobamos
            print('ERROR: no existe ', f2, '\n\tRenombramos: ',
                  f1, ' a ', F2, ' y recomprobamos...')
            os.rename(f1, F2)
            bajar_fichero()
            comprobar_ficheros(F1, F2)

    else:
        # f1 no existe
        print('ERROR: no existe ', f1, '\n\tBajamos datos y recomprobamos...')
        bajar_fichero()
        comprobar_ficheros(F1, F2)


def comprobar_cambios(f1, f2):

    if filecmp.cmp(f1, f2, shallow=False):
        #print('No hay versiones nuevas')
        telegram('No hay versiones nuevas')
    else:
        #print('HAY CAMBIOS!')
        telegram('HAY CAMBIOS!')

        with open(f1, "r", encoding="utf-8") as f1, open(f2, "r") as f2:
            diff = difflib.ndiff(f2.readlines(), f1.readlines())
            for line in diff:
                if line.startswith('+'):
                    cambio = line.strip('+')
                    # print(cambio)
                    telegram(cambio)

# NO USADO: para seguir redirecciones web (ASUS)


def get_hops(url):
    redirect_re = re.compile('<meta[^>]*?url=(.*?)["\']', re.IGNORECASE)
    hops = []
    while url:
        if url in hops:
            url = None
        else:
            hops.insert(0, url)
            response = urlopen(url)
            if response.geturl() != url:
                hops.insert(0, response.geturl())
            # check for redirect meta tag
            match = redirect_re.search(response.read())
            if match:
                url = urlparse.urljoin(url, match.groups()[0].strip())
            else:
                url = None
    return hops


def gimp():
    # h3.entry-title
    url = "https://www.gimp.org/news/"
    soup = req(url)
    version = soup.select_one(
        "a[href*=released]").text.replace("GIMP", "GIMP:").rstrip()
    return version.replace("Released", " ")


def github(proyect):
    url = "https://github.com/" + proyect + "/releases/latest"
    # print(url)
    soup = req(url)
    salida = " "

    try:

        version = soup.find(
            class_="f1 flex-auto min-width-0 text-normal").text.lstrip().rstrip()
        tags = (soup.find(class_="css-truncate-target",
                          attrs={'style': "max-width: 125px"}).text).lstrip()
        time = soup.find("relative-time", class_="no-wrap").text
        body = soup.find("div", class_="markdown-body").text[:250] + "..."

        links = soup.find_all(
            "div", class_="d-flex flex-justify-between flex-items-center py-1 py-md-2 Box-body px-2")

        salida = '\n\n[X] {0} {1} [{2}]: {3} \n {4} \n \t{5}'.format(
            proyect, tags, time, version, url, textwrap.indent(body, '  \t-'))

        #salida = "===",links,"==="

        for asset in links:
            t = asset.find("a").text.lstrip().rstrip()
            size = asset.find("small").text.lstrip()
            download = asset.find("a")["href"]
            salida += '\n\n\t * {0} ({1}): github.com{2}'.format(t, size, download)

        """         if ("koreader" in url):
                filter = ["armhf", "amd64", "android", "kobo"]
                if any(x in t for x in filter):
                    print('\n\t- {0} ({1}): github.com{2}'.format(t, size, download))
            else:
            print('\n\t- {0} ({1}): github.com{2}'.format(t, size, download))
        """

    except AttributeError:
        pass

    return salida


def inkscape():
    url = "https://inkscape.org/release/"
    soup = req(url)
    texto = soup.find("div", id="sidecategory")
    version = texto.h1
    return version.text


def kodi():
    # firetv: arm (armv7a 32bits)
    url_android = "https://kodi.tv/download/852"
    url_android_32 = "http://mirrors.kodi.tv/releases/android/arm/"
    url_android_64 = "http://mirrors.kodi.tv/releases/android/arm64-v8a/"


def libreoffice():
    url = "https://libreoffice.org/download/download"
    soup = req(url)
    texto = soup.find_all("span", class_="dl_version_number")
    lreciente = texto[0].string
    lestable = texto[1].string
    return lreciente, lestable


def nuevo():
    bajar_fichero()
    telegram('#actualizaciones ULTIMAS VERSIONES:')
    telegram(F1)
    os.rename(F1, F2)


def pythonv():
    return(platform.python_version())


def req(url):
    html_content = requests.get(url, headers=H1).text
    #r = requests.get(url)
    #html_content = r.text
    return bs(html_content, 'lxml')


def raspbian():
    url = "https://www.raspberrypi.org/downloads/raspbian/"
    soup = req(url)

    imagenes = soup.find("div", class_="image-info")
    with open("raspbian.txt", "w") as f:
        print(imagenes, file=f)

    f = open("raspbian.txt", "r")
    contenido = f.read()

    #detalles = soup.find_all("div", class_="image-details")
    #descarga = soup.find("a", class_="btn dl-zip", href=True)
    soup = bs(contenido, 'html.parser')
    #print('h3:', soup.div.h3.string)
    #print('content:', soup.div.h3.contents[0])
    titulo = soup.div.h3.string
    # titulo.replace("with desktop an recommended software") #NO FUNCIONA BIEN
    nombre = titulo[:-37] + "(desktop + software)"
    #dato = soup.div.div.string
    version = soup.div.find_next('div').find_next('div').strong.string

    dia = version.find_next('div').strong.string
    fecha = datetime.datetime.strptime(dia, "%Y-%m-%d")
#    print('dia: ',dia,'\nfecha: [{:%d %b. %Y}]'.format(fecha))

    kernel = dia.find_next('div').strong.string
    tam = kernel.find_next('div').strong.string
    enlace = tam.find_next('a').find_next('a').find_next('a')['href']

    texto = 'Raspbian:\n\t'+nombre + \
        '\n\t[{:%d %b. %Y}]'.format(fecha)+'    ' + \
        tam+'    '+kernel+' kernel\n\t'+enlace
    # print(texto)

#    print('nombre: ',nombre,'\nfecha: [{:%d %b. %Y}]'.format(fecha),
#    '\nkernel: ',kernel,'\ntamaño: ',tam,'\nenlace: ',enlace)

#    for child in soup.div.children:
#        print(child.string)

    return texto


def restar(data):
    # using list comprehension + list slicing
    # remove last character from list of strings
    return data[:-2]


def telegram(mensaje):

    UR = "https://api.telegram.org/bot{}/sendMessage"
    URLL = UR.format(TOKEN1)

    if os.path.isfile(mensaje):

        f = open(mensaje, 'r')
        contenido = f.read()
        # print(contenido)
        r = requests.post(URLL, data={'chat_id': CHAT1, 'text': contenido})

    else:
        r = requests.post(URLL, data={'chat_id': CHAT1, 'text': mensaje})

        # Forma 2: curl y pasando argumento a argumento
        #entrad = "curl -s -X POST {} -d chat_id={} -d text='{}'".format(URLL, ID, mensaje)
        # print(entrad)
        #args = shlex.split(entrad)
        #p = subprocess.Popen(args)
        # print(args)
        # print(p)

    #data = json.loads(r.text)
    # print(data['ok'])


def titul(url):
    t = lxml.html.parse(url)
    return t.find(".//title").text


def titulo(url):
    soup = bs(urlopen(url).read().decode('utf-8'), features="lxml")
    linea = soup.title.string.strip('Release').strip(
        'GitHub').replace(" · ", ": ")
    resul = restar(linea).split(':')
    return resul[1]+": "+resul[0]


def vlc():
    # NO TERMINADO
    url_windows = "http://get.videolan.org/vlc/last/win64/"
    url_android = "http://get.videolan.org/vlc-android/"
    soup_windows = req(url_windows)
    soup_android = req(url_android)

    version = soup_windows.find_all('h2')[0].string
    print(version)

    texto = version
    return texto


def bajar_fichero():

    print("Comprobando en línea...\n")

    with open(F1, "w", encoding="utf-8") as f:

        print("[X]", android(), file=f)

        print(" ", file=f)
        print("[X]",asus(), file=f)

        print(" ", file=f)
        print("[X]", calibre(), file=f)
        print("[X]", gimp(), file=f)
        print("[X]", inkscape(), file=f)

        nuevo, viejo = libreoffice()
        print("\n[X] LibreOffice:", file=f)
        print("\tLibreOffice Fresh (Reciente): ", nuevo, file=f)
        print("\tLibreOffice Still (Estable):  ", viejo, file=f)

        print(" ", file=f)
        print("[X]", raspbian(), file=f)

        retropie = github("RetroPie/RetroPie-Setup")
        retro = retropie.replace(" RetroPie-Setup Script ", " ").rstrip()
        print("[X]", retro, file=f)

        print(github("sumatrapdfreader/sumatrapdf"), file=f)
        print(github("pirate/ArchiveBox"), file=f)
        print(github("FreshRSS/FreshRSS"), file=f)
        print(github("pi-hole/pi-hole"), file=f)

        print(" ", file=f)
        print(github("buggins/coolreader"), file=f)
        print(github("apprenticeharper/DeDRM_tools"), file=f)
        print(github("koreader/koreader"), file=f)
        print(github("seblucas/cops"), file=f)
        print(github("janeczku/calibre-web"), file=f)

        print(" ", file=f)
        print(github("microsoft/terminal"), file=f)
        print(github("microsoft/PowerToys"), file=f)

        print(" ", file=f)
        print(github("atom/atom"), file=f)
        print(github("microsoft/vscode"), file=f)
        print(github("headmelted/codebuilds"), file=f)

        print(" ", file=f)
        print(github("ytdl-org/youtube-dl"), file=f)
        print(github("TeamNewPipe/NewPipe"), file=f)
        print(github("jellyfin/jellyfin"), file=f)

        f.close()


if __name__ == "__main__":

    # bajar_fichero()

    # print(github("microsoft/vscode"))
    # print(github("janeczku/calibre-web/"))

    comprobar_ficheros(F1, F2)
    # print(inkscape())
    # telegram(F1)
