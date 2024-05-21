# # from pymediainfo import MediaInfo
# # music = MediaInfo.parse("D:\\音乐\\Guns N' Roses\\Don't cry.flac")
# # for track in music.tracks:
# #     print(track.title)
#
# import os,mutagen,cv2
# from mutagen import flac,mp3
# from mutagen.easyid3 import EasyID3
# import numpy as np
#
# # l = []
# # def findAllFile(base):
# #     for root, ds, fs in os.walk(base):
# #         for f in fs:
# #             if f.endswith('.mp3') or f.endswith('.flac') or f.endswith('.ape'):
# #                 fullname = os.path.join(root, f)
# #                 l.append(fullname)
# #             else:
# #                 continue
# # findAllFile('D:\\音乐')
# # print(l)
#
# # def getinfo(p):
# #     # music = MediaInfo.parse(p)
# #     # print(music.tracks[0].img)
# #     music = mutagen.File(p,easy=True)
# #     print(music.[0])
#
# # for p in l:
# #     getinfo(p)
# #
# # m = flac.FLAC("D:\\音乐\\mihoyo\\阿云嘎 HOYO-MiX - Regression.flac")
# # print(m['lyrics'])
# # i = cv2.imread(),,
# # cv2.imshow('1',cv2.imdecode(np.array(bytearray(m.pictures[0].data),dtype='uint8'),cv2.IMREAD_UNCHANGED))
# # cv2.waitKey(0)
#
# # m = mutagen.File("D:\\音乐\\Plastic Love.mp3")
# # print(m.tags.getall('artist'))
# # cv2.imshow('1',cv2.imdecode(np.array(bytearray(m.tags.getall('APIC')[0].data),dtype='uint8'),cv2.IMREAD_UNCHANGED))
# #
# # m = mp3.MP3("D:\\音乐\\Plastic Love.mp3")
# # print(m.getTitle())
#
# # m = EasyID3("D:\\音乐\\Plastic Love.mp3")
# # print(m.valid_keys.keys())
#
# from tinytag import TinyTag
# lyric = []
# duration = []
# trans_lyric = []
# lyrics:str = TinyTag.get("D:\\music\\丸之内虐待狂-椎名林檎.mp3", image=True).extra['lyrics']
# lyrics = lyrics.split('\n')
# for l in lyrics:
#     l = l.split(']')
#     lyric.append(l[1])
#     duration.append((l[0])[1:-1])
#
# for i,l in enumerate(lyric):
#     if '\u2009' in l:
#         l = l.split('\u2009')
#         lyric[i] = l[0]
#         trans_lyric.append(l[1])
#     else:
#         trans_lyric.append('')
#
# print(lyric)
# print(trans_lyric)
# print(duration)
#
# # cv2.imshow('1',cv2.imdecode(np.array(bytearray(m.get_image()),dtype='uint8'),cv2.IMREAD_UNCHANGED))
# # cv2.waitKey(0)



import sqlite3

conn = sqlite3.connect('hanzi.db') #括号里面的是数据库地址，可以先创建一个，扩展名为.db
cursor = conn.cursor()
sql_create = 'create table hanzi (jianti TEXT,jbihua TEXT,fanti TEXT,fbihua TEXT)'   #这是创建数据表的命令语句，其中table后面的hanzi为数据表的名字，可以替换。
                                                                                                #括号里面粉色的是每一列元素的种类名字，可以改变，后期用来定位数据。
                                                                                                #橘黄色的为每一个单元格储存的数据类型，TEXT代表储存字符类型
cursor.execute(sql_create) #执行创建数据表的指令

sql_insert = 'insert into hanzi (jianti,jbihua,fanti,fbihua) values (?,?,?,?)' #hanzi代表需要被添加的数据表名称，可以修改。
                                                                            #前面一个括号里面代表相应名称的列，就是前面创建数据表所赋予的名称，需要向哪一列追加内容就写哪一列的名字
                                                                            #后面一个括号里面的问号是占位符，就是代表需要添加的数据

cursor.execute(sql_insert,(jianti,bihua,fanti,bihua)) #执行插入语句，同时后面一个括号代表你需要添加的内容，注意顺序。

conn.commit() #每次修改数据表后都需要执行这个函数，代表提交修改。
cursor.close()#这两个函数都是断开与数据库的连接
conn.close()