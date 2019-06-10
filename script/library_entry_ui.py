  #!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(r"C:/cgteamwork5/bin/base")
sys.path.append(r"C:/cgteamwork5/bin/lib/pyside")




from PySide import QtGui, QtCore
import os
import library_api as cgtw_api
import fllb
import webbrowser
import time
import traceback
from CgtwQss.qss import styleData
import re



def GetaccountNmae():
    import cgtw
    t_tw = cgtw.tw()
    id = t_tw.sys().get_account_id()
    t_info = t_tw.info_module("public",'account')
    filters = [["account.id",'=',id]]
    t_info.init_with_filter(filters)
    data = t_info.get(["account.name"])
    return [data[0]["account.name"]][0]

ADMIN = [u'李丁',u'王天祥']

MOVE_SUFFIX = 'avi,mp4,mov,wmv,mpeg,mkv,flv,f4v,m4v,rmvb,rm,3gp,dat,ts,mts,vob,MOV,MP4'
JPG_SUFFIX = 'jpg,png,gif,fpx,bmp,tiff,pcx,tga,exif,svg,cdr,pcd,dxf,ufo,eps,ai,raw,WMF,webp,tif,exr,hdr,vrmap,vrlmap'

CGTW_TYPE = cgtw_api.CGTW().getAllAssetType()  # 获取CGteamwork客户端资产类型
# CGTW_TYPE = ['Elements','HDRI','Matte','NukeGizmo','PhotoShop']
ASSET_TYPES = ['type', 'Name', 'assetType', 'Path', 'Thumbnail', 'label', 'fileSize', 'frameRange', 'Time',
               'resolution', 'Nuke']

ASSET_TYPE = ''
ASSET_LABEL = ''

LOCAL_CHECK = {}

QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))

ZH_PATTERN = re.compile(u'[\u4e00-\u9fa5]+')  # 判断中文

def _contain_zh(word):
    word = word.decode()
    global ZH_PATTERN
    match = ZH_PATTERN.search(word)
    return match


def _getFilePath(urls):  # 转换正常路径
    if '///' in urls.toString():
        filePath = urls.toString().split('///')[-1]
        return filePath
    elif '///' not in urls.toString():
        filePath = urls.toString()[1:]
        return filePath


class Dialog(QtGui.QDialog):  # 重写关闭函数的类
    def closeEvent(self, event):
        reply = QtGui.QMessageBox(QtGui.QMessageBox.Information, 'program', 'Whether to quit the program?',
                                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No).exec_()
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

## 重载QLable的点击事案件
class Mypic_Label(QtGui.QLabel):
    def __init__(self, pic_path, parent=None):
        super(Mypic_Label, self).__init__(parent)
        self.path = pic_path

    def mousePressEvent(self, e):  ##重载一下鼠标点击事件
        webbrowser.open(self.path)


class MainView(Dialog):
    def __init__(self, parent=None):
        super(MainView, self).__init__(parent)
        self._cgtw = cgtw_api.CGTW()
        self._api = cgtw_api.Fun()
        self.count = 0  # 控制上传的数量
        self.cgtw_list = []  # 控制上传的信息
        self.Pause = True  # 用来控制暂停
        self._mainUI()
        self.createContextMenu()
        self.setWindowFlags(QtCore.Qt.WindowMinMaxButtonsHint)  # 激活最小化、最大化和关闭按钮

    def _mainUI(self):
        self.setGeometry(450, 250, 1200, 600)
        self.setWindowTitle("UPload")

        self.table_view = TableWidget(self)
        self.table_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table_view.setColumnCount(11)
        # self.table_view.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)  # 自适应行宽
        self.table_view.verticalHeader().setDefaultSectionSize(70)  # 设置默认行高
        self.table_view.setHorizontalHeaderLabels(ASSET_TYPES)
        self.table_view.horizontalHeader().setStretchLastSection(True)  # 允许列宽可伸展
        self.table_view.horizontalHeader().setMovable(True)  # 允许表头的拖拽
        self.table_view.verticalHeader().setVisible(True)

        self.progressBar = QtGui.QProgressBar()  # 创建进度条
        self.label = QtGui.QLabel(u'进度条 ：')
        self.upload_lable = QtGui.QLabel()
        upload_button = QtGui.QPushButton("Upload")
        upload_button.setStyleSheet("QPushButton{color:rgb(200, 180, 190);background-color:#212732}"
                                    "QPushButton:checked{color:rgb(0, 160, 230);}")

        down_layout = QtGui.QHBoxLayout()
        down_layout.addWidget(self.label)
        down_layout.addWidget(self.progressBar)
        down_layout.addWidget(self.upload_lable)
        down_layout.addStretch()
        down_layout.addWidget(upload_button)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.table_view)
        main_layout.addLayout(down_layout)
        self.setLayout(main_layout)

        # 链接
        upload_button.clicked.connect(self.upload_cgtw_run)

    # 通过键盘esc终止                                                    这个不知道怎么用的
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.Pause = False

    # 获取文件夹中对应的信息
    def getInformation(self, datas):
        '''
        获取文件夹中对应的信息
        :return:
        '''
        information_dicts = []
        number = 0
        list_data = []
        CheckState = False
        # 判断上传的文件类型，分类上传
        if LOCAL_CHECK['checkBox'].checkState() == QtCore.Qt.CheckState.Checked:
            CheckState = True
        if ASSET_TYPE == 'Matte':
            for path in datas:
                informations = fllb.query(path, unSeqExts=MOVE_SUFFIX, sequencePattern='', getAllSubs=True)
                list_data.append(informations)
        # 上传PSD文件必须上传到“PhotoShop”资产类型下边，并且是和同名图片一并上传。
        elif ASSET_TYPE == 'PhotoShop':
            for path in datas:
                informations = fllb.query(path, exts='psd,PSD', unSeqExts=MOVE_SUFFIX, sequencePattern='',
                                          getAllSubs=True)
                list_data.append(informations)
        # 上传Nuke文件必须上传到“NukeFile”资产类型下边，并且是和同名图片一并上传。
        elif ASSET_TYPE == 'NukeGizmo':
            for path in datas:
                informations = fllb.query(path, exts='nk', unSeqExts=MOVE_SUFFIX, sequencePattern='', getAllSubs=True)
                list_data.append(informations)
        elif ASSET_TYPE == 'Elements':
            for path in datas:
                informations = fllb.query(path, unSeqExts=MOVE_SUFFIX, sequencePattern='#.', getAllSubs=True)
                list_data.append(informations)
        else:
            if CheckState ==True:
                for path in datas:
                    informations = fllb.query(path,unExts='jpg', unSeqExts=MOVE_SUFFIX, sequencePattern='', getAllSubs=True)
                    list_data.append(informations)
            else:
                for path in datas:
                    informations = fllb.query(path,unSeqExts=MOVE_SUFFIX, sequencePattern='', getAllSubs=True)
                    list_data.append(informations)
        # 判断文件是单帧还是序列帧
        for i in list_data:
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(len(i))
            for index, j in enumerate(i):
                if self.Pause == False:  # 终止功能
                    self.progressBar.reset()
                    self.upload_lable.setText('')
                    return []
                if _contain_zh(j['path']):  # 判断是否有中文路径
                    continue
                if j['type'] == 'single':
                    data_dicts = self._api.getSingleInformation(j['path'], j['extension'],CheckState)
                    if data_dicts == 'error':
                        continue
                    data_dicts['asset.asset_path'] = j['path']
                    data_dicts['asset.asset_type'] = j['extension']
                    data_dicts['asset.asset_size'] = j['size']
                    data_dicts['asset.asset_name'] = j['filenames'][0]
                    data_dicts['asset.nuke_import'] = j['full_path']
                    information_dicts.append(data_dicts)
                    self.upload_lable.setText('Loading:' + data_dicts['asset.asset_name'])
                    self.progressBar.setValue(int(index) + 1)
                    app.processEvents()
                    number += 1

                elif j['type'] == 'seq':
                    length = len(j['paths']) / 2
                    data_dicts = self._api.getSeqInformation(j['paths'][length], j['extension'], j['last_frame'],CheckState)
                    data_dicts['asset.asset_path'] = j['paths'][length]
                    data_dicts['asset.asset_type'] = j['extension']
                    data_dicts['asset.asset_size'] = j['size']
                    data_dicts['asset.asset_name'] = j['filenames'][length]
                    data_dicts['asset.asset_frame'] = j['frame_range']
                    data_dicts['asset.nuke_import'] = j['full_path']
                    information_dicts.append(data_dicts)
                    self.upload_lable.setText('Loading:' + data_dicts['asset.asset_name'])
                    self.progressBar.setValue(int(index) + 1)
                    app.processEvents()
                    number += 1
                else:
                    pass
        self.upload_lable.setText('')
        if number > 0:
            self.successfulWindow()
        else:
            pass
        #print information_dicts
        
        return information_dicts

    # 成功弹窗
    def successfulWindow(self):
        load = QtGui.QMessageBox
        msg_load = load(load.Information, "prompt", "Load the success!!", load.Yes)
        msg_load.exec_()
        self.progressBar.reset()


    # 将获取到的信息写入UI页面中
    def listView(self, informations):
        '''
        将获取到的信息写入UI页面中
        :return:
        '''
        global ASSET_TYPE, ASSET_LABEL
        loadPath = informations
        if loadPath != []:
            self.table_view.setRowCount(len(loadPath) + self.count)
            for index, data in enumerate(loadPath):
                upload_information = {}
                item_0 = QtGui.QTableWidgetItem(ASSET_TYPE)
                self.table_view.setItem(self.count, 0, item_0)  # 类型
                item_0.setToolTip(ASSET_TYPE)

                item_1 = QtGui.QTableWidgetItem(data['asset.asset_name'])  # 资产名
                self.table_view.setItem(self.count, 1, item_1)
                item_1.setToolTip(data['asset.asset_name'])

                item_2 = QtGui.QTableWidgetItem(data['asset.asset_type'])  # 资产类型
                self.table_view.setItem(self.count, 2, item_2)
                item_2.setToolTip(data['asset.asset_type'])

                item_3 = QtGui.QTableWidgetItem(data['asset.asset_path'])  # 资产路径
                self.table_view.setItem(self.count, 3, item_3)
                item_3.setToolTip(data['asset.asset_path'])

                ## 判断是图片还是视频
                if data['asset.asset_time'] == '' and data['asset.image'] == '':
                    # 视频错误时，上传的内容
                    self.setVideoPicture(self.count, 4, data['asset.asset_path'], '')
                else:
                    self.setPicture(self.count, 4, data['asset.image'])
                if data['asset.asset_time'] != '' and data['asset.image'] != '':
                    self.setVideoPicture(self.count, 4, data['asset.asset_path'], data['asset.image'])  # 截取图片路径

                item_5 = QtGui.QTableWidgetItem(ASSET_LABEL)  # 标签
                self.table_view.setItem(self.count, 5, item_5)
                item_5.setToolTip(ASSET_LABEL)

                item_6 = QtGui.QTableWidgetItem(data['asset.asset_size'])
                self.table_view.setItem(self.count, 6, item_6)  # 大小
                item_6.setToolTip(data['asset.asset_size'])

                item_7 = QtGui.QTableWidgetItem(data['asset.asset_frame'])
                self.table_view.setItem(self.count, 7, item_7)  # 帧范围
                item_7.setToolTip(data['asset.asset_frame'])
                
                item_8 = QtGui.QTableWidgetItem(data['asset.asset_time'])
                self.table_view.setItem(self.count, 8, item_8)  # 时间
                item_8.setToolTip(data['asset.asset_time'])
                
                item_9 = QtGui.QTableWidgetItem(data['asset.asset_resolution'])
                self.table_view.setItem(self.count, 9, item_9)  # 分辨率
                item_9.setToolTip(data['asset.asset_resolution'])

                item_10 = QtGui.QTableWidgetItem(data['asset.nuke_import'])
                self.table_view.setItem(self.count, 10, item_10)
                item_10.setToolTip(data['asset.nuke_import'])

                upload_information['asset.image_path'] = data['asset.image'].replace('\\', '/')  # 提交cgteamwork 缩略图路径
                upload_information['asset.image'] = data['asset.image'].replace('\\', '/')  # 缩略图
                upload_information['asset.asset_name'] = data['asset.asset_name']  # 资产名称

                upload_information['asset.asset_sign'] = ASSET_LABEL  # 标签
                upload_information['asset.asset_time'] = data['asset.asset_time']  # 视频时长
                upload_information['asset.asset_size'] = data['asset.asset_size']  # 大小

                upload_information['asset.type_name'] = ASSET_TYPE
                upload_information['asset.asset_frame'] = data['asset.asset_frame']  # 帧范围
                upload_information['asset.asset_resolution'] = data['asset.asset_resolution']  # 分辨率
                upload_information['asset.asset_path'] = data['asset.asset_path'].replace('//', '/')  # 资产路径
                upload_information['asset.nuke_import'] = data['asset.nuke_import']  # Nuke导入路径
                upload_information['asset.asset_type'] = data['asset.asset_type']  # 资产类型
                self.cgtw_list.append(upload_information)  # 用来提供上传CGTW
                app.processEvents()

                # print index, data
                self.count += 1
            ASSET_TYPE = ''
            ASSET_LABEL = ''

    # 右键菜单删除
    def createContextMenu(self):
        '''
        创建右键菜单添加删除
        :return:
        '''
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.contextMenu = QtGui.QMenu(self)  # 创建QMenu
        self.actionA = self.contextMenu.addAction('delete')
        self.actionA.triggered.connect(self.DelItem)

    def showContextMenu(self, pos):
        '''显示右键列表'''
        if self.table_view.currentColumn() == 0:
            self.contextMenu.move(self.pos() + pos)  # 菜单显示前，将它移动到鼠标点击的位置
            self.contextMenu.show()

    def getRow(self):
        '''
        得到选择的列数
        :return:
        '''
        self.selectedRow = []
        item = self.table_view.selectedItems()
        for i in item:
            if self.table_view.indexFromItem(i).row() not in self.selectedRow:
                self.selectedRow.append(self.table_view.indexFromItem(i).row())
        return self.selectedRow

    def DelItem(self):
        '''
        删除item
        :return:
        '''
        del_dict = []
        to_del = self.getRow()
        ow = sorted(to_del, reverse=True)
        for index in ow:
            for data in self.cgtw_list:
                if data["asset.asset_path"] != self.table_view.item(index, 3).text():
                    del_dict.append(data)
            self.cgtw_list = del_dict
            del_dict = []
        for i in ow:
            self.table_view.removeRow(i)
            self.count -= 1

    # 设置图片缩略图
    def setPicture(self, row, column, path):
        '''
        :param row:行号
        :param column:列号
        :param path:Png图片路径
        :return:
        '''
        self.tab_pic = Mypic_Label(path)  # 继承修改后的QLable类
        # self.tab_pic.setScaledContents(True)  #自适应宽度
        Path = QtGui.QPixmap(path).scaled(100, 70, QtCore.Qt.KeepAspectRatio)
        self.tab_pic.setPixmap(Path)
        self.table_view.setCellWidget(row, column, self.tab_pic)

    # 设置视频缩略图
    def setVideoPicture(self, row, column, vid_path, pic_path):
        '''
        :param row:行号
        :param column:列号
        :param path:Png图片路径
        :return:
        '''
        self.tab_pic = Mypic_Label(vid_path)  # 继承修改后的QLable类
        if pic_path != '':
            Path = QtGui.QPixmap(pic_path).scaled(100, 70, QtCore.Qt.KeepAspectRatio)
            self.tab_pic.setPixmap(Path)
        else:
            self.tab_pic.setText("Thumbnail is Error！")
        self.table_view.setCellWidget(row, column, self.tab_pic)

    def Upload(self):
        upLoad = self.cgtw_list
        # 此处加入进度条
        if upLoad != []:
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(len(upLoad))
            for index, items in enumerate(upLoad):
                result = self._cgtw.getSameInformation(items)
                if not result:
                    self.progressBar.setValue(int(index) + 1)
                    self.upload_lable.setText('Loading:' + items['asset.asset_name'])
                    app.processEvents()
                    continue
                self._cgtw.createAssetInformation(items)
                self._cgtw.setAssetImage(items['asset.type_name'], items['asset.asset_path'], items['asset.image'])
                self.progressBar.setValue(int(index) + 1)
                self.upload_lable.setText('Loading:' + items['asset.asset_name'])
                app.processEvents()
            return True
        else:
            return False

    # Upload按钮所链接函数
    def upload_cgtw_run(self):
        result = self.Upload()
        if result:
            qtm = QtGui.QMessageBox
            msg_box = qtm(qtm.Warning, "Prompt", "Upload cgteamwork successfully", qtm.Yes)
            msg_box.exec_()
            self.cgtw_list = []
            self.table_view.clearContents()
            self.table_view.setRowCount(0)
            self.progressBar.reset()
            self.upload_lable.setText('')
            self.count = 0
        else:
            qtms = QtGui.QMessageBox
            msg_boxs = qtms(qtms.Warning, "Prompt", "Upload data is incorrect!", qtms.Yes)
            self.progressBar.reset()
            msg_boxs.exec_()

# 基本信息显示面板，支持文件拖拽动作
class TableWidget(QtGui.QTableWidget):
    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)
        self._parent = parent
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        self.information = []
        data = event.mimeData()
        urls = data.urls()
        if (urls and urls[0].scheme() == 'file'):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if (urls and urls[0].scheme() == 'file'):
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if (urls and urls[0].scheme() == 'file'):
            urls[0].setScheme("")
            for uu in urls:
                uu = _getFilePath(uu)
                if not _contain_zh(uu):
                    self.information.append(uu)
        self.runWindow()
        self.runGetInformation()

    def runWindow(self):
        newWindow = TypeWindow(self)
        if newWindow is None:
            newWindow.show()
        else:
            newWindow.exec_()

    def runGetInformation(self):
        if ASSET_LABEL == '':
            qtm = QtGui.QMessageBox
            msg_box = qtm(qtm.Warning, "prompt", "Please fill in the label!！", qtm.Yes)
            msg_box.exec_()
        else:
            datas = self._parent.getInformation(self.information)
            self._parent.listView(datas)

    def returnPath(self):
        return self.information


# 拖拽之后的类型选取提示窗口
class TypeWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        super(TypeWindow, self).__init__(parent)
        self.setStyleSheet(styleData)
        self._main()

    def _main(self):
        self.setGeometry(600, 250, 250, 100)
        self.setWindowTitle('Type Choice')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Window)
        style_label = QtGui.QLabel("Asset Type:")
        self.style_ComboBox = QtGui.QComboBox()
        self.style_ComboBox.addItems(CGTW_TYPE)
        label_label = QtGui.QLabel("Label:")
        self.label_Edit = QtGui.QLineEdit()
        check_button = QtGui.QPushButton("Load")
        check_button.setStyleSheet("QPushButton{color:rgb(200, 180, 190);background-color:#212732}"
                                    "QPushButton:checked{color:rgb(0, 160, 230);}")
        
        check_image = QtGui.QCheckBox(u'添加本地缩略图')
        LOCAL_CHECK['checkBox'] = check_image
        
        layout = QtGui.QHBoxLayout()
        layout.addStretch()
        layout.addWidget(check_image)
        layout.addStretch()
       
        layout1 = QtGui.QHBoxLayout()
        layout1.addWidget(style_label)
        layout1.addWidget(self.style_ComboBox)
        
        layout2 = QtGui.QHBoxLayout()
        layout2.addWidget(label_label)
        layout2.addWidget(self.label_Edit)

        sSearchLayout = QtGui.QVBoxLayout()
        sSearchLayout.addLayout(layout1)
        sSearchLayout.addLayout(layout2)
        sSearchLayout.addLayout(layout)
        sSearchLayout.addWidget(check_button)
        self.setLayout(sSearchLayout)

        check_button.clicked.connect(self.LinkText)

    def LinkText(self):
        global ASSET_TYPE, ASSET_LABEL
        ASSET_TYPE = self.style_ComboBox.currentText()
        ASSET_LABEL = self.label_Edit.text()
        self.close()


if __name__ == '__main__':
    app = QtGui.QApplication.instance()
    if app == None:
        app = QtGui.QApplication(sys.argv)
    if GetaccountNmae() not in ADMIN:
        admin = QtGui.QMessageBox
        msg_box = admin(admin.Warning, u"提示!", u"您没有权限!", admin.Yes)
        msg_box.exec_()
    else:
        lib = MainView()
        lib.setStyleSheet(styleData)
        lib.show()
        app.exec_()