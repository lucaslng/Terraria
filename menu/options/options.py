import pygame as pg
from widgets.button import Button
from utils.constants import SURF, HEIGHT, WIDTH, FRAME
from utils.screens import Screens
import utils.defaultKeys as defaultKeys
import utils.userKeys as userKeys
import importlib
import os


class KeybindButton(Button):
    def __init__(self, x, y, width, height, actionName, key):
        super().__init__(x, y, width, height, self.getDisplayName(key))
        self.action = actionName
        self.key = key
        self.waitingForKey = False
        self.isDuplicate = False
    
    def getDisplayName(self, key):
        display_mappings = {
            pg.K_SPACE: "SPACE",
            pg.K_RETURN: "RETURN",
            pg.K_ESCAPE: "ESC",
            pg.K_TAB: "TAB",
            pg.K_BACKSPACE: "BACK",
            pg.K_DELETE: "DE",
            pg.K_UP: "↑",
            pg.K_DOWN: "↓",
            pg.K_LEFT: "←",
            pg.K_RIGHT: "→",
            pg.K_LEFTBRACKET: "[",
            pg.K_RIGHTBRACKET: "]",
            pg.K_QUOTE: "'",
            pg.K_QUOTEDBL: '"',
            pg.K_SLASH: "/",
            pg.K_BACKSLASH: "\\",
            pg.K_MINUS: "-",
            pg.K_EQUALS: "=",
            pg.K_SEMICOLON: ";",
            pg.K_COMMA: ",",
            pg.K_PERIOD: ".",
            pg.K_BACKQUOTE: "`"
        }
        
        if key in display_mappings:
            return display_mappings[key]
            
        keyname = pg.key.name(key)
        if len(keyname) == 1 and keyname.isalpha():
            return keyname.upper()
        
        return keyname.upper()
    
    def handleEvent(self, event, mousePos) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mousePos):
                self.isPressed = True
                self.waitingForKey = True
                self.text = "Press a key..."
                return True
            
        elif event.type == pg.KEYDOWN and self.waitingForKey:
            self.key = event.key
            self.text = self.getDisplayName(event.key)
            self.waitingForKey = False
            
            setattr(userKeys, self.action, event.key)
            return True
        
        elif event.type == pg.MOUSEBUTTONUP:
            self.isPressed = False
            
        return False
        
    def draw(self, font, textColor, backgroundColor) -> None:
        #Draw red background for duplicate bindings
        if self.isDuplicate:
            duplicateRect = self.rect.inflate(6, 6)
            pg.draw.rect(SURF, (255, 0, 0), duplicateRect)
        
        super().draw(font, textColor, backgroundColor)

class OptionsMenu:
    def __init__(self):
        self.font = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 32)
        self.titleFont = pg.font.Font("assets/MinecraftRegular-Bmg3.otf", 48)
        
        #Layout parameters
        self.layout = {
            'buttonWidth': 200,
            'buttonHeight': 40,
            'verticalSpacing': 60,
            'categorySpacing': 80,
            'labelOffset': 250,
            'titleHeight': 80,
            'footerHeight': 100,
            'sidePadding': 50,
            'titleToContentSpacing': 40
        }
        
        self.scrollY = 0
        self.scrollSpeed = 30
        self.viewportHeight = HEIGHT - self.layout['titleHeight'] - self.layout['footerHeight']
        
        centerX = FRAME.centerx
        
        self.loadKeybinds()
        
        self.keybindButtons = [
            ("Movement", [
                ("walkLeft", "Walk Left", self.currentKeys.walkLeft),
                ("walkRight", "Walk Right", self.currentKeys.walkRight),
                ("jump", "Jump", self.currentKeys.jump)
            ]),
            ("Actions", [
                ("interact", "Interact", self.currentKeys.interact),
                ("interactEntity", "Interact Entity", self.currentKeys.interactEntity),
                ("consume", "Consume", self.currentKeys.consume)
            ]),
            ("Inventory", [
                ("slot1", "Slot 1", self.currentKeys.slot1),
                ("slot2", "Slot 2", self.currentKeys.slot2),
                ("slot3", "Slot 3", self.currentKeys.slot3),
                ("slot4", "Slot 4", self.currentKeys.slot4),
                ("slot5", "Slot 5", self.currentKeys.slot5),
                ("slot6", "Slot 6", self.currentKeys.slot6),
                ("slot7", "Slot 7", self.currentKeys.slot7),
                ("slot8", "Slot 8", self.currentKeys.slot8),
                ("slot9", "Slot 9", self.currentKeys.slot9)
            ])
        ]
        
        self.hasConflicts = False
        
        self.specialKeys = {
            pg.K_SPACE: "SPACE",
            pg.K_RETURN: "RETURN",
            pg.K_ESCAPE: "ESCAPE",
            pg.K_TAB: "TAB",
            pg.K_BACKSPACE: "BACKSPACE",
            pg.K_DELETE: "DELETE",
            pg.K_UP: "UP",
            pg.K_DOWN: "DOWN",
            pg.K_LEFT: "LEFT",
            pg.K_RIGHT: "RIGHT",
            pg.K_LEFTBRACKET: "LEFTBRACKET",
            pg.K_RIGHTBRACKET: "RIGHTBRACKET",
            pg.K_QUOTE: "QUOTE",
            pg.K_QUOTEDBL: "QUOTEDBL",
            pg.K_SLASH: "SLASH",
            pg.K_BACKSLASH: "BACKSLASH",
            pg.K_MINUS: "MINUS",
            pg.K_EQUALS: "EQUALS",
            pg.K_SEMICOLON: "SEMICOLON",
            pg.K_COMMA: "COMMA",
            pg.K_PERIOD: "PERIOD",
            pg.K_BACKQUOTE: "BACKQUOTE"
        }
        
        self.buttons = []
        totalHeight = self.layout['verticalSpacing']        #Initial spacing from top
        
        for category, bindings in self.keybindButtons:
            totalHeight += self.layout['categorySpacing']
            
            for actionName, displayName, key in bindings:
                self.buttons.append({
                    'label': displayName,
                    'button': KeybindButton(
                        centerX + self.layout['labelOffset'],
                        totalHeight,
                        self.layout['buttonWidth'],
                        self.layout['buttonHeight'],
                        actionName,
                        key
                    ),
                    'yOffset': totalHeight
                })
                totalHeight += self.layout['verticalSpacing']
        
        self.maxScroll = max(0, totalHeight - self.viewportHeight)
        
        #Create back and reset buttons
        buttonY = HEIGHT - self.layout['footerHeight'] + 20
        self.backButton = Button(
            centerX - self.layout['buttonWidth'] - 10,
            buttonY,
            self.layout['buttonWidth'],
            self.layout['buttonHeight'],
            "Back"
        )
        
        self.resetButton = Button(
            centerX + 10,
            buttonY,
            self.layout['buttonWidth'],
            self.layout['buttonHeight'],
            "Reset binds"
        )
        
    def updateDuplicateFlags(self):
        """Update the duplicate flags for all keybind buttons and check for conflicts"""
        #Create a dictionary to track key counts
        keyCount = {}
        
        #Count occurrences of each key
        for button in self.buttons:
            key = button['button'].key
            keyCount[key] = keyCount.get(key, 0) + 1
        
        #Check for conflicts
        self.hasConflicts = False
        for button in self.buttons:
            isDuplicate = keyCount[button['button'].key] > 1
            button['button'].isDuplicate = isDuplicate
            if isDuplicate:
                self.hasConflicts = True

    def loadKeybinds(self):
        #Check if userKeys.py exists and has data
        if os.path.exists("utils/userKeys.py") and os.path.getsize("utils/userKeys.py") > 0:
            self.currentKeys = userKeys
        else:
            self.currentKeys = defaultKeys

    def resetToDefault(self):
        with open("utils/userKeys.py", "w") as f:
            f.write("import pygame as pg\n\n")
            
            #Write each default keybind
            for category, bindings in self.keybindButtons:
                for actionName, _, _ in bindings:
                    keyValue = getattr(defaultKeys, actionName)
                    
                    if keyValue in self.specialKeys:
                        keyName = self.specialKeys[keyValue]
                    else:
                        #regular keys use lowercase
                        keyName = pg.key.name(keyValue).lower()
                    
                    formattedKey = f"pg.K_{keyName}"
                    f.write(f"{actionName} = {formattedKey}\n")
                f.write("\n")
        
        importlib.reload(userKeys)
        self.loadKeybinds()
        
        # Update all button texts
        for button in self.buttons:
            action = button['button'].action
            newKey = getattr(self.currentKeys, action)
            button['button'].key = newKey
            button['button'].text = button['button'].getDisplayName(newKey)

    def handleEvents(self) -> None | Screens:
        mousePos = pg.mouse.get_pos()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.saveKeybinds()
                return Screens.QUIT
            
            #Handle scrolling
            elif event.type == pg.MOUSEWHEEL:
                self.scrollY = max(0, min(self.maxScroll, self.scrollY - event.y * self.scrollSpeed))
            
            #Handle buttons
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.backButton.rect.collidepoint(mousePos) and self.hasConflicts == False:
                    self.saveKeybinds()
                    return Screens.MENU
                
                elif self.resetButton.rect.collidepoint(mousePos):
                    self.resetToDefault()
                
                elif self.layout['titleHeight'] <= mousePos[1] <= HEIGHT - self.layout['footerHeight']:
                    if not any(button['button'].waitingForKey for button in self.buttons):
                        for button in self.buttons:
                            if button['button'].rect.collidepoint(mousePos):
                                button['button'].handleEvent(event, mousePos)
                                break
                    else:
                        for button in self.buttons:
                            if button['button'].waitingForKey:
                                button['button'].handleEvent(event, mousePos)
                                break
            
            # Handle key events for active keybind button
            elif event.type == pg.KEYDOWN:
                for button in self.buttons:
                    if button['button'].waitingForKey:
                        if button['button'].handleEvent(event, mousePos):
                            self.updateDuplicateFlags()
                        break
        
        return None

    def saveKeybinds(self):
        with open("utils/userKeys.py", "w") as f:
            f.write("import pygame as pg\n\n")
            
            for category, bindings in self.keybindButtons:
                for actionName, _, _ in bindings:
                    keyValue = getattr(userKeys, actionName)
                    
                    #Get the key name
                    if keyValue in self.specialKeys:
                        #special keys remain uppercase
                        keyName = self.specialKeys[keyValue]
                    else:
                        #regular letter keys are lowercase
                        keyName = pg.key.name(keyValue).lower()
                    
                    f.write(f"{actionName} = pg.K_{keyName}\n")
                f.write("\n")

    def draw(self):
        SURF.fill((25, 25, 25))
        
        #Draw title
        title = self.titleFont.render("Controls", True, (255, 255, 255))
        titleRect = title.get_rect(centerx=FRAME.centerx, top=(self.layout['titleHeight'] - title.get_height()) // 2)
        SURF.blit(title, titleRect)
        
        scrollRect = pg.Rect(0, self.layout['titleHeight'], WIDTH, self.viewportHeight)
        SURF.set_clip(scrollRect)
        
        #Draw categories and buttons
        currentY = self.layout['titleHeight'] + self.layout['titleToContentSpacing'] - self.scrollY
        
        for category, bindings in self.keybindButtons:
            #Draw category header
            categoryText = self.font.render(category, True, (255, 255, 255))
            categoryRect = categoryText.get_rect(centerx=FRAME.centerx - self.layout['labelOffset'], centery=currentY)
            
            if (self.layout['titleHeight'] <= categoryRect.centery <= 
                HEIGHT - self.layout['footerHeight']):
                SURF.blit(categoryText, categoryRect)
            
            currentY += self.layout['verticalSpacing']
            
            for button in (b for b in self.buttons if b['label'] in [binding[1] for binding in bindings]):
                actualY = button['yOffset'] - self.scrollY
                
                if (self.layout['titleHeight'] - self.layout['buttonHeight'] <= actualY <= 
                    HEIGHT - self.layout['footerHeight']):
                    button['button'].rect.y = actualY
                    
                    #Draw label
                    label = self.font.render(button['label'], True, (200, 200, 200))
                    labelRect = label.get_rect(
                        right=FRAME.centerx + self.layout['labelOffset'] - 20,
                        centery=actualY + self.layout['buttonHeight'] // 2
                    )
                    SURF.blit(label, labelRect)
                    
                    #Draw button
                    button['button'].draw(self.font, (255, 255, 255), (100, 100, 100))
                
                currentY += self.layout['verticalSpacing']
            
            if category != self.keybindButtons[-1][0]:
                currentY += self.layout['categorySpacing']
        
        SURF.set_clip(None)
        
        resetColor = (100, 100, 100)
        backColor = (100, 100, 100) if not self.hasConflicts else (50, 50, 50)
        
        self.resetButton.draw(self.font, (255, 255, 255), backColor)
        self.backButton.draw(self.font, (255, 255, 255) if not self.hasConflicts else (150, 150, 150), resetColor)
        
        #Draw scroll indicators if needed
        if self.scrollY > 0:
            pg.draw.polygon(SURF, (200, 200, 200), [
                (FRAME.right - 20, self.layout['titleHeight'] + 10),
                (FRAME.right - 10, self.layout['titleHeight'] + 20),
                (FRAME.right - 30, self.layout['titleHeight'] + 20)
            ])
        
        if self.scrollY < self.maxScroll:
            pg.draw.polygon(SURF, (200, 200, 200), [
                (FRAME.right - 20, HEIGHT - self.layout['footerHeight'] - 10),
                (FRAME.right - 10, HEIGHT - self.layout['footerHeight'] - 20),
                (FRAME.right - 30, HEIGHT - self.layout['footerHeight'] - 20)
            ])

    def run(self) -> Screens:
        while True:
            mousePos = pg.mouse.get_pos()
            
            nextScreen = self.handleEvents()
            if nextScreen is not None:
                return nextScreen
            
            #Update buttons
            self.backButton.update(mousePos)
            self.resetButton.update(mousePos)
            
            scrollAdjustedPos = (mousePos[0], mousePos[1] + self.scrollY)
            for btn in self.buttons:
                if self.layout['titleHeight'] <= btn['button'].rect.y <= HEIGHT - self.layout['footerHeight']:
                    btn['button'].update(scrollAdjustedPos)
            
            self.draw()
            pg.display.flip()

def optionsScreen() -> Screens:
    menu = OptionsMenu()
    return menu.run()