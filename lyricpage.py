from tinytag import TinyTag
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, \
    QVBoxLayout,  QListWidgetItem, QAbstractItemView, QTableWidgetItem, QStyle, QSlider, QGraphicsBlurEffect
from PySide6.QtCore import QSize, QUrl, QEvent, Qt, QPoint
from PySide6.QtGui import QPixmap, QImage, QCursor, QFont
from ui_musicplayer import Ui_Form
from qfluentwidgets import ImageLabel, FluentIcon, PopUpAniStackedWidget, ListWidget, ToolButton, TitleLabel, \
                            TableWidget, MessageBoxBase, SubtitleLabel, LineEdit, TransparentTogglePushButton, RoundMenu, Action, \
                            PrimaryPushButton, StateToolTip, SingleDirectionScrollArea, TransparentToolButton, Slider, setCustomStyleSheet, \
                            setThemeColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from qframelesswindow import FramelessWindow
from page3 import page3
import re,copy,cv2,numpy

class lyricPage(QWidget):
    def __init__(self):
        super().__init__()
        self.backButton = TransparentToolButton()
        self.backButton.setIcon(FluentIcon.LEFT_ARROW)

        self.cover = ImageLabel()
        self.cover.setStyleSheet("QLabel{background:transparent}")
        self.cover.setBorderRadius(8,8,8,8)
        self.cover.setMinimumSize(200,200)
        self.cover.setMinimumSize(200,200)


        self.title = TitleLabel()
        self.title.setMaximumWidth(200)
        self.title.setMinimumWidth(200)
        self.title.setWordWrap(True)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("QLabel{background:transparent}")
        f = QFont()
        f.setPointSize(16)
        f.setBold(True)
        self.title.setFont(f)

        self.lyric = []
        self.trans_lyric = []
        self.duration = []
        self.lyricLable = {}
        self.currentSong = {}

        self.lyric_font = QFont()
        self.lyric_font.setPointSize(14)
        self.lyric_font.setBold(False)

        self.lyric_scroll = SingleDirectionScrollArea(orient=Qt.Vertical)
        self.lyric_scroll.setStyleSheet("QScrollArea{background: transparent; border: none}")
        self.lyric_scroll.setAlignment(Qt.AlignCenter)
        self.lyric_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lyric_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimumWidth(200)
        self.slider.setMaximumWidth(200)
        qss = ("QSlider{background:transparent} \
                QSlider::groove:horizontal{height:6px;background-color:transparent} \
                QSlider::sub-page:horizontal{background-color:rgba(100,100,100,200);border-radius:3px} \
                QSlider::add-page:horizontal{background-color:rgba(200,200,200,100);border-radius:3px} \
                QSlider::handle:horizontal{background-color: rgba(150, 150, 150, 255);width: 10px;height:6px;border-radius:3px}")
        self.slider.setStyleSheet(qss)
        g = QGraphicsBlurEffect(self.slider)
        g.setBlurRadius(2)
        self.slider.setGraphicsEffect(g)


        self.nextButton = TransparentToolButton()
        self.nextButton.setIcon(FluentIcon.CARE_RIGHT_SOLID)
        self.nextButton.setMinimumSize(20,20)
        self.nextButton.setMaximumSize(20,20)

        self.lastButton = TransparentToolButton()
        self.lastButton.setIcon(FluentIcon.CARE_LEFT_SOLID)
        self.lastButton.setMinimumSize(20,20)
        self.lastButton.setMaximumSize(20,20)

        self.playButton = TransparentToolButton()
        self.playButton.setIcon(FluentIcon.PLAY_SOLID)
        self.playButton.setMinimumSize(20,20)
        self.playButton.setMaximumSize(20,20)

        self.step = 0
        self.currentTime = 0
        self.index = 0
        self.value = 0
        self.backgroundImg = QImage()

        h3 = QHBoxLayout()
        h3.addSpacing(8)
        h3.addWidget(self.lastButton)
        h3.addWidget(self.playButton)
        h3.addWidget(self.nextButton)

        v1 = QVBoxLayout()
        v2 = QVBoxLayout()
        v2.addWidget(self.backButton)
        v2.addSpacing(800)
        v1.addSpacing(250)
        v1.addWidget(self.cover)
        v1.addSpacing(20)
        v1.addWidget(self.title)
        v1.addWidget(self.slider)
        v1.addLayout(h3)
        v1.addSpacing(250)
        h1 = QHBoxLayout()
        h1.addLayout(v2)
        h1.addSpacing(150)
        h1.addLayout(v1)
        h1.addWidget(self.lyric_scroll)
        h1.addSpacing(100)
        self.setLayout(h1)

    def getLyric(self):
        lyrics = TinyTag.get(self.currentSong['path'], image=True).extra['lyrics']
        lyrics = lyrics.split('\n')
        for l in lyrics:
            if not re.match("\[\d\d:\d\d\.\d\d\]",l):
                continue
            l = l.split(']')
            if l[1] == '':
                continue
            self.lyric.append(l[1])
            self.duration.append(l[0][1:])

        for i,lyric in enumerate(self.lyric):
            if '\u2009' in lyric:
                lyric = lyric.split('\u2009')
                self.lyric[i] = lyric[0]
                self.trans_lyric.append(lyric[1])
            else:
                self.trans_lyric.append('')
                
    def initScrollArea(self):
        q = QWidget()
        v = QVBoxLayout()
        for i in range(len(self.lyric)):
            lb = TitleLabel()
            lb.setAlignment(Qt.AlignCenter)
            lb.setStyleSheet("QLabel{background:transparent}")
            lb.setText(self.lyric[i]+'\n'+self.trans_lyric[i])
            lb.setFont(self.lyric_font)
            lb.setWordWrap(True)
            lb.setMaximumHeight(90)
            lb.setMinimumHeight(90)

            time:float = int(self.duration[i][0:2])*60 + int(self.duration[i][3:5]) + int(self.duration[i][6:])/100
            self.duration[i] = time
            self.lyricLable[time] = lb
            v.addWidget(lb)
        q.setLayout(v)
        q.setStyleSheet("QWidget{background:transparent}")
        self.lyric_scroll.setWidget(q)
        self.step = 10000/len(self.lyricLable)

    def getImage(self):
        tag = TinyTag.get(self.currentSong['path'], image=True)
        img = cv2.imdecode(numpy.array(bytearray(tag.get_image())),cv2.COLOR_RGB2BGR)
        img = cv2.GaussianBlur(img,(299,299),90)
        img = cv2.imencode('.png',img)[1]
        img = img.tobytes()
        qimg = QImage()
        qimg.loadFromData(img)
        qimg = qimg.scaledToWidth(1000)
        self.backgroundImg = qimg


    def init(self,song:map):
        if song['title'] == '暂无歌曲':
            self.title.setText(song['title'])
            return
        self.currentSong = song
        self.lyric = []
        self.trans_lyric = []
        self.duration = []
        self.lyricLable = {}
        self.value = 0
        self.getLyric()
        self.initScrollArea()
        self.getImage()
        f = QFont()
        f.setPointSize(18)
        f.setBold(True)
        self.lyricLable[0.0].setFont(f)
        self.cover.setImage(self.currentSong['img'])
        self.title.setText(self.currentSong['title'])

    def updateLyric(self,duration):
        f = QFont()
        f.setPointSize(16)
        f.setBold(True)
        for k in range(len(self.duration)):
            if duration < self.duration[k]:
                self.index = k-1
                break

        if self.duration[self.index] != self.currentTime:
            for k in self.lyricLable:
                self.lyricLable[k].setFont(self.lyric_font)
            self.lyricLable[self.duration[self.index]].setFont(f)
            self.currentTime = self.duration[self.index]

            value = (self.index-3)*95

            self.lyric_scroll.verticalScrollBar().setValue(value if value > 0 else 0)
            self.update()


