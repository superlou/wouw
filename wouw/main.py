#!/usr/bin/python3
import os
from pathlib import Path
import json
from threading import Timer
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from queue import Queue
from .docx_reader import DocxReader
from .project import Project


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
    parser.add_argument('-c', '--config', default='project.json',
                        help='Project configuration JSON file')
    args = parser.parse_args()

    events = Queue()

    try:
        config = json.load(open(args.config))
    except FileNotFoundError:
        print(f'Configuration file "{args.config}" not found')
        return
    except json.JSONDecodeError as e:
        print(f'Parsing error in "{args.config}"\n{e}')
        return

    project = Project(config, Path(args.config).parent)

    observer = Observer()

    for filename in project.filenames:
        event_handler = DebouncedEventHandler(str(filename), events)
        # Watching the directory is required for LibreOffice
        observer.schedule(event_handler,
                          filename.parent,
                          recursive=True)

    observer.start()

    try:
        while True:
            event = events.get()
            print(event)
            try:
                analyze_requirements_docx(event)
            except IOError as e:
                # MS Word locks files sometimes
                pass

    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == '__main__':
    main()
