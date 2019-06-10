#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Description：这个文件就是cgteamwork api ，用于写往cgteamwork上上传数据跟读取数据的函数api
import sys
sys.path.append(r"C:/cgteamwork5/bin/base")
DOWNLOAD_PATH="D:/"
# 上传临时文件的文件夹

TEMP_PATH = r"O:/Public/config/cgtw_upload_image/images"
FFMPEG_PATH=r"O:\Users\fankaijun\ffmpeg\bin\ffmpeg.exe"
FFPROBE_PATH = r"O:\Users\fankaijun\ffmpeg\bin\ffprobe.exe"
FFPLAY_PATH  = r"O:\Users\fankaijun\ffmpeg\bin\ffplay.exe"

class Fun(object):
    def __init__(self):
        import sys
        import os
        import subprocess
        import cv2
        import json
        from PIL import Image
        self._sys = sys
        self._os = os
        self._subprocess =subprocess
        self._cv2 = cv2
        self._image = Image
        self._json = json
        self.moveSuffix = ['avi', 'mp4', 'mov', 'wmv', 'mpeg', 'mkv', 'flv', 'f4v', 'm4v', 'rmvb', 'rm', '3gp', 'dat', 'ts','mts','vob','MOV','MP4',]
        self.photoSuffix = ['jpg', 'png', 'gif', 'fpx',  'bmp', 'tiff', 'pcx', 'tga', 'exif', 'svg', 'cdr', 'pcd', 
                          'dxf','ufo','eps', 'ai', 'raw', 'WMF', 'webp','tif','vrmap','vrlmap']
                          
        self.FF_image = ['exr','dpx']
        self.Cv_image = ['hdr']
        self.ZIP_FILE = ['rar','zip']
        self.PhotoShop = ['PSD','psd']
        self.NukeFile = ['nk']
    def getSingleInformation(self,path,type,CheckState):
        '''
        get single information
        :param path: file path
        :param type: dict
        :return:
        '''
        if type in self.moveSuffix:
            messageDict = {}
            if not CheckState:
                vc = self._cv2.VideoCapture(path)
                if vc.isOpened():
                    print 'Cv2 Open successful'
                    messageDict['asset.image'] = self.getMoviePicture(path)
                    messageDict['asset.asset_frame'] = self.getMovieFramRange(path)
                    messageDict['asset.asset_time'] = self.getMovieTimes(path)
                    messageDict['asset.asset_resolution'] = self.getMovieResoultion(path)
                    return messageDict
                else :
                    print 'FFmepg Open successful'
                    time = self.getFFmepgTimes(path)[0]
                    messageDict['asset.image'] =self.cutVideoImage_reAndTime(path,time)
                    messageDict['asset.asset_frame'] = self.getFFmepgTimes(path)[1]
                    messageDict['asset.asset_time'] =str(time)+ 's'
                    messageDict['asset.asset_resolution'] =self.getLength(path)
                    return messageDict
            else:
                imagePath = path.split('.')[0]+'.jpg'
                if self._os.path.exists(imagePath):
                    print 'have img'
                    messageDict['asset.image'] = self.getPsdImage(imagePath)
                    messageDict['asset.asset_resolution'] = ''
                    messageDict['asset.asset_frame'] = ''
                    messageDict['asset.asset_time'] = ''
                    return messageDict
                else:
                    print 'No img'
                    messageDict['asset.image'] = ''
                    messageDict['asset.asset_resolution'] = 'No Images'
                    messageDict['asset.asset_frame'] = ''
                    messageDict['asset.asset_time'] = ''
                    return messageDict
                
                
        elif type in self.FF_image:
            print 'FFmepg Open successful'
            messageDict = {}
            messageDict['asset.image'] = self.ImageFormatTrans(path)
            messageDict['asset.asset_resolution']=self.getLength(path)
            messageDict['asset.asset_frame'] = ''
            messageDict['asset.asset_time'] = ''
            return messageDict
            
            
        elif type in self.Cv_image:
            print 'Opencv Open Images'
            messageDict = {}
            messageDict['asset.image'] = self.getPsdImage(path)
            messageDict['asset.asset_resolution']=self.cv2GetImage_res(path)
            messageDict['asset.asset_frame'] = ''
            messageDict['asset.asset_time'] = ''
            return messageDict
            
        elif type in self.NukeFile:
            print 'Nuke Open'
            messageDict = {}
            imagePath = path.split('.')[0]+'.jpg'
            if self._os.path.exists(imagePath):
                print 'Nuke have img'
                messageDict['asset.image'] = self.getPsdImage(imagePath)
                messageDict['asset.asset_resolution'] = ''
                messageDict['asset.asset_frame'] = ''
                messageDict['asset.asset_time'] = ''
                return messageDict
            else:
                print 'Nuke No img'
                messageDict['asset.image'] = ''
                messageDict['asset.asset_resolution'] = 'No Images'
                messageDict['asset.asset_frame'] = ''
                messageDict['asset.asset_time'] = ''
                return messageDict

        elif type in self.photoSuffix:
            messageDict = {}
            image = self.getPictures(path)
            if not image:
                return 'error'
            messageDict['asset.image'] = image
            messageDict['asset.asset_resolution']=self.getPictureResoultion(path)
            messageDict['asset.asset_frame'] = ''
            messageDict['asset.asset_time'] = ''
            return messageDict
            
            
        elif type in self.PhotoShop:#仅限
            messageDict = {}
            imagePath = path.split('.')[0]+'.jpg'
            if self._os.path.exists(imagePath):
                messageDict['asset.image'] = self.getPsdImage(imagePath)
                messageDict['asset.asset_resolution'] = ''
                messageDict['asset.asset_frame'] = ''
                messageDict['asset.asset_time'] = ''
                return messageDict
            else:
                print 'No img'
                messageDict['asset.image'] = ''
                messageDict['asset.asset_resolution'] = 'No Images'
                messageDict['asset.asset_frame'] = ''
                messageDict['asset.asset_time'] = ''
                return messageDict
     
        else:
            print 'This is another',type
            if CheckState:
                messageDict = {}
                imagePath = path.split('.')[0]+'.jpg'
                if self._os.path.exists(imagePath):
                    messageDict['asset.image'] = self.getPsdImage(imagePath)
                    messageDict['asset.asset_resolution'] = ''
                    messageDict['asset.asset_frame'] = ''
                    messageDict['asset.asset_time'] = ''
                    return messageDict
                else:
                    print 'No img'
                    messageDict['asset.image'] = ''
                    messageDict['asset.asset_resolution'] = 'No Images'
                    messageDict['asset.asset_frame'] = ''
                    messageDict['asset.asset_time'] = ''
                    return messageDict
            else:
                print 'error',type
                return 'error'
        return messageDict
        
        
    def ChangeFilePath(self,path):
        FilePath = ''
        if '/' in path:
            FilePath = path.split('/')
        elif '\\' in path:
            FilePath = path.replace('\\','/')
            FilePath = FilePath.split('/')
        else:
            pass
        new_FilePath = "'"
        for length  in range(len(FilePath)):
            if length == 0:
                new_FilePath = new_FilePath +'"'+ FilePath[length]+"/"
            elif length == len(FilePath)-1:
                new_FilePath = new_FilePath + FilePath[length] + '"' + "'"
            elif length != 0 and length != len(FilePath)-1:
                new_FilePath = new_FilePath + FilePath[length] + '/'
        return new_FilePath.replace("'","")
    def getSeqInformation(self,path,type,seq_num,CheckState):
        '''
        get sequence information
        :param path: sequence path
        :param type: picture type such as jpg,png
        :param seq_num: Number of sequence frames
        :return:
        '''
        if type in self.photoSuffix:
            messageDict = {}
            messageDict['asset.image'] = self.getPictures(path)
            messageDict['asset.asset_resolution'] = self.getPictureResoultion(path)
            messageDict['asset.asset_time'] = self.getSeqTimes(seq_num)
            return messageDict
            
        elif type in self.FF_image:
            print 'FFmepg Open successful'
            messageDict = {}
            messageDict['asset.image'] = self.ImageFormatTrans(path)
            messageDict['asset.asset_resolution']=self.getLength(path)
            messageDict['asset.asset_time'] = self.getSeqTimes(seq_num)
            return messageDict
            
        elif type in self.Cv_image:
            print 'Opencv Open Images'
            messageDict = {}
            messageDict['asset.image'] = self.getPsdImage(path)
            messageDict['asset.asset_resolution']=self.cv2GetImage_res(path)
            messageDict['asset.asset_time'] = self.getSeqTimes(seq_num)
            return messageDict
        else:
            messageDict = {}
            messageDict['asset.image'] = ''
            messageDict['asset.asset_time'] = self.getSeqTimes(seq_num)
            messageDict['asset.asset_resolution'] = ''
            return messageDict
            
    def ImageFormatTrans(self,imagePath):
        pngname = self._os.path.split(imagePath)[-1].split('.')[0]
        dirName = self._os.path.split(imagePath)[0].split('/')[-1]
        dirPath = (TEMP_PATH + "/" + dirName)
        if not self._os.path.exists(dirPath):  # 判断下载图片的路径是否存在，不存在则创建
            self._os.makedirs(dirPath)
        self.img_path = TEMP_PATH + "/" + dirName + '/' + pngname + '.jpg'
        if self._os.path.exists(self.img_path):
            return self.img_path
        #self.img_path = 'D:/Text ure/62.jpg'
        
        imagePath = self.ChangeFilePath(imagePath).decode('utf-8')
        self.img_path = self.ChangeFilePath(self.img_path).decode('utf-8')
        
        cmd = FFMPEG_PATH+" -y -i " + imagePath + " -ac 1 -acodec libamr_nb" \
        " -ar 8000 -ab 12200 -s 512x512 -b 128 -r 15 " + self.img_path
        cmd = cmd.encode(sys.getfilesystemencoding())
        if "?" in cmd:
            cmd = cmd.replace("?","")
        self._subprocess.call(cmd , shell=True)
        SavePath = self.img_path.replace('"','')
        return SavePath
        
    def getFFmepgTimes(self,filename):
        command = [FFPROBE_PATH, "-loglevel", "quiet", "-print_format", "json", "-show_format", "-show_streams", "-i",filename]
        result = self._subprocess.Popen(command, shell=True, stdout=self._subprocess.PIPE, stderr=self._subprocess.STDOUT)
        out = result.stdout.read()
        temp = str(out.decode('utf-8'))
        
        data = self._json.loads(temp)["format"]['duration']
        Frame = '1-' + self._json.loads(temp)["streams"][0]['nb_frames']
        return float(data), Frame

    def getLength(self,filename):
        command = [FFPROBE_PATH, "-loglevel", "quiet", "-print_format", "json", "-show_format", "-show_streams", "-i",
                   filename]
        result = self._subprocess.Popen(command, shell=True, stdout=self._subprocess.PIPE, stderr=self._subprocess.STDOUT)
        out = result.stdout.read()
        temp = str(out.decode('utf-8'))
        try:
            data = self._json.loads(temp)['streams'][1]['width']
            data1 = self._json.loads(temp)['streams'][1]['height']
        except:
            data = self._json.loads(temp)['streams'][0]['width']
            data1 = self._json.loads(temp)['streams'][0]['height']

        return str(data) + "*" + str(data1)

    def cv2GetImage_res(self,imagePath):
        img = self._cv2.imread(imagePath)
        return str(img.shape[1]) + '*' + str(img.shape[0])
        
    def cutVideoImage_reAndTime(self,videoPath,time):
        resolution ="512x512"
        pngname = self._os.path.split(videoPath)[-1].split('.')[0]
        dirName = self._os.path.split(videoPath)[0].split('/')[-1]
        dirPath = (TEMP_PATH + "/" + dirName)
        if not self._os.path.exists(dirPath):  # 判断下载图片的路径是否存在，不存在则创建
            self._os.makedirs(dirPath)
        self.img_path = TEMP_PATH + "/" + dirName + '/' + pngname + '.jpg'
        if self._os.path.exists(self.img_path):
            return self.img_path
        videoPath = videoPath.decode('utf-8')
        fileName=self.img_path.decode('utf-8').replace('\\','/')
        time = int(time/2)
        videoPath = self.ChangeFilePath(videoPath)
        fileName = self.ChangeFilePath(self.img_path)
        cmd=FFMPEG_PATH+" -i " + videoPath+" -y "  + " -ss " + str(time)\
             + " -t 0.001 -s "+ resolution + " " + fileName
        self._subprocess.call(cmd.encode(sys.getfilesystemencoding()) , shell=True)
        return self.img_path

    def getMoviePicture(self,urls):
        '''
        get the cut image
        :param urls:
        :return:
        '''
        pngname = self._os.path.split(urls)[-1].split('.')[0]
        dirName= self._os.path.split(urls)[0].split('/')[-1]
        dirPath =TEMP_PATH+"\\"+dirName
        if not self._os.path.exists(dirPath):#判断下载图片的路径是否存在，不存在则创建
            self._os.makedirs(dirPath)
        self.img_path = TEMP_PATH+"\\"+dirName+'\\'+pngname+'.jpg'
        if self._os.path.exists(self.img_path):
            return self.img_path
        else:
            vc = self._cv2.VideoCapture(urls)  # 读入视频文件
            frames_num = int(vc.get(7) / 4)  # 获取视频总帧数
            vc.set(self._cv2.CAP_PROP_POS_FRAMES,frames_num)#
            rval, frame = vc.read()#
            self._cv2.imwrite(self.img_path , frame)#
            # frames_num = int(vc.get(7) / 4)  # 获取视频总帧数
            print 'Save successful'
            # c = 1  # 做循环判断
            # while rval:  # 循环读取视频帧vc
            #     rval, frame = vc.read()
            #     if (c % frames_num == 0):  # 每隔timeF帧进行存储操作
            #         self._cv2.imwrite(self.img_path, frame)  # 存储为图像
            #         print 'Save successful'
            #         break
            #     c = c + 1
            #     self._cv2.waitKey(1)
            self._cv2.waitKey(1)#
            vc.release()
            # print'end'
            return self.img_path

    def getMovieFramRange(self,urls):
        '''
        get movie framRange
        :param urls:
        :return:
        '''
        vc = self._cv2.VideoCapture(urls)  # 读入视频文件
        framRange = vc.get(7)
        return '1-' + str(int(framRange))

    def getMovieTimes(self,urls):
        '''
        get movie times
        :param urls:
        :return:
        '''
        vc = self._cv2.VideoCapture(urls)
        framRange = vc.get(7)
        time = framRange / 24
        if len(str(time).split('.')) <= 1:
            times = str(time)
        elif len(str(time).split('.')) > 1:
            if len(str(time).split('.')[-1]) <= 2:
                times = str(time).split('.')[0] + '.' + str(time).split('.')[-1]
            elif len(str(time).split('.')[-1]) > 2:
                times = str(time).split('.')[0] + '.' + str(time).split('.')[-1][:2]
        return times + 's'

    def getMovieResoultion(self,urls):
        video = self._cv2.VideoCapture(str(urls))
        videoWidth = int(video.get(3))
        videoHight = int(video.get(4))
        pngname = self._os.path.split(urls)[-1].split('.')[0]
        dirName = self._os.path.split(urls)[0].split('/')[-1]
        self.img_path = TEMP_PATH + "\\" + dirName + '\\' + pngname + '.jpg'
        if self._os.path.exists(self.img_path) :
            img = self._cv2.imread(self.img_path)
            pic = self._cv2.resize(img, (512, 512), interpolation=self._cv2.INTER_CUBIC)
            self._cv2.imwrite(self.img_path,pic)
            return str(videoWidth)+'*'+str(videoHight)
        else:
            return ''
    def getPsdImage(self,urls):
        pngname = self._os.path.split(urls)[-1].split('.')[0]
        dirName = self._os.path.split(urls)[0].split('/')[-1]
        dirPath = TEMP_PATH+"\\"+dirName
        self.img_path = TEMP_PATH + "\\" + dirName + '\\' + pngname + '.jpg'
        if not self._os.path.exists(dirPath):  # 判断下载图片的路径是否存在，不存在则创建
            self._os.makedirs(dirPath)
        if self._os.path.exists(self.img_path):
            return self.img_path
        else:
            img = self._cv2.imread(urls)
            self.img_path = self.img_path.replace('/' , '\\')
            pic = self._cv2.resize(img , (1024 , 1024) , interpolation = self._cv2.INTER_CUBIC)
            self._cv2.imwrite(self.img_path , pic)
            
        SavePath = self.img_path.replace('"','')
        return SavePath

    def getPictures(self, urls):
        '''
        get PNG type images of picture
        :param urls:
        :return:
        '''
        pngname = self._os.path.split(urls)[-1].split('.')[0]
        dirName = self._os.path.split(urls)[0].split('/')[-1]
        dirPath = self.img_path = TEMP_PATH + "\\" + dirName
        if not self._os.path.exists(dirPath):#判断下载图片的路径是否存在，不存在则创建
            self._os.makedirs(dirPath)
        self.img_path = TEMP_PATH + "\\" + dirName + '\\' + pngname + '.jpg'
        if self._os.path.exists(self.img_path):
            return self.img_path
        try:#如果图片PIL解析不了
            img = self._image.open(urls)
            print 'Yes'
        except IOError:
            return False
        img  = img.convert('RGB')
        img.save(self.img_path)
        #压缩
        img = self._cv2.imread(self.img_path)
        pic = self._cv2.resize(img, (512, 512), interpolation=self._cv2.INTER_CUBIC)
        self._cv2.imwrite(self.img_path,pic)
        return self.img_path

    def getPictureResoultion(self,urls):
        '''
        get picture resolution
        :param urls:
        :return:
        '''
        img = self._image.open(urls)
        return str(img.size[0]) + '*' + str(img.size[1])

    def getSeqTimes(self,seq_num):
        time = int(seq_num) / 24
        if len(str(time).split('.')) <= 1:
            times = str(time)
        elif len(str(time).split('.')) > 1:
            if len(str(time).split('.')[-1]) <= 2:
                times = str(time).split('.')[0] + '.' + str(time).split('.')[-1]
            elif len(str(time).split('.')[-1]) > 2:
                times = str(time).split('.')[0] + '.' + str(time).split('.')[-1][:2]
        return times + 's'

class CGTW(object):
    def __init__(self):
        import cgtw
        # from cgtw import tw
        import os
        self._os = os
        self._t_tw = cgtw.tw()
        self.getProjectDatabase()
        self.server_ip = self._t_tw.sys().get_server_ip()

    # 获取CGteamwork的登录状态
    def getServerIsLogin(self):
        status = self._t_tw.sys().get_is_login()
        return status

    # 初始化传入项目数据
    def getProjectDatabase(self):
        '''
        此函数为初始化对应项目的数据库
        :param project: 传入相应的项目名称
        :return:
        '''
        t_info = self._t_tw.info_module("public", "project")
        filters = [
            ["project.code", "=", 'LIB'],
        ]
        t_info.init_with_filter(filters,a_limit="50000")
        fields = ["project.database"]
        database = t_info.get(fields)[0]['project.database']
        self._database = database
    def getAllAssetType(self):
        '''
        获取资产的信号
        :param pro:
        :return:
        '''
        assetType = []
        # t_tw = tw()
        t_info = self._t_tw.info_module("public", "project")
        filters = [
            ["project.code", "=", 'LIB'],
        ]
        t_info.init_with_filter(filters,a_limit="50000")
        fields = ["project.database"]
        projectDb = t_info.get(fields)[0]['project.database']

        # 获取同一项目(TST,projectDb)下所有的资产类型
        data = self._t_tw.con._send("c_config", "get_all",{"table": projectDb + ".conf_type", "field_array": ["entity_name"]})
        for index, i in enumerate(data):
            assetType.append(i[-1])
        assetTypeList = sorted(list(set(assetType)))
        return assetTypeList
        
    def getAssetInformation(self, field):
        projectDb = self._database
        t_info = self._t_tw.info_module(projectDb, 'asset')

        filters = [
            ["asset.type_name", '=', field["asset.type_name"]],
            ["asset.asset_sign", '=', field["asset.asset_sign"]]
        ]
        t_info.init_with_filter(filters,a_limit="50000")  # 过滤器
        fields = ["asset.asset_resolution", "asset.asset_name", "asset.asset_path", "asset.asset_size",
                  "asset.asset_frame", "asset.asset_time", "asset.asset_sign", "asset.type_name",'asset.asset_type','asset.nuke_import','asset.image_path']  # 查询的内容
        # 作者 模块 任务名称  阶段
        data = t_info.get(fields)
        return data

    def getGlobalInformations(self,string):
        projectDb = self._database
        t_info = self._t_tw.info_module(projectDb, 'asset')
        filters = [
            ["asset.type_name", 'has', string],
            'or',["asset.asset_resolution",'has',string],'or',["asset.asset_path",'has',string],'or',["asset.asset_size",'has',string],'or',
            ["asset.asset_frame",'has',string],'or',["asset.asset_time",'has',string],'or',["asset.asset_sign",'has',string],'or',['asset.asset_type','has',string]
        ]

        t_info.init_with_filter(filters,a_limit="50000")  # 过滤器

        fields = ["asset.asset_resolution", "asset.asset_name", "asset.asset_path",
                  "asset.asset_size", "asset.asset_frame", "asset.asset_time", "asset.asset_sign",
                  "asset.type_name", 'asset.asset_type', 'asset.nuke_import', 'asset.image_path']  # 查询的内容
        # 作者 模块 任务名称  阶段
        data = t_info.get(fields)
        result = self.MessageImage(data)
        return result

    def MessageImage(self,datas):
        list_image =[]
        informations = datas
        for data in informations:
            if not self._os.path.exists(data['asset.image_path']):
                imagePath=self.download_serverImg(data)
                if imagePath[0]['asset.image']=='':
                    continue
                list_image.append(imagePath[0])

        if list_image==[]:
            return informations
        else:
            length_base = len(informations)
            length_image = len(list_image)
            for i  in range(length_base):
                for j in range(length_image):
                    if list_image[j]['id'] == informations[i]['id']:
                        #informations[i]['asset.image_path'] = DOWNLOAD_PATH.split(':')[0] + ':' +list_image[j]['asset.image'][0]
                        informations[i]['asset.image_path'] =list_image[j]['asset.image'][0]
                        print list_image[j]['asset.image'][0]
            return informations

    def createAssetInformation(self, data):
        projectDb = self._database
        t_info = self._t_tw.info_module(projectDb, 'asset')
        t_info.create(data)
    def setAssetImage(self, type_name, asset_path, image_path):

        projectDb = self._database
        t_info = self._t_tw.info_module(projectDb, 'asset')
        filters = [
            ["asset.type_name", '=', type_name],
            ["asset.asset_path", '=', asset_path]
        ]
        t_info.init_with_filter(filters,a_limit="50000")
        t_info.set_image("asset.image", image_path)

    def getAssetImage(self, field):

        projectDb = self._database
        t_info = self._t_tw.info_module(projectDb, 'asset')
        filters = [
            ["asset.type_name", '=', field["asset.type_name"]],
            ["asset.asset_sign", '=', field["asset.asset_sign"]]
        ]
        t_info.init_with_filter(filters,a_limit="50000")
        t_info.download_image("asset.image", False, self.server_ip, DOWNLOAD_PATH)
        return t_info.get_image("asset.image", False)

    def getAssetSign(self, pro):
        '''
        获取资产的信号
        :param pro:
        :return:
        '''
        projectDb = self._database
        t_info = self._t_tw.info_module(projectDb, 'asset')
        filters = [
            ["asset.type_name", '=', pro]
        ]
        t_info.init_with_filter(filters,a_limit="50000")  # 过滤器
        fields = ["asset.asset_sign"]  # 查询的内容
        data = t_info.get(fields)
        return data


    def getSameInformation(self,parm):
        projectDb = self._database
        t_info = self._t_tw.info_module(projectDb, 'asset')
        filters = [
            ["asset.type_name", '=', parm["asset.type_name"]],
            ["asset.asset_sign", '=', parm["asset.asset_sign"]],
            ["asset.asset_name", '=', parm["asset.asset_name"]]
        ]
        t_info.init_with_filter(filters,a_limit="50000")  # 过滤器
        fields = ["asset.asset_name"]
        data = t_info.get(fields)
        if data !=[]:
            return False
        else:
            return True
    def download_serverImg(self,fields):
        projectDb = self._database
        t_info = self._t_tw.info_module(projectDb, 'asset')
        filters = [
            ["asset.type_name", '=', fields["asset.type_name"]],
            ["asset.asset_sign", '=', fields["asset.asset_sign"]],
            ["asset.id",'=',fields["id"]]
        ]
        t_info.init_with_filter(filters,a_limit="50000")
        try:
            datas = t_info.download_image("asset.image", False, self.server_ip, DOWNLOAD_PATH)
        except:
            datas = t_info.download_image("asset.image", False,'', DOWNLOAD_PATH)
        return datas
        #return t_info.get_image("asset.image", False)

    def getServe_image(self,asset_types, label_text):
        '''
        获取如果本地无缩略图图片则从cgteamwork下载
        :param asset_types:
        :param label_text:
        :param id:
        :return:
        '''
        datas_massage = self.getAssetInformation({"asset.type_name": asset_types, "asset.asset_sign": label_text})
        return self.MessageImage(datas_massage)

    # def mergeMessage(self, asset_types, label_text,serve):
    #     '''
    #     融合图片路径和信息
    #     :param asset_types:
    #     :param label_text:
    #     :return:
    #     '''
    #     base_massage = self.getAssetInformation({"asset.type_name": asset_types, "asset.asset_sign": label_text})
    #     if not serve:
    #         return base_massage
    #     image_massage = self.getAssetImage({"asset.type_name": asset_types, "asset.asset_sign": label_text})
    #     length_base_massage = len(base_massage)
    #     length_image_massage = len(image_massage)
    #     for i in range(length_base_massage):
    #         for j in range(length_image_massage):
    #             if  image_massage[j]['id'] == base_massage[i]['id']:
    #                 if image_massage[j]['asset.image'] != '':
    #                     base_massage[i]['asset.image'] = DOWNLOAD_PATH.split(':')[0] + ':' + \
    #                                                      image_massage[j]['asset.image'][0]
    #                 else:
    #                     base_massage[i]['asset.image'] = ''
    #     return base_massage

    # def global_image(self, type):
    #     '''
    #     获取对应类型的图片
    #     :param type:
    #     :return:
    #     '''
    #     projectDb = self._database
    #     t_info = self._t_tw.info_module(projectDb, 'asset')
    #     filters = [
    #         ["asset.type_name", '=', type]
    #     ]
    #     t_info.init_with_filter(filters)
    #     t_info.download_image("asset.image", False, self.server_ip, DOWNLOAD_PATH)
    #     return t_info.get_image("asset.image", False)
    #
    # def global_Message(self, global_list, type):
    #     image_massage = self.global_image(type)
    #     data_list = global_list
    #     length_base_massage = len(data_list)
    #     length_image_massage = len(image_massage)
    #     for i in range(length_base_massage):
    #         for j in range(length_image_massage):
    #             if image_massage[j]['id'] == data_list[i]['id']:
    #                 if image_massage[j]['asset.image'] != '':
    #                     data_list[i]['asset.image'] = DOWNLOAD_PATH.split(':')[0] + ':' + \
    #                                                   image_massage[j]['asset.image'][0]
    #                 else:
    #                     data_list[i]['asset.image'] = ''
    #     return data_list