from tinytag import TinyTag
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, \
    QVBoxLayout,  QListWidgetItem, QAbstractItemView, QTableWidgetItem, QGraphicsBlurEffect
from PySide6.QtCore import QSize, QUrl, QEvent, Qt, QPoint
from PySide6.QtGui import QPixmap, QImage, QCursor, QPalette, QBrush
from ui_musicplayer import Ui_Form
from qfluentwidgets import ImageLabel, FluentIcon, PopUpAniStackedWidget, ListWidget, ToolButton, TitleLabel, \
                            TableWidget, MessageBoxBase, SubtitleLabel, LineEdit, TransparentTogglePushButton, RoundMenu, Action, \
                            PrimaryPushButton, StateToolTip
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QAudioDevice
from qframelesswindow import FramelessWindow
from page3 import page3
from lyricpage import lyricPage
import os, random, sqlite3

# 创建音乐播放媒体类
class mediaPlayer(QMediaPlayer):
    def __init__(self):
        super().__init__()
        self.sign = False
        self.dur = 0
        self.curtime = 0
        self.setLoops(0)

        self.audio = QAudioOutput()
        self.setAudioOutput(self.audio)
        self.audio.setVolume(0.1)

    # 设置媒体路径，并且设置为可播放状态
    def load(self, p):
        self.setSource(QUrl.fromLocalFile(p))
        self.sign = True

    # 获取当前已播放的时间，并返回
    def getCurrenttime(self):
        self.curtime = self.position()
        return '{:0>2d}:{:0>2d}'.format(int(self.curtime / 1000 // 60),
                                        int(self.curtime / 1000 - (self.curtime / 1000 // 60) * 60))

    # 获取歌曲总时长，并返回
    def getDuration(self):
        self.dur = self.duration()
        return '{:0>2d}:{:0>2d}'.format(int(self.dur / 1000 // 60),
                                        int(self.dur / 1000 - (self.dur / 1000 // 60) * 60))

    # 获取当前歌曲进度百分比，并返回
    def getSliderPosition(self):
        return ((self.curtime / self.dur) * 100)

    # 根据移动后滑条的位置，修改歌曲的进度
    def moveSlider(self, r):
        toposition = int(self.dur * r / 100)
        self.setPosition(toposition)

class playListPage(QWidget, Ui_Form):
    def __init__(self, wigdet):
        super().__init__()
        self.playlistStack = PopUpAniStackedWidget(wigdet)
        self.playlistBar = QWidget()
        self.playlistStack.addWidget(self.playlistBar)
        self.listname = ''
        title = QLabel(self.playlistStack)
        title.setText("播放列表")
        title.setStyleSheet("font-size:20px;color:black")
        self.delete = ToolButton(self.playlistStack)
        self.delete.setIcon(FluentIcon.DELETE)
        self.delete.setMinimumSize(30, 30)
        self.delete.setMaximumSize(30, 30)

        self.width = wigdet.width()
        self.playlistBar.setStyleSheet('background-color:#ffffff')
        self.playlistStack.setGeometry(self.width, 35, 0, 0)
        self.playlistBarList = ListWidget()
        self.playlistBarList.setIconSize(QSize(50, 50))
        # self.playlistBar.addWidget(self.playlistBarList)
        self.playlistButtonPressed = False
        self.playlist = []
        h1 = QHBoxLayout()
        h1.addWidget(title)
        h1.addWidget(self.delete)
        v1 = QVBoxLayout()
        v1.addLayout(h1)
        v1.addWidget(self.playlistBarList)
        self.playlistBar.setLayout(v1)
        self.playlistStack.setCurrentIndex(0)



    def drawPlaylist(self, playlist):
        for i in range(len(self.playlist)):
            if self.playlist[i]['title'] == playlist['title']:
                self.playlistBarList.setCurrentRow(i)
                return

        iq = QWidget()
        iq.setMinimumSize(330, 60)
        iq.setMaximumSize(330, 60)
        iq.setStyleSheet('background-color:rgba(255,255,255,0)')
        img = ImageLabel()
        # temp = QPixmap()
        # temp.loadFromData(bytearray(playlist['img']))
        img.setPixmap(playlist['img'])
        img.scaledToWidth(50)
        img.setBorderRadius(8, 8, 8, 8)
        l1 = QLabel()
        l1.setText(playlist['title'])
        l1.setStyleSheet('font-size: 14px;color: black')
        l2 = QLabel()
        l2.setText(playlist['artist'])
        l2.setStyleSheet('font-size: 12px;color: black')
        v1 = QVBoxLayout()
        v1.addWidget(l1)
        v1.addWidget(l2)
        h1 = QHBoxLayout()
        h1.addWidget(img)
        h1.addLayout(v1)
        iq.setLayout(h1)
        lt = QListWidgetItem()
        lt.setSizeHint(iq.size())
        self.playlistBarList.addItem(lt)
        self.playlistBarList.setItemWidget(lt, iq)
        if not playlist in self.playlist:
            self.playlist.append(playlist)
        self.playlistBarList.setCurrentRow(self.playlistBarList.count())

    # 弹出播放列表组件
    def popupPlaylist(self):
        self.playlistStack.setGeometry(self.width - 360, 35, 360, 615)
        # self.playlistBar.setCurrentWidget(self.playlistBarList, True)
        self.playlistButtonPressed = True

    def setlist(self,l):
        self.playlist.clear()
        self.playlistBarList.clear()
        for i in l:
            self.drawPlaylist(i)
        self.playlist = l

#歌单界面类
class songListPage(QWidget):
    def __init__(self,name):
        super().__init__()
        self.pagename = name
        self.list = list()
        self.title = TitleLabel()
        self.table = TableWidget()
        self.cover = ImageLabel()
        self.cover.setBorderRadius(8,8,8,8)
        self.cover.scaledToWidth(0)

        self.changenameButton = ToolButton()
        self.changenameButton.setIcon(FluentIcon.LABEL)
        self.changenameButton.setMinimumSize(20,20)
        self.changenameButton.setMaximumSize(20,20)

        self.selectButton = TransparentTogglePushButton()
        self.selectButton.setIcon(FluentIcon.CHECKBOX)
        self.selectButton.setText('选择')
        self.selectButton.setMinimumSize(QSize(80, 30))
        self.selectButton.setMaximumSize(QSize(80, 30))

        self.playallButton = PrimaryPushButton()
        self.playallButton.setIcon(FluentIcon.PLAY)
        self.playallButton.setText("播放全部")
        self.playallButton.setMinimumSize(QSize(120,30))
        self.playallButton.setMaximumSize(QSize(120,30))

        self.moreBUtton = ToolButton()
        self.moreBUtton.setIcon(FluentIcon.MORE)
        self.moreBUtton.setMaximumSize(QSize(25,25))
        self.moreBUtton.setMinimumSize(QSize(25,25))


        h1 = QHBoxLayout()
        h1.addWidget(self.title)
        h1.addWidget(self.changenameButton)
        h1.addSpacing(500)
        v2 = QVBoxLayout()
        v2.addLayout(h1)
        h3 = QHBoxLayout()
        h3.addWidget(self.playallButton)
        h3.addSpacing(10)
        h3.addWidget(self.selectButton)
        h3.addSpacing(10)
        h3.addWidget(self.moreBUtton)
        h3.addSpacing(500)
        v2.addLayout(h3)
        h2 = QHBoxLayout()
        h2.addWidget(self.cover)
        h2.addSpacing(20)
        h2.addLayout(v2)

        v1 = QVBoxLayout()
        v1.addLayout(h2)
        v1.addWidget(self.table)

        self.table.setWordWrap(False)
        self.table.setColumnCount(5)
        self.table.setBorderRadius(5)
        width = 800
        self.table.setColumnWidth(0, width / 10)
        self.table.setColumnWidth(1, (width * 5) / 20)
        self.table.setColumnWidth(2, (width * 2) / 10)
        self.table.setColumnWidth(3, (width * 3) / 10)
        self.table.setColumnWidth(4, (width * 3) / 20)
        self.table.setHorizontalHeaderLabels([' ', '歌名', '歌手', '专辑', '时长'])
        self.table.verticalHeader().hide()
        self.table.setSelectionMode(QAbstractItemView.NoSelection)

        self.setLayout(v1)

    def fullTable(self):
        self.table.setRowCount(len(self.list))
        for i in range(len(self.list)):
            if self.list[i]['title'] == None:
                self.list[i]['title'] = 'unknown'

            if self.list[i]['artist'] == None:
                self.list[i]['artist'] = 'unknown'

            self.table.setItem(i, 1, QTableWidgetItem(self.list[i]['title']))
            self.table.setItem(i, 2, QTableWidgetItem(self.list[i]['artist']))
            self.table.setItem(i, 3, QTableWidgetItem(self.list[i]['album']))
            self.table.setItem(i, 4, QTableWidgetItem(self.list[i]['duration']))

            if self.list[i]['img'] == None:
                self.list[i]['img'] = QPixmap()
                self.list[i]['img'].load('noimage.svg')
                self.list[i]['img'] = self.list[i]['img'].scaledToWidth(200)

            it = QWidget()
            it.setStyleSheet('background:rgba(255,255,255,0)')
            im = ImageLabel()
            im.setPixmap(self.list[i]['img'])
            im.scaledToWidth(50)
            im.setBorderRadius(8, 8, 8, 8)
            it.setMaximumSize(60, 60)
            it.setMinimumSize(60, 60)
            h = QHBoxLayout()
            v = QVBoxLayout()
            h.addWidget(im)
            v.addLayout(h)
            it.setLayout(v)
            self.table.setCellWidget(i, 0, it)
            self.table.setRowHeight(i,80)

            if self.list:
                self.cover.setPixmap(self.list[0]['img'])
                self.cover.scaledToWidth(150)
    def createDataBase(self):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        sql = 'create table {} (title TEXT,artist TEXT,album TEXT,duration TEXT,path TEXT);'.format(self.pagename)
        cursor.execute(sql)
        cursor.close()
        conn.close()

    def saveData(self):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("delete from {}".format(self.pagename))
        sql = "insert into {} (title,artist,album,path) values (?,?,?,?)".format(self.pagename)
        for i in self.list:
            cursor.execute(sql, (i['title'], i['artist'], i['album'], i['path']))
        conn.commit()
        cursor.close()
        conn.close()

#选择歌单的消息框类
class selectMessageBox(MessageBoxBase):
    def __init__(self,parent,list):
        super().__init__(parent)
        self.list = ListWidget()
        for i in list:
            self.list.addItem(i)
        title = SubtitleLabel('添加到歌单')
        self.viewLayout.addWidget(title)
        self.viewLayout.addWidget(self.list)

        self.yesButton.setText('选择')
        self.cancelButton.setText('取消')
        self.widget.setMinimumWidth(400)

#修改歌单名字的消息框类
class changeNameBox(MessageBoxBase):
    def __init__(self,parent):
        super().__init__(parent)
        self.edit = LineEdit()
        title = SubtitleLabel('输入修改的名字')
        self.viewLayout.addWidget(title)
        self.viewLayout.addWidget(self.edit)

        self.yesButton.setText('确定')
        self.cancelButton.setText('取消')
        self.widget.setMinimumWidth(300)


# 创建主窗口
class mainWindows(FramelessWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.setWindowIcon(FluentIcon.MUSIC)
        self.initVar()
        self.initSet()

        self.page3 = page3(self)
        self.playlist = self.page3.playlist
        self.index = self.page3.index

        self.lyricPage = lyricPage()

        # 声明音乐媒体播放类
        self.mediaplayer = mediaPlayer()

        # 创建播放列表组件
        self.playlistPage = playListPage(self)
        self.loadPlaylist()
        self.bind()
        self.creatDataBase()

        self.lyricPage.init(self.playlist[self.index] if self.playlist else {'title':'暂无歌曲','img':QImage()})
        self.mainStack.addWidget(self.lyricPage)


    def initVar(self):
        # 声明当前播放状态
        self.isplaying = False
        # 声明循环播放模式
        self.loopModel = 0  # 0为顺序播放，1为随机播放，2为单曲循环
        # 声明当前播放音乐处于播放列表什么位置
        self.index = 0
        # 声明播放栏是否为打开状态
        self.playlistButtonPressed = False

        self.playbar = 0

        self.isSelect = False
        self.selectedSongs = []

        #歌单
        self.songListPage = list()

        #被选择的tablewidgets和列表
        self.selectedTable = list()
        self.selectedList = list()

    def initSet(self):
        # 设置滑条的最大值与最小值
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.volSlider.setMaximum(100)
        self.volSlider.setMinimum(0)
        self.volSlider.setValue(100)

        # 设置播放栏按钮图标
        self.play.setIcon(FluentIcon.PLAY_SOLID)
        self.last.setIcon(FluentIcon.CARE_LEFT_SOLID)
        self.next.setIcon(FluentIcon.CARE_RIGHT_SOLID)
        self.playlistButton.setIcon(FluentIcon.MENU)

        self.volIcon.setIcon(FluentIcon.VOLUME)

        self.selectsongs.setIcon(FluentIcon.FOLDER_ADD)

        self.playbarstack.setCurrentIndex(1)

        self.selectmore.setIcon(FluentIcon.CHECKBOX)
        self.selectAllButton.setIcon(FluentIcon.ACCEPT)
        self.addSongListButton.setIcon(FluentIcon.ADD_TO)
        self.deleteLocalButton.setIcon(FluentIcon.DELETE)

        self.createListButton.setIcon(FluentIcon.ADD)

        self.loopButton.setIcon('loop.svg')

        self.mainStack.setStyleSheet("QStackedWidget{background: transparent}")



    # 绑定所有按钮
    def bind(self):
        self.stackedWidget.setCurrentIndex(0)
        self.mainButton.clicked.connect(lambda: self.changePage(0))
        self.mainButton.setChecked(True)
        self.localButton.clicked.connect(lambda: self.changePage(2))
        self.recentlyButton.clicked.connect(lambda: self.changePage(3))
        self.statisticsButton.clicked.connect(lambda: self.changePage(4))

        self.selectsongs.clicked.connect(self.page3.selectFolder)

        self.localmusic.cellClicked.connect(lambda row, c: self.selectSong(row))

        self.play.clicked.connect(self.play2pause)
        self.last.clicked.connect(self.lastSong)
        self.next.clicked.connect(self.nextSong)
        self.lyricPage.nextButton.clicked.connect(self.nextSong)
        self.lyricPage.lastButton.clicked.connect(self.lastSong)
        self.lyricPage.playButton.clicked.connect(self.play2pause)

        self.mediaplayer.positionChanged.connect(self.playing)
        self.progressBar.sliderMoved.connect(lambda value: self.mediaplayer.moveSlider(value))
        self.lyricPage.slider.sliderMoved.connect(lambda value: self.mediaplayer.moveSlider(value))

        self.playlistButton.clicked.connect(self.playlistPage.popupPlaylist)

        self.mediaplayer.mediaStatusChanged.connect(self.playerStatusChange)
        # self.mediaplayer.audioOutputChanged.connect(lambda : print(1))
        # # self.mediaplayer.setAudioOutput(QAudioDevice()))

        self.volSlider.valueChanged.connect(self.volMove)

        self.playlistPage.playlistBarList.clicked.connect(self.playlistSwitch)
        self.playlistPage.delete.clicked.connect(self.deleteAllPlaylist)

        self.selectmore.clicked.connect(lambda :self.selectMore(self.localmusic,self.page3.localList))
        self.selectAllButton.clicked.connect(self.selectAllSongs)
        self.deleteLocalButton.clicked.connect(self.delSelectedSongs)
        self.addSongListButton.clicked.connect(self.selectSongList)

        self.createListButton.clicked.connect(self.createSongList)

        self.loopButton.clicked.connect(self.switchLoopModel)

        self.List.clicked.connect(self.switchSongListPage)

        for page in self.songListPage:
            page.table.cellClicked.connect(lambda row, c: self.playsonglist(row))
            page.changenameButton.clicked.connect(self.changeName)
            page.selectButton.clicked.connect(lambda: self.selectMore(self.stackedWidget.currentWidget().table, self.stackedWidget.currentWidget().list))
            page.moreBUtton.clicked.connect(lambda: self.listMenu(QCursor.pos()))
            self.stackedWidget.addWidget(page)

        self.ImageLabel.clicked.connect(self.switchTolyricpage)

        self.lyricPage.backButton.clicked.connect(self.switchTomainpage)

    def updateBackground(self):
        p = QPalette()
        p.setBrush(self.backgroundRole(), QBrush(self.lyricPage.backgroundImg))
        self.setPalette(p)

    def switchTolyricpage(self):
        self.updateBackground()
        self.mainStack.setCurrentIndex(1)

    def switchTomainpage(self):
        self.setStyleSheet("background:(255,255,255)")
        self.mainStack.setCurrentIndex(0)

    #判断是否进入播放模式
    def selectModel(self):
        if  not self.isSelect:
            self.selectedTable.setSelectionMode(QAbstractItemView.MultiSelection)
            self.isSelect = True
        else:
            self.selectedTable.setSelectionMode(QAbstractItemView.NoSelection)
            self.isSelect = False

    # 选择按钮对应的事件，激活多选模式
    def selectMore(self, table, list):
        self.selectedTable = table
        self.selectedList = list
        self.playbarstack.setCurrentIndex(self.playbar)
        self.playbar = not self.playbar
        self.selectedTable.clearSelection()
        self.selectedSongs.clear()
        self.selectModel()

    #播放列表删除所有歌曲
    def deleteAllPlaylist(self):
        self.playlist.clear()
        self.playlistPage.playlistBarList.clear()
        self.playlistPage.playlist.clear()
        self.page3.playlist.clear()
        self.index = 0
        self.page3.index = 0

    #弹出消息框，选择需要添加歌曲的歌单
    def selectSongList(self):
        songList = list()
        for i in self.songListPage:
            songList.append(i.pagename)
        message = selectMessageBox(self,songList)
        if message.exec():
            index = message.list.currentRow()
            if index != -1:
                self.addToSongList(index)

    #添加歌曲到歌单
    def addToSongList(self,index):
        addcount = 0
        exccount = 0
        for i in self.selectedSongs:
            if self.selectedList[i] in self.songListPage[index].list:
                exccount += 1
                continue
            self.songListPage[index].list.append(self.selectedList[i])
            addcount += 1
        self.songListPage[index].fullTable()
        statetool = StateToolTip("添加歌曲","已成功添加{}首歌，{}首已存在".format(addcount,exccount),self)
        statetool.move(700,50)
        statetool.setState(True)
        statetool.show()

    #从列表中删除歌曲
    def delSelectedSongs(self):
        self.selectedSongs.sort()
        for i in range(len(self.selectedSongs)):
            i = self.selectedSongs[i] - i #每次弹出会使列表元素前移，消除前移的下标数。逆序删除也能解决这个问题
            self.selectedTable.removeRow(i)
            self.selectedList.pop(i)
        self.selectedTable.clearSelection()

    #全选
    def selectAllSongs(self):
        if self.selectAllButton.isChecked():
            self.selectedTable.selectAll()
            self.selectedSongs = [i for i in range(len(self.selectedList))]
        else:
            self.selectedTable.clearSelection()
            self.selectedSongs.clear()

    #本地歌曲页面的点击歌曲对应的事件
    def selectSong(self,row):
        if self.isSelect:
            if row in self.selectedSongs:
                self.selectedSongs.remove(row)
            else:
                self.selectedSongs.append(row)
        else:
            self.index = self.page3.selectSong(row)

    # 设置音量条事件
    def volMove(self):
        if self.volSlider.value() == 0:
            self.volIcon.setIcon(FluentIcon.MUTE)
        else:
            self.volIcon.setIcon(FluentIcon.VOLUME)
        self.mediaplayer.audio.setVolume(self.volSlider.value() / 1000)

    # 左侧边栏按钮事件
    def changePage(self, toPage):
        if (toPage != self.stackedWidget.currentIndex()):
            self.stackedWidget.setCurrentIndex(toPage)
        self.List.clearSelection()

    # 暂停和播放相互切换
    def play2pause(self):
        if self.mediaplayer.sign:
            self.endTime.setText(self.mediaplayer.getDuration())
            if self.isplaying:
                self.mediaplayer.pause()
                self.play.setIcon(FluentIcon.PLAY_SOLID)
                self.lyricPage.playButton.setIcon(FluentIcon.PLAY_SOLID)
                self.isplaying = False
            else:
                self.mediaplayer.play()
                self.play.setIcon(FluentIcon.PAUSE_BOLD)
                self.lyricPage.playButton.setIcon(FluentIcon.PAUSE_BOLD)
                self.isplaying = True

    # 获取音乐当前已播放时间，并且改变滑条滑块位置
    def playing(self):
        self.currentTime.setText(self.mediaplayer.getCurrenttime())
        self.progressBar.setSliderPosition(self.mediaplayer.getSliderPosition())
        self.lyricPage.slider.setSliderPosition(self.mediaplayer.getSliderPosition())
        self.lyricPage.updateLyric(self.mediaplayer.position()/1000)

    #播放器状态改变对应的事件
    def playerStatusChange(self):
        if self.mediaplayer.mediaStatus() == QMediaPlayer.MediaStatus.EndOfMedia:
            self.loopPlay()
        elif self.mediaplayer.mediaStatus() == QMediaPlayer.MediaStatus.LoadedMedia:
            self.endTime.setText(self.mediaplayer.getDuration())
            self.switchSongs(self.index)

    #切歌对应的事件
    def switchSongs(self, index):
        self.lyricPage.init(self.playlist[index] if self.playlist else {'title':'暂无歌曲','img':QImage()})
        if self.mainStack.currentIndex() == 1:
            self.updateBackground()
        self.bottomTitle.setText(self.playlist[index]['title'])
        self.bottomArtist.setText(self.playlist[index]['artist'])
        self.ImageLabel.setPixmap(self.playlist[index]['img'])
        self.ImageLabel.scaledToWidth(50)
        self.ImageLabel.setBorderRadius(8, 8, 8, 8)
        self.playlistPage.drawPlaylist(self.playlist[index])


    #设置播放模式（顺序、随机、单曲）
    def switchLoopModel(self):
        self.loopModel += 1
        if self.loopModel > 2:
            self.loopModel = 0

        if self.loopModel == 0:
            self.loopButton.setIcon('loop.svg')
        elif self.loopModel == 1:
            self.loopButton.setIcon('loop_random.svg')
        elif self.loopModel == 2:
            self.loopButton.setIcon('loop_one.svg')

    # 根据设置的播放模式来确定下一首
    def loopPlay(self):
        if self.loopModel == 0:
            self.index += 1
            if self.index >= len(self.playlist):
                self.index = 0
            self.mediaplayer.load(self.playlist[self.index]['path'])
        elif self.loopModel == 1:
            self.index = random.randint(0, len(self.playlist) - 1)
            self.mediaplayer.load(self.playlist[self.index]['path'])
        elif self.loopModel == 2:
            self.mediaplayer.load(self.playlist[self.index]['path'])

        if self.isplaying:
            self.mediaplayer.play()

    # 声明下一曲按钮的槽
    def nextSong(self):
        if self.loopModel == 0 or self.loopModel == 2:
            self.index += 1
            if self.index >= len(self.playlist):
                self.index = 0
        elif self.loopModel == 1:
            self.index = random.randint(0, len(self.playlist) - 1)

        self.mediaplayer.load(self.playlist[self.index]['path'])

        if self.isplaying:
            self.mediaplayer.play()

    # 声明上一曲按钮的槽
    def lastSong(self):
        if self.loopModel == 0 or self.loopModel == 2:
            self.index -= 1
            if self.index < 0:
                self.index = len(self.playlist) - 1
        elif self.loopModel == 1:
            self.index = random.randint(0, len(self.playlist) - 1)

        self.mediaplayer.load(self.playlist[self.index]['path'])

        if self.isplaying:
            self.mediaplayer.play()

    # 重载鼠标按下事件，用以关闭播放侧边栏
    def mousePressEvent(self, event):
        if self.playlistPage.playlistButtonPressed:
            if event.pos().x() < self.width() - 350 or event.pos().y() > 615:
                self.playlistPage.playlistStack.setGeometry(1000, 0, 0, 0)
                self.playlistPage.playlistButtonPressed = False

    #从播放列表切歌对应的事件
    def playlistSwitch(self):
        self.index = self.playlistPage.playlistBarList.currentRow()
        self.mediaplayer.load(self.playlist[self.index]['path'])
        if self.isplaying:
            self.mediaplayer.play()


#以下为歌单功能模块相关函数
    #创建新的歌单类
    def createSongList(self):
        name = '新建的歌单'+str(len(self.songListPage) if len(self.songListPage) != 0 else '')
        self.List.addItem(name)
        newPage = songListPage(name)
        newPage.title.setText(name)
        try:
            newPage.createDataBase()
        except:
            pass
        newPage.table.cellClicked.connect(lambda row,c:self.playsonglist(row))
        newPage.changenameButton.clicked.connect(self.changeName)
        newPage.selectButton.clicked.connect(lambda: self.selectMore(newPage.table, newPage.list))
        newPage.moreBUtton.clicked.connect(lambda: self.listMenu(QCursor.pos()))
        self.stackedWidget.addWidget(newPage)
        self.songListPage.append(newPage)

    #点击歌单里面的歌曲对应的事件
    def playsonglist(self,row):
        page = self.stackedWidget.currentWidget()
        if not self.isSelect:
            if self.playlistPage.listname != page.pagename:
                self.playlistPage.setlist(page.list)
                self.playlist = []
                self.playlist = page.list
                self.playlistPage.listname = page.pagename

            self.index = row
            self.isplaying = True
            self.play.setIcon(FluentIcon.PAUSE_BOLD)
            self.lyricPage.playButton.setIcon(FluentIcon.PAUSE_BOLD)
            self.mediaplayer.load(self.playlist[self.index]['path'])
            self.mediaplayer.play()
        else:
            if row in self.selectedSongs:
                self.selectedSongs.remove(row)
            else:
                self.selectedSongs.append(row)

    #改变歌单的名字
    def changeName(self):
        message = changeNameBox(self)
        if message.exec():
            pass
        else:
            return 
        newName = message.edit.text()
        oldName = self.stackedWidget.currentWidget().pagename
        self.stackedWidget.currentWidget().pagename = newName
        self.stackedWidget.currentWidget().title.setText(newName)
        self.List.currentItem().setText(newName)

        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE songList SET name=? WHERE name=?',(newName,oldName))
        cursor.execute('DROP TABLE IF EXISTS {}'.format(oldName))
        cursor.execute('''create table {}(
                           title TEXT,
                           artist TEXT,
                           album TEXT,
                           duration TEXT,
                           path TEXT);'''.format(newName))
        conn.commit()
        cursor.close()
        conn.close()

    #切换到歌单页面
    def switchSongListPage(self):
        self.stackedWidget.setCurrentWidget(self.songListPage[self.List.currentRow()])
        self.buttonGroup.setExclusive(False)
        self.mainButton.setChecked(False)
        self.localButton.setChecked(False)
        self.recentlyButton.setChecked(False)
        self.statisticsButton.setChecked(False)
        self.buttonGroup.setExclusive(True)

    def listMenu(self,pos):
        menu = RoundMenu()
        menu.addAction(Action(FluentIcon.DELETE,"删除",triggered=self.deleteList))
        # menu.addAction(Action(FluentIcon.CHECKBOX,"重命名",triggered=self.changeName))
        menu.exec(pos)

    def deleteList(self):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM songList WHERE name=?',(self.stackedWidget.currentWidget().pagename,))
        cursor.execute('DROP TABLE IF EXISTS {}'.format(self.stackedWidget.currentWidget().pagename))
        conn.commit()
        cursor.close()
        conn.close()

        self.songListPage.pop(self.List.currentRow())
        self.List.takeItem(self.List.currentRow())
        self.stackedWidget.removeWidget(self.stackedWidget.currentWidget())

        self.List.setCurrentRow(len(self.songListPage)-1)


    #重载事件过滤器，实现歌单右键删除
    def eventFilter(self, obj, event):
        if obj == self.List.viewport():
            if event.type() == QEvent.MouseButtonPress:
                if event.buttons() == Qt.RightButton:
                    self.listMenu(QCursor.pos())


    #判断是否存在data.db文件，如果没有则创建
    def creatDataBase(self):
        if not os.path.exists('data.db'):
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            cursor.execute('''create table localsong (
                           title TEXT,
                           artist TEXT,
                           album TEXT,
                           duration TEXT,
                           path TEXT);''')
            cursor.execute('''create table playlist (
                           title TEXT,
                           artist TEXT,
                           album TEXT,
                           path TEXT);''')
            cursor.execute('''create table currentIndex (
                            currentIndex INTEGER,
                            n NULL);''')
            cursor.execute('''create table songList  (
                                       name TEXT);''')
            cursor.close()
            conn.close()

    #保存
    def savePlaylist(self):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("delete from playlist")
        cursor.execute("delete from currentIndex")
        cursor.execute("delete from songList")

        sql = "insert into playlist (title,artist,album,path) values (?,?,?,?)"

        for i in self.playlist:
            cursor.execute(sql,(i['title'],i['artist'],i['album'],i['path']))
        cursor.execute("insert into currentIndex (currentIndex,n) values (?,?)",(self.index, None))

        for j in self.songListPage:
            cursor.execute("insert into songList (name) values (?)",(j.pagename,))

            cursor.execute("delete from {}".format(j.pagename))
            for i in j.list:
                cursor.execute("insert into {} (title,artist,album,duration,path) values (?,?,?,?,?)".format(j.pagename),
                               (i['title'], i['artist'], i['album'], i['duration'], i['path']))

        conn.commit()
        cursor.close()
        conn.close()

    #加载
    def loadPlaylist(self):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("select * from playlist")
        data = cursor.fetchall()
        for d in data:
            temp = {}
            temp['title'] = d[0]
            temp['artist'] = d[1]
            temp['album'] = d[2]
            temp['path'] = d[3]
            tag = TinyTag.get(d[3], image=True)
            t = QImage()
            t.loadFromData(tag.get_image())
            t = t.scaledToWidth(200)
            temp['img'] = t

            if not temp in self.playlist:
                self.playlist.append(temp)

            self.playlistPage.drawPlaylist(temp)

        #加载歌单内容
        cursor.execute("select * from songList")
        data = cursor.fetchall()
        songList = list()
        for d in data:
            songList.append(d[0])

        for s in songList:
            page = songListPage(s)
            cursor.execute("select * from {}".format(s))
            data = cursor.fetchall()
            for d in data:
                temp = {}
                temp['title'] = d[0]
                temp['artist'] = d[1]
                temp['album'] = d[2]
                temp['path'] = d[4]
                temp['duration'] = d[3]
                tag = TinyTag.get(d[4], image=True)
                t = QImage()
                t.loadFromData(tag.get_image())
                t = t.scaledToWidth(200)
                temp['img'] = t

                if not temp in page.list:
                    page.list.append(temp)

            page.fullTable()
            page.title.setText(s)
            self.songListPage.append(page)
            self.List.addItem(s)

        if cursor.execute("select currentIndex from currentIndex").fetchall() and cursor.execute("select currentIndex from currentIndex").fetchall()[0][0] != None:
            self.index = cursor.execute("select currentIndex from currentIndex").fetchall()[0][0]
        else:
            self.index = 0

        if len(self.playlist) != 0:
            self.playlistPage.playlistBarList.setCurrentRow(self.index)
            self.mediaplayer.load(self.playlist[self.index]['path'])

        cursor.close()
        conn.close()

    #重载关闭窗口事件，用以保存相关数据
    def closeEvent(self, event):
        self.savePlaylist()
        self.page3.saveLocalSongs()

if __name__ == '__main__':
    app = QApplication([])
    windows = mainWindows()
    windows.show()
    app.exec()
