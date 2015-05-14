import threading


class ServiceWorker(threading.Thread):
    """ Respond to commands from ctl program """

    def __init__(self, service, **kwargs):
        super(ServiceWorker, self).__init__(**kwargs)
        self.service = service

    def run(self):
        self.service.start()


class Worker(threading.Thread):
    """ Another thread for performing work """

    def run(self):
        import time
        while True:
            print('Inside worker ...')
            time.sleep(0.5)
