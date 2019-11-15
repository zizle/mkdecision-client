# _*_ coding:utf-8 _*_
# __Author__： zizle
""" Excel 文件监测系统 """
from watchdog.observers import Observer
from watchdog.events import *
import time


class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if event.is_directory:
            # print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
            pass
        else:
            # print("file moved from {0} to {1}".format(event.src_path,event.dest_path))
            pass

    def on_created(self, event):
        if event.is_directory:
            # print("directory created:{0}".format(event.src_path))
            pass
        else:
            # print("file created:{0}".format(event.src_path))
            pass

    def on_deleted(self, event):
        if event.is_directory:
            # print("directory deleted:{0}".format(event.src_path))
            pass
        else:
            # print("file deleted:{0}".format(event.src_path))
            pass

    def on_modified(self, event):
        if event.is_directory:
            # print("directory modified:{0}".format(event.src_path))
            pass
        else:
            print("file modified:{0}".format(event.src_path), event.__dict__)

            # import os
            # import time
            # pos = 0
            # while True:
            #     time.sleep(1)
            #     fd = open(event.src_path)
            #     if pos != 0:
            #         fd.seek(pos, 0)
            #     while True:
            #         line = fd.readline()
            #         if line.strip():
            #             print(line.strip())
            #         pos = pos + len(line)
            #         if not line.strip():
            #             break
            #     fd.close()


if __name__ == "__main__":
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler,"e:/files",True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()