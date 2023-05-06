from importlib.resources import path
from os import mkdir
import os.path
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import shutil
from difflib import SequenceMatcher
from sys import platform


def getDirectory():
    print("Please enter the directory where you can find your mod files.")
    workingDir = Path(input("Enter Path: "))

    if workingDir.is_dir() == True:
        return workingDir
    else:
        print("This is not a valid directory! Please try again.")
        return(getDirectory())

def getCategory():
    print("Input what category the majority of your mods belong to. Please use the category as it appears in the url for a mod. E.g. 'skyrimspecialedition' instead of 'Skyrim Special Edtion'")
    categoryInput = input ("Enter Category: ")

    if categoryInput not in validCategories:
        print("The category you entered is either incorrect or is not one of the most common categories.")
        categoryResponse = input("Are you sure you want to continue? (Y/N): ")
        if categoryResponse == "Y":
            return categoryInput
        else:
            return(getCategory())
    else:
        return categoryInput
    
def getModID(modFileName):
    try:
        unmoddedModID = modFileName.split(sep,1)[1].strip()
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

def getFileModName(modFileName):
    return modFileName.split(sep,1)[0].strip()

def isSimilar(modFileName, modName):
    similarityRatio = SequenceMatcher(None, modFileName.lower(), modName.lower()).ratio()
    if similarityRatio >= 0.75:
        return True
    else:
        return False
    
def isSameName(modFileName, modName):
    if modName.find(modFileName) >= 0 or modFileName.find(modName) >=0:
        return True
    else:
        return False

def checkModName(modFileName, modName):
    if isSimilar(modFileName, modName) == True or isSameName(modFileName, modName) == True:
        return True
    else:
        return False

def getTitle(nexusCategory, modID):
    url = 'https://www.nexusmods.com/' + nexusCategory + '/mods/' + str(modID)
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    title = soup.find('title').get_text().split(sep,1)[0].split(" at ")[0]
    return title

def moveFile(modPath, filePath, similarity):
    if os.path.isdir(modPath) and similarity == True:
        try:
            shutil.move(filePath, modPath)
        except Exception as e:
            print('There was an error moving the file!')
            print(e)
    elif similarity == True:
        try:
            mkdir(modPath)
        except:
            print(modPath + " already exists!")
        try:
            shutil.move(filePath, modPath)
        except Exception as e:
            print('There was an error moving the file!')
            print(e)
    else:
        print("Mod name appears very different than the file name")            
        try:
            shutil.move(filePath, unsortedPath)
        except Exception as e:
            print('There was an error moving the file!')
            print(e)
    return

def findAccurateTitle (modID, fileModName, nexusCategory):
    output = []
    for category in validCategories:
        url = 'https://www.nexusmods.com/' + category + '/mods/' + str(modID)
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, 'html.parser')

        modName = soup.find('title').get_text().split(sep,1)[0].split(" at ")[0]
        similarity = checkModName(fileModName, modName)
        if similarity == True:
            output = [category, modName, similarity]
            return output
        else:
            print("Not from " + category)
    output = [nexusCategory, "modName", similarity]
    return output    

validCategories = ["skyrimspecialedition", "skyrim", "fallout4", "newvegas", "oblivion", "stardewvalley", "fallout3", "cyberpunk2077", "witcher3", "dragonage", "mountandblade2bannerlord", "bladeandsorcery", "monsterhunterworld", "morrowind", "dragonage2"]

workingDir = getDirectory()
nexusCategory = getCategory()

unsortedPath = os.path.join(workingDir, "UNSORTED")
categoryPath = os.path.join(workingDir, nexusCategory)


try:
    mkdir(unsortedPath)
except Exception as e:
    print(unsortedPath + " already exists!")

try:
    mkdir(categoryPath)
except:
    print(categoryPath + " already exists!")

for file in os.listdir(workingDir):
    sep = '-'
    filename = os.fsdecode(file)
    filePath = workingDir + filename
    if os.path.isdir(filePath) == False:
        print("filename = " + filename)

        print("I am working with the file: " + filename)
        modID = getModID(filename)
        print("Mod ID = " and modID)  

        if modID != 0:
            title = getTitle(nexusCategory, modID)
            fileModName = getFileModName(filename)
            similarity = checkModName(fileModName, title)
            modPath = (categoryPath + title).strip()

            if similarity == False:
                newInfo = findAccurateTitle(modID, fileModName, nexusCategory)
                newCategoryPath = os.path.join(workingDir, newInfo[0].upper().strip())

                if newInfo[1] != "modName":
                    title = newInfo[1]
                try:
                    mkdir(newCategoryPath)
                except Exception as e:
                    print(newCategoryPath + " already exists")
                modPath = os.path.join(newCategoryPath, title.strip())
                moveFile(modPath, filePath, newInfo[2])
            else:
                moveFile(modPath, filePath, similarity)
        else:
            try:
                print("This mod has no ModID and will be moved to the UNSORTED path.")
                shutil.move(filePath, unsortedPath)
            except Exception as e:
                print('There was an error moving the file!')
                print(e)
    else:
        print("This is a directory. Skipping.")

print("Complete")

        

        





    



