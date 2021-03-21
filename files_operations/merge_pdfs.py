import PyPDF2, os, sys
import locale, struct #for __readlink() method

FILES = []
OUTPUT = "Result.pdf"

# resolve real link to file in Windows
def __readLink(path):
    # print("readlink(",path,")\n")
    # https://gist.github.com/Winand/997ed38269e899eb561991a0c663fa49
    # http://stackoverflow.com/a/28952464/1119602
    with open(path, 'rb') as stream:
        content = stream.read()
        # skip first 20 bytes (HeaderSize and LinkCLSID)
        # read the LinkFlags structure (4 bytes)
        lflags = struct.unpack('I', content[0x14:0x18])[0]
        position = 0x18
        # if the HasLinkTargetIDList bit is set then skip the stored IDList 
        # structure and header
        if (lflags & 0x01) == 1:
            position = struct.unpack('H', content[0x4C:0x4E])[0] + 0x4E
        last_pos = position
        position += 0x04
        # get how long the file information is (LinkInfoSize)
        length = struct.unpack('I', content[last_pos:position])[0]
        # skip 12 bytes (LinkInfoHeaderSize, LinkInfoFlags and VolumeIDOffset)
        position += 0x0C
        # go to the LocalBasePath position
        lbpos = struct.unpack('I', content[position:position+0x04])[0]
        position = last_pos + lbpos
        # read the string at the given position of the determined length
        size = (length + last_pos) - position - 0x02
        content = content[position:position+size].split(b'\x00', 1)
        return content[-1].decode('utf-16' if len(content) > 1
                                  else locale.getdefaultlocale()[1])


# change directory path to generate thing in the correct folder
# https://unix.stackexchange.com/questions/334800/python-script-output-in-the-wrong-directory-when-called-from-cron
os.chdir(sys.path[0]) 

for filename in os.listdir():
    f = os.path.splitext(filename) # split name and extension
    num = f[0][0:2] # check order: 01 (01_Name.lnk)
    if f[1] == '.lnk':
        # print("order: '{0}', name: '{1}', ext: '{2}' \n".format(num,f[0],f[1]))
        FILES.append(filename)

print("\nFILES: ",FILES,"\n")

#Check what directory we are in
# print("\ndirectory:",os.path.abspath)

# Create a new PdfFileWriter object which represents a blank PDF document
pdfWriter = PyPDF2.PdfFileWriter()

for file in FILES:
    print("■ Processing file: ",file)
    file_link = __readLink(file)
    print("\nReal file is: ",file_link)
    # Read the file opened
    file_reader = PyPDF2.PdfFileReader(file_link)
    # Loop through all the pagenumbers for the current document
    for pageNum in range(file_reader.numPages):
        pageObj = file_reader.getPage(pageNum)
        pdfWriter.addPage(pageObj)
    print("\nFile added\n\n")

# Write all the pages copied to a new final document
pdfOutputFile = open(OUTPUT, 'wb')
pdfWriter.write(pdfOutputFile)

# Close file and open it using default app
pdfOutputFile.close()
print("■■■■ Opening resulting file... ■■■■\n\n")
os.startfile(OUTPUT)
# file1.close()
# file2.close()