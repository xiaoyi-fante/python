import argparse
import stat
from pathlib import Path
from datetime import datetime

parser = argparse.ArgumentParser(prog='ls',description='list directory contents',add_help=False)
parser.add_argument('path',nargs='?',default='.',help="directory")
parser.add_argument('-l',action='store_true',help="show all files, do not ignore entries starting with .")
parser.add_argument('-h','--human-readable',action='store_true',help="with -l, print sizes in human readable format")
parser.add_argument('-a', '--all', action='store_true', help='show all files, do not ignore entries start with .')
def listdir(path, all=False, detail=False, human=False):
    def _gethuman(size:int):
        units=' KMGTP'
        depth = 0
        while size>=1000:
            size=size//1000
            depth+=1
        return '{}{}'.format(size,units[depth])

    def _listdir(path, all=False, detail=False, human=False):
        p = Path(path)
        for i in p.iterdir():
            if not all and i.name.startswith('.'):
                continue
            if not detail:
                yield (i.name,)
            else:
                st = i.stat()
                mode = stat.filemode((st.st_mode))
                atime = datetime.fromtimestamp(st.st_atime).strftime('%Y-%m-%d %H:%M:%S')
                size = str(st.st_size) if not human else _gethuman(st.st_size)
                yield (mode, st.st_nlink, st.st_uid, st.st_gid, size, atime, i.name)
    yield from sorted(_listdir(path, all, detail, human), key=lambda x:x[len(x)-1])

if __name__=='__main__':
    args=parser.parse_args()
    print(args)
    parser.print_help()
    files = listdir(args.path, args.all, args.l, args.human_readable)
    print(list(files))