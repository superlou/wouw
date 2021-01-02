#!/usr/bin/python3
from pathlib import Path
import json
from threading import Timer
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from queue import Queue
from .project import Project


console = Console()
print = console.print


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


def create_observer(project, events_queue):
    observer = Observer()

    for path in project.paths:
        event_handler = DebouncedEventHandler(str(path), events_queue)
        # Watching the directory is required for LibreOffice
        observer.schedule(event_handler,
                          path.parent,
                          recursive=True)

    observer.start()
    return observer


def print_document_status(document, verb):
    print('')
    print(f'{verb} [color(2)]{document.path}[/color(2)]')
    print(f'{len(document.requirements)} requirements parsed')
    print('Next requirement:', document.next_requirement_id())

    for warning in document.warnings:
        print(f'[color(1)]{warning}[/color(1)]')


def main():
    parser = argparse.ArgumentParser(description='Watch docx file for changes')
    parser.add_argument('-c', '--config', default='project.json',
                        help='Project configuration JSON file')
    parser.add_argument('-w', '--watch', action='store_true',
                        help='Watch project files for changes')
    args = parser.parse_args()

    try:
        config = json.load(open(args.config))
    except FileNotFoundError:
        print(f'Configuration file "{args.config}" not found')
        return
    except json.JSONDecodeError as e:
        print(f'Parsing error in "{args.config}"\n{e}')
        return

    project = Project(config, Path(args.config).parent)

    for document in project.documents:
        verb = 'Watching' if args.watch else 'Scanned'
        print_document_status(document, verb)

    if not args.watch:
        return

    events = Queue()
    observer = create_observer(project, events)

    try:
        while True:
            event = events.get()
            try:
                document = project.get_document_by_path(Path(event))
                document.refresh()
                print_document_status(document, 'Updated')
            except IOError:
                # MS Word locks files sometimes
                pass

    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == '__main__':
    main()
