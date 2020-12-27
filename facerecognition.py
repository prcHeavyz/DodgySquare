import sys
import cv2
import random
import time

cascPath ='haarcascade_frontalface_default.xml'

class DodgyDot:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.lastMoveTime = time.time()
        self.x = random.randrange(0, self.width, 1)
        self.y = random.randrange(0, self.height, 1)
        self.color = (0, 255, 0)
        self.danger = False
        self.useTargeting = random.randrange(1,3,1)

    def GetNumWithinBounds(self, low, high, val):
        result = max(low, val)
        result = result if high > result else high
        return result

    # Looks at the current time and the time when last move
    # was made. If the time difference is larger than 
    # refreshSec, return true. False otherwise
    def CanMove(self, refreshSec):
        delta = time.time() - self.lastMoveTime
        if delta > refreshSec:
            print('Can move')
            return True
        else:
            return False

    # x,y describes coordinate to move near around
    # dist describes the max variation from target x, y
    # updates DodgyDot's x and y
    # Do we want equally likely dot with while loop?
    def MoveNear(self, x, y, dist, refreshSec):
        x = x + random.randrange(-dist, dist, 1)
        y = y + random.randrange(-dist, dist, 1)

        if self.CanMove(refreshSec):
            self.lastMoveTime = time.time()
            self.x = self.GetNumWithinBounds(0, self.width, x)
            self.y = self.GetNumWithinBounds(0, self.height, y)

    def MoveRandomly(self, refreshSec):
        if self.CanMove(refreshSec):
            self.lastMoveTime = time.time()
            self.x = random.randrange(0, self.width, 1)
            self.y = random.randrange(0, self.height, 1)
    
    def UpdateColor(self, refreshSec):
        third = (refreshSec)/12
        delta = time.time() - self.lastMoveTime
        self.danger = False
        if (delta/third<5):
            self.color = (0,255,0)
        elif (delta/third<10):
            self.color = (0,255,255)
        else:
            self.color = (0,0,255)
            self.danger = True

def Game():
    refreshTime = 5
    dots = []
    levelTime = 30
    levelStartTime = time.time()
    playing = True
    level = 1
    dotRadius = 60
    targetVar = 100
    startingBlockCount = 5
    

    faceCascade = cv2.CascadeClassifier(cascPath)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    fwidth = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    fheight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    for x in range(startingBlockCount):
        dots.append(DodgyDot(fheight, fwidth))
    ret, frame = cap.read()

    while playing:
        if(time.time() > levelStartTime + levelTime):
            level +=1
            levelStartTime = time.time()
            dots.append(DodgyDot(fheight, fwidth))
            if refreshTime > 2:
                refreshTime -= 1 
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(30,30)
        )


        for dot in dots:
            if(dot.useTargeting == 1 and len(faces) > 0):
                index = random.randrange(0, len(faces), 1)
                (tx, ty, tw, th) = faces[index]
                dot.MoveNear(
                    tx + tw/2,
                    ty + th/2,
                    targetVar,
                    refreshTime
                )
            else:
                dot.MoveRandomly(refreshTime)
                print("Random")
            
            dot.UpdateColor(refreshTime)
            cv2.rectangle(frame, (int(dot.x - dotRadius/2), int(dot.y - dotRadius/2)), (int(dot.x + dotRadius/2), int(dot.y + dotRadius/2)), dot.color, 2)

        for(x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,55,50), 2)
            for dot in dots:
                if DoRectIntersect(
                    x+w, 
                    x, 
                    y+h, 
                    y, 
                    int(dot.x + dotRadius/2), 
                    int(dot.x - dotRadius/2),
                    int(dot.y + dotRadius/2),
                    int(dot.y - dotRadius/2)
                    ) and dot.danger:
                    playing = False
        
        org = (50,50)
        font = cv2.FONT_HERSHEY_COMPLEX
        color = (255,0,0)
        frame = cv2.putText(frame, f'Level {level}' , org, font, 1, color, 2, cv2.LINE_AA)
        cv2.imshow(f"Faces", frame)
        
        c = cv2.waitKey(1)
        if c == 27:
            break
    print(f"GAME OVER: YOU MADE IT TO LEVEL {level}")
    if playing is False:
        cv2.imwrite('LastFail.jpg', frame)
        input("Press Enter to continue...")
        cap.release()
        cv2.destroyAllWindows()
        return

def DoRectIntersect(ahx, alx, ahy, aly, bhx, blx, bhy, bly):
    return Compare(ahx, alx, ahy, aly, bhx, blx, bhy, bly) or Compare(bhx, blx, bhy, bly, ahx, alx, ahy, aly)

def Compare(ahx, alx, ahy, aly, bhx, blx, bhy, bly):
    return CheckCorner(alx, aly, bhx, blx, bhy, bly) or CheckCorner(ahx, aly, bhx, blx, bhy, bly) or CheckCorner(alx, ahy, bhx, blx, bhy, bly) or CheckCorner(ahx, ahy, bhx, blx, bhy, bly)

def CheckCorner(ax, ay, bhx, blx, bhy, bly):
    return (ax >= blx and ax <= bhx) and (ay >= bly and ay <= bhy) 

Game()