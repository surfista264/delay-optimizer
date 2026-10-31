import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
    def __init__(self, script_to_run):
        self.script_to_run = script_to_run
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        print(f"\n[HOT RELOAD] A iniciar {self.script_to_run}...")
        self.process = subprocess.Popen([sys.executable, self.script_to_run])

    def on_modified(self, event):
        # Reinicia apenas se for um ficheiro Python (.py) e não for este próprio script
        if event.src_path.endswith('.py') and not event.src_path.endswith('run.py'):
            print(f"\n[HOT RELOAD] Alteração detetada! A reiniciar...")
            self.start_process()

if __name__ == "__main__":
    script_alvo = "main.py"
    
    event_handler = RestartHandler(script_alvo)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    
    print(f"[HOT RELOAD] A vigiar o projeto. Podes alterar o código e gravar (Ctrl + S)!")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()