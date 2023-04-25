def countAutomatedCards():
    file = open("totalcards.txt", "r")

    count = 0

    for card in file:
        card = card.rstrip()
        if not card: # ignore empty lines
            continue

        if card[0] in {'#','\t', ' '}: # ignore hashtags
            continue

        count += 1
    
    file.close()
            
    return count

if __name__ == "__main__":
    print(countAutomatedCards())