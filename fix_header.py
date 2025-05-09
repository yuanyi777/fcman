import binascii
import os
from pathlib import Path

import nointro

game_dir = Path(str(Path.cwd()) + "/../fc")

nointro_list = []
nointro_map = {}

def scan_game_files(game_dir):
    print('Scanning games...')
    file_list = os.listdir(game_dir)
    for f in file_list:
        fn = os.path.join(game_dir, f)
        if os.path.isdir(fn):
            continue
        if not f.endswith('.nes'):
            continue
        game_name = os.path.splitext(f)[0]
        nointro_entry = nointro_map[game_name]
        if nointro_entry.get('header') == None:
            continue
        postfix = '.nes'
        #print(fn)
        with open(fn, 'r+b') as game_file:
            header_tag = game_file.read(3)
            game_file.seek(0)
            if header_tag != b'NES':
                print('No header tag NES found in the file. Please fix it manually. - ', f)
                continue
            correct_header = nointro_entry['header'].split()
            correct_header = bytes(list(map(lambda b: int(b, 16), correct_header)))
            game_file.seek(0)
            game_file.write(correct_header)

            game_file.seek(0)
            size = os.path.getsize(fn)
            buf = bytearray(size)
            game_file.readinto(buf)
        crc = '%08X' % (binascii.crc32(buf)&0xffffffff)
        print(crc)

if __name__ == '__main__':
    fc_dat_file = str(list(Path.cwd().glob("Nintendo - Nintendo Entertainment System (Headered) (*).dat"))[0])

    reader = nointro.xml_reader()
    nointro_list = reader.read_dat(fc_dat_file)

    for item in nointro_list:
        nointro_map[item['name']] = item

    scan_game_files(os.path.join(game_dir, 'games'))
    