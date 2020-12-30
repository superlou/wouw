#!/usr/bin/python3
import os
from threading import Timer
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from queue import Queue
from .docx_reader import DocxReader


console = Console()
print = console.print


def analyze_requirements_docx(filename):
    dr = DocxReader(filename, 'r')
    print('')
    print('Updated [color(2)]{}[/color(2)]'.format(dr.filename))
    print('{} requirements parsed'.format(len(dr.requirements)))
    print('Next requirement:', dr.next_requirement_id())


class DebouncedEventHandler(FileSystemEventHandler):
    def __init__(self, watched_file, events):
        super().__init__()
        self.watched_file = watched_file
        self.events = events
        self.debounce_timers = {}

    def on_modified(self, event):
        if event.src_path == self.watched_file:
            self.debounced_enqueue(event.src_path)

    def debounced_enqueue(self, file):
        if file in self.debounce_timers:
            self.debounce_timers[file].cancel()

        timer = Timer(0.2, lambda: self.events.put(file))
        self.debounce_timers[file] = timer
        timer.start()


def main():
    parser = argparse.ArgumentParser(description='Watch docx file for changes')
    parser.add_argument('file')
    args = parser.parse_args()

    events = Queue()

    watched_file = args.file
    event_handler = DebouncedEventHandler(watched_file, events)
    observer = Observer()
    observer.schedule(event_handler,
                      os.path.dirname(watched_file),
                      recursive=True)
    observer.start()

    print('Watching', watched_file)

    try:
        while True:
            event = events.get()
            try:
                analyze_requirements_docx(event)
            except IOError as e:
                # MS Word locks files during its first save
                pass

    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == '__main__':
    main()
