#! /usr/bin/python3
# encoding=utf-8
#import IPython
picfmts=['png','jpg','jpeg','bmp','gif','webp','bmp']
#能力有限，只知道这些图片格式
#你可以在这添加你知道的图片格式
badstr=['static.hdslb.com', 'img/512.png', '4adb9255ada5b97061e610b682b8636764fe50ed.png', 'i2.hdslb.com','/face/']
#在链接中出现以上字符串，那么该链接将被舍弃
#目前包括b站的icon，分界图,作者头像。
#可自行添加
import requests
import os
import time
import sys
import json
import re
def downloader(url,mode='t'):
	req=requests.get(url,headers={'User-Agent': 'Mozilla/7.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'})
	if mode == 'b':
		return req.content
	elif mode == 't': 
		return req.text
	elif mode == 'r':
		return req
	else :
		return None
def getUsername(uid):
	try:
		mediaid=downloader('https://api.bilibili.com/medialist/gateway/base/created?pn=1&ps=1&up_mid={}&is_space=0'.format(uid),'r').json()['data']['list'][0]['id']
		#获取一个收藏夹的ID，一般是默认收藏夹，每个用户都有的收藏夹
		username=downloader('https://api.bilibili.com/medialist/gateway/base/spaceDetail?media_id={}&pn=1&ps=1'.format(mediaid),'r').json()['data']['info']['upper']['name']
		return username
	except :
		print('Warning: Unable to get username')
		return ''

def mkdirs(path):
	try:
		os.makedirs(path)
	except:
		pass

def greatThanMaxpage(pagen, maxpage):
	if (maxpage != 0) and (pagen > maxpage):
		return True
	else :
		return False

def tPages(uid,maxpage):
	'''下载一个用户的所有动态ID，描述，图片链接们'''
	#print(__name__,uid)
	pn=0
	pg=[]
	ps=15
	while True:
		if greatThanMaxpage((pn)*ps,maxpage) == True:
			break
		url='https://api.vc.bilibili.com/link_draw/v1/doc/doc_list?uid={}&page_num={}&page_size={}'.format(uid,pn,ps)
		print('Downloading user dynimic pages',url)
		items=json.loads(downloader(url))['data']['items']
		if items==[]:
			break
		else:
			for i in items:
				pic=[]
				for j in i['pictures']:
					pic.append(j['img_src'])
				pg.append([i['doc_id'],i['description'],pic])
			pn+=1
	return pg

def fDownloader(url,path='.'):
	'''下载文件，保存至路径path'''
	print('Downloading {}...'.format(url),end='')
	mkdirs(path)
	if os.path.split(path)[1]!='':
		path=path+os.sep
	fpath=path+os.path.split(url)[1]
	if os.path.exists(fpath) == True:
		print('existed, skip')
		return
	with open(fpath,'wb') as fl:
		pic=downloader(url,mode='b')
		fl.write(pic)
		print('Succeeded')

def tAPageDownload(uid,i,username):
	'''下载一个动态的动态的图片与描述'''
	#i[0] 动态ID i[1] 动态文字 i[2] 图片链接
	#path='UID'+str(uid)+os.sep+'T'+i[0]+os.sep
	if username != '':
		path='UID{}.{}{}T{}{}'.format(uid,username,os.sep,i[0],os.sep)
	else:
		path='UID{}{}T{}{}'.format(uid,os.sep,i[0],os.sep)
	print('Download to',path)
	for j in i[2]:
		#print('Downloading picture:',j)
		fDownloader(j,path)
	with open(path+'Description','wt') as f:
		f.write(i[1])

def textInStr(texts,string):
	if texts==[]:
		return True
	for i in texts:
		if i in string:
			return True

def tDownloader(uid,maxpage=0,texts=[]):
	'''下载有关键字之一的所有动态'''
	#动态页数 0-无限
	#链接https://api.vc.bilibili.com/link_draw/v1/doc/doc_list?uid=用户ID&page_num=页数
	username=getUsername(uid)
	page=tPages(uid,maxpage)
	times=0
	for i in page:
		if (times<maxpage or maxpage==0)and textInStr(texts,i[1]):
			tAPageDownload(uid,i,username)
			times+=1
		else:
			break

def cvTags(j):
	try :
		j['tags']
	except KeyError:
		return []
	else:
		tags=[]
		for i in j['tags']:
			tags.append(i['name'])
		#IPython.embed()
		return tags

def cvPages(uid,maxpage):
	pn=1
	pg=[]
	ps=15
	while True:
		if greatThanMaxpage((pn-1)*ps, maxpage) == True :
			break
		url='https://api.bilibili.com/x/space/article?mid={}&pn={}&ps={}'.format(uid,pn,ps)
		print('Downloading user article pages:',url)
		js=json.loads(downloader(url))
		try:
			articles=json.loads(downloader(url))['data']['articles']
		except:
			break
		if articles==[]:
			break
		for i in articles:
			pg.append([i['id'],i['title'],cvTags(i),i['summary']])
		pn+=1
	return pg

def textInView(text,string):
	return textInStr(text,string)

def textInTag(text,tag):
	string=''
	#print(tag)
	#IPython.embed()
	for i in tag:
		string=string+i
	#IPython.embed()
	return textInStr(text,string)

def rmTheSameUrl(urls):
	#print(urls)
	ret=[]
	for i in urls:
		if i not in ret:
			ret.append(i)
	#print(ret)
	return ret

def isPic(path,fmtlist):
	for i in fmtlist:
		if '.{}'.format(i) in path:
			return True
	return False

def findPic(strings):
	pic=[]
	for i in strings:
		if True == isPic(i,picfmts):
			#能力有限，只知道这些图片格式
			pic.append(i)
	return pic
def inStr(string, arg):
	#确认string里有数组arg中的任意一个内容
	for i in arg:
		if i in string:
			return True
	return False

def rmDivAndIcon(picurl):
	'''
	分隔：4adb9255ada5b97061e610b682b8636764fe50ed.png
	其他图片：i2.hdslb.com
	B站的logo：4adb9255ada5b97061e610b682b8636764fe50ed.png
	'''
	pic=[]
	for i in picurl:
		if inStr(i, badstr) == False:
			#把与专栏无关以及专栏内置图片元素过滤
			pic.append(i)
	return pic
			
def webfileFilter(txt):
	'''过滤网页文件，返回图片的地址'''
	strings=re.findall(r'"(.*?)"',txt)
	pic=findPic(strings)
	pic=rmTheSameUrl(pic)
	pic=rmDivAndIcon(pic)
	return pic

def cvDownloader(uid,maxpage=0,texts=[]):
	'''传入用户ID与必有关键字'''
	#专栏页数 1-无限
	#链接https://api.bilibili.com/x/space/article?mid=用户ID&pn=页数
	username=getUsername(uid)
	pn=1
	pg=cvPages(uid,maxpage)
	#pg[0] 专栏ID pg[1] 专栏标题 pg[2] 专栏的标签们 pg[3] 专栏的预览
	for i in pg:
		#IPython.embed()
		if (pn<=maxpage or maxpage==0) and (textInTag(texts,i[2]) or textInView(texts,i[3]) or textInStr(texts,i[1])):
			url='https://www.bilibili.com/read/cv{}'.format(i[0])
			print('Downloading the article:',url,'...',end='')
			urltext=downloader(url)
			print('Succeeded')
			picurl=webfileFilter(urltext)
			pn+=1
			for j in picurl:
				if 'http' not in j:
					j='http:'+j
				if username != '':
					fDownloader(j,'UID{}.{}{}cv{}{}'.format(uid,username,os.sep,i[0],os.sep))
				else:
					fDownloader(j,'UID{}{}cv{}{}'.format(uid,os.sep,i[0],os.sep))
def argInput():
	arg=[]
	string=''
	choice=input('启动搜索模式？[y/n]\n')
	if 'y' in choice:
		while True:
			string=input('不输入内容，单按下回车就会停止输入：\n')
			if string=='':
				break
			else:
				arg.append(string)
	return arg
def modChoice():
	mod=input('选择下载模式：\n\t专栏：c\t动态：t\t帮助：h\n')
	if 'c' in mod:
		uid=int(input('输入作者的UID：\n'))
		maxpage=int(input('下载的最大页数（输入0表示即为最大）：\n'))
		text=argInput()
		cvDownloader(uid,maxpage,text)
	elif 't' in mod:
		uid=int(input('输入作者的UID：\n'))
		maxpage=int(input('下载的最大页数（输入0表示即为最大）：\n'))
		text=argInput()
		tDownloader(uid,maxpage,text)
		input('按下回车键退出')
	elif 'h' in mod:
		usage_friendly()
	else:
		usage_friendly()
def usage_friendly():
	print('本程序由Bilibili的用户Afeather制作,使用方法如下')
	print('使用方法: {} 运行模式(c/v/h) 用户UID 最大下载页数 字符串1 字符串2 字符串3 ......'.format(sys.argv[0]))
	print('			 或直接双击运行程序，按提示正确输入')
	print('最大下载页数，为最大，则输入0。字符串可以不指定')
	print('字符串1：专栏或相簿描述必须有字符串1')
	print('字符串2：专栏或相簿描述必须有字符串2')
	print('字符串3：专栏或相簿描述必须有字符串3')
	print('你可以在我个人主页反馈BUG或提出建议)')
	print('Bilibili个人主页链接: https://space.bilibili.com/87132208')
	
def usage_programmer():
	'''
		这是防喷子说我身为程序员做命令行程序居然不用英语的
		第一我不是程序员，就是个高中生而已
		第二你觉得一般用户喜欢到处是英文的命令行吗
	'''
	print('Made by Afeather from Bilibili.')
	print('Usage: {} run_mode UID maxpage arg1 arg2 arg3 ...'.format(sys.argv[0]))
	print('You can feed back on my personal homepage')
	print('Homepage: https://space.bilibili.com/87132208')
	
if __name__ == "__main__":
	if len(sys.argv)==1:
		modChoice()
	else :
		'''mod uid maxpage arg...'''
		uid=0
		maxpage=0
		if len(sys.argv)<3:
			usage_programmer()
			exit()
		try:
			uid=int(sys.argv[2])
			maxpage=int(sys.argv[3])
		except ValueError:
			usage_programmer()
			exit()
		else:
			text=[]
			for i in sys.argv[4:]: 
				text.append(i)
			if 'c' in sys.argv[1]:
				cvDownloader(uid,maxpage,text)
			elif 't' in sys.argv[1]:
				tDownloader(uid,maxpage,text)
			else:
				usage_programmer()
	exit()

