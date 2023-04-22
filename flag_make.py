import sys

if len(sys.argv) == 2:
    box = lambda char: chr(ord(char.upper()) + 0x1F1A5)
    print(''.join([box(char) for char in sys.argv[1].replace('-', '')]))
else:
    box = lambda char: chr(ord(char.upper()) + 0xE0020)
    print(chr(0x1F3F4) + ''.join([box(char) for char in sys.argv[1].replace('-', '')]) + chr(0xE007F))
