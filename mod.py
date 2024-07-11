class Mod:
    modID = 0000
    modName = ""
    modURL = ""
    modGame = ""
    
    def __init__(self, filelocation, filename):
        self.filelocation = filelocation
        self.filename = filename
    
    def getModID(self):
        sep = '-'
        try:
            unmoddedModID = self.filename.split(sep,1)[1].strip()
        except:
            print("This mod has no ModID")
            return(0)
        
        if unmoddedModID[0] == sep:
            unmoddedModID = unmoddedModID[1:].strip()
            self.modID = unmoddedModID
            self.getModID
        elif unmoddedModID[0].isdigit():
            modID = unmoddedModID.split(sep,1)[0].strip()
            print (f'ModID = {modID}')
            return(modID)
        else:
            try:
                unmoddedModID = unmoddedModID.split(sep,1)[1].strip()
                if unmoddedModID[0].isdigit():
                    modID = unmoddedModID.split(sep,1)[0].strip()
                    print (f'ModID = {modID}')
                    return(modID)
                else:
                    print("This ModID is broken: " + unmoddedModID)
                    return(0)
            except Exception as e: 
                print(e)
                print("This ModID is broken " + unmoddedModID)
                return(0)
