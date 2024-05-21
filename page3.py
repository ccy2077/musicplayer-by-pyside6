from tinytag import TinyTag
from PySide6.QtWidgets import QWidget, QTableWidgetItem, QFileDialog, QHBoxLayout, \
    QVBoxLayout
from PySide6.QtGui import QPixmap, QImage, QIcon
from ui_musicplayer import Ui_Form
from qfluentwidgets import ImageLabel, FluentIcon, StateToolTip
import os, sqlite3

class page3(QWidget):
    def __init__(self,mainWindows):
        super().__init__()
        self.localList = list()
        self.path = ''
        self.playlist = []
        self.index = 0
        self.statetooltip = None
        self.mainWindows = mainWindows

        mainWindows.localmusic.setWordWrap(False)
        mainWindows.localmusic.setColumnCount(5)
        mainWindows.localmusic.setBorderRadius(5)
        width = 800
        mainWindows.localmusic.setColumnWidth(0, width / 10)
        mainWindows.localmusic.setColumnWidth(1, (width * 5) / 20)
        mainWindows.localmusic.setColumnWidth(2, (width * 2) / 10)
        mainWindows.localmusic.setColumnWidth(3, (width * 3) / 10)
        mainWindows.localmusic.setColumnWidth(4, (width * 3) / 20)
        mainWindows.localmusic.setHorizontalHeaderLabels([' ', '歌名', '歌手', '专辑', '时长'])
        mainWindows.localmusic.verticalHeader().hide()

        self.loadLocalSongs()

    # 填充本地歌曲界面的音乐列表
    def fullTable(self):
        self.mainWindows.localmusic.setRowCount(len(self.localList))
        for i in range(len(self.localList)):
            if self.localList[i]['title'] == None:
                self.localList[i]['title'] = 'unknown'

            if self.localList[i]['artist'] == None:
                self.localList[i]['artist'] = 'unknown'

            self.mainWindows.localmusic.setItem(i, 1, QTableWidgetItem(self.localList[i]['title']))
            self.mainWindows.localmusic.setItem(i, 2, QTableWidgetItem(self.localList[i]['artist']))
            self.mainWindows.localmusic.setItem(i, 3, QTableWidgetItem(self.localList[i]['album']))
            self.mainWindows.localmusic.setItem(i, 4, QTableWidgetItem(self.localList[i]['duration']))

            if self.localList[i]['img'] == None:
                self.localList[i]['img'] = QPixmap()
                self.localList[i]['img'].load('noimage.svg')
                self.localList[i]['img'] = self.localList[i]['img'].scaledToWidth(200)

            it = QWidget()
            it.setStyleSheet('background:rgba(255,255,255,0)')
            im = ImageLabel()
            im.setPixmap(self.localList[i]['img'])
            im.scaledToWidth(50)
            im.setBorderRadius(8, 8, 8, 8)
            it.setMaximumSize(60, 60)
            it.setMinimumSize(60, 60)
            h = QHBoxLayout()
            v = QVBoxLayout()
            h.addWidget(im)
            v.addLayout(h)
            it.setLayout(v)

            self.mainWindows.localmusic.setCellWidget(i, 0, it)

            self.mainWindows.localmusic.setRowHeight(i, 80)

        # 调用QFileDialog类，来选择音乐路径

    def selectFolder(self):

        self.path = QFileDialog.getExistingDirectory(self, "选择路径", 'D:\\music')
        if not self.path:
            return
        self.localList.clear()
        self.showInfo()
        self.findAllFile(self.path)
        self.fullTable()
        self.showInfo()

    # 找到指定目录下的所有音乐文件
    def findAllFile(self, base):
        for root, ds, fs in os.walk(base):
            for f in fs:
                if f.endswith('.mp3') or f.endswith('.flac'):
                    fullname = os.path.join(root, f)
                    tempdir = {}
                    tag = TinyTag.get(fullname, image=True)
                    tempdir['path'] = fullname
                    tempdir['title'] = tag.title
                    tempdir['artist'] = tag.artist
                    tempdir['duration'] = '{:0>2d}:{:0>2d}'.format(int(tag.duration // 60),
                                                        int(tag.duration - (tag.duration // 60) * 60))
                    tempdir['album'] = tag.album
                    if tag.get_image() != None:
                        temp = QImage()
                        temp.loadFromData(bytearray(tag.get_image()))
                        temp = temp.scaledToWidth(200)
                        tempdir['img'] = temp
                    else:
                        tempdir['img'] = None

                    self.localList.append(tempdir)

                else:
                    continue

            self.saveLocalSongs()

    # 选择要播放的歌曲
    def selectSong(self, row):
        if not (self.localList[row] in self.playlist):
            self.playlist.append(self.localList[row])

        for i, l in enumerate(self.playlist):
            if l['title'] == self.localList[row]['title']:
                self.index = i
                break
            else:
                self.index = len(self.playlist)-1

        self.mainWindows.playlistPage.drawPlaylist(self.playlist[self.index])
        self.mainWindows.playlistPage.listname = 'local'
        self.mainWindows.mediaplayer.load(self.localList[row]['path'])
        self.mainWindows.mediaplayer.play()
        self.mainWindows.play.setIcon(FluentIcon.PAUSE_BOLD)
        self.mainWindows.lyricPage.playButton.setIcon(FluentIcon.PAUSE_BOLD)
        self.mainWindows.isplaying = True

        return self.index

    def showInfo(self):
        if self.statetooltip:
            self.statetooltip.setContent("扫描完成，共扫描{:d}首歌".format(len(self.localList)))
            self.statetooltip.setState(True)
            self.statetooltip = None
        else:
            self.statetooltip = StateToolTip("正在扫描歌曲","正在扫描，请等待",self.mainWindows)
            self.statetooltip.move(700, 50)
            self.statetooltip.setState(False)
            self.statetooltip.show()

    def loadLocalSongs(self):
        if os.path.exists('data.db'):
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            cursor.execute("select * from localsong")
            data = cursor.fetchall()
            for d in data:
                tempdir = {}
                tempdir['path'] = d[4]
                tempdir['title'] = d[0]
                tempdir['artist'] = d[1]
                tempdir['duration'] = d[3]
                tempdir['album'] = d[2]
                tag = TinyTag.get(d[4], image=True)
                if tag.get_image() != None:
                    temp = QImage()
                    temp.loadFromData(tag.get_image())
                    temp = temp.scaledToWidth(200)
                    tempdir['img'] = temp
                else:
                    tempdir['img'] = None

                self.localList.append(tempdir)

            cursor.close()
            conn.close()
            self.fullTable()
        else:
            return

    def saveLocalSongs(self):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM localsong")
        # cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'localsong'")
        sql = "insert into localsong (title,artist,album,duration,path) values (?,?,?,?,?)"
        for i in range(len(self.localList)):
            cursor.execute(sql,(self.localList[i]['title'],self.localList[i]['artist'],self.localList[i]['album'],self.localList[i]['duration'],self.localList[i]['path']))
        conn.commit()
        cursor.close()
        conn.close()
