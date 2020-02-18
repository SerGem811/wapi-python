import os
import threading

from webwhatsapi import WhatsAPIDriver

#BASE_DIR = "/app"

IS_HEADLESS = True
#CHROME_CACHE_PATH = BASE_DIR + '/profiles/'
CHROME_DISABLE_GPU = True
CHROME_WINDOW_SIZE = "910,512"


def init_driver(client_id):
    """Initialises a new driver via webwhatsapi module

    @param client_id: ID of user client
    @return webwhatsapi object
    """

    # Create profile directory if it does not exist
    # profile_path = CHROME_CACHE_PATH + str(client_id)
    # if not os.path.exists(profile_path):
    #    os.makedirs(profile_path)

    # Create a whatsapidriver object
    d = WhatsAPIDriver(
     #   executable_path='/app/vendor/firefox/firefox',
        username=client_id,
    #   profile=profile_path,
        client='firefox',
        loadstyles=True,
        headless=IS_HEADLESS
    )
    return d


class RepeatedTimer(object):
    '''
    A generic class that creates a timer of specified interval and calls the
    given function after that interval
    '''

    def __init__(self, interval, function, *args, **kwargs):
        ''' Starts a timer of given interval
        @param self:
        @param interval: Wait time between calls
        @param function: Function object that is needed to be called
        @param *args: args to pass to the called functions
        @param *kwargs: args to pass to the called functions
        '''
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        """Creates a timer and start it"""

        if not self.is_running:
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        """Stop the timer"""
        self._timer.cancel()
        self.is_running = False
