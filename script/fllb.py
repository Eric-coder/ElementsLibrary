# -*- coding: utf-8 -*-

'''
File Library

A module contains common used functions dealing with files.
    1. Get files by sequence
    2. Copy, move, rename file sequence
'''

__version__ = '0.1.6'
import os
import sys
import re
import math
import glob
import time
import shutil
def getHumanReadableSize(size):
    '''
    Gets a human readable format like this:
        45.89 MB
        32.3 KB
    '''
    size = abs(size)
    if size == 0:
        return '0 B'
    units = ['B','KB','MB','GB','TB','PB','EB','ZB','YB']
    p = math.floor(math.log(size, 2)/10)
    return '%.2f %s' % (size/math.pow(1024,p), units[int(p)])

def secondTimeToString(second):
    '''
    Converts a second time number to a string.
    For instance:
        second: 15694
        return: 1970-01-01 12:21:34
    '''
    t = time.localtime(second)
    return time.strftime('%Y-%m-%d %H:%M', t)

def framesToFrameRange(frames):
    '''
    Gets frame range from frame numbers.
    The frame numbers must be all positive numbers.
    Example:
        frames: [1,2,3,4,60,8,9,10,56,57,58]
        return: '1-4,8-10,56-58,60'
    '''
    temp = []
    
    # Remove duplicated items and sort the list
    frames = sorted(list(set(frames)))
    
    # Collect frames in ranges
    for i in range(len(frames)):
        f = frames[i]
                
        if type(f) == int:
            if f < 0:
                raise Exception('frame number must be a positive number')
        else:
            raise Exception('frame number must be an integer value')
        
        if i == 0:
            temp.append([f])
            continue
        
        else:
            if f-frames[(i-1)] == 1:
                temp[-1].append(f)
            
            else:
                temp.append([f])
    
    # Get frame range string
    lst = []
    for i in temp:
        if len(i) == 1:
            unit = '%s' % i[0]
        else:
            unit = '%s-%s' % (i[0], i[-1])
        lst.append(unit)
    
    return ','.join(lst)

def frameRangeToFrames(frameRange):
    '''
    Gets frame numbers from frame range.
    The frame numbers must be all positive numbers.
    Example:
        frameRange: '1-4,8-10,56-58,60'
        return: [1,2,3,4,60,8,9,10,56,57,58]
    '''
    frameRange = frameRange.strip(',').strip('-').replace(' ','')
    frames = []
    split1 = frameRange.split(',')
    for s in split1:
        split2 = s.split('-')
        
        # Check number value
        if len(split2) <= 2:
            for i in split2:
                if i.isdigit():
                    f = int(i)
                    if f < 0:
                        raise Exception('frame number must be a positive number "%s"' % f)
                else:
                    raise Exception('frame number must be an integer value "%s"' % f)
            
            f1,f2 = int(split2[0]),int(split2[-1])
            if len(split2) == 2:
                if f1 > f2:
                    raise Exception('first frame number must be smaller than the last one "%s"' % s)
        
        else:
            raise Exception('frame range can only contains one or two numbers "%s"' % s)
        
        frames.extend(range(f1, f2+1))
    
    return sorted(list(set(frames)))

def hasWildcard(string, wildcards=('*', '?')):
    '''Check whether there is wildcard in the given string.'''
    has = False
    for w in wildcards:
        if w in string:
            has = True
            break

    return has

def wildcardToRePattern(string):
    '''Turns string with wildcard to a re pattern.'''
    pattern = string.replace('*', '.+').replace('?', '.')
    if pattern != string:  
        return re.compile(pattern)
    else:
        return string

def getAllSubDirs(dir):
    '''Get all sub directories in the dir.'''
    dirs = []
    def getSubs(d):
        if os.path.isdir(d):
            files = os.listdir(d)
            for f in sorted(files):
                fPath = '%s/%s' % (d, f)
                if os.path.isdir(fPath):
                    dirs.append(fPath)
                    getSubs(fPath)
    getSubs(dir)
    return dirs

def getSequencePattern(pattern):
    pattern = pattern.replace(' ','')
    if pattern.count('#') == 1:
        result = pattern.replace('.', '\.').replace('#', '\d+')
    else:
        result = pattern.replace('.', '\.').replace('#', '\d')
    return result

#_framesPattern = re.compile('\.(%\d*d)\.[a-zA-Z0-9]+ (\d+\-\d+[,\d\-]*)$')
_framesPatterns = [
    re.compile('\.(#+)\.[a-zA-Z0-9]+ (\d+\-\d+[,\d\-]*)$'),
    re.compile('\.(%\d*d)\.[a-zA-Z0-9]+ (\d+\-\d+[,\d\-]*)$'),
    re.compile('\.(#+)\.[a-zA-Z0-9]+ (\d+)$'),
    re.compile('\.(%\d*d)\.[a-zA-Z0-9]+ (\d+)$'),
    re.compile('\.(#+)\.[a-zA-Z0-9]+ (\d+[,\d]*)$')
]
def pathToFrames(path):
    '''
    Gets frames from the path string.
    The path string contains two parts:####.exr 1,11,21,31
        path: like /abc/abc00101_lgt_pre_v001.####.tga
        frame range: 101-102,104-300
    Returns a list of frame paths.
    '''
    result = []
    #print path
    for pat in _framesPatterns:
        find = pat.findall(path)
        #print 'file_lib.pathToFrames.find:', find
        if find:
            pad,frameRange = find[-1]
            
            # pad: ###
            if '#' in pad:
                n = len(pad)
            
            # pad: %03d
            else:
                n = int(pad[1:-1])
            
            frames = frameRangeToFrames(frameRange)
            path = ' '.join(path.split(' ')[:-1])
            
            #print 'file_lib.pathToFrames.pad:', pad
            #print 'file_lib.pathToFrames.frameRange:', frameRange
            
            for i in frames:
                f = str(i).rjust(n, '0')
                #print 'file_lib.pathToFrames.path:', path
                p = path.replace(pad, f)
                #print i,n,f,path,'file_lib.pathToFrames.p:', p
                result.append(p)
    
    #print 'file_lib.pathToFrames.result:', result
    if result:
        return result
    else:
        return [path]

_parsePatterns = [
    re.compile('\.(#+)\.[a-zA-Z0-9]+$'),
    re.compile('\.(%\d*d)\.[a-zA-Z0-9]+$')
]
def parseSequence(path):
    '''
    Parses the image sequence path. The path has two formats:
        /abc/abc00101_lgt_pre_v001.####.tga
        /abc/abc00101_lgt_pre_v001.%04d.tga
    Returns the padding length and the padding.
    
    Example:
        path: C:/jinxi/abc.%06d.jpg
        return: 
            {'basename': 'abc',
            'directory': 'C:/jinxi',
            'extension': 'jpg',
            'padding': '%06d',
            'padding_length': 6
            }
    '''
    path = path.replace('\\', '/')
    
    for pat in _parsePatterns:
        find = pat.findall(path)
        #print 'file_lib.getPadding.find:', find
        if find:
            pad = find[-1]
            
            # pad: ###
            if '#' in pad:
                n = len(pad)
            
            # pad: %03d
            else:
                if pad == '%d':
                    n = 1
                else:
                    n = int(pad[1:-1])
            
            token = path.split('.'+pad+'.')
            basename,ext = token
            directory = os.path.dirname(basename)
            basename = os.path.basename(basename)
            
            result = {
                'directory': directory,
                'basename': basename,
                'extension': ext,
                'padding': pad,
                'padding_length': n
            }
            
            return result
    
    result = {
        'directory': os.path.dirname(path),
        'basename': os.path.splitext(os.path.basename(path))[0],
        'extension': os.path.splitext(os.path.basename(path))[-1].replace('.', ''),
        'padding': '',
        'padding_length': 0
    }
    return result

def query(path,unExts='', exts='', unSeqExts='', keyword='', sequence=True, sequencePattern='.#.',
          getAllSubs=False, hideHiddenFiles=True):
    '''
    Gets files by sequence with given argument into a dictionary.
    Directories will not be collected as sequence.
        path: two options:
            root directory: you can use wildcard characters * and ?
            file path with frame range: like this: /abc/abc00101_lgt_pre_v001.####.tga 101-102,104-300
        exts: extensions of the files
            /: folder
            tga: file extension
            if you want to get multi types of files, like tga, jpg and folders,
            you can give multi filters, like this: tga,jpg,/
        unSeqExts: extensions of files which will not be collected as sequence
        keyword: get file whose name contains the given keyword, you can use wildcard characters * and ?
        sequence: collect file sequence or not
            True: abc00101_lgt_pre_v001.####.tga 101-300
            False: abc00101_lgt_pre_v001.0101.tga
        sequencePattern: which type of numbers will be treated as frame sequence
            default: ".#.", it means that this type of file name will be treated as frame sequence
                abc.123.jpg, ffff.0101.tga
        getAllSubs: get all sub files
            True: get all sub files of the dir, 
            False: just get files in dir
        hideHiddenFiles: default is True
    
    The final data is like this:
    [
        {
        'code': 'abc00101_lgt_pre_v001.####.tga',
        'filename': 'abc00101_lgt_pre_v001.####.tga',
        'name': 'abc00101_lgt_pre_v001.####.tga',
        'full_name': 'abc00101_lgt_pre_v001.####.tga 101-102,104-300',
        'path': '/abc/abc00101_lgt_pre_v001.####.tga',
        'full_Path': '/abc/abc00101_lgt_pre_v001.####.tga 101-102,104-300',
        'directory': '/abc',
        'digits': '####',
        'extension': 'tga',
        'frames': [101,102,104,..],
        'missings': [103],
        'frame_range:'101-102,104-300',
        'first_frame': 101,
        'last_frame': 300,
        'filenames': [],
        'paths': [],
        'real_size': 1293393,
        'size': '5.2MB',
        'modified_time': '1970-01-01 12:21',
        'created_time': '1970-01-01 12:45',
        'type': 'seq',
        'basename': 'abc00101_lgt_pre_v001',
        },
    ]
    '''
    if type(exts) == list:
        pass
    else:
        exts = exts.replace(' ','').replace('.','')
        if exts:
            exts = exts.split(',')
        else:
            exts = []
            
    if type(unExts) == list:
        pass
    else:
        unExts = unExts.replace(' ','').replace('.','')
        if unExts:
            unExts = unExts.split(',')
        else:
            unExts = []
            
    if type(unSeqExts) == list:
        pass
    else:
        unSeqExts = unSeqExts.replace(' ','').replace('.','')
        if unSeqExts:
            unSeqExts = unSeqExts.split(',')
        else:
            unSeqExts = []
    
    #if exts.replace('*','') == '':
    #    exts = ''
    
    if type(path) == list:
        ps = path[:]
    else:
        ps = [path]
    
    # check the path to see whether there is wildcard in it
    paths = []
    for p in ps:
        if p:
            p = p.replace('\\', '/')
            if hasWildcard(p):
                paths.extend(glob.glob(p))
            else:
                paths.append(p)
    
    if getAllSubs:
        allSubs = []
        for p in paths:
            allSubs.extend(getAllSubDirs(p))
        
        paths.extend(allSubs)
    
    #print 'file_lib.query.paths:',paths
    
    # turn wildcard to a regular pattern
    keyword = wildcardToRePattern(keyword)
    
    data = {}
    
    pat = getSequencePattern(sequencePattern)
    
    for path in sorted(paths):
        path = path.replace('\\','/')
        
        #print
        #print 'file_lib.query.path: %s' % path
        if os.path.isdir(path):
            temp = sorted(os.listdir(path))
            files = []
            for t in temp:
                p = '%s/%s' % (path, t)
                files.append(p)
        else:
            files = pathToFrames(path)
        
        #print 'file_lib.query.files:',files
        
        for fPath in files:
            #print 'file_lib.query.fPath:',fPath
            #print [os.path.exists(fPath)]
            
            if not os.path.exists(fPath):
                continue
            
            #print 'file_lib.qury.go 1'
            
            f = os.path.basename(fPath)
            path = os.path.dirname(fPath)
            
            if hideHiddenFiles:
                if f.startswith('.') or f.endswith('~') or f == 'Thumbs.db':
                    continue
            
            #print 'keyword: %s' % keyword
            gogo = False
            if type(keyword) in (str, unicode):
                if keyword in f:
                    gogo = True
            else:
                if keyword.findall(f):
                    gogo = True
            
            if gogo:
                try:
                    mtime = os.path.getmtime(fPath)
                except:
                    mtime = 0
                try:
                    ctime = os.path.getctime(fPath)
                except:
                    ctime = 0
                
                # if f is a directory, we take the extension as dir
                if os.path.isdir(fPath):
                    ext = '/'
                else:
                    ext = os.path.splitext(f)[1][1:]
                
                # if filter is empty string, just go forward
                # else, if extension is in the filter, go forward
                go = True
                if exts:
                    if ext not in exts:
                        go = False
                        
                if unExts:
                    if ext in unExts:
                        go = False
                if go:
                    try:
                        size = os.path.getsize(fPath)
                    except:
                        size = 0
                    
                    # do not collect as sequence for directory
                    if os.path.isdir(fPath) == False and sequence and ext not in unSeqExts:
                        # try to find the last group of continuous digits
                        continuousDigitsList = re.findall(pat, f)
                        #print continuousDigitsList
                        try:
                            continuousDigits = re.findall('\d+', continuousDigitsList[-1])[0]
                            fBaseName = f.split(continuousDigitsList[-1])[0]
                        except:
                            continuousDigits = ''
                            fBaseName = os.path.splitext(f)[0]
                        
                        # replace last group of continuousDigits with same number of # as the format
                        digitStyle = len(continuousDigits)*'#'
                        format = f[::-1].replace(continuousDigits[::-1], digitStyle, 1)[::-1]
                    else:
                        fBaseName = os.path.splitext(f)[0]
                        continuousDigits = 0
                        digitStyle = ''
                        format = f
                    
                    key = '%s/%s' % (path, format)
                    if data.has_key(key) == False:
                        data[key] = {
                            'basename': fBaseName,
                            'directory': path, 
                            'digits': digitStyle,
                            'padding': digitStyle,
                            'extension': ext,
                            'frames': [],
                            'missings': [],
                            'missing': '', 
                            'filenames': [],
                            'paths': [],
                            'real_size': size,
                            'modified_times': [],
                            'created_times': [],
                            }
                    else:
                        data[key]['real_size'] += size
                    
                    #data[key]['digits'].append(continuousDigits)
                    if continuousDigits == '':
                        continuousDigits = 0
                    else:
                        continuousDigits = int(continuousDigits)
                    
                    data[key]['frames'].append(continuousDigits)
                    data[key]['filenames'].append(f)
                    data[key]['paths'].append(fPath)
                    data[key]['modified_times'].append(mtime)
                    data[key]['created_times'].append(ctime)
    
    result = []
    for key in sorted(data.keys()):
        # Only get files if getAllSubs is True
        if getAllSubs:
            if data[key]['extension'] == '/':
                continue
        
        baseName = os.path.basename(key)
        if data[key]['digits']:
            data[key]['type'] = 'seq'
            frames = sorted(data[key]['frames'])
            data[key]['frame_range'] = framesToFrameRange(frames)
            data[key]['first_frame'] = frames[0]
            data[key]['last_frame'] = frames[-1]
            data[key]['filename'] = baseName
            data[key]['name'] = baseName
            data[key]['code'] = baseName
            data[key]['full_name'] = '%s %s' % (baseName, data[key]['frame_range'])
            data[key]['path'] = '%s/%s' % (data[key]['directory'], baseName)
            data[key]['full_path'] = '%s %s' % (data[key]['path'], data[key]['frame_range'])
            
            # find missing frames
            for f in range(frames[0], frames[-1]+1):
                if f not in frames:
                    data[key]['missings'].append(f)
            
            temp = [str(i) for i in data[key]['missings']]
            if temp:
                data[key]['missing'] = '%s Missing: %s' % (len(temp), ','.join(temp))
        
        else:
            if data[key]['extension'] == '/':
                data[key]['type'] = 'dir'
            else:
                data[key]['type'] = 'single'
            
            data[key]['frame_range'] = ''
            data[key]['first_frame'] = 1
            data[key]['last_frame'] = 1
            data[key]['name'] = baseName
            data[key]['full_name'] = data[key]['name']
            data[key]['path'] = '%s/%s' % (data[key]['directory'], baseName)
            data[key]['full_path'] = data[key]['path']
        
        data[key]['size'] = getHumanReadableSize(data[key]['real_size'])
        
        latestMTime = sorted(data[key]['modified_times'])[-1]
        data[key]['modified_time'] = secondTimeToString(latestMTime)
        
        latestCTime = sorted(data[key]['created_times'])[-1]
        data[key]['created_time'] = secondTimeToString(latestCTime)
        
        result.append(data[key])
    
    return result

def copy(srcPath, dstFolder):
    '''
    Copies the source path into the target folder.
    The srcPath can be a normal path or a file sequence path:
        /abc/abc00101_lgt_pre_v001.####.tga
    '''
    files = pathToFrames(srcPath)
    for path in files:
        #print 'path:',[path]
        #print 'exists:',[os.path.exists(path)]
        if os.path.exists(path):
            filename = os.path.basename(path)
            dstPath = os.path.join(dstFolder, filename)
            #print '%s -> %s' % (path, dstPath)
            shutil.copyfile(path, dstPath)

def copyFile(srcPath, dstPath):
    shutil.copyfile(srcPath, dstPath)

def rename(srcPath, dstPath):
    os.rename(srcPath, dstPath)

if __name__ == '__main__':
    data = query(*sys.argv[1:])
    for f in data:
        print '%s  %s  %s  %s' % (f['type'], f['size'], f['modified time'], f['full path'])

