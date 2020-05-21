class mVars:
    address='C:/Users/EA/Desktop/yixin/'    # 使用到的文件所存放地址
    ip = '10.234.21.167:5555'               #ip 地址，详见adb模块中adb连接教程

    boradOne = 67                           #一个相邻落子点的像素间隔
    boradBegin = (65,480)                   #棋盘的初始像素点，用来将图片像素坐标和棋盘坐标互转
    confirmBW = (820,1590,820+55,1590+60)   #用来确定己方是黑棋还是白棋的区域
    confirmWin = (660,1780,660+46,1780+46)  #用来确定是否胜利的区域
    confirmReg = (130,990,220,1060)         #用来确定是否悔棋的区域
    
    chickBack = (100,1820)                  #胜利后 返回图标 的位置
    chickBegin = (540,940)                  #开始匹配 的位置
    chickRegret = (290,1050)                #对方若后悔，则点击拒绝


import subprocess as sub
class YiXin:
    mYixin = sub.Popen(mVars.address+"Yixin.exe", stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE)
    #设定参数
    def __init__(self):
        self.input('START 15')
        self.input('INFO timeout_match 200000')
        self.input('INFO timeout_turn 3500')    #控制思考快慢

        self.output()
        print("YiXin ready!!")

    #向Yixin 输入对手落子指令
    def input(self,str): 
        print('Human: '+str)
        self.mYixin.stdin.write((str+'\n').encode())
        self.mYixin.stdin.flush()
    
    #获取Yixin 的输出
    def output(self):   
        #一直获取Yixin 输出，直到落子的指令或其它
        while True: 
            str = bytes.decode(self.mYixin.stdout.readline())
            print('YiXin: '+ str,end='')
            if ((',' in str) or ('OK' in str)):
                break;
        self.mYixin.stdout.flush()
        if(',' in str):
            return str

    #新的一局
    def restart(self):
        self.input('RESTART 15')
        self.output()



import aircv as ac
class ImageProcess:
    #缩放检测的图片
    def zoomImage(self,zoom):
        img = ac.imread(mVars.address+"confirmb.jpg")
        self.confirmB = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])

        img = ac.imread(mVars.address+"confirmw.jpg")
        self.confirmW = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])

        img = ac.imread(mVars.address+"confirmwin.jpg")
        self.confirmWin = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])

        img = ac.imread(mVars.address+"None.jpg")
        self.bareBorad = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])

        img = ac.imread(mVars.address+"objb.jpg")
        self.objb = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])

        img = ac.imread(mVars.address+"objw.jpg")
        self.objw = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])

        img = ac.imread(mVars.address+"regret.jpg")
        self.regret = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])
        
    
    #如果匹配成功，则返回中心像素点
    def matchImg(self,imgsrc,imgobj,confidence=0.8):
        coord = None
        res = ac.find_template(imgsrc,imgobj,confidence)
        if res != None:
            coord = (int(res['result'][0]),int(res['result'][1]))
        return coord
    
    #将像素坐标转化为棋盘坐标
    def transformBoard(self,coord):
        x = coord[0]
        y = coord[1]
        xcoord = ycoord = 0
        while x>=mVars.boradBegin[0]:
            x-=mVars.boradOne
            xcoord+=1
        while y>=mVars.boradBegin[1]:
            y-=mVars.boradOne
            ycoord+=1

        return xcoord-1,ycoord-1

    #将棋盘坐标转化为像素坐标
    def transfromScreen(self,coord):
        return (coord[0]*mVars.boradOne+mVars.boradBegin[0],coord[1]*mVars.boradOne+mVars.boradBegin[1])
    
    #对比两张图片的差异
    def difference(self,img1,img2):
        return img1-img2







import os
import time
class mAdb:
    #无线连接手机
    def __init__(self):
        os.system('adb connect '+mVars.ip)
        os.system('adb devices')

    #获取手机的分辨率
    def resolution(self):
        res = os.popen('adb shell wm size').read()
        print(res)
        a = res.find('x')
        b = res.find('\n')
        return (int(res[15:a]),int(res[a+1:b]))

    #捕获截图
    def capture(self):
        os.system('adb exec-out screencap -p > '+mVars.address+'sc.jpg')
        return ac.imread(mVars.address+'sc.jpg')

    #点击特定位置
    def click(self,piexl):
        os.system('adb shell input tap %d %d'%(piexl[0],piexl[1]))
    
    def doubleClick(self,piexl):
        self.click(piexl)
        time.sleep(0.1)
        self.click(piexl)

 


class System:
    mYixin = YiXin() 
    mImageP = ImageProcess()
    mAdb = mAdb()
    certain = 0     #0表示未确认，1表示己方为白，2表示己方为黑
    

    #按手机像素适配
    def __init__(self):
        piexl = self.mAdb.resolution()
        zoom = (piexl[0]/1080,piexl[1]/1920)
        self.zoomVars(zoom)
        self.mImageP.zoomImage(zoom)
   
    #缩放像素参数
    def zoomVars(self,zoom):
        mVars.boradOne = int(mVars.boradOne*zoom[0])
        mVars.boradBegin = (int(mVars.boradBegin[0]*zoom[0]),int(mVars.boradBegin[1]*zoom[1]))
        mVars.confirmBW = (
            int(mVars.confirmBW[0]*zoom[0]),int(mVars.confirmBW[1]*zoom[1]),
            int(mVars.confirmBW[2]*zoom[0]),int(mVars.confirmBW[3]*zoom[1])
        )
        mVars.confirmWin = (
            int(mVars.confirmWin[0]*zoom[0]),int(mVars.confirmWin[1]*zoom[1]),
            int(mVars.confirmWin[2]*zoom[0]),int(mVars.confirmWin[3]*zoom[1])
        )
        mVars.chickBack = (int(mVars.chickBack[0]*zoom[0]),int(mVars.chickBack[1]*zoom[1]))
        mVars.chickBegin = (int(mVars.chickBegin[0]*zoom[0]),int(mVars.chickBegin[1]*zoom[1]))
        mVars.chickRegret = (int(mVars.chickRegret[0]*zoom[0]),int(mVars.chickRegret[1]*zoom[1]))

    #确认是否胜利
    def confirmWin(self,imgsrc):
        x0,y0,x1,y1 = mVars.confirmWin
        imgsrc = imgsrc[y0:y1,x0:x1]

        return self.mImageP.matchImg(imgsrc,self.mImageP.confirmWin,0.9)
    
    #确认己方是黑棋还是白棋
    def confirmBW(self,imgsrc):
        x0,y0,x1,y1 = mVars.confirmBW
        imgsrc = imgsrc[y0:y1,x0:x1]
        
        if (self.mImageP.matchImg(imgsrc,self.mImageP.confirmW)):
            self.certain = 1
            self.mImageP.imgobj = self.mImageP.objb
        elif (self.mImageP.matchImg(imgsrc,self.mImageP.confirmB)):
            self.certain = 2
            self.mImageP.imgobj = self.mImageP.objw

    #做好比赛前准备，
    def ready(self):
        while True:
            imgsrc = self.mAdb.capture()
            self.confirmBW(imgsrc)
            if(self.certain != 0):
                break;
            print('UnCertain')
            time.sleep(1)
        
        if self.certain == 2:
            self.runCommand('BEGIN')
            return imgsrc
        elif self.certain == 1:
            return self.mImageP.bareBorad
    
    #向Yixin 输入对方落点，获得Yixin 落点并点击屏幕
    def runCommand(self,COMMAND):
        self.mYixin.input(COMMAND)
        str = self.mYixin.output()
        a = str.find(',')
        b = str.find('\r')

        piexl = self.mImageP.transfromScreen((int(str[0:a]),int(str[a+1:b])))
        
        
        self.mAdb.click(mVars.chickRegret)
        self.mAdb.doubleClick(piexl)

    #开始游戏
    def play(self,imgsrc):
        oldimg = newimg = imgsrc
        while self.confirmWin(newimg) == None:
            imgdif = self.mImageP.difference(oldimg,newimg)
            coord = self.mImageP.matchImg(imgdif,self.mImageP.imgobj)
            print(coord)
            if(coord != None):
                x, y = self.mImageP.transformBoard(coord)
                COMMAND = "TURN %d,%d"%(x,y)
                self.runCommand(COMMAND)             
            time.sleep(1)
            oldimg,newimg = newimg,self.mAdb.capture()

    #新一轮游戏
    def newGame(self):
        os.system('cls')
        self.mAdb.click(mVars.chickBack)
        time.sleep(0.5)
        self.mAdb.click(mVars.chickBegin)

        
        self.mYixin.restart()
        self.certain = 0
        self.mImageP.imgobj = None



if __name__ == "__main__":
    msys = System()

    # n = input("请输入你想玩的局数：")
    # for i in range(1,int(n)+1):
    while True:
        imgBegin = msys.ready()
        msys.play(imgBegin)
        print("You Win !! Next Game Will Begin After 4sec")
        time.sleep(4)
        msys.newGame()    


