import json
import subprocess
import random

def addCards() -> list:
    CARDS_IN_M15 = getCardNamesFromJson("../../parser/data/M15.json")
    
    m15File = open("../../data/m15_cards.txt", "a")
    cubeCardsFile = open("../../data/cube_cards.txt", "a")

    automationFile = open("totalcards.txt", "r")

    addedCubeCards, addedM15Cards = [], []

    lines = [] 
    for line in automationFile:
        line = line.rstrip()
        if not line:
            continue

        if line[:3] != '###':  # end of a card
            lines.append(line)
            continue

        if not lines: 
            continue

        cardName = lines[0]
        if cardName in CARDS_IN_M15: 
            addCardtoFile(m15File, lines)
            addedM15Cards.append(cardName)
        else: 
            addCardtoFile(cubeCardsFile, lines)
            addedCubeCards.append(cardName)

        lines = []
            
    automationFile.close()
    m15File.close()
    cubeCardsFile.close()

    addedCards = [addedCubeCards, addedM15Cards]

    addCardsToParser(addedCards)

    return addedCards

def getCardNamesFromJson(jsonFilename) -> list:
    jsonFile = open(jsonFilename)
    cards = json.load(jsonFile)

    card_list = []
    
    for _set in cards.values():
        card_list.extend(_set['cards'])

    jsonFile.close()

    cards = set()
    for card in card_list:
        cards.add(card["name"])

    return cards

def addCardtoFile(file_to_write, card) -> None: 
    file_to_write.write("#"*30 + "\n")

    for info in card:
        file_to_write.write(info)
        file_to_write.write("\n")

    file_to_write.write("\n\n" + "#"*30)

def addCardsToParser(cards):
    addCardsToParserList(cards = cards[0], 
                        path = "../../parser/cube_card_list.txt")
    
    addCardsToParserList(cards = cards[1], 
                         path = "../../parser/m15_card_list.txt")

def addCardsToParserList(cards, path=''):
    """ In order for the cards to actually be in game, they have to be added to the parser's list and so they need to go through this function"""
    if not path:
        return

    currentCardsInList = getCardsInParserList(path)
    with open(path, "a") as file:
        for card in cards:
            if card in currentCardsInList:
                continue

            file.write(f"{card}\n")
    
def getCardsInParserList(path):
    parserList = open(path, 'r')
    cards = []
    for line in parserList:
        cards.append(line.replace("\n",""))
    return cards

def createDecks(deck_num, size, cards) -> set:
    """ deck_num: number of decks to create
        size: how many cards a deck must have
        cards: a list of cards to randomly pick from """
    
    files = [open(f'../../data/decks/deck{i + 1}.txt', 'w') for i in range(deck_num)]
    cards_in_decks = set()

    for file in files:
        for i in range(size):
            card = random.choice(cards)
            file.write(f'{random.randint(1,10)} {card}')

            if i + 1 == size: 
                continue

            file.write("\n")
            cards_in_decks.add(card)

        file.close()

    return cards_in_decks

def isParserSuccessful():
    process = runParser()
    return True if not process.stderr else False

def runParser() -> bool:
    """ Run everytime we add cards, so we can actually use them in the game """
    process = subprocess.Popen("cd ../..; python3 -m parser.parse_mtgjson", 
                            shell=True, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT)
    return process

def runMTGUnitTests(command='') -> bool:
    """ Runs the game's unit tests - checks for errors as well """
    if not command: 
        command = "cd ../..; ./test.sh" # make sure we're in the actual directory and run the unit tests
    
    process = subprocess.Popen(command, 
                               shell=True, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.STDOUT)
    return process

def passesUnitTests():
    unitTestsProcess = runMTGUnitTests()
    outputLines = unitTestsProcess.stdout.readlines()

    for line in outputLines:
        line = str(line)

        if "FAILED" in line:
            # print(line)
            return False
        
    return True

if __name__ == "__main__":
    cards = addCards()

    if not isParserSuccessful():
        raise Exception("Parser failed to run")

    if not passesUnitTests():
        raise Exception("Failed Unit Tests")
    
    createDecks(2, 10, cards[0])