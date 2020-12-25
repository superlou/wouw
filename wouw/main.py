#!/usr/bin/python3
import os
import time
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich import print
from .docx_reader import DocxReader


class EventHandler(FileSystemEventHandler):
    def __init__(self, watched_file):
        super().__init__()
        self.watched_file = watched_file

    def on_modified(self, event):
        if event.src_path == self.watched_file:
            dr = DocxReader(event.src_path, 'r')
            print('')
            print('Updated', dr.filename)
            print('{} requirements parsed'.format(len(dr.requirements)))
            print('Next requirement:', dr.next_requirement_id())


def main():
    parser = argparse.ArgumentParser(description='Watch docx file for changes')
    parser.add_argument('file')
    args = parser.parse_args()

    watched_file = args.file
    event_handler = EventHandler(watched_file)
    observer = Observer()
    observer.schedule(event_handler,
                      os.path.dirname(watched_file),
                      recursive=True)
    observer.start()

    print('Watching', watched_file)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == '__main__':
    main()
