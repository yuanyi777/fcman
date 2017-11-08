import os
import os.path
import shutil
import sys
import binascii

import nointro

IDX_CRC = 0
IDX_NAME = 1
IDX_PLAT = 2
IDX_COLLECTED = 3

working_dir = '/Users/yiyuan/Desktop/emu/fc'

nointro_list = [None, None]

mylist = list()
collected = 0
uncollected = 0

def read_mylist(filename):
	global mylist
	with open(filename, 'r') as fin:
		lines = fin.readlines()
		for ln in lines:
			it = ln.split('|')
			it[IDX_COLLECTED] = '0'
			mylist.append(it)
	mylist.sort(key = lambda x:x[IDX_NAME])

def update_mylist():
	print('Updating mylist according to the nointro dat files...')
	name_dict = dict()
	for i in range(len(nointro_list)):
		if nointro_list[i] == None:
			continue
		for item in nointro_list[i]:
			if item['crc'] in name_dict:
				print('-- Replicated crc ', item)
				continue
			name_dict[item['crc']] = item['name']
	for game in mylist:
		if game[IDX_CRC] == '':
			continue
		if game[IDX_CRC] not in name_dict:
			print('-- No such a crc in nointro dat: ' + game[IDX_NAME] + ' : ' + game[IDX_CRC])
			game[IDX_CRC] = ''
			game[IDX_COLLECTED] = '0'
			continue
		if game[IDX_NAME] != name_dict[game[IDX_CRC]]:
			print('-- Change game name from ' + game[IDX_NAME] + ' to ' + name_dict[game[IDX_CRC]])
			game[IDX_NAME] = name_dict[game[IDX_CRC]]
	mylist.sort(key = lambda x:x[IDX_NAME])

	# Find the entries that are not in the game list but in nointro dat.
	print('Games not included in my game list:')
	game_dict = dict()
	for game in mylist:
		game_dict[game[IDX_CRC]] = game[IDX_NAME]
	for i in range(len(nointro_list)):
		if nointro_list[i] == None:
			continue
		for item in nointro_list[i]:
			if item['crc'] not in game_dict:
				print('-- ' + item['crc'] + ' : ' + item['name'])

def traverse_game_files(game_dir):
	print('Traverse game files...')
	game_dict = {}
	for gi in mylist:
		game_dict[gi[IDX_CRC]] = gi
	file_list = os.listdir(game_dir)
	if not os.path.exists('deleted'):
		recycle = os.mkdir('deleted')
	for f in file_list:
		fn = os.path.join(game_dir, f)
		if os.path.isdir(fn):
			continue
		if not (f.endswith('.nes') or f.endswith('.fds')):
			continue
		postfix = '.nes'
		if f.endswith('.fds'):
			postfix = '.fds'
		#print(fn)
		with open(fn, 'rb') as game_file:
			size = os.path.getsize(fn)
			header = game_file.read(3)
			game_file.seek(0)
			if header == b'NES' or header == b'FDS':
				game_file.seek(16)
				size -= 16
			buf = bytearray(size)
			game_file.readinto(buf)
		crc = '%08X' % (binascii.crc32(buf)&0xffffffff)
		#print(crc)
		if crc in game_dict:
			game_info = game_dict[crc]
			if game_info[IDX_COLLECTED] == '1':
				print('-- Duplicated rom:', f)
			else:
				game_info[IDX_COLLECTED] = '1'
				if game_info[IDX_NAME] != '' and game_info[IDX_NAME]+postfix != f:
					new_fn = os.path.join(game_dir, game_info[IDX_NAME])+postfix
					print('-- Renaming: ', f, '-> '+game_info[IDX_NAME]+postfix)
					os.rename(fn, new_fn)
		else: # wrong game file
			print('-- CRC of the game file not in mylist: ', fn, crc, ' (removed)')
			shutil.move(fn, 'deleted')

def regenerate_mylist():
	global collected
	global uncollected
	al_file = open('fc.txt', 'w')
	cl_file = open('fc_col.txt', 'w')
	ul_file = open('fc_unc.txt', 'w')
	for g in mylist:
		item = '|'.join(g) + '\n'
		al_file.write(item)
		if g[IDX_COLLECTED] == '1':
			collected += 1
			cl_file.write(item)
		else:
			uncollected += 1
			ul_file.write(item)
	al_file.close()
	cl_file.close()
	ul_file.close()
	print('The number of collected in mylist: ' + str(collected))
	print('The number of non collected in mylist: ' + str(uncollected))

def get_reader(filename):
	if filename.startswith('Nintendo - Nintendo'):
		return nointro.xml_reader()
	elif filename.startswith('Nintendo - Family'):
		return nointro.xml_reader()

def main():
	global nointro_list
	if len(sys.argv) > 1:
		reader = get_reader(sys.argv[1])
		nointro_list[0] = reader.read_dat(sys.argv[1])
		if len(sys.argv) > 2:
			reader = get_reader(sys.argv[2])
			nointro_list[1] = reader.read_dat(sys.argv[2])
	read_mylist(os.path.join(working_dir, 'fc.txt'))
	if nointro_list[0] != None:
		update_mylist()
	traverse_game_files(os.path.join(working_dir, 'games'))
	regenerate_mylist()

if __name__ == '__main__':
	main()

