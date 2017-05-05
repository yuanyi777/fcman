import sys
import os
import binascii

fn = sys.argv[1]
with open(fn, 'rb') as fin:
	size = os.path.getsize(fn)
	buf_all = bytearray(size)
	fin.readinto(buf_all)

	fin.seek(0)
	header = fin.read(3).decode('utf-8')
	fin.seek(0)
	if header == 'NES' or header == 'FDS':
		fin.seek(16)
		size -= 16
	buf_raw = bytearray(size)
	fin.readinto(buf_raw)
crc_all = '%08X' % (binascii.crc32(buf_all)&0xffffffff)
crc_raw = '%08X' % (binascii.crc32(buf_raw)&0xffffffff)
print('crc with header: ' + crc_all)
print('crc for raw game data: ' + crc_raw)

