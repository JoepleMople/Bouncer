import pygame as p
from pygame import mixer
import os
import sys
import time as t
import random as r
import math
import json
global score

p.init()
mixer.init()
p.display.init()

screen = p.display.set_mode((1280, 800))
p.display.set_caption('NEA')
clock = p.time.Clock()

running = True
main_init = True
main = False
newOrLoad_init = False
newOrLoad = False
newGame = False
loadExistingGame = False
failedLoad = False
maingame_init = False
maingame = False
settings_init = False
settings = False
shop_init = False
shop = False
pause_init = False
pause = False
gameOver_init = False
gameOver = False

fillerColour = (255,255,255)

background = p.image.load("backdrop.jpeg").convert_alpha()
background = p.transform.scale(background, (screen.get_width(), screen.get_height()))

gameFont = p.font.Font('press2start.ttf', size=20) # gameOver-init

jump = False # maingame-init
left = False #
right = False #

doubleJumpUpgrade = False # 
secondLifeUpgrade = False # 

player_pos = p.Vector2(screen.get_width() / 2, 337) # maingame_init (but only for the new game)

character = p.image.load("character_idle.png").convert_alpha()
character = p.transform.scale(character, (character.get_width()*3,character.get_height()*3))

hostileNPC = p.image.load("enemy.png").convert_alpha()
hostileNPC = p.transform.scale(hostileNPC, (hostileNPC.get_width()*3,hostileNPC.get_height()*3))

platformSurface = p.image.load("platform.png").convert_alpha()
platformSurface = p.transform.scale(platformSurface, (platformSurface.get_width()*2, platformSurface.get_height()*2))

cursorShape = (
  "XX                      ",
  "XXX                     ",
  "XXXX                    ",
  "XXXXX                   ",
  "XXXXXX                  ",
  "XXXXXXX                 ",
  "XXXXXXXX                ",
  "XXXXXXXXX               ",
  "XXXXXXXXXX              ",
  "XXXXXXXXXXX             ",
  "XXXXXXXXXXXX            ",
  "XXXXXXXXXXXXX           ",
  "XXXXXXXXXXXXXX          ",
  "XXXXXXXXXXX             ",
  "XX  XXXXXXX             ",
  "     XXXXXX             ",
  "     XXXXXX             ",
  "      XXXXXX            ",
  "      XXXXXX            ",
  "       XXXX             ",
  "                        ",
  "                        ",
  "                        ",
  "                        ")

cursor = p.cursors.compile(cursorShape)
p.mouse.set_cursor((24, 24), (0, 0), *cursor)

last_time_ms = int(round(t.time()*1000))
state = 0 

score = 0
highScore = 0
gold = 0

p.mixer.set_num_channels(1)
backgroundMusic = p.mixer.Sound("backgroundMusic.mp3")
p.mixer.Sound.play(backgroundMusic, loops=-1)

volumePercentageValue = 50 
p.mixer.Sound.set_volume(backgroundMusic, int(volumePercentageValue)/100)

bufferVariable = True
revive = False
xbool = False
enemies = []

class Platform:
    def __init__(self, x, y):
        self.hitbox = p.Rect(x, y, platformSurface.get_width(), platformSurface.get_height())
        #creates hitbox of platform

class Character:
    def __init__(self, player_pos):
        self.x = player_pos.x
        self.y = player_pos.y
        self.width = character.get_width()
        self.height = character.get_height()
        self.vert_vel = 0 # Initial velocity for movement
        self.hitbox = p.Rect(self.x, self.y, self.width, self.height)
        #creates class usuable variables
        
    def move_right(self):
        self.x += 5
        return self.x # moves player position right by 5 pixels

    def move_left(self):
        self.x -= 5
        return self.x # moves player position left by 5 pixels

    def jump(self, doubleJump):
        possibleToJump = OnPlatform(pcharacter, platforms) # if the player is on a platform, then it is possible to jump
        if possibleToJump or doubleJump:
            self.vert_vel = -20 # when space is pressed and it is possible to jump, sets vertical velocity to -20
        if doubleJump:
            doubleJump = False
        return doubleJump
    
    def get_vert_vel(self):
        return self.vert_vel #returns the vlue of vertical velocity for saving the game
    
    def set_vert_vel(self, vert_vel):
        self.vert_vel = vert_vel # sets the value of vertical velocity when loading the game
        
    def draw(self, screen):
        # Draw the character on the screen
        screen.blit(character, (player_pos.x, player_pos.y))

    def update(self, player_pos):
        self.x = player_pos.x # updates the constantly updating player_pos.x variable to self.x for consistency
        self.y = player_pos.y
        self.hitbox = p.Rect(self.x, self.y, self.width, self.height)
        self.y += self.vert_vel # If you have velocity, Move
        onPlatform = OnPlatform(pcharacter, platforms)
        if onPlatform and self.vert_vel > 0: # character is falling and is on a platform so gravity must not occur
            self.vert_vel = 0
            self.y = onPlatform.hitbox.top - pcharacter.height
        else: # Not on platform so they must fall due to gravity
            self.vert_vel += 1
        return self.y

def platformOverlap(platform1, platform2): # return True or False as to if the two platforms overlap
    return platform1.hitbox.colliderect(platform2.hitbox)

def generateInitialPlatforms(platforms, numOfPlatforms):
    counter = 0
    global enemies
    for _ in range(numOfPlatforms): # generate x number of platforms where 'x' is numOfPlatforms
        xcoord = r.randint(0, int(screen.get_width()-58))
        ycoord = r.randint(-24, int(screen.get_height()-24))
        # random x and y coordinates
        newPlatform = Platform(xcoord, ycoord) # generate hitbox of platform at random coords
        overlap = False
        for existingPlatform in platforms: # checks for each existing platform generated
            if r.randint(1,80) == 80:
                enemy = enemyGeneration((xcoord+7.5), (ycoord-63))
                enemies.append(enemy)
            if platformOverlap(newPlatform, existingPlatform): 
                overlap = True # if overlap has been found, the new platform is not added to the screen
                counter += 1 # counter is incremented up one to keep number of generated platforms consistent as 35
                try:
                    enemies.remove(enemy)
                except:
                    pass
        if not overlap: 
            platforms.append(newPlatform)# if no overlap is found, add the platform object to the screen
    if counter >= 1:
        generateInitialPlatforms(platforms, counter)   
    return platforms, enemies # return generated platforms list

def drawPlatforms(platforms): # small module that draws all generated platforms to the screen
    for platform in platforms:
        screen.blit(platformSurface, platform.hitbox.topleft) # draws platform from the top left, as thats where (0,0) is

def OnPlatform(pcharacter, platforms):
    pcharacterBottom = pcharacter.y + (character.get_height()) # assigns y coordinate value to the bottom of the character
    pcharacterCentreX = pcharacter.x + pcharacter.width/2 # assigns x coordinate value to the centre of the character (middle line through sprite)
    for platform in platforms:
        if (platform.hitbox.bottom >= pcharacterBottom >= platform.hitbox.top) and (platform.hitbox.left <= pcharacterCentreX <= platform.hitbox.right):
            # if the character if standing on the platform...
            return platform # ...return the platform currently 'being stood' on.
    return False 

def startPlatform():
    starterPlatform = Platform((player_pos.x-7.5), (player_pos.y+character.get_height())) # generate a platform object under the charcter's feet
    return [starterPlatform]

def scrollUp(score):
    player_pos.y += 3 # begin moving the character and platforms down, giving the illusion of scrolling up
    score += 3 # character moves upwards and increases their score
    for platform in platforms: # moves all platforms down
        p.Rect.move_ip(platform.hitbox, 0,3)
    for enemy in enemies: #moves all enemies down
        p.Rect.move_ip(enemy["hitbox"], 0,3)
    drawPlatforms(platforms) # we have changed the position of all platforms, so we blit them to update positions, same deal with the character
    pcharacter.draw(screen) # same deal with the character
    return score

def scrollDown(): # exactly the same but inverse of the above function (move everything up instead of down)
    if not gameOver or not gameOver_init:
        player_pos.y -= 3
        for platform in platforms:
            p.Rect.move_ip(platform.hitbox, 0,-3)
        for enemy in enemies:
            enemy["hitbox"].y -= 3
        drawPlatforms(platforms)
        pcharacter.draw(screen)
    return enemies

def platformOnScreen(platform): # checking to see if the platform is on the screen, using the screenObject Rect object as defined above.
    return (platform.hitbox.y > screen.get_height())

def newPlatformGeneration(platforms, numOfPlatforms): # same deal as generateInitialPlatforms() but different generation parameters
    # instead it is called to generate only 1 new platform everytime 1 platform leaves the screenObject and is deleted
    counter = 0
    for _ in range(numOfPlatforms):
        xcoord = r.randint(0, int(screen.get_width()-58))
        ycoord = r.randint(-234, -24) # generate new platform at the top of the screen, essentially infinite platform generation
        newPlatform = Platform(xcoord, ycoord)
        overlap = False
        for existingPlatform in platforms:
            if r.randint(1,80) == 80:
                enemy = enemyGeneration((xcoord+7.5), (ycoord-63))
                enemies.append(enemy)
            if platformOverlap(newPlatform, existingPlatform):
                overlap = True
                counter += 1
                try:
                    enemies.remove(enemy)
                except:
                    pass
        if not overlap:
            platforms.append(newPlatform)    
        if counter >= 1:
            newPlatformGeneration(platforms, counter)
    return platforms # returns the updated version of the 'platforms' list to draw everything to the screen

def displayText(text, font):
    textSurface = font.render((str(text)), False, (0,0,0)) # creates a modular blittable surface of some text
    return textSurface

def enemyGeneration(x, y): # creates a dictionary containing all enemy attributes
    width = hostileNPC.get_width()
    height = hostileNPC.get_height()
    return {
        "hitbox": p.Rect(x, y, width, height), # creates a Rect hitbox of the enemy with the given x and y coordinates from generating platforms
        "lives": 50 # lives goes down very quickly so i set it high
    }

def enemyCollisionEvent(enemy, enemies, score): # if the character and enemy hitboxes overlap, then this module runs
    if player_pos.x <= enemy["hitbox"].centerx: # detects if the player is to the left side of the enemy
            for _ in range(3):
                player_pos.x -= 0.5 # attempts to move the player off the platform, killing them
    else: # or if the player is to the right
            for _ in range(3):
                player_pos.x += 0.5
    enemy["lives"] -= 1 # enemies and characters colliding also means the character attacks the enemy
    score += 2 # attacking and killing enemies gives you a boost in score
    if enemy["lives"] <= 0:
        enemies.remove(enemy) # the enemy dies if it loses all it's lives
    return player_pos.x, enemies, score

def saveGame(file, player_pos, platforms, enemies, pcharacter, gold, doubleJumpUpgrade, secondLifeUpgrade, last_jump_time_ms, highScore):
    
    saveData = { # creates a JSON-parsable python dictionary of all necessary game data 
        "player_pos": {
            "x": player_pos.x,
            "y": player_pos.y
            },
        "highScore": highScore,
        "score": score,
        "gold": gold,
        "lastJumpTimeMs": last_jump_time_ms,
        "doubleJumpUpgrade": doubleJumpUpgrade, # these are Boolean variables
        "reviveUpgrade": secondLifeUpgrade,     #
        "verticalVel": pcharacter.get_vert_vel(),
        "platforms": { # platforms and enemies can be of variable size, so we declare them here and deal with them later
        },
        "enemies": {
        }
    }
    
    for i in platforms:
        saveData["platforms"][str(platforms.index(i)+1)] = { # iterates through platforms, appending x and y attributes to new entries with the index+1 as the key
            "x": i.hitbox.x,
            "y": i.hitbox.y
        } # (this makes it more human-readable)
        
    for n in enemies: # the same thing is done with the enemies 
        saveData["enemies"][str(enemies.index(n)+1)] = {
            "x": n["hitbox"].x,
            "y": n["hitbox"].y,
            "lives": n["lives"] # but we also save the 'lives' attribute too
        } 
    
    with open((str(file)+".txt"), "w") as (file): # creates and opens a file in 'read' mode, this is modular as we can either define it as a cache or save file.
        json.dump(saveData, file, indent=4) # parse through our dictionary of data (indent=4 to make it more human-readable)

    file.close() # close the file as good practice
    
def loadGame(file): # the reverse of saving the data
    with open((str(file)+".txt"), "r") as file: # open either cache file or save file, depending on which we reference upon calling
        saveData = json.load(file) # load the JSON dictionary back to python and save to a variable, which we can use to access the save data
    return(saveData)

while running: # main program loop

    if main_init: # initialising the main menu with required variables
        
        frameNo = 0
        titleAnim = [] # creates list variables for each 'gif'
        playAnim = []
        settingsAnim = []
        quitAnim = []
        last_time_ms = 0
        maingame = False # validating that certain parts of the game don not load when they are meant to
        settings = False
        failedLoad = False # required variable validation when returning from the new/load menu upon an unsuccessful load game
        
        for file_name in os.listdir("titles"): # loading each frame of the main title 'gif' animation
            titleSurface = p.image.load("titles" + os.sep + file_name).convert_alpha()
            titleSurface = p.transform.scale(titleSurface, (titleSurface.get_width()*2.5, titleSurface.get_height()*2.5)) # scaling as appropriate
            titleAnim.append(titleSurface) # append to a list containing pygame usable frames
        
        for file_name in os.listdir("play_button"): # loading each frame of the play button 'gif' animation
            playSurface = p.image.load("play_button" + os.sep + file_name).convert_alpha()
            playSurface = p.transform.scale(playSurface, (playSurface.get_width()*2, playSurface.get_height()*2)) # scaling as appropriate
            playAnim.append(playSurface)# append to a list containing pygame usable frames
            
        for file_name in os.listdir("settings_button"): # loading each frame of the settings butto 'gif' animation
            settingsSurface = p.image.load("settings_button" + os.sep + file_name).convert_alpha()
            settingsSurface = p.transform.scale(settingsSurface, (settingsSurface.get_width()*1.5, settingsSurface.get_height()*1.5)) # scaling as appropriate
            settingsAnim.append(settingsSurface)# append to a list containing pygame usable frames
        
        for file_name in os.listdir("quit_button"): # loading each frame of the quit button 'gif' animation
            quitSurface = p.image.load("quit_button" + os.sep + file_name).convert_alpha()
            quitSurface = p.transform.scale(quitSurface, (quitSurface.get_width()*1.5, quitSurface.get_height()*1.5)) # scaling as appropriate
            quitAnim.append(quitSurface)# append to a list containing pygame usable frames
            
        main_init = False # stops initialising the main menu
        main = True # begins the main menu loop where the functions are

    if main: # main menu loop
        
        clock.tick(60) #60 FPS
        
        #button animation timings
        dif_time_ms = int(round(t.time()*1000)) - last_time_ms
        if dif_time_ms >= 115:
            frameNo += 1
            last_time_ms = int(round(t.time()*1000))
        if frameNo > 4:
            frameNo = 0 
            
        #poll event queue
        for event in p.event.get():
            
            if event.type == p.QUIT: # if close (X) button is pressed
                main = False
                running = False
                if os.path.exists("cache_file.txt"):
                    os.remove("cache_file.txt") # remove any existing cache files in storage, thereby deleting any unsaved game data
                p.quit()
                sys.exit()
                
            if event.type == p.MOUSEBUTTONDOWN and event.button == 1: # if right click is pressed
                if mainPlayButtonRect.collidepoint(event.pos): # if the play button is pressed on the main menu
                    main = False # stops the main menu loop
                    newOrLoad_init = True # begin initialising the new/load game menu
                    
                if mainSettingsButtonRect.collidepoint(event.pos): # if the settings button is pressed on the main menu
                    main = False
                    settings_init = True # begin initialising the settings menu
                    
                if mainQuitButtonRect.collidepoint(event.pos): # if the quit button is pressed on the main menu
                    main = False
                    running = False # stops the main program loop
                    if os.path.exists("cache_file.txt"):
                        os.remove("cache_file.txt")
                    p.quit()
                    sys.exit() # stop and close the program

        #blitting sprites
        screen.blit(background, (0,0))
        screen.blit(titleAnim[frameNo], (((screen.get_width()-titleSurface.get_width())/2),((screen.get_height()-titleSurface.get_height())/2)-250)) # blit title 'gif' to screen
        
        playButton = screen.blit(playAnim[frameNo], (((screen.get_width()-playSurface.get_width())/2),((screen.get_height()-playSurface.get_height())/2)-50))
        #blits the play button 'gif' to the screen and assigns it a variable name
        
        settingsButton = screen.blit(settingsAnim[frameNo], (((screen.get_width()-settingsSurface.get_width())/2),((screen.get_height()-settingsSurface.get_height())/2)+100))
        #blits the settings button 'gif' to the screen and assigns it a variable name
        
        quitButton = screen.blit(quitAnim[frameNo], (((screen.get_width()-quitSurface.get_width())/2),((screen.get_height()-quitSurface.get_height())/2)+180))
        #blits the quit button 'gif' to the screen and assigns it a variable name
        
        mainPlayButtonRect = p.Rect(playButton.x, playButton.y, playSurface.get_width(), playSurface.get_height()) # creates Rect objects (hitboxes) of each blitted button sprite
        mainSettingsButtonRect = p.Rect(settingsButton.x, settingsButton.y, settingsSurface.get_width(), settingsSurface.get_height())
        mainQuitButtonRect = p.Rect(quitButton.x, quitButton.y, quitSurface.get_width(), quitSurface.get_height())
        # used for when detecting which button is clicked
        
        #update section
        p.display.flip()
        screen.fill(fillerColour)

    if settings_init: # initialises te settings menu
        volumeAnim = [] # creates list for any 'gifs'
        frameNo = 0
        last_time_ms = 0
        typingActive = False #validating that typing is off until the volume text box is clicked
        
        for file_name in os.listdir("volume_headers"): # loads each frame of the volume title 'gif'
            volumeSurface = p.image.load("volume_headers" + os.sep + file_name).convert_alpha()
            volumeSurface = p.transform.scale(volumeSurface, (volumeSurface.get_width()*2.5, volumeSurface.get_height()*2.5)) # scaling as appropriate
            volumeAnim.append(volumeSurface) # append frame to the respective list
        
        homeIconSurface = p.image.load("homeIcon.png").convert_alpha() # loads the home icon as is (no scaling required)
        
        controlsSurface = p.image.load("controls.png").convert_alpha() # loads the controls panel image to the system
        controlsSurface = p.transform.scale(controlsSurface, (controlsSurface.get_width()*3, controlsSurface.get_height()*3)) # scaling as appropriate
        
        volumeTextBoxSurface = p.image.load("volumeTextBox.png").convert_alpha() # loads the background to the voume text box to the system
        volumeTextBoxSurface = p.transform.scale(volumeTextBoxSurface, (volumeTextBoxSurface.get_width()*2.5, volumeTextBoxSurface.get_height()*2.5)) # scaling as appropriate
        
        volumeSettingFont = p.font.Font('press2start.ttf', size=40) # sets font size for the settings menu
        
        settings_init = False # stops initialising the settings menu
        settings = True # begin the settings menu loop

    if settings: # settings menu loop
        
        clock.tick(60) # 60 FPS
        
        #heading animation timings
        dif_time_ms = int(round(t.time()*1000)) - last_time_ms
        if dif_time_ms >= 115:
            frameNo += 1
            last_time_ms = int(round(t.time()*1000))
        if frameNo > 4:
            frameNo = 0
        
        for event in p.event.get():
            if event.type == p.QUIT: # generatl procedure of shutting down the game if quit
                settings = False
                if os.path.exists("cache_file.txt"):
                    os.remove("cache_file.txt")
                p.quit()
                sys.exit()
                
            if event.type == p.MOUSEBUTTONDOWN and event.button == 1: # checks if left click was pressed
                if settingsHomeIconRect.collidepoint(event.pos): # if the home icon is pressed
                    settings = False
                    main_init = True # go back to the main menu
                    
                if settingsVolumeTextBoxRect.collidepoint(event.pos): # if the volume text box was clicked
                    typingActive = True
                    volumePercentageValue = "" # allow typing into the system and empty the contents of the text box
                
                if not settingsVolumeTextBoxRect.collidepoint(event.pos): # if the player clicks off of the text box
                    typingActive = False # stop allowing the user to type
                    try:
                        p.mixer.Sound.set_volume(backgroundMusic, (int(volumePercentageValue)/100)) # attempt to set the volume percentage to the percentage amount the user typed in,
                        # casting and valdating it into an integer
                    except:
                        print("volume value must be an integer, please try again.") # if an error occurs, the user did not enter an integer as python could not convert it correctly
                        
            elif event.type == p.KEYDOWN and typingActive: # if keys on the keyboard are pressed and typing is allowed
                if event.key == p.K_RETURN: # if the [ENTER] key is pressed
                    typingActive = False # do the same thing as if the user clicked off of the text box, preventing any accidental editing
                    try:
                        p.mixer.Sound.set_volume(backgroundMusic, (int(volumePercentageValue)/100))
                    except:
                        print("volume value must be an integer, please try again.")
                         
                elif event.key == p.K_BACKSPACE: # if the [BACKSPACE] key is pressed
                    volumePercentageValue = volumePercentageValue[:-1] # removes the last letter in the string array of what the user typed in
                else:
                    volumePercentageValue += event.unicode # if return and backspace are not the keys pressed, add the unicode character of the corresponding key to the string array
                    
        volumeTextSurface = displayText(volumePercentageValue, volumeSettingFont) # makes a text surface of what the user typed in
        
        #blitting sprites
        screen.blit(background, (0,0))
        screen.blit(volumeAnim[frameNo], (30, 100))
        
        settingsHomeIcon = screen.blit(homeIconSurface, (30,30)) # blit home icon in the top left of the screen
        settingsHomeIconRect = p.Rect(settingsHomeIcon.x, settingsHomeIcon.y, homeIconSurface.get_width(), homeIconSurface.get_height())
        # make a Rect object of it so it can be used to detect if the user presses it
        
        settingsVolumeTextBox = screen.blit(volumeTextBoxSurface, (400, 165)) # blits the text box to the screen
        settingsVolumeTextBoxRect = p.Rect(settingsVolumeTextBox.x, settingsVolumeTextBox.y, volumeTextBoxSurface.get_width(), volumeTextBoxSurface.get_height())
        # create a Rect hitbox of the sprite so it can be used to detect if the player clicks on it
        
        screen.blit(volumeTextSurface, volumeTextSurface.get_rect(center = settingsVolumeTextBoxRect.center))
        # blit the text the user inputted on top of the text box and align them to eachother's centres
        
        screen.blit(controlsSurface, (((screen.get_width()-controlsSurface.get_width())/2), 300)) # blit the controls panel to the screen
        
        p.display.flip()
        screen.fill(fillerColour)

    if pause_init: # initialises the pause menu
        
        saveGame("cache_file", player_pos, platforms, enemies, pcharacter, gold, doubleJumpUpgrade, secondLifeUpgrade, last_jump_time_ms, highScore) # saves the game to a cache file
        
        # pause menu variables
        volumeAnim = [] # creates empty lists for the 'gifs'
        saveGameAnim = []  
        frameNo = 0
        last_time_ms = 0
        typingActive = False
        savedGame = False # used in displaying tool tips in the pause menu loop
        
        for file_name in os.listdir("volume_headers"):
            volumeSurface = p.image.load("volume_headers" + os.sep + file_name).convert_alpha()
            volumeSurface = p.transform.scale(volumeSurface, (volumeSurface.get_width()*2.5, volumeSurface.get_height()*2.5))
            volumeAnim.append(volumeSurface)
        
        for file_name in os.listdir("save_game_button"):
            saveGameSurface = p.image.load("save_game_button" + os.sep + file_name).convert_alpha()
            saveGameSurface = p.transform.scale(saveGameSurface, (saveGameSurface.get_width()*1.75, saveGameSurface.get_height()*1.75))
            saveGameAnim.append(saveGameSurface)
        
        backIconSurface = p.image.load("backIcon.png")
        controlsSurface = p.image.load("controls.png")
        controlsSurface = p.transform.scale(controlsSurface, (controlsSurface.get_width()*3, controlsSurface.get_height()*3))
         
        volumeTextBoxSurface = p.image.load("volumeTextBox.png")
        volumeTextBoxSurface = p.transform.scale(volumeTextBoxSurface, (volumeTextBoxSurface.get_width()*2.5, volumeTextBoxSurface.get_height()*2.5))
        
        volumeSettingFont = p.font.Font('press2start.ttf', size=40)
        toolTipsFont = p.font.Font('press2start.ttf', size=10)
        
        pause_init = False
        pause = True
        
    if pause:
    
        clock.tick(60)
        
        #button and title animation timings
        dif_time_ms = int(round(t.time()*1000)) - last_time_ms
        if dif_time_ms >= 115:
            frameNo += 1
            last_time_ms = int(round(t.time()*1000))
        if frameNo > 4:
            frameNo = 0
        
        for event in p.event.get():
            if event.type == p.QUIT:
                pause = False
                if os.path.exists("cache_file.txt"):
                    os.remove("cache_file.txt")
                p.quit()  
                sys.exit()
                
            if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
                if pauseBackIconRect.collidepoint(event.pos):
                    pause = False
                    maingame_init = True

                if pauseVolumeTextBoxRect.collidepoint(event.pos):
                    typingActive = True
                    volumePercentageValue = ""
                
                if not pauseVolumeTextBoxRect.collidepoint(event.pos):
                    typingActive = False
                    try:
                        p.mixer.Sound.set_volume(backgroundMusic, (int(volumePercentageValue)/100))
                    except:
                        print("volume value must be an integer, please try again.")
                        
                if pauseQuitButton.collidepoint(event.pos):
                    if os.path.exists("cache_file.txt"):
                        os.remove("cache_file.txt")
                    pause = False
                    main_init = True
                    
                if pauseSaveButtonRect.collidepoint(event.pos):
                    saveGame("save_file", player_pos, platforms, enemies, pcharacter, gold, doubleJumpUpgrade, secondLifeUpgrade, last_jump_time_ms, highScore)
                    savedGame = True
            
            if event.type == p.KEYDOWN:
                if event.key == p.K_ESCAPE:
                    pause = False
                    maingame_init = True
                        
            if event.type == p.KEYDOWN and typingActive:
                if event.key == p.K_RETURN:
                    typingActive = False
                    try:
                        p.mixer.Sound.set_volume(backgroundMusic, (int(volumePercentageValue)/100))
                    except:
                        print("volume value must be an integer, please try again.")
                         
                elif event.key == p.K_BACKSPACE:
                    volumePercentageValue = volumePercentageValue[:-1]
                else:
                    volumePercentageValue += event.unicode
                    
        volumeTextSurface = displayText(volumePercentageValue, volumeSettingFont)
        
        screen.blit(background, (0,0))
        screen.blit(volumeAnim[frameNo], (30, 100))
        pauseQuitButton = screen.blit(quitAnim[frameNo], (1055, 200))
        pauseSaveButton = screen.blit(saveGameAnim[frameNo], (910, 30))
        
        pauseBackIcon = screen.blit(backIconSurface, (30,30))
        pauseBackIconRect = p.Rect(pauseBackIcon.x, pauseBackIcon.y, backIconSurface.get_width(), backIconSurface.get_height())
        
        pauseVolumeTextBox = screen.blit(volumeTextBoxSurface, (400, 165))
        pauseVolumeTextBoxRect = p.Rect(pauseVolumeTextBox.x, pauseVolumeTextBox.y, volumeTextBoxSurface.get_width(), volumeTextBoxSurface.get_height())
        
        pauseQuitButtonRect = p.Rect(pauseQuitButton.x, pauseQuitButton.y, quitSurface.get_width(), quitSurface.get_height())
        pauseSaveButtonRect = p.Rect(pauseSaveButton.x, pauseSaveButton.y, saveGameSurface.get_width(), saveGameSurface.get_height())
        
        screen.blit(volumeTextSurface, volumeTextSurface.get_rect(center = pauseVolumeTextBoxRect.center))
        screen.blit(controlsSurface, (((screen.get_width()-controlsSurface.get_width())/2), 300))
        
        if savedGame:
            saveGameToolTip = displayText("Your game has been saved!", toolTipsFont)
            screen.blit(saveGameToolTip, (1000, 150))
        elif not savedGame:
            saveGameToolTip = displayText("Warning: Saving the game will overwrite any existing save files.", toolTipsFont)
            screen.blit(saveGameToolTip, (625, 150))
            
        p.display.flip()
        screen.fill(fillerColour)

    if shop_init:
        
        shopHeaderAnim = []
        reviveUpgradeAnim = []
        doubleJumpUpgradeAnim = []
        frameNo = 0
        last_time_ms = 0
        boughtItem = False
        balanceTooLow = False
        
        doubleJumpUpgradeSurface = p.image.load("doubleJump.png").convert_alpha()
        doubleJumpUpgradeSurface = p.transform.scale(doubleJumpUpgradeSurface, (doubleJumpUpgradeSurface.get_width()*3, doubleJumpUpgradeSurface.get_height()*3))
        
        reviveUpgradeSurface = p.image.load("revive.png").convert_alpha()
        reviveUpgradeSurface = p.transform.scale(reviveUpgradeSurface, (reviveUpgradeSurface.get_width()*3, reviveUpgradeSurface.get_height()*3))
        
        shopBackIconSurface = p.image.load("backIcon.png").convert_alpha()
        
        for file_name in os.listdir("shop_headers"):
            shopSurface = p.image.load("shop_headers" + os.sep + file_name).convert_alpha()
            shopSurface = p.transform.scale(shopSurface, (shopSurface.get_width()*2, shopSurface.get_height()*2))
            shopHeaderAnim.append(shopSurface)
            
        reviveHeaderSurface = p.image.load("reviveHeader.png").convert_alpha()
        
        doubleJumpHeaderSurface = p.image.load("doubleJumpHeader.png").convert_alpha()
        
        for file_name in os.listdir("buy_revive_upgrade"):
            buyReviveUpgradeSurface = p.image.load("buy_revive_upgrade" + os.sep + file_name).convert_alpha()
            buyReviveUpgradeSurface = p.transform.scale(buyReviveUpgradeSurface, (buyReviveUpgradeSurface.get_width()*2, buyReviveUpgradeSurface.get_height()*2))
            reviveUpgradeAnim.append(buyReviveUpgradeSurface)
            
        for file_name in os.listdir("buy_double_jump_upgrade"):
            buyDoubleJumpUpgradeSurface = p.image.load("buy_double_jump_upgrade" + os.sep + file_name).convert_alpha()
            buyDoubleJumpUpgradeSurface = p.transform.scale(buyDoubleJumpUpgradeSurface, (buyDoubleJumpUpgradeSurface.get_width()*2, buyDoubleJumpUpgradeSurface.get_height()*2))
            doubleJumpUpgradeAnim.append(buyDoubleJumpUpgradeSurface)
            
        shopToolTip = displayText("You have: " + str(gold) + " gold available to spend", gameFont)
            
        shop_init = False
        shop = True
        
    if shop:
        clock.tick(60)
        
        dif_time_ms = int(round(t.time()*1000)) - last_time_ms
        if dif_time_ms >= 115:
            frameNo += 1
            last_time_ms = int(round(t.time()*1000))
        if frameNo > 4:
            frameNo = 0
            
        for event in p.event.get():
            if event.type == p.QUIT:
                shop = False
                running = False
                if os.path.exists("cache_file.txt"):
                    os.remove("cache_file.txt")
                p.quit()
                sys.exit()
                
            if event.type == p.KEYDOWN:
                if event.key == p.K_ESCAPE:
                    shop = False
                    maingame_init = True
            
            if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
                if shopBackIconRect.collidepoint(event.pos):
                    shop = False
                    maingame_init = True
                if buyReviveUpgradeRect.collidepoint(event.pos) and not boughtItem:
                    if gold >= 380:
                        gold -= 380
                        secondLifeUpgrade = True
                        boughtItem = True
                    else:
                        balanceTooLow = True
                if buyDoubleJumpUpgradeRect.collidepoint(event.pos) and not boughtItem:
                    if gold >= 240:
                        gold -= 240
                        doubleJumpUpgrade = True
                        boughtItem = True
                    else:
                        balanceTooLow = True
                        
        saveGame("cache_file", player_pos, platforms, enemies, pcharacter, gold, doubleJumpUpgrade, secondLifeUpgrade, last_jump_time_ms, highScore) 
                
        if boughtItem == True:
            shopToolTipText = "Purchase successful..."
        if balanceTooLow == True:
            shopToolTipText = "Your Gold balance is too low for this purchase..."
        else:
            shopToolTipText = "You have:" + str(gold) + " gold available to spend"
            
        shopToolTip = displayText(shopToolTipText, gameFont)
            
        screen.blit(background, (0, 0))
        screen.blit(shopHeaderAnim[frameNo], ((screen.get_width()-shopSurface.get_width())/2, 30))
        
        screen.blit(doubleJumpUpgradeSurface, (((screen.get_width()-doubleJumpUpgradeSurface.get_width())*0.25), 170))
        screen.blit(doubleJumpHeaderSurface, (((screen.get_width()-doubleJumpHeaderSurface.get_width())*0.25)+20, 370))
        
        screen.blit(reviveUpgradeSurface, (((screen.get_width()-reviveUpgradeSurface.get_width())*0.75)-50, 170))
        screen.blit(reviveHeaderSurface, (((screen.get_width()-reviveHeaderSurface.get_width())*0.75)-60, 370))
        
        screen.blit(shopToolTip, ((screen.get_width()-shopToolTip.get_width())/2, screen.get_height()-90))
        
        shopBackIcon = screen.blit(shopBackIconSurface, (30, 30))
        
        buyReviveUpgrade = screen.blit(reviveUpgradeAnim[frameNo], (((screen.get_width()-buyReviveUpgradeSurface.get_width())*0.75)-20, 450))
        buyDoubleJumpUpgrade = screen.blit(doubleJumpUpgradeAnim[frameNo], (((screen.get_width()-buyDoubleJumpUpgradeSurface.get_width())*0.25)-20, 450))
        
        shopBackIconRect = p.Rect(shopBackIcon.x, shopBackIcon.y, shopBackIconSurface.get_width(), shopBackIconSurface.get_height())
        buyReviveUpgradeRect = p.Rect(buyReviveUpgrade.x, buyReviveUpgrade.y, buyReviveUpgradeSurface.get_width(), buyReviveUpgradeSurface.get_height())
        buyDoubleJumpUpgradeRect = p.Rect(buyDoubleJumpUpgrade.x, buyDoubleJumpUpgrade.y, buyDoubleJumpUpgradeSurface.get_width(), buyDoubleJumpUpgradeSurface.get_height())
        
        p.display.flip()
        screen.fill(fillerColour)

    if newOrLoad_init:
        
        playHeadersAnim = []
        newGameAnim = []
        loadGameAnim = []
        frameNo = 0
        last_time_ms = 0
        errorFont = p.font.Font("press2start.ttf", 14)
        
        if failedLoad == True:
            loadErrorText = displayText("The game has failed to load: There is no save file associated with this game.", errorFont)
            
        for file_name in os.listdir("play_headers"):
            playHeaderSurface = p.image.load("play_headers" + os.sep + file_name).convert_alpha()
            playHeaderSurface = p.transform.scale(playHeaderSurface, (playHeaderSurface.get_width()*4, playHeaderSurface.get_height()*4))
            playHeadersAnim.append(playHeaderSurface)
            
        for file_name in os.listdir("new_game_button"):
            newGameSurface = p.image.load("new_game_button" + os.sep + file_name).convert_alpha()
            newGameSurface = p.transform.scale(newGameSurface, (newGameSurface.get_width()*2, newGameSurface.get_height()*2))
            newGameAnim.append(newGameSurface)
            
        for file_name in os.listdir("load_game_button"):
            loadGameSurface = p.image.load("load_game_button" + os.sep + file_name).convert_alpha()
            loadGameSurface = p.transform.scale(loadGameSurface, (loadGameSurface.get_width()*2, loadGameSurface.get_height()*2))
            loadGameAnim.append(loadGameSurface)
            
        newOrLoadBackIconSurface = p.image.load("backIcon.png").convert_alpha()
            
        newOrLoad_init = False
        newOrLoad = True
            
    if newOrLoad:

        clock.tick(60)
        
        dif_time_ms = int(round(t.time()*1000)) - last_time_ms
        if dif_time_ms >= 115:
            frameNo += 1
            last_time_ms = int(round(t.time()*1000))
        if frameNo > 4:
            frameNo = 0
            
        for event in p.event.get():
            
            if event.type == p.QUIT:
                newOrLoad = False
                running = False
                if os.path.exists("cache_file.txt"):
                    os.remove("cache_file.txt")
                p.quit()
                sys.exit()
                
            if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
                if newGameButtonRect.collidepoint(event.pos):
                    newOrLoad = False
                    newGame = True
                
                if loadGameButtonRect.collidepoint(event.pos):
                    newOrLoad = False
                    loadExistingGame = True
                    
                if newOrLoadBackIconRect.collidepoint(event.pos):
                    newOrLoad = False
                    main_init = True
        
        screen.blit(background, (0, 0))
        screen.blit(playHeadersAnim[frameNo], ((screen.get_width()-playHeaderSurface.get_width())/2,30))
        newGameButton = screen.blit(newGameAnim[frameNo], ((screen.get_width()-newGameSurface.get_width())*0.25, 400))
        loadGameButton = screen.blit(loadGameAnim[frameNo], ((screen.get_width()-loadGameSurface.get_width())*0.75, 400))
        newOrLoadBackIcon = screen.blit(newOrLoadBackIconSurface, (30,30))
        
        if failedLoad:
            screen.blit(loadErrorText, ((screen.get_width()-loadErrorText.get_width())/2, screen.get_height()-200))   
        
        newGameButtonRect = p.Rect(newGameButton.x, newGameButton.y, newGameSurface.get_width(), newGameSurface.get_height())
        loadGameButtonRect = p.Rect(loadGameButton.x, loadGameButton.y, loadGameSurface.get_width(), loadGameSurface.get_height())
        newOrLoadBackIconRect = p.Rect(newOrLoadBackIcon.x, newOrLoadBackIcon.y, newOrLoadBackIconSurface.get_width(), newOrLoadBackIconSurface.get_height())
        
        p.display.flip()
        screen.fill(fillerColour)
        
    if newGame:
        
        player_pos = p.Vector2(screen.get_width()/2, 337)
        
        score = 0
        
        platforms =  []
        enemies = []
        
        platforms = startPlatform()
        platforms, enemies = generateInitialPlatforms(platforms, 34)
        
        last_jump_time_ms = 0
        last_time_ms = 0
        
        pcharacter = Character(player_pos)
        
        left = False
        right = False
        jump = False
        
        gamePauseIconSurface = p.image.load("pauseIcon.png").convert_alpha()
        gameShopIconSurface = p.image.load("shopIcon.png").convert_alpha()
        gameFunctionIconRect = p.Rect(30, 30, gamePauseIconSurface.get_width(), gamePauseIconSurface.get_height())
        
        newGame = False
        maingame = True
         
    if loadExistingGame:
        
        if os.path.exists("save_file.txt"):
            
            savedData = loadGame("save_file")
            
            platforms = []
            enemies = []
            
            player_pos = p.Vector2(savedData["player_pos"]["x"], savedData["player_pos"]["y"])
            
            highScore = savedData["highScore"]
            score = savedData["score"]
            
            gold = savedData["gold"]
            
            for platform in savedData["platforms"].values():
                platformXcoord = platform["x"]
                platformYcoord = platform["y"]
                savedPlatform = Platform(platformXcoord, platformYcoord)
                platforms.append(savedPlatform)
            
            for enemy in savedData["enemies"].values():
                enemyXcoord = enemy["x"]
                enemyYcoord = enemy["y"]
                savedEnemy = enemyGeneration(enemyXcoord, enemyYcoord)
                savedEnemy["lives"] = enemy["lives"]
                enemies.append(savedEnemy)
                    
            pcharacter = Character(player_pos)
            pcharacter.set_vert_vel((savedData["verticalVel"]))
            
            last_jump_time_ms = savedData["lastJumpTimeMs"]
            last_time_ms = 0
            
            secondLifeUpgrade = savedData["reviveUpgrade"]
            doubleJumpUpgrade = savedData["doubleJumpUpgrade"]
            
            left = False
            right = False
            
            gamePauseIconSurface = p.image.load("pauseIcon.png").convert_alpha()
            gameShopIconSurface = p.image.load("shopIcon.png").convert_alpha()
            gameFunctionIconRect = p.Rect(30, 30, gamePauseIconSurface.get_width(), gamePauseIconSurface.get_height())
            
            loadExistingGame = False
            maingame = True
            
        else:
            loadExistingGame = False
            newOrLoad_init = True
            failedLoad = True

    if maingame_init:
        
        cacheData = loadGame("cache_file")
        
        platforms = []
        enemies = []
        del(pcharacter)
        
        player_pos = p.Vector2(cacheData["player_pos"]["x"], cacheData["player_pos"]["y"])
        
        pcharacter = Character(player_pos)
        pcharacter.set_vert_vel((cacheData["verticalVel"]))
        
        secondLifeUpgrade = cacheData["reviveUpgrade"]
        doubleJumpUpgrade = cacheData["doubleJumpUpgrade"]
        
        if revive:
            player_pos = p.Vector2(screen.get_width() / 2, 337)
            platforms = startPlatform()
            pcharacter.set_vert_vel(0)
            revive = False
            secondLifeUpgrade = False
        
        highScore = cacheData["highScore"]
        score = cacheData["score"]
        
        gold = cacheData["gold"]
        
        for platform in cacheData["platforms"].values():
            platformXcoord = platform["x"]
            platformYcoord = platform["y"]
            savedPlatform = Platform(platformXcoord, platformYcoord)
            platforms.append(savedPlatform)
        
        for enemy in cacheData["enemies"].values():
            enemyXcoord = enemy["x"]
            enemyYcoord = enemy["y"]
            savedEnemy = enemyGeneration(enemyXcoord, enemyYcoord)
            savedEnemy["lives"] = enemy["lives"]
            enemies.append(savedEnemy)

        last_jump_time_ms = cacheData["lastJumpTimeMs"]
        last_time_ms = 0
        
        left = False
        right = False
        
        if os.path.exists("cache_file.txt"):
            os.remove("cache_file.txt")
            
        gamePauseIconSurface = p.image.load("pauseIcon.png").convert_alpha()
        gameShopIconSurface = p.image.load("shopIcon.png").convert_alpha()
        gameFunctionIconRect = p.Rect(30, 30, gamePauseIconSurface.get_width(), gamePauseIconSurface.get_height())
        
        maingame_init = False
        maingame = True
                
    if maingame:
        ## limits program to maingame at 60FPS
        clock.tick(60)

        jump = False # sets jusmp to False to inhibit the character from jumping every frame

        ## clock used to change player sprite models at regular intervals
        dif_time_ms = int(round(t.time()*1000)) - last_time_ms
        if dif_time_ms >= 150:
            state += 1
            last_time_ms = int(round(t.time()*1000))
            if state > 1:
                state = 0

        ## polls events in the queue        
        for event in p.event.get():

            ## polls if the close button is pressed; the system terminates
            if event.type == p.QUIT:
                maingame = False
                if os.path.exists("cache_file.txt"):
                    os.remove("cache_file.txt")
                p.quit()
                sys.exit()  

            ## polls if a key is pressed on the device
            if event.type == p.KEYDOWN:
                if event.key == p.K_ESCAPE:
                    maingame = False # stop the main game loop
                    pause_init = True # begin
                    
                if event.key == p.K_SPACE:
                    bufferVariable = pcharacter.jump(False) # jump the character, returns either True or False to a buffer variable to ensure the program works correctly
                    last_jump_time_ms = int(round(t.time()*1000)) # marks the time since the last press of the spacebar
                if event.key == p.K_a: # if [A] is pressed
                    left = True # begins a localised loop
                    
                if event.key == p.K_d: # if [D] is pressed
                    right = True # beigns a localised loop
                if event.key == p.K_SPACE and doubleJumpUpgrade == True and dif_jump_time_ms <= 500: 
                    # ^ if the user has a double jump upgrade, and presses [SPACE] within 500 ms of the last they pressed space
                    doubleJumpUpgrade = pcharacter.jump(True) # perform a double jump
                    doubleJumpUpgrade = False # validating that the doubleJumpUpgrade variable is set back to False once used
                    
            if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
                if gameFunctionIconRect.collidepoint(event.pos) and score > 0: # if the left mouse button is pressed in the top left corner 'fucntion' button and score is greater than 0
                    maingame = False # stop the main game loop
                    pause_init = True # initialise the pause menu
                if gameFunctionIconRect.collidepoint(event.pos) and score <= 0: 
                    # ^ if the left mouse button is pressed in the top left corner button Rect and the score is less than (validation) or equal to 0
                    maingame = False # stop the main game loop
                    shop_init = True # initialise the shop menu

            ## polls if a key is released, used to reset player sprites and make the game run as proper
            if event.type == p.KEYUP:
                if event.key == p.K_a:
                    left = False # stop the nested localised loop, preventing the character from perpetually going left
                if event.key == p.K_d:
                    right = False # stops the nested localised loop, preventing the character from perpetually going right
                    
        if right: # if [D] is pressed
            player_pos.x = pcharacter.move_right() # continually iterate the character to move right
        if left: # if [A] is pressed 
            player_pos.x = pcharacter.move_left() # continually 
        
        for enemy in enemies:
            if pcharacter.hitbox.colliderect(enemy["hitbox"]):
                player_pos.x, enemies, score = enemyCollisionEvent(enemy, enemies, score)
            if enemy["hitbox"].y >= screen.get_height():
                enemies.remove(enemy)
        # check game over
        if player_pos.y >= screen.get_height():
            maingame = False
            gameOver_init = True
            
        
        player_pos.y = pcharacter.update(player_pos)
        dif_jump_time_ms = int(round(t.time()*1000)) - last_jump_time_ms

        if left:
            xbool = True
            character = (
                p.image.load("character_walk_1.png").convert_alpha()
                if state == 0
                else p.image.load("character_walk_2.png").convert_alpha()
            )
        elif right:
            xbool = False
            character = (
                p.image.load("character_walk_1.png").convert_alpha()
                if state == 0
                else p.image.load("character_walk_2.png").convert_alpha()
            )
        else:
            character = p.image.load("character_idle.png").convert_alpha()

        character = p.transform.scale(character, (character.get_width()*3,character.get_height()*3))
        character = p.transform.flip(character, xbool, False)

        if player_pos.y <= 180:
            score = scrollUp(score) # all objects move down, giving the illusion of scrolling upwards, also returns score
        elif player_pos.y >= 404:
            enemies = scrollDown() # all object move up, giving the illusion of scrolling downwards
            
        for platform in platforms:
            platformIndex = platforms.index(platform)
            if platformOnScreen(platform):
                platforms.pop(platformIndex)
                platforms = newPlatformGeneration(platforms, 1)
        
        scoreRender = displayText(("Score: " + str(score)), gameFont)

        ## draws everything to the screen every frame, layers are applied as first come first served
        screen.blit(background, (0,0))
        drawPlatforms(platforms)
        for enemy in enemies:
            screen.blit(hostileNPC, (enemy["hitbox"].x, enemy["hitbox"].y))
        else:
            pcharacter.draw(screen)
            screen.blit(scoreRender, (50, 110)) 
        
        if score <= 0:
            screen.blit(gameShopIconSurface, (30, 30))
        elif score > 0:
            screen.blit(gamePauseIconSurface, (30, 30))
        
        ## wipes the last frame and updates the entire screen
        p.display.flip()
        screen.fill(fillerColour)

    if gameOver_init: # initialises the game over menu
        
        gameOverAnim = [] # creates a new list for the 'gameOver' 'gif'
        
        for file_name in os.listdir("game_over"): # loads each frame of the 'game over' heading to pygame
            gameOverSurface = p.image.load("game_over" + os.sep + file_name).convert_alpha()
            gameOverSurface = p.transform.scale(gameOverSurface, (gameOverSurface.get_width()*5, gameOverSurface.get_height()*5)) # scaling as appropriate
            gameOverAnim.append(gameOverSurface) # appends each frame to the list
        
        scoreText = ("Your score was: " + (str(score))) # creates a string displaying the last run's score, casting score into a string
        gameOverScore = displayText(scoreText, gameFont) # creates a surface for the text displaying last run's score
        
        gold += math.trunc(int(round(score))/60)
        # gold is incremented by the score divided by 60 (validating score as an integer and truncating the output as a whole number, for simplicity)
        
        goldGainedText = ("You recieve: " + str(math.trunc(int(round(score))/60)) + " Gold!") # creates a string of how much the gold has incremented by
        goldTotalText = ("You now have " + str(gold) + " Gold.") # creates a string of how much gold the user currenly has
        
        gameOverGoldGained = displayText(goldGainedText, gameFont) # creates a surface for the text of how much the gold incremented
        gameOverGoldTotal = displayText(goldTotalText, gameFont) # creates a surface for the text of how much gold the user has
        
        if secondLifeUpgrade: # if the user has a revive upgrade
            reviveMessage = displayText("Press [E] To Revive...", gameFont) # create a surface for the text to let the user know they have the option to revive

        if score > highScore: # if the high score was beaten
            highScore = score # the hgih score becomes the new high score
            highScoreAlert = displayText("NEW HIGH SCORE!", gameFont) # create a surface for the text that alerts the user they have beaten their high score
            highScoreAlertFlag = True # used in the game over menu loop to alert the ser they have beaten their high score
        else:
            highScoreAlertFlag = False # otherwise validate that this alert does not appear when it is not required to
            
        gameOver_init = False # stop intialising the game over menu
        gameOver = True # begin the main loop of the game over menu

    if gameOver: # main game over 'menu' loop ( not really a menu tho is it?)
        
        clock.tick(60) # 60 FPS
        
        #title sprite animation timings
        dif_time_ms = int(round(t.time()*1000)) - last_time_ms
        if dif_time_ms >= 115:
            frameNo += 1
            last_time_ms = int(round(t.time()*1000))
        if frameNo > 4:
            frameNo = 0
            
        if not secondLifeUpgrade and os.path.exists("cache_file.txt"): # if the user doesnt have the revive upgrade and the cache file path exists
            os.remove("cache_file.txt") # then ther is no point in keeping the cache file
        if secondLifeUpgrade: # if the user does have the option to revive
            saveGame("cache_file", player_pos, platforms, enemies, pcharacter, gold, doubleJumpUpgrade, secondLifeUpgrade, last_jump_time_ms, highScore)
            # overwrite the last cache file save of current game data, that way, if the user wants to revive, the current game data can just be loaded.
            
        for event in p.event.get(): # polls the event queue
            
            if event.type == p.QUIT: # standard quitting procedure
                gameOver = False
                running = False
                if os.path.exists("cache_file.txt"):
                    os.remove("cache_file.txt")
                p.quit()
                sys.exit()
                
            if event.type == p.KEYDOWN: # if the user presses a key on their keyboard
                
                if event.key == p.K_SPACE: # if [SPACE] is pressed (New game)
                    del(pcharacter) # validates that the pcharacter Character object is deleted from memory to avoid data overwriting (it has happened but i couldnt get a screenshot of it)
                    gameOver = False # stop the game over menu loop
                    newGame = True # and initialise a new game
                    if os.path.exists("cache_file.txt"):
                        os.remove("cache_file.txt") # If there is a new game we do not need to keep the data of the past game anymore
                        
                elif event.key == p.K_ESCAPE: # if [ESCAPE] is pressed (Main menu)
                    del(pcharacter) # validates that the pcharacter Character object is deleted from memory
                    gameOver = False
                    main_init = True # initialise the main menu
                    if os.path.exists("cache_file.txt"):
                        os.remove("cache_file.txt") # remove past game data
                        
                elif event.key == p.K_e and secondLifeUpgrade: # if the user has the revive upgrade and presses [E]
                    gameOver = False # stop the game over menu loop
                    maingame_init = True # essentialy initialise the game using 'cache_file.txt'
                    revive = True 
                    # ^ flag to carry ("pass through") to the maingame_init script, just changes the loading order of variables to accomodate for just appending a new starter platform
                    secondLifeUpgrade = False # the user has now used their revive upgrade
                
        #blitting sprites
        screen.blit(background, (0,0))
        drawPlatforms(platforms) # platforms remain in the background 
        
        for enemy in enemies:
            screen.blit(hostileNPC, (enemy["hitbox"].topleft)) # enemies also remain in the background
        
        if highScoreAlertFlag: # if the high score was broken
            screen.blit(highScoreAlert, ((screen.get_width()-highScoreAlert.get_width())/2, 350)) # blit to the screen the text that alerts the user they broke their high score
            
        screen.blit(gameOverScore, ((screen.get_width()-gameOverScore.get_width())/2, 400)) # blit the text that tells the user their score of the last run
        screen.blit(gameOverGoldGained, ((screen.get_width()-gameOverGoldGained.get_width())/2, 430)) # blit the text that tells the user how much their gold has incremented by
        screen.blit(gameOverGoldTotal, ((screen.get_width()-gameOverGoldTotal.get_width())/2, 460)) # blit the text that tells the user how much gold they now have
        screen.blit(gameOverAnim[frameNo], (((screen.get_width()-gameOverSurface.get_width())/2), ((screen.get_height()-gameOverSurface.get_height())/2)-230))
        # ^ blit the game over title 'gif' to the screen
        
        if secondLifeUpgrade: # if the user ha sthe revive upgrade
            screen.blit(reviveMessage, ((screen.get_width()-reviveMessage.get_width())/2, screen.get_height()-300)) 
            # ^ blit to the screen the text that tells the user they have the option to revive
        
        #update the screen
        p.display.flip()
        screen.fill(fillerColour)
   
p.quit() # quit the game if the main program loop is not running 
