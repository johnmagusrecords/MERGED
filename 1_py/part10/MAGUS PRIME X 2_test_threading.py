import threading


def print_message():
    print("Thread is running!")


thread = threading.Thread(target=print_message)
thread.start()
thread.join()
