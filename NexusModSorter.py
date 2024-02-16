from importlib.resources import path
from os import mkdir
import os.path
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import shutil
from difflib import SequenceMatcher
from sys import platform
import tkinter
import threading


modsToSearch = []  
threads = []

validCategories = ["skyrimspecialedition", "skyrim", "fallout4", "newvegas", "oblivion", "stardewvalley", "fallout3", "cyberpunk2077", "witcher3", "dragonage", "mountandblade2bannerlord", "bladeandsorcery", "monsterhunterworld", "morrowind", "dragonage2"]

def getDirectory(): #responsible for displaying the UI and collecting desired selections
    
    print("NexusModSorter")
    print("===============")
    
    while True:
        try:
            tkinter.Tk().withdraw()
            workingDir = tkinter.filedialog.askdirectory(initialdir = "/", title = "Select the directory which contains your images") #Tkinter allows for the creation of pop-up file directories
        except:
            workingDir = input("Enter the full file path of the folder where your mods are stored:\n")
        if os.path.exists(workingDir): #pathlib is incompatible with pyinstaller, so I'm using os.path
            return workingDir
        else:
            print("This is not a valid directory! Please try again.")
    
def getModID(filename):
    try:
        unmoddedModID = filename.split(sep,1)[1].strip()
    except:
        print("This mod has no ModID")
        return(0)
    
    if unmoddedModID[0] == sep:
        unmoddedModID = unmoddedModID[1:].strip()
        getModID(unmoddedModID)
    elif unmoddedModID[0].isdigit():
        modID = unmoddedModID.split(sep,1)[0].strip()
        return(modID)
    else:
        try:
            unmoddedModID = unmoddedModID.split(sep,1)[1].strip()
            if unmoddedModID[0].isdigit():
                modID = unmoddedModID.split(sep,1)[0].strip()
                return(modID)
            else:
                print("This ModID is broken: " + unmoddedModID)
                return(0)
        except Exception as e: 
            print(e)
            print("This ModID is broken " + unmoddedModID)
            return(0)

def isSimilar(modFileName, modName):
    strippedModFileName = modFileName.split("-", 1)[0]
    similarityRatio = SequenceMatcher(None, strippedModFileName.lower(), modName.lower()).ratio()
    if modName.find(modFileName) >= 0 or modFileName.find(modName) >=0:
        isContained = True
    else:
        isContained = False

    if similarityRatio >= 0.70 or isContained == True:
        return True
    else:
        return False

def moveFile(mod):
    sourcePath = os.path.join(mod[2])
    destinationPath = os.path.join(workingDir, mod[3].upper(), mod[4])
    if os.path.isdir(destinationPath):
        try:
            shutil.move(sourcePath, destinationPath)
        except Exception as e:
            print('There was an error moving the file!')
            print(e)
    else:
        try:
            mkdir(destinationPath)
        except:
            print(destinationPath + " already exists!")
        try:
            shutil.move(sourcePath, destinationPath)
        except Exception as e:
            print('There was an error moving the file!')
            print(e)

def titleSearch (modID, modFileName, categoryToSearch):
    url = f'https://www.nexusmods.com/{categoryToSearch}/mods/{str(modID)}'
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    modName = soup.find('title').get_text().split(sep,1)[0].split(" at ")[0]
    similarity = isSimilar(modFileName, modName)
    if similarity == True:
        return [categoryToSearch, modName]
    else:
        return False
            
def iterateCategories (mod, category=0):
    modID = mod[0]
    filename = mod[1]
    currentCategory = category
    print(f'ModID = {modID}, filename = {filename}, currentCategory = {currentCategory}')
    while currentCategory < len(validCategories):
        foundTitle = titleSearch(modID, filename, validCategories[currentCategory])
        if  foundTitle == False:
            print (f'Not {validCategories[currentCategory]}')
            currentCategory += 1
            iterateCategories(mod, currentCategory)
        else:
            print (f'Found in {validCategories[currentCategory]}')
            mod.append(foundTitle[0])
            mod.append(foundTitle[1])
            foundModTitles.append(mod)
            return foundModTitles
        break

def parallelModSearch():
    global foundModTitles
    foundModTitles = []
    for mod in modsToSearch:
        print(f'mod = {mod}')
        thread = threading.Thread(target=iterateCategories, args=(mod, 0))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threading.enumerate():
        if thread.daemon:
            continue
        try:
            thread.join()
        except RuntimeError as err:
            if 'cannot join current thread' in err.args[0]:
                # catchs main thread
                continue
            else:
                raise
    #return foundModTitles




workingDir = getDirectory()
unsortedPath = os.path.join(workingDir, "UNSORTED")

try:
    mkdir(unsortedPath)
except Exception as e:
    print(unsortedPath + " already exists!")

for file in os.listdir(workingDir):
    sep = '-'
    filename = os.fsdecode(file)
    filePath = os.path.join(workingDir, file)
    if os.path.isdir(filePath) == False:
        print("filename = " + filename)

        print("I am working with the file: " + filename)

        modID = getModID(filename)
        if modID == 0:
            try:
                print("This mod has no ModID and will be moved to the UNSORTED path.")
                shutil.move(filePath, unsortedPath)
            except Exception as e:
                print('There was an error moving the file!')
                print(e)
            continue

        print("Mod ID = " and modID)  
        output = [modID, filename, filePath]
        modsToSearch.append(output)

parallelModSearch()
print (foundModTitles)
for mod in foundModTitles:
    categoryPath = os.path.join(workingDir, mod[3].upper())
    if not os.path.isdir(categoryPath):
        mkdir(categoryPath)
    moveFile(mod)
