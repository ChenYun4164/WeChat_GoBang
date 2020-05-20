>    苦练技术是不可能的，这辈子都练不会，学技术又太枯燥，就只有靠辅助才能维持的生活这样子。

[TOC]

#### 简述

需要的工具主要分为以下三类：

1.   <a href="https://www.aiexp.info/pages/yixin-cn.html "> Yixin 奕心引擎</a>，这个引擎是国人所作，可以说是非商用版里面最强的五子棋AI

     一开始我想使用奕心的界面+引擎那款，因为可定制性足够强，结果发现Python 不好与GUI程序交互，所以就选择了引擎。然而尴尬的一点是，把官方文档翻了个遍都没有找到引擎的使用方法。不过后来在<a href="https://gomocup.org/"> 世界五子棋锦标赛</a>  找到了参加比赛的AI 必备的两种接口。

     -    http://petr.lastovicka.sweb.cz/protocl2en.htm 使用输入输出流，本文选择的就是这种方式

     -    http://petr.lastovicka.sweb.cz/protocl1en.htm 使用文件

2.   Python 简单图片处理

3.   Python adb 操作手机 



#### 思路

<img src="https://img2020.cnblogs.com/blog/1512048/202005/1512048-20200520161002204-2008792351.png" alt="image-20200329134722139" style="zoom: 67%;" />

整个思路顺下来程序其实是比较好写的，就是前期**需要手动的截取匹配图片，设置查找区域像素点位置**比较麻烦，不过新添加自适配功能，这些都不需要做。



#### 实现

##### 前期准备

你需要预先掌握的知识：

1.   会运行python 文件，并且安装文中的库
2.   <a href="https://jingyan.baidu.com/article/22fe7cedf67e353002617f25.html">安装Adb</a> 并 <a href="https://github.com/mzlogin/awesome-adb#%E6%97%A0%E7%BA%BF%E8%BF%9E%E6%8E%A5%E9%9C%80%E8%A6%81%E5%80%9F%E5%8A%A9-usb-%E7%BA%BF">无线连接成功</a> 
3.   在开发者选项里，打开 USB 调试 和 USB允许模拟点击
4.   修改mVars 里的address 和 ip 



这个是需要进行适配的参数，除前两项address 和 ip 外，其它在分辨率适配正常的情况下都不需要更改

```c++
class mVars:
    address='C:/Users/EA/Desktop/yixin/'    # 使用到的文件所存放地址
    ip = '10.224.133.140:5555'              #ip 地址，详见adb模块中adb连接教程

    boradOne = 67                           #一个相邻落子点的像素间隔
    borad = (65,480)                        #棋盘的初始像素点，用来将图片像素坐标和棋盘坐标互转
    confirmBW = (820,1590,820+55,1590+60)   #用来确定己方是黑棋还是白棋的区域
    confirmWin = (660,1780,660+46,1780+46)  #用来确定是否胜利的区域
    chickBack = (100,1820)                  #胜利后 返回图标 的位置
    chickBegin = (540,940)                  #开始匹配 的位置
```



##### Yixin 引擎

从<a href="http://gomocup.org/static/download-ai/YIXIN18.zip">官网</a>上可以下载Yixin 引擎,结合 <a href ="http://petr.lastovicka.sweb.cz/protocl2en.htm">协议</a>  可以知道如何与引擎交互

使用 subprocess 让 python 与 引擎交互

```python
import subprocess as sub
class YiXin:
    mYixin = sub.Popen(mVars.address+"Yixin.exe", stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE)
    #设定参数
    def __init__(self):
        self.input('START 15')
        self.input('INFO timeout_match 200000')
        self.input('INFO timeout_turn 7500')    #控制思考快慢

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

```



##### 图片处理

这个模块需要做的事就是处理跟图片相关的，包括比较图片，转换坐标等

关于识别对手落子位置，有两种实现思路：

1.   每隔一段时间获取截一张图，对比两张图不同的地方，从而获取对手落点位置。
2.   每隔一段时间截一张图，识别图上的所有有棋的位置并保存，然后通过比较，得到对手落子位置。

目前只实现第一种方法，不过使用第二种方法可以从半局开始。

```python
import aircv as ac
class ImageProcess:
    #缩放检测的图片
    def zoomImage(self,zoom):
        img = ac.imread(mVars.address+"confirmb.jpg")
        img = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])
        ac.cv2.imwrite(mVars.address+'confirmb.jpg',img)

        img = ac.imread(mVars.address+"confirmw.jpg")
        img = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])
        ac.cv2.imwrite(mVars.address+'confirmw.jpg',img)

        img = ac.imread(mVars.address+"confirmwin.jpg")
        img = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])
        ac.cv2.imwrite(mVars.address+'confirmwin.jpg',img)

        img = ac.imread(mVars.address+"None.jpg")
        img = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])
        ac.cv2.imwrite(mVars.address+'None.jpg',img)

        img = ac.imread(mVars.address+"objb.jpg")
        img = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])
        ac.cv2.imwrite(mVars.address+'objb.jpg',img)

        img = ac.imread(mVars.address+"objw.jpg")
        img = ac.cv2.resize(img,(0,0),fx = zoom[0],fy = zoom[1])
        ac.cv2.imwrite(mVars.address+'objw.jpg',img)
    
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
        while x>=mVars.borad[0]:
            x-=mVars.boradOne
            xcoord+=1
        while y>=mVars.borad[1]:
            y-=mVars.boradOne
            ycoord+=1

        return xcoord-1,ycoord-1

    #将棋盘坐标转化为像素坐标
    def transfromScreen(self,coord):
        return (coord[0]*mVars.boradOne+mVars.borad[0],coord[1]*mVars.boradOne+mVars.borad[1])
    
    #对比两张图片的差异
    def difference(self,img1,img2):
        return img1-img2

```



##### ADB 模块

这个模块与手机交互，用的是无线ADB连接，见 <a href="https://github.com/mzlogin/awesome-adb">ADB连接教程</a> 

```python
import os
import time
class Adb:
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
        time.sleep(0.1)
        os.system('adb shell input tap %d %d'%(piexl[0],piexl[1]))

```



##### 游戏系统模块

衔接各个模块

```python
class System:
    Yixin = YiXin() 
    ImageP = ImageProcess()
    Adb = Adb()
    imgobj = None   #用来检测对手落子的图片
    certain = 0     #0表示未确认，1表示己方为白，2表示己方为黑
    
    #按手机像素适配
    def __init__(self):
        piexl = self.Adb.resolution()
        zoom = (piexl[0]/1080,piexl[1]/1920)
        self.zoomVars(zoom)
        self.ImageP.zoomImage(zoom)
        
    #缩放像素参数
    def zoomVars(self,zoom):
        mVars.boradOne = int(mVars.boradOne*zoom[0])
        mVars.borad = (int(mVars.borad[0]*zoom[0]),int(mVars.borad[1]*zoom[1]))
        mVars.confirmBW = (
            int(mVars.confirmBW[0]*zoom[0]),int(mVars.confirmBW[1]*zoom[1]),
            int(mVars.confirmBW[2]*zoom[0]),int(mVars.confirmBW[3]*zoom[1])
        )
        mVars.confirmWin = (
            int(mVars.confirmWin[0]*zoom[0]),int(mVars.confirmWin[1]*zoom[1]),
            int(mVars.confirmWin[2]*zoom[0]),int(mVars.confirmWin[3]*zoom[1])
        )
        mVars.chickBack = (
            int(mVars.chickBack[0]*zoom[0]),
            int(mVars.chickBack[1]*zoom[1]),
        )
        mVars.chickBegin = (
            int(mVars.chickBegin[0]*zoom[0]),
            int(mVars.chickBegin[1]*zoom[1]),
        )

    #确认是否胜利
    def confirmWin(self,imgsrc):
        x0,y0,x1,y1 = mVars.confirmWin
        imgsrc = imgsrc[y0:y1,x0:x1]
        imgobj = ac.imread(mVars.address+'confirmwin.jpg')
        return self.ImageP.matchImg(imgsrc,imgobj,0.9)
    
    #确认己方是黑棋还是白棋
    def confirmBW(self,imgsrc):
        x0,y0,x1,y1 = mVars.confirmBW
        imgsrc = imgsrc[y0:y1,x0:x1]

        imgobjw = ac.imread(mVars.address+'confirmw.jpg')
        imgobjb = ac.imread(mVars.address+'confirmb.jpg')
        
        if (self.ImageP.matchImg(imgsrc,imgobjw,0.8) != None):
            self.certain = 1
            self.imgobj=ac.imread(mVars.address+'objb.jpg')
        elif (self.ImageP.matchImg(imgsrc,imgobjb,0.8)!= None):
            self.certain = 2
            self.imgobj=ac.imread(mVars.address+'objw.jpg')
    
    #做好比赛前准备，
    def ready(self):
        while True:
            imgsrc = self.Adb.capture()
            self.confirmBW(imgsrc)
            if(self.certain != 0):
                break;
            print('UnCertain')
            time.sleep(1)
        
        if self.certain == 2:
            self.runCommand('BEGIN')
            return imgsrc
        elif self.certain == 1:
            return ac.imread(mVars.address+'None.jpg')
    
    #向Yixin 输入对方落点，获得Yixin 落点并点击屏幕
    def runCommand(self,COMMAND):
        self.Yixin.input(COMMAND)
        str = self.Yixin.output()
        a = str.find(',')
        b = str.find('\r')

        piexl = self.ImageP.transfromScreen((int(str[0:a]),int(str[a+1:b])))
        print(piexl)
        self.Adb.click(piexl)

    #开始游戏
    def play(self,imgsrc):
        flag=False
        imagep = self.ImageP
        oldimg = newimg = imgsrc
        while self.confirmWin(newimg) == None:
            imgdif = imagep.difference(oldimg,newimg)
            # ac.cv2.imwrite(mVars.address+'diff.jpg',imgdif)
            coord = imagep.matchImg(imgdif,self.imgobj)
            print(coord)
            if(coord != None):
                x, y = imagep.transformBoard(coord)
                COMMAND = "TURN %d,%d"%(x,y)
                self.runCommand(COMMAND)
            
            time.sleep(1)
            oldimg,newimg = newimg,self.Adb.capture()
        
    #新一轮游戏
    def newGame(self):
        os.system('cls')
        os.system('adb shell input tap %d %d'%(mVars.chickBack))
        time.sleep(0.5)
        os.system('adb shell input tap %d %d'%(mVars.chickBegin))
        
        self.Yixin.restart()
        self.certain = 0
        self.imgobj = None

```



##### 主函数

```python
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
```



#### 其它

如果想自定义的话，可以按照以下教程

>    在已连接adb 的情况下，可以通过下面这条语句快速截图
>
>    ```python
>    import os
>    address='C:/Users/EA/Desktop/yixin/'
>    os.system('adb exec-out screencap -p > '+address+'sc.jpg')
>    ```

主要用系统自带的画图工具，在屏幕左下角查找相应位置的像素坐标

-    检测己方是黑白棋

     <img src="https://img2020.cnblogs.com/blog/1512048/202005/1512048-20200520161003410-1386067403.png" alt="image-20200401170446037" style="zoom:50%;" />

     建议用下面的命令获取

     ```python
     import aircv as ac
     address='C:/Users/EA/Desktop/yixin/'
     
     imgsrc = ac.imread(address+'sc.jpg')
     x0,y0,x1,y1 = (820,1590,820+45,1590+60) #这个坐标以用画图工具量取为准
     imgsrc = imgsrc[y0:y1,x0:x1]
     
     #分别在这个位置保存己方黑白棋识别标志
     ac.cv2.imwrite(address+'confirmw.jpg',imgsrc)
     #ac.cv2.imwrite(address+'confirmb.jpg',imgsrc)
     
     #检测所选的图片是否正常识别
     imgw = ac.imread(address+'confirmw.jpg')
     print(ac.find_template(imgsrc,imgw,0.01))
     ```

     注意，1. 不要把整个棋子都截取，因为右边不时有绿色关环影响识别。2. 与电脑对战时这个标志的位置偏右，所以在mVars.confirmBW 的范围应该稍大一点。3. 在弄完之后，最好识别一下检测一下。

-    胜利的检测，我选的是这个

     <img src="https://img2020.cnblogs.com/blog/1512048/202005/1512048-20200520161004343-226297140.png" alt="image-20200401171752084" style="zoom:50%;" />

-    空棋盘，就弄张空棋盘的截图，这个图是必要的，如果没有，当己方执白时，对方第一子下的很快还没来得及截图，那么系统就检测不到这个对方落子。

-    检测对方落子简单起见，我是直接两张图片相减然后直接截图保存。

     <img src="https://img2020.cnblogs.com/blog/1512048/202005/1512048-20200520161005181-963416149.png" alt="image-20200401172652696" style="zoom: 50%;" />

     ```
     img1 = ac.imread(address+'old.jpg')
     img2 = ac.imread(address+'new.jpg')
     ac.cv2.imwrite(address+'diff.jpg',img1-img2)
     ```

     需要注意的是，一定要统一顺序，旧减新或新减旧，我的实现是用旧减新，新减旧也可以，只是棋子的图不一样，下面就是新减旧

     <img src="https://img2020.cnblogs.com/blog/1512048/202005/1512048-20200520161005824-2030586172.png" alt="image-20200401173039933" style="zoom:50%;" />

