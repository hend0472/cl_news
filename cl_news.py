import time
import urllib
import requests
import os.path as path
import bs4
import logging
import sys
from tqdm import *
import os
import textwrap

global news_list
global news_list_num

title_pic = '''\

 ██████╗██╗             ███╗   ██╗███████╗██╗    ██╗███████╗
██╔════╝██║             ████╗  ██║██╔════╝██║    ██║██╔════╝
██║     ██║             ██╔██╗ ██║█████╗  ██║ █╗ ██║███████╗
██║     ██║             ██║╚██╗██║██╔══╝  ██║███╗██║╚════██║
╚██████╗███████╗███████╗██║ ╚████║███████╗╚███╔███╔╝███████║
 ╚═════╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝ ╚══════╝
                                                            
'''
print('Loading...')

if os.path.isfile('cl_news.log'):
	os.remove('cl_news.log')

logging.basicConfig(level=logging.INFO, filename='cl_news.log', filemode='a+',
					format='%(asctime)-15s %(levelname) -8s %(message)s')

logging.info('COMMAND LINE NEWS SESSION STARTED')
logging.getLogger('requests').setLevel(logging.WARNING)


main_site = 'https://finance.yahoo.com/news/?bypass=true'
linklist = []
news_list = {}
news_list_num = {}


def pause():
	time.sleep(.01)


def clear_screen():
	if sys.platform == 'win32':
		os.system('cls')
	else:
		os.system('clear')


def check_terminal_size():
	global sizex
	global sizey
	if sys.platform == 'win32':
		import struct
		from ctypes import windll, create_string_buffer
		h = windll.kernel32.GetStdHandle(-12)
		csbi = create_string_buffer(22)
		res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
		if res:
			(bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
			sizex = right - left + 1
			sizey = bottom - top + 1

	else:
		sizex, sizey = os.popen('stty size', 'r').read().split()
	# print(sizex)
	# print(sizey)


def check_main_page():
	try:
		pause()
		res = requests.get(main_site)
		res.raise_for_status()
		soup = bs4.BeautifulSoup(res.text, 'html.parser')
		data = soup.find_all('div', attrs={'class': 'Bfc'})
		clear_screen()
		print(title_pic)
		print('Checking the Yahoo Finance News Page...')
		pause()
		for div in data:
			links = div.findAll('a')
			for a in links:
				link = a['href']
				if 'finance.yahoo.com/q?s=' not in link:
					if link not in linklist:
						linklist.append(link)
		pause()
		check_links()
	except Exception as e:
		logging.error('Error with main page function: ' + str(e))


def check_links():
	pause()
	print('Pulling story for ' + str(len(linklist)) + ' new stories...')
	pause()
	counter = 1
	for i in tqdm(linklist):
		try:
			if i.startswith('http://finance.yahoo.com'):
				articletext = ''
				headline = ''
				res = requests.get(i)
				res.raise_for_status()
				soup = bs4.BeautifulSoup(res.text, 'html.parser')
				for tag in soup.find_all('h1', attrs={'class': 'Lh(36px) Fz(25px)--sm Fz(32px) Mb(17px)--sm Mb(20px) Mb(30px)--lg Ff($ff-primary) Lts($lspacing-md) Fw($fweight) Fsm($fsmoothing) Fsmw($fsmoothing) Fsmm($fsmoothing) Wow(bw)'}):
					headline += str(tag.contents[0])
				for tag in soup.find_all('p', attrs={'class': 'canvas-atom canvas-text Mb(1.0em) Mb(0)--sm Mt(0.8em)--sm'}):
					articletext += str(tag.contents[0])
				articletext += '\n\n\n\n\n-----' + str(i)
				cleantext = bs4.BeautifulSoup(articletext, 'html.parser').text
				articletext = cleantext
				news_list[headline] = articletext
				news_list_num[str(counter)] = headline
				counter += 1
		except Exception as e:
			linklist.remove(i)
			pause()
			logging.error('Error with: ' + str(i) + ' ' + str(e))


def run():
	clear_screen()
	print('\nHere are the news stories.\n')
	pause()
	for key, value in news_list_num.items():
		print(str(key) + ': ' + str(value))
	print('\nR. Reload News Stories.')
	print('\nQ. Quit')
	pause()
	selection = str(input('\nWhich story would you like to read?: '))
	if selection.lower() == 'r':
		check_main_page()
	elif selection.lower() == 'q':
		sys.exit()
	elif selection not in news_list_num.keys():
		print('Bad Selection. Reloading articles...')
		time.sleep(1)
		run()
	elif selection in news_list_num.keys():
		clear_screen()
		check_terminal_size()
		print('\n')
		print(news_list_num[selection])
		print('\n')
		article = news_list[news_list_num[selection]].split('-----')
		print(textwrap.fill(article[0],sizex))
		print('\n\n' + article[1])
		done_reading = input('\nPress Enter when done or Q to quit: ')
		if done_reading.lower() == 'q':
			sys.exit()
		else:
			run()

if __name__ == '__main__':
	check_main_page()
	run()
