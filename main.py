import csv


def copyFromROM(currentItemPointer, romPointer, structSize):
    j = structSize

    while j > 0:
        WRAM[currentItemPointer + j - 1] = ROM[romPointer + j - 1]
        j -= 1


def getItemROMPointer(itemID):
    offset_pointer = itemID * 2 + int.from_bytes(ROM[0x38010:0x38010 + 2], byteorder='little')
    offset = int.from_bytes(ROM[0x038000 + offset_pointer:0x038000 + offset_pointer + 2], byteorder='little')
    return offset + int.from_bytes(ROM[0x38010:0x38010 + 2], byteorder='little')


def printOutput():
    current_offset = 0
    ID = 1
    out_txt = "PID: {0:>3}, ID: {1:<20}, Durability: {2:<3}, Kills: {3:<3}"
    while current_offset < 0x348:
        if WRAM[0x003D8B + current_offset] <= 137:
            print(out_txt.format(ID, rows[WRAM[ItemRAMPointer + 4 + current_offset] + 1][0], WRAM[ItemRAMPointer + 4 + current_offset + 1],
                                 WRAM[ItemRAMPointer + 4 + current_offset + 5]))
        else:
            print(out_txt.format(ID, hex(WRAM[ItemRAMPointer + 4 + current_offset]), WRAM[ItemRAMPointer + 4 + current_offset + 1],
                                 WRAM[ItemRAMPointer + 4 + current_offset + 5]))
        current_offset += 6
        ID += 1


if __name__ == '__main__':

    ROMfile = input('Spefify the path of your unheadered FE4 ROM file: ')
    WRAMfile = input('Spefify the path of your WRAM dump .bin file: ')
    ItemNames = input('Spefify the path of your ItemDataOffsets.csv file: ')

    with open(ROMfile, "rb") as i:
        ROM = bytearray(i.read())

    with open(ItemNames, "r", encoding="UTF-8") as c:
        sheet = csv.reader(c)
        rows = [row for row in sheet]

    while True:

        with open(WRAMfile, "rb") as i:
            WRAM = bytearray(i.read())

        ItemRAMPointer = 0x003D87
        ItemROMPointer = 0x000000
        StructSize = 0xDD
        PlayerItemID = int(input("Insert the starting PID (decimal):"))
        print("\n")
        CurrentItemRAMPointer = ((PlayerItemID - 1) * 6) + 4 + ItemRAMPointer

        CurrentLoop = 0

        while CurrentLoop < 2:

            ROMPointer = 0x3F0004
            InventorySlot = 1

            while InventorySlot < 0xB6:
                CurrentROMPointer = (InventorySlot - 1) * StructSize + ROMPointer

                corrupt_txt = "Corrupting PID: {0}: Pointer {1} with data from {2}"
                print(corrupt_txt.format(hex(PlayerItemID), hex(CurrentItemRAMPointer), hex(CurrentROMPointer)))

                copyFromROM(CurrentItemRAMPointer, CurrentROMPointer, StructSize)

                if CurrentItemRAMPointer & 0x00FF >= 0x8C:
                    print("PID: " + hex(CurrentItemRAMPointer & 0x00FF) + " is not within the valid 0x8C range, loop completed.")
                    CurrentLoop += 1
                    break
                else:
                    PlayerItemID = CurrentItemRAMPointer & 0x00FF
                    print("PID: " + hex(PlayerItemID) + " is within the valid 0x8C range, evaluate its item ID.")
                    CurrentItemRAMPointer = ((PlayerItemID - 1) * 6) + 4 + ItemRAMPointer
                    EvaluatedItemID = int(WRAM[CurrentItemRAMPointer])

                    ItemROMPointer = getItemROMPointer(EvaluatedItemID)

                    if WRAM[CurrentItemRAMPointer + 1] == 0:
                        # Item is treated as a broken weapon
                        ItemROMPointer = ItemROMPointer & 0x7FFF
                        WeaponRank = WRAM[ItemROMPointer + 7] + 1

                        if WRAM[ItemROMPointer + 1] >= 2:
                            WeaponType = 0
                        else:
                            WeaponType = WRAM[ItemROMPointer + 10]

                        offset = int.from_bytes(ROM[WeaponType * 2 + 0x07E2DC:WeaponType * 2 + 0x07E2DC+2], byteorder='little')
                        EvaluatedItemID = ROM[0x07E2DC + offset + WeaponRank]
                        ItemROMPointer = getItemROMPointer(EvaluatedItemID)

                    txt = 'Item Durability: {0}, Item ID: {1}, Type: {2}'

                    match ROM[0x038000 + ItemROMPointer + 1]:
                        case 0:
                            ItemType = 'Weapon'
                        case 1:
                            ItemType = "Staff"
                        case 2:
                            ItemType = "Item"
                        case _:
                            ItemType = "Invalid: " + hex(ROM[0x038000 + ItemROMPointer])

                    eval_text = "Evaluating: Durability: {0}, equals Item ID: {1}, Equip Type: {2}"
                    if EvaluatedItemID <= 137:
                        print(eval_text.format(int(WRAM[CurrentItemRAMPointer + 1]), rows[EvaluatedItemID+1][0], ItemType))
                    else:
                        print(
                            eval_text.format(int(WRAM[CurrentItemRAMPointer + 1]), hex(EvaluatedItemID), ItemType))

                    if ROM[0x038000 + ItemROMPointer + 1] == 0:
                        print("Weapon found, loop completed.\n")
                        CurrentLoop += 1
                        break
                    else:
                        print("Not a weapon, look at next inventory slot.\n")
                        InventorySlot += 1

        print("Result:\n")
        printOutput()
        print("\n")
