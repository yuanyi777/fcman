import os
import os.path
from pathlib import Path
import shutil
import sys
import binascii

import nointro

IDX_CRC = 0
IDX_NAME = 1
IDX_PLAT = 2
IDX_COLLECTED = 3

game_dir = Path(str(Path.cwd()) + "/../fc")

nointro_list = []

mylist = list()
collected = 0
uncollected = 0

def read_mylist(filename):
    with open(filename, 'r') as fin:
        lines = fin.readlines()
        for ln in lines:
            it = ln.split('|')
            it[IDX_COLLECTED] = '0'
            mylist.append(it)
    mylist.sort(key = lambda x:x[IDX_NAME])

def update_mylist():
    print('Updating mylist according to the nointro dat files...')
    nointro_crc2name = dict()
    for i in range(len(nointro_list)):
        if nointro_list[i] == None:
            continue
        for item in nointro_list[i]:
            crc = item['crc'].upper()
            if crc in nointro_crc2name and len(crc) > 0:
                print('-- Replicated crc ', item)
                continue
            nointro_crc2name[crc] = item['name']
    for mylist_game in mylist:
        if mylist_game[IDX_CRC] == '':
            continue
        if mylist_game[IDX_CRC] not in nointro_crc2name:
            print('-- No such a crc in nointro dat: ' + mylist_game[IDX_NAME] + ' : ' + mylist_game[IDX_CRC])
            mylist_game[IDX_CRC] = ''
            continue
        if mylist_game[IDX_NAME] != nointro_crc2name[mylist_game[IDX_CRC]]:
            print('-- Change game name from ' + mylist_game[IDX_NAME] + ' to ' + nointro_crc2name[mylist_game[IDX_CRC]])
            mylist_game[IDX_NAME] = nointro_crc2name[mylist_game[IDX_CRC]]
    mylist.sort(key = lambda x:x[IDX_NAME])

    # Find the entries that are not in the game list but in nointro dat.
    print('Games not included in my game list:')
    my_crc2name = dict()
    for mylist_game in mylist:
        my_crc2name[mylist_game[IDX_CRC]] = mylist_game[IDX_NAME]
    for i in range(len(nointro_list)):
        if nointro_list[i] == None:
            continue
        for item in nointro_list[i]:
            crc = item['crc'].upper()
            if crc not in my_crc2name:
                print('-- ' + crc + ' : ' + item['name'])

def traverse_game_files(game_dir):
    print('Traverse game files...')
    my_game_dict = {}
    for gi in mylist:
        my_game_dict[gi[IDX_CRC]] = gi
    file_list = os.listdir(game_dir)
    if not os.path.exists('deleted'):
        os.mkdir('deleted')
    for f in file_list:
        fn = os.path.join(game_dir, f)
        if os.path.isdir(fn):
            continue
        if not (f.endswith('.nes') or f.endswith('.fds') or f.endswith('.fcn') or f.endswith('.bin')):
            continue
        postfix = '.nes'
        if f.endswith('.fds'):
            postfix = '.fds'
        elif f.endswith('.fcn'):
            postfix = '.fcn'
        elif f.endswith('.bin'):
            postfix = '.bin'
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
        if crc in my_game_dict:
            my_game_info = my_game_dict[crc]
            if my_game_info[IDX_COLLECTED] == '1':
                print('-- Duplicated rom:', f)
            else:
                my_game_info[IDX_COLLECTED] = '1'
                if my_game_info[IDX_NAME] != '' and my_game_info[IDX_NAME]+postfix != f:
                    new_fn = os.path.join(game_dir, my_game_info[IDX_NAME])+postfix
                    print('-- Renaming: ', f, '-> '+my_game_info[IDX_NAME]+postfix)
                    os.rename(fn, new_fn)
        else: # wrong game file
            print('-- CRC of the game file not in mylist: ', fn, crc, ' (removed)')
            try:
                shutil.move(fn, 'deleted')
            except Exception as e:
                print(e)

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
    return nointro.xml_reader()

def main():
    fc_dat_file = str(list(Path.cwd().glob("Nintendo - Nintendo Entertainment System (Headerless) (*).dat"))[0])
    fds_dat_file = str(list(Path.cwd().glob("Nintendo - Family Computer Disk System (FDS) (*).dat"))[0])
    fcn_dat_file = str(list(Path.cwd().glob("Nintendo - Family Computer Network System (*).dat"))[0])

    file_list = [fc_dat_file, fds_dat_file, fcn_dat_file]

    for dat_file in file_list:
        print('Reading dat file ' + dat_file)
        reader = get_reader(dat_file)
        nointro_list.append(reader.read_dat(dat_file))

    read_mylist(os.path.join(game_dir, 'fc.txt'))
    update_mylist()
    traverse_game_files(os.path.join(game_dir, 'games'))
    regenerate_mylist()

if __name__ == '__main__':
    main()
