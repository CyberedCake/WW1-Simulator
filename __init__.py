import os, traceback, re

os.system("color")
os.system("title WWI Simulator - Loading...")
print("Loading program... please wait!")
def title(titleWhat=""):
    if(titleWhat.strip() == ""):
        os.system("title WWI Simulator")
        return
    os.system("title WWI Simulator - " + titleWhat)
def clear():
    os.system("cls")

import time, sys, math, subprocess, random, inspect, progressbar, re, json
from datetime import datetime
from os.path import exists
import urllib.request

def stripColor(string):
    addBack, nextCharErase = [], False
    index = 0
    for value in list(string):
        index += 1
        if(value == "&"):
            if(index == len(list(string))):
                addBack.append("&")
                continue
            nextCharErase = True
            continue
        if(nextCharErase == True):
            if(value == " "):
                addBack.append("&")
                addBack.append(" ")
            nextCharErase = False
            continue
        addBack.append(value)
    return ''.join(addBack)

# yes i know this function code sucks but oh well it works and
# the main reason it exist is because i'm used3 to minecraft
# color codes lol
def printF(string, doPrint=True):
    if(doPrint == False):
        return
    string = str(string)
    string = string.replace("&0", "\u001b[30m")
    string = string.replace("&1", "\u001b[34m")
    string = string.replace("&2", "\u001b[32m")
    string = string.replace("&3", "\u001b[36m")
    string = string.replace("&4", "\u001b[31m")
    string = string.replace("&5", "\u001b[35m")
    string = string.replace("&6", "\u001b[33m")
    string = string.replace("&7", "\u001b[37m")
    string = string.replace("&8", "\u001b[30;1m")
    string = string.replace("&9", "\u001b[34;1m")
    string = string.replace("&a", "\u001b[32;1m")
    string = string.replace("&b", "\u001b[36;1m")
    string = string.replace("&c", "\u001b[31;1m")
    string = string.replace("&d", "\u001b[35;1m")
    string = string.replace("&e", "\u001b[33;1m")
    string = string.replace("&f", "\u001b[37;1m")
    string = string.replace("&o", "")
    string = string.replace("&l", "\u001b[1m")
    string = string.replace("&n", "\u001b[4m")
    string = string.replace("&h", "\u001b[7m")
    string = string.replace("&r", "\u001b[0m")
    sys.stdout.write(string + "\u001b[0m" + ("\n" if "\r" not in string else ""))
    sys.stdout.flush()

# define static variables
reset = "\u001b[0m"
ending = "\u001b[36;1m"
seperator = "&c&l&h----------------------------------------------------------------------------------------------"

global randomSeed
randomSeed = str(time.time()).replace(".", "WW1SIMULATOR")
random.seed(randomSeed)

mustardGas = 15
grenades = 8
found = 2
flamethrower = 15

# define non-static global variables
mostRecentSaved = False

gameLogs = {}
results = {}
data = {}

currentLogs = []

startupErrors = []

try:
    checkDirectories = []
    cwd = os.getcwd()
    checkDirectories.append(cwd)
    checkDirectories.append(cwd + "\\saves")

    for cDirectory in checkDirectories:
        for fileName in os.listdir(cDirectory):
            try:
                fileAndDir = os.path.join(cDirectory, fileName)

                if (os.path.isfile(fileAndDir) and ".save" in fileAndDir.lower().strip() and "ww1-save" not in fileAndDir.lower().strip()):
                    file = open(fileAndDir, 'r')
                    noSave = fileName.replace(".save", "")
                    data[noSave] = json.loads(file.read())
                    file.close()
            except Exception as err:
                startupErrors.append(traceback.format_exc())
                startupErrors.append("&c&lSTARTUP ERROR: &fAn error occurred while trying to read file: &2" + fileName + " &f... &d" + str(err))

except Exception as err:
    if not("The system cannot find the path" in str(err) and "\\saves" in str(err)):
        startupErrors.append(traceback.format_exc())
        startupErrors.append("&c&lSTARTUP ERROR: &fAn error occurred within the save read service: &d" + str(err))

registered = []
for key in data.keys():
    registered.append(key + ".save")
if(len(registered) > 0):
    startupErrors.append("&a&lAUTOMATICALLY READ! &fAutomatically read these save files: &b" + ('&f, &b'.join(registered)))

clear()
printF("&6WORLD WAR I SIMULATOR")
printF(" ")
printF("&bRULES (how it works):")
printF("&e1) &fRolled 2 &8(snake eyes)&f: Reinforcements! Roll again and multiply by 10 and gain that amount.")
printF("&e2) &fRolled 3: Mustard Gas! You lose " + str(mustardGas) + " soldiers.")
printF("&e3) &fRolled 4: Grenades! You lose " + str(grenades) + " soldiers.")
printF("&e4) &fRolled 5: Found! You gain " + str(found) + " soldiers.")
printF("&e5) &fRolled 6-9: You lose *amount rolled* soldiers.")
printF("&e6) &fRolled 10: Quick rest! No soldiers gained or lost.")
printF("&e7) &fRolled 11: Flamethrower! You lose " + str(flamethrower) + " soldiers.")
printF("&e8) &fRolled 12 &8(box cars)&f: Ambush! Roll again and multiply by 10 and lose that amount.")

printF(" ")

for string in startupErrors:
    printF(string)

if(len(startupErrors) > 0):
    printF(" ")

def command():
    title()
    form = input(reset + "/" + ending)
    try:
        form = form.lower().strip()
        cmd = form.split(" ")[0]
        args = form.split(" ")
        args.pop(0)
        if(cmd.strip() == ""):
            command()
            return

        def functionNotFound(args):
            throwError("That command does not exist: /" + cmd)

        commands = Commands()
        getattr(commands, cmd.lower().strip(), functionNotFound)(args)

    except KeyboardInterrupt as keyboard:
        printF(" ")
        printF("&c&lERROR: &fYou manually cancelled the current command's process!")
    except Exception as err:
        throwError(err, True)

    command()

global logsFromID
def logsFromID(gameid):
    return gameLogs[gameid]
    
def toGameID(gameid, log):
    global currentLogs
    currentLogs.append(log)

def runSimulation(times=1, soldiersToStart=500, continueAfterZero=False):
    global gameLogs, currentLogs, results, mostRecentSaved
    try:
        gameLogs = {}
        results = {}
        
        currentLogs = []
        
        widgets = [' ',
                               progressbar.Bar('█'), ' ',
                               progressbar.Percentage(), ' (',
                               progressbar.ETA(), ') [',
                               progressbar.Timer(format="Elapsed: %(elapsed)s"), ']'
                           ]
        bar = progressbar.ProgressBar(max_value=(times+1)*101, widgets=widgets).start()
        iterationsSoFar = 0
        
        for game in range(1, times+1):
            soldiers, positives, negatives, neutrals = soldiersToStart, 0, 0, 0
            for rangeNumber in range(1, 101):
                bar.update(iterationsSoFar)
                
                diceRoll = random.randint(1, 6)
                diceRoll2 = random.randint(1, 6)
                number = diceRoll + diceRoll2

                originalAmount = soldiers
                soldiers = gameEvalNumber(game, rangeNumber, soldiers, number)

                if(originalAmount > soldiers):
                    negatives = negatives + 1
                if(originalAmount < soldiers):
                    positives = positives + 1
                if(originalAmount == soldiers):
                    neutrals = neutrals + 1

                if(soldiers <= 0 and continueAfterZero == False):
                    soldiers = 0
                    break

                iterationsSoFar = iterationsSoFar + 1

            results[game] = {'soldiers': soldiers,
                             'positives': positives,
                             'negatives': negatives,
                             'neutrals': neutrals}

            gameLogs[game] = currentLogs
            currentLogs = []

        for integer in range(0, 10):
            bar.update((times+1)*101)
            time.sleep(0.01)

        printF(" ")
        printF(" ")
        printF("&6RESULTS:")
        success, failed, total = 0, 0, 0
        for key in results.keys():
            printF(fromResults(key, results[key]))
            if(results[key]['soldiers'] > 0):
                success = success + 1
            elif(results[key]['soldiers'] <= 0):
                failed = failed + 1
            total = total + 1
        printF(" ")
        printF("&aSUCCESS RATE: &f" + str(round((success/total)*100)) + "&f%")
        printF("&cFAILURE RATE: &f" + str(round((failed/total)*100)) + "&f%")
        printF("&6TOTAL: &f" + str(total))
        printF(" ")
        mostRecentSaved = False
    except KeyboardInterrupt as err:
        printF(" ")
        throwError("You cancelled the simulation!")

def fromResults(gameID, results):
    replace = '''{gameID} {soldiers} &8|| {positives} &8|| {negatives} &8|| {neutrals}'''.format(
        gameID=expandStringBy("&e(ID: " + str(gameID) + "&e)", 10),
        soldiers=expandStringBy("&dSoldiers Remain: &f" + str(results['soldiers']), 20),
        positives=expandStringBy("&aPositives: &f" + str(results['positives']), 13),
        negatives=expandStringBy("&cNegatives: &f" + str(results['negatives']), 13),
        neutrals=expandStringBy("&6Neutrals: &f" + str(results['neutrals']), 13))
    return replace.replace("\n", "")

def expandStringBy(string, characterMeasurement):
    stringColor = string
    string = stripColor(string)
    for value in range(len(string), characterMeasurement):
        stringColor = stringColor + " "
    return stringColor

def gameEvalNumber(gameid, number, soldiers, diceRoll, doPrint=False):
    returnThis = soldiers
    if(diceRoll == 2):
        amountToReinforce = (random.randint(1, 12))*10

        returnThis = soldiers + amountToReinforce

        toGameID(gameid, dict({'soldiersLeft': returnThis, 'diceRoll': diceRoll, 'additionalNumber': amountToReinforce, 'index': number}))
        #toGameID(gameid, "&e" + str(number) + "&e) " + "&a&hREINFORCEMENTS!&r &fYou gained " + str(amountToReinforce) + " &fsoldiers! &8" + str(returnThis) + " soldiers remain!")
    elif(diceRoll == 3):
        returnThis = soldiers - mustardGas
        #toGameID(gameid, "&e" + str(number) + "&e) " + "&c&hMUSTARD GAS!&r &fYou lost " + str(mustardGas) + " soldiers! &8" + str(returnThis) + " soldiers remain!")
    elif(diceRoll == 4):
        returnThis = soldiers - grenades
        #toGameID(gameid, "&e" + str(number) + "&e) " + "&c&hGRENADES!&r &fYou lost " + str(grenades) + " soldiers! &8" + str(returnThis) + " soldiers remain!")
    elif(diceRoll == 5):
        returnThis = soldiers + found
        #toGameID(gameid, "&e" + str(number) + "&e) " + "&a&hFOUND!&r &fYou found " + str(found) + " soldiers! &8" + str(returnThis) + " soldiers remain!")
    elif(diceRoll == 10):
        toGameID(gameid, dict({'soldiersLeft': returnThis, 'diceRoll': diceRoll, 'additionalNumber': 0, 'index': number}))
    elif(diceRoll == 11):
        returnThis = soldiers - flamethrower
        #toGameID(gameid, "&e" + str(number) + "&e) " + "&c&hFLAMETHROWER!&r &fYou lost " + str(flamethrower) + " soldiers! &8" + str(returnThis) + " soldiers remain!")
    elif(diceRoll == 12):
        amountToLose = (random.randint(1, 6))*10

        returnThis = soldiers - amountToLose
        toGameID(gameid, dict({'soldiersLeft': returnThis, 'diceRoll': diceRoll, 'additionalNumber': amountToLose, 'index': number}))
        #toGameID(gameid, "&e" + str(number) + "&e) " + "&c&hAMBUSH!&r &fYou lost " + str(amountToLose) + " soldiers! &8" + str(returnThis) + " soldiers remain!")
    else:
        returnThis = soldiers - diceRoll
        toGameID(gameid, dict({'soldiersLeft': returnThis, 'diceRoll': diceRoll, 'additionalNumber': 0, 'index': number}))
        #toGameID(gameid, "&e" + str(number) + "&e) " + "&c&hDEATHS!&r &fYou lost " + str(diceRoll) + " soldiers! &8" + str(returnThis) + " soldiers remain!")

    if(diceRoll == 3 or diceRoll == 4 or diceRoll == 5 or diceRoll == 11):
        toGameID(gameid, dict({'soldiersLeft': returnThis, 'diceRoll': diceRoll, 'additionalNumber': 0, 'index': number}))
    return returnThis

# {'soldiersLeft': 500, 'diceRoll': 2, 'additionalNumber': 0}
# 500,2,0

global fromDictLog
def fromDictLog(log):
    returnThis = ""
    soldiersRemain = log['soldiersLeft']
    index = log['index']
    additNum = log['additionalNumber']
    diceRoll = log['diceRoll']
    # log['soldiersLeft'], log['index'], log['additionalNumber'], log['diceRoll']
    if(diceRoll == 2):
        returnThis = "&a&hREINFORCEMENTS!&r &fYou gained " + str(additNum) + " &fsoldiers!"
    elif(diceRoll == 3):
        returnThis = "&c&hMUSTARD GAS!&r &fYou lost " + str(mustardGas) + " &fsoldiers!"
    elif(diceRoll == 4):
        returnThis = "&c&hGRENADES!&r &fYou lost " + str(grenades) + " &fsoldiers!"
    elif(diceRoll == 5):
        returnThis = "&a&hFOUND!&r &fYou found " + str(found) + " &fsoldiers!"
    elif(diceRoll == 10):
        returnThis = "&e&hRELAX!&r &fYou have not lost nor gained soldiers!"
    elif(diceRoll == 11):
        returnThis = "&c&hFLAMETHROWER!&r &fYou lost " + str(flamethrower) + " &fsoldiers!"
    elif(diceRoll == 12):
        returnThis = "&c&hAMBUSH!&r &fYou lost " + str(additNum) + " &fsoldiers!"
    else:
        returnThis = "&c&hDEATHS!&r &fYou lost " + str(diceRoll) + " &fsoldiers!"
    returnThis = "&e(" + str(index) + "&e) &r" + returnThis + " &8" + str(soldiersRemain) + " &8soldiers remain!"
    
    return returnThis

commandsList = []
    
class Commands:
    def commandsList(self):
        cmdList = []
        for value in (inspect.getmembers(Commands, predicate=inspect.isfunction)):
            appended = str(str(value).split(",")[0])
            appended = appended.replace("('", "")
            appended = appended.replace("'", "")
            if(appended.lower() != appended):
                continue
            cmdList.append(appended)
        return cmdList

    # commands

    def help(self, args):
        if(len(args) > 1 and args[0] == "cmd_info"):
            return {'name': 'help',
                    'usage': '/help',
                    'description': 'Prints a list of commands.'
                    }
        
        for string in Commands().commandsList():
            printF(string)

    def seed(self, args):
        if(len(args) > 1 and args[0] == "cmd_info"):
            return {'name': 'seed',
                    'usage': '/seed [new seed]',
                    'description': 'Shows the current random generator seed.'
                    }
        
        if(len(args) > 0):
            random.seed(args[0])
            global randomSeed
            randomSeed = args[0]
            printF("&fYou set the current seed to &a" + str(args[0]))
            return
        
        printF("&aSeed: &f" + str(randomSeed))

    def roll(self, args):
        if(len(args) > 0 and args[0] == "cmd_info"):
            return {'name': 'roll',
                    'usage': '/roll [amount of dice]',
                    'description': 'Rolls some dice using the same RNG as the simulator.'
                    }
        
        amount = 3
        if(len(args) > 0):
            if(isInteger(args[0]) == False):
                throwError("You must enter the amount of dice as an integer!")
                return
            elif(int(args[0]) <= 0 or int(args[0]) > 100):
                throwError("The number of dice must be between 1 and 100!")
                return
            amount = int(args[0])+1
        printF("&7&nRolling " + str(amount-1) + " dice...")
        time.sleep(0.5)

        added = 0
        printF(" ")
        alternating, alternateCharacter = 0, ""
        for dice in range(1, amount):
            if(alternating == 0):
                alternating, alternateCharacter, alternateCharacter2 = 1, "&b", "&f"
            elif(alternating == 1):
                alternating, alternateCharacter, alternateCharacter2 = 0, "&9", "&7"
            diceValue = random.randint(0, 6)
            added = added + diceValue
            printF(alternateCharacter + "DICE #" + str(dice) + ": " + alternateCharacter2 + str(diceValue))
        
        printF("&6ADDED: &f" + str(added))
        printF(" ")

    def game(self, args):
        if(len(args) > 0 and args[0] == "cmd_info"):
            return {'name': 'game',
                    'usage': 'Use /game help for more information',
                    'description': 'The main command to-be used in this simulator.'
                    }
        
        global mostRecentSaved
        if(len(args) < 1):
            throwError("You must provide some game action!")
        elif(args[0] == "startsimulation"):
            if(len(args) < 3):
                throwError("You must provide the right usage! /game startsimulation <timesToRun> <soldiersToStart> <continueAfterZero>")
            elif(isInteger(args[1]) == False):
                throwError("You must enter the amount of times to run the simulation as an integer!")
            elif(isInteger(args[2]) == False):
                throwError("You must enter the amount of soldiers that the simulation will start with as an integer!")
            elif(isBoolean(args[3]) == False):
                throwError("You must enter whether to continue after 0 soldiers as a boolean!")
            else:
                printF("&7Fighting " + args[1] + " battle(s), this may take a second!")
                runSimulation(int(args[1]), int(args[2]), stringToBoolean(args[3]))
        elif(args[0] == "getfromid"):
            if(len(args) < 2):
                throwError("You must provide the right usage! /game getfromid <gameid>")
            elif(isInteger(args[1]) == False):
                throwError("You must enter the game ID as an integer!")
            else:
                try:
                    logs = logsFromID(int(args[1]))
                    printF(" ")
                    printF("&6LOGS FROM ID " + args[1] + ":")
                    for log in logs:
                        printF(fromDictLog(log))
                    printF(" ")
                except KeyError as keyError:
                    throwError("Unknown game ID: " + args[1])
        elif(args[0] == "read"):
            if(len(args) < 2):
                throwError("You must provide the right usage! /game read <file> <name>")
            elif(os.path.exists("saves/" + args[1] + ("" if ".save" in args[1] else ".save")) == False and os.path.exists(args[1] + ("" if ".save" in args[1] else ".save")) == False):
                throwError("You must enter a file that exists!")
            elif(len(args) < 3):
                throwError("You must provide the right usage! /game read <file> <name>")
            elif(args[2].replace("_", "").replace("-", "").isalnum() == False):
                throwError("Your name can only contain alphabetical characters, numerical numbers, underscores, and dashes!")
            elif(len(args[2]) >= 32):
                throwError("Your names can only be 32 characters or shorter!")
            elif(len(args) > 3 and args[3] != "-raw"):
                throwError("Your names cannot have multiple words!")
            elif("ww1-save" in args[2].lower().strip()):
                throwError("Sorry, but the \"ww1-save\" keyword cannot be used in the name!")
            else:
                printF("&7Reading file, this can take a moment...")
                fileName = ("" if os.path.exists("saves/" + args[1]) == True else "saves/") + args[1] + ("" if ".save" in args[1] else ".save")
                callThis = args[2]
                try:
                    if(os.path.exists(fileName) == False):
                        fileName = "saves\\" + fileName
                    fileName = fileName + ("" if ".save" in fileName else ".save")
                    file = open(fileName, "r")

                    data[callThis] = json.loads(file.read())
                    registered.append(callThis + ".save")
                    if(len(args) > 3 and args[3] == "-raw"):
                        printF("&6RAW Data: &8" + str(data))

                    file.close()

                    toRename = fileName.replace(args[1], args[2])
                    os.rename(fileName, toRename + ("" if ".save" in toRename else ".save"))
                    
                    printF("&aSuccessfully read and re-saved &f" + args[1] + " &ato &f" + args[2] + "&a!")
                except Exception as err:
                    throwError(err, True)
        elif(args[0] == "recent"):
            if(len(results.keys()) <= 0):
                throwError("There are no recent games to pull from!")
            elif(len(args) < 2):
                throwError("You must provide the right usage! /game recent <action...>")
            elif(args[1] == "sort"):
                if(len(args) < 3):
                    throwError("You must provide the right usage! /game recent sort <soldiers|positives|negatives|neutrals>")
                else:
                    resultsCopy = results.copy()
                    sortedValues = {}

                    try:
                        sortedValues = reverse({k: v for k, v in sorted(resultsCopy.items(), key=lambda x: x[1][args[2]])})

                        remove0, howManyRemoved = False, 0
                        if(len(args) > 3 and args[3] == "-remove0"):
                            remove0 = True

                        printF(" ")
                        printF("&6MOST " + args[2].upper() + "&6:")
                        for string in sortedValues.keys():
                            if(remove0 == True and results[string][args[2]] == 0):
                                howManyRemoved += 1
                                continue
                            printF(fromResults(int(string), results[int(string)]))
                        if(remove0 == True):
                            printF("&8           ... removed " + str(howManyRemoved) + " games that have zero " + args[2] + "!")
                        printF(" ")
                    except KeyError as keyError:
                        throwError("Game does not store value by the name of: " + args[2])
            elif(args[1] == "save"):
                if(mostRecentSaved == True):
                    throwError("The most recent game is already saved!")
                    return
                printF("&7Saving most recent game, this can take a moment...")
                fileName = "saves\\ww1-save-" + datetime.today().strftime('%m-%d-%Y-%H-%M-%S') + ".save"
                try:
                    os.makedirs("saves")
                except FileExistsError as fileExistsErr:
                    ignored = True
                try:
                    file = open(fileName, "a")
                    saveToFile = []
                    
                    save = {}
                    for key in results.keys():
                        result = {'overall': results[key],
                                  'logs': logsFromID(int(key))}
                        save[key] = result

                    file.write(str(json.dumps(save)))
                    file.close()

                    mostRecentSaved = True
                except Exception as err:
                    throwError(err, True)
                    return

                printF("&aSuccessfully saved most recent game to &f" + fileName + "&a!")
            else:
                throwError("Unknown recent game action: " + args[1])
                throwError("Available recent game actions: save, sort")
        elif(args[0] == "list"):
            printF(" ")
            printF("&b&hAVAILABLE AND READ GAMES:")
            for string in registered:
                printF("&f" + string)
            printF(" ")
        elif(args[0] == "recent" or args[0] in registered or args[0] + ".save" in registered):
            
            dataValue = args[0].replace(".save", "")
            if not(args[0] == "recent"):
                dataCopy = data[dataValue].copy()
            if(args[0] == "recent"):
                if(len(results.keys()) <= 0):
                    throwError("There are no recent games to pull from!")
                    return
                dataCopy = results.copy()


            if(len(args) < 2):
                throwError("You must provide the right usage! /game " + args[0] + " <action...>")
            elif(args[1] == "getfromid"):
                if(len(args) < 3):
                    throwError("You must provide the right usage! /game " + args[0] + " getfromid <id>")
                else:
                    logs = dataCopy[args[2]]['logs']
                    
                    printF(" ")
                    printF("&6LOGS FROM ID " + args[2] + ", GAME '" + dataValue.upper() + "':")
                    for log in logs:
                        printF(fromDictLog(log))
                    printF(" ")
            elif(args[0] == "recent" and args[1] == "save"):
                if(mostRecentSaved == True):
                    throwError("The most recent game is already saved!")
                    return
                printF("&7Saving most recent game, this can take a moment...")
                fileName = "saves\\ww1-save-" + datetime.today().strftime('%m-%d-%Y-%H-%M-%S') + ".save"
                try:
                    os.makedirs("saves")
                except FileExistsError as fileExistsErr:
                    ignored = True
                try:
                    file = open(fileName, "a")
                    saveToFile = []
                    
                    save = {}
                    for key in results.keys():
                        result = {'overall': results[key],
                                  'logs': logsFromID(int(key))}
                        save[key] = result

                    file.write(str(json.dumps(save)))
                    file.close()

                    mostRecentSaved = True
                except Exception as err:
                    throwError(err, True)
                    return

                printF("&aSuccessfully saved most recent game to &f" + fileName + "&a!")

            elif(args[1] == "show"):
                resultsCopy = {}
                for key in dataCopy.keys():
                    resultsCopy[int(key)] = dataCopy[key]['overall']

                printThis=[]
                printThis.append(" ")
                printThis.append("&6RESULTS:")
                success, failed, total = 0, 0, 0
                for string in resultsCopy.keys():
                    if(resultsCopy[int(string)]['soldiers'] > 0):
                        success = success + 1
                    elif(resultsCopy[int(string)]['soldiers'] <= 0):
                        failed = failed + 1
                    total = total + 1
                    printThis.append(fromResults(string, resultsCopy[int(string)]))
                printThis.append(" ")
                printThis.append("&aSUCCESS RATE: &f" + str(round((success/total)*100)) + "&f%")
                printThis.append("&cFAILURE RATE: &f" + str(round((failed/total)*100)) + "&f%")
                printThis.append("&6TOTAL: &f" + str(total))
                printThis.append(" ")
                printF('\n'.join(printThis))
                #if(args[2].lower() == "-file"):
                #    saveLog(args[0])
            elif(args[1] == "sort"):
                if(len(args) < 3):
                    throwError("You must provide the right usage! /game " + args[0] + " sort <soldiers|positives|negatives|neutrals>")
                else:
                    resultsCopy = {}
                    for key in dataCopy.keys():
                        # print(str(key) + " " + str(dataCopy[key]))
                        try:
                            resultsCopy[int(key)] = dataCopy[key]['overall']
                        except KeyError as keyError:
                            resultsCopy[int(key)] = dataCopy[key]

                    sortedValues = {}

                    try:
                        if(args[2] == "numerical" or args[2] == "default"):
                            executeCommand("game " + args[0] + " show")
                            return

                        remove0, howManyRemoved = False, 0
                        if(len(args) > 3 and args[3] == "-remove0"):
                            remove0 = True
                        
                        sortedValues = reverse({k: v for k, v in sorted(resultsCopy.items(), key=lambda x: x[1][args[2]])})

                        printF(" ")
                        printF("&6MOST " + args[2].upper() + "&6:")
                        for string in sortedValues.keys():
                            if(remove0 == True and resultsCopy[string][args[2]] == 0):
                                howManyRemoved += 1
                                continue
                            printF(fromResults(int(string), resultsCopy[int(string)]))
                        if(remove0 == True):
                            printF("&8           ... removed " + str(howManyRemoved) + " games that have zero " + args[2] + "!")
                        printF(" ")
                    except KeyError as keyError:
                        printF(traceback.format_exc())
                        throwError("Game does not store value by the name of: " + args[2] + " &8(" + str(keyError) + "&8)")
            else:
                throwError("Unknown " + args[0] + " game action: " + args[1])
                throwError("Available " + args[0] + " game actions: sort, show, getfromid")
        else:
            throwError("Unknown game action: " + args[0])
            throwError("Available actions: startsimulation, getfromid, recent, save, read, list, <game name>")

    def exit(self, args):
        printF(" ")
        printF("&cExiting program, please wait...")
        title("Exiting program, please wait...")
        exit()

    def eexit(self, args):
        exit()

    def restart(self, args):
        printF(" ")
        printF("&aRebooting program, please wait...")
        title("Rebooting program, please wait...")
        os.startfile(__file__)
        exit()

def saveLogs(gameType):
    fileName = "logs\\ww1-log-" + gameType + "-" + datetime.today().strftime('%m-%d-%Y-%H-%M-%S') + ".save"
    try:
        os.makedirs("logs")
    except FileExistsError as fileExistsErr:
        ignored = True
    try:
        file = open(fileName, "a")

        file.write(str(stripColor('\n'.join(printThis))))
        file.close()
    except Exception as err:
        throwError(err, True)
        return

def executeCommand(string):
    try:
        string = string.lower().strip()
        cmd = string.split(" ")[0]
        args = string.split(" ")
        args.pop(0)
        if(cmd.strip() == ""):
            command()
            return

        def functionNotFound(args):
            raise KeyError(cmd)

        commands = Commands()
        result = getattr(commands, cmd.lower().strip(), functionNotFound)(args)
        
    except Exception as err:
        throwError(err, True)

def isInteger(string):
    try:
        int(string)
        return True
    except ValueError as err:
        return False

def isBoolean(string):
    n = string.lower()
    if(n == "true" or n == "yes" or str(n) == "1" or n == "yeah"
       or n == "false" or n == "no" or str(n) == "0" or n == "nah"):
        return True
    else:
        return False

def stringToBoolean(boolean):
    n = boolean.lower()
    if(n == "true" or n == "yes" or str(n) == "1" or n == "yeah" or n == "active"):
        return True
    else:
        return False

global throwError
def throwError(why, stacktrace=False):
    if(isinstance(why, Exception) == True and stacktrace == True):
        if(isinstance(why, json.decoder.JSONDecodeError) == True):
            printF(seperator)
            printF("&6STACK TRACE:")
            tb = traceback.format_exc().strip()
            printF("&c" + tb)
            printF(seperator)
            printF("&c&lERROR: &fAn error occurred while reading a save file! Maybe the format is outdated?")
            return
        printF(seperator)
        printF("&6STACK TRACE:")
        tb = traceback.format_exc().strip()
        printF("&c" + tb)
        printF(seperator)
    printF("&c&lERROR: &f" + str(why))

global reverse
def reverse(dictionary):
    keys = list(dictionary.keys())
    returned = {}
    keys.reverse()
    for key in keys:
        returned[key] = dictionary[key]
    return returned
    
#for number in range(1, 100):
#    diceRoll = random.randint(1, 6)
#    diceRoll2 = random.randint(1, 6)
#    print(str(diceRoll) + " | " + str(diceRoll2) + " = " + str(diceRoll+diceRoll2))

if __name__ == "__main__":
  command()
