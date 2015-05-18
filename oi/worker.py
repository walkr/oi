import threading


class Worker(threading.Thread):
    """ General purpose worker """

    def __init__(self, program=None, **kwargs):
        super(Worker, self).__init__(**kwargs)
        self.program = program

    def run(self):
        raise Exception('Implement this method in your subclass')


class ServiceWorker(Worker):
    """ Respond to commands from ctl program """

    def __init__(self, service, **kwargs):
        super(ServiceWorker, self).__init__(**kwargs)
        self.service = service

    def run(self):
        self.service.start()
