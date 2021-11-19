from .my_random import RandomVariable, choice
from .my_collections import SortedQueue
from .cprint import cprint, BColors


class Event:
    '''
    Events related to ships
        time: timeline value whether event occurs
        id: id of the ship
        next: function to execute
    '''
    def __init__(self, time, id, next):
        self.time = time
        self.id = id
        self.next = next

    def __lt__(self, other):
        return self.time < other.time
    
    def __gt__(self, other):
        return self.time > other.time

    def __eq__(self, other):
        return self.time == other.time


class HarborSimulation:
    '''
    Overloaded Harbor Simulator
    '''
    def __init__(self, n, docks, verbose=True):
        self.SHIP_SIZE_PROB = [0.25, 0.25, 0.5]
        self.SHIP_CARGO_TIME_PARAMS = [(9, 1), (12, 2), (18, 3)]
        self.ARRIVAL_TIME_LAMBDA = 8
        self.TUGBOAT_MOVE_SHIP_TIME_LAMBDA = 2
        self.TUGBOAT_MOVE_TIME_LAMBDA = 15
        self.TUGBOAT_MOVE_SHIP_OUT_TIME_LAMBDA = 1

        self.n = n
        self.time = 0
        self.tugboat_state = 0 # 0 -> docks. 1 -> port
        self.tugboat_blocked = False
        self.s_counter = 0
        self.events = SortedQueue([])
        self.docks = docks
        self.size = [0] * n
        self.arrivals = [0] * n
        self.departures = [0] * n
        self.dock_arrivals = [0] * n
        self.dock_departures = [0] * n

        self.exp = RandomVariable('exp')
        self.normal = RandomVariable('normal')

        self.verbose = verbose

    def _print(self, color, msg):
        '''
        Print if self.verbose=True
        '''
        if (self.verbose):
           cprint(color, msg) 

    def info(self, id, msg):
        '''
        Print info message for ship id
        '''
        self._print(BColors.OKGREEN, f'{id}: {msg}')

    def error(self, id, msg):
        '''
        Print error message
        '''
        self._print(BColors.FAIL, f'{id}: {msg}')

    def time_forward(self, ntime):
        self.time = max(self.time, ntime)

    def do_arrival(self):
        '''
        Generate a new arrival
        '''
        if self.s_counter < self.n:
            self.info(self.s_counter, f'Generating arrival')
            time = self.time + self.exp(self.ARRIVAL_TIME_LAMBDA) * 60
            e = Event(time, self.s_counter, self.enqueue)
            self.s_counter += 1
            self.events.append(e)

        return True

    def enqueue(self, e):
        '''
        Enqueue a new ship that just arrived
        '''
        self.size[e.id] = choice(self.SHIP_SIZE_PROB)
        self.arrivals[e.id] = e.time
        self.time_forward(e.time)
        self.info(e.id, f'Arrive to the port')
        self.events.append(Event(self.time, e.id, self.move))
        
        return self.do_arrival()

    def move(self, e):
        '''
        Move a ship to a dock
        '''
        if (self.docks == 0) or self.tugboat_blocked:
            self.error(e.id, f'Tugboat is blocked or there is no docks')
            return False
        self.update_tugboat_state(1)
        self.info(e.id, f'Moving to a dock')
        self.tugboat_blocked = True
        time = self.time + self.exp(self.TUGBOAT_MOVE_SHIP_TIME_LAMBDA) * 60
        self.events.append(Event(time, e.id, self.dock))

        return True

    def dock(self, e):
        '''
        Start load the cargo of a ship
        '''
        self.info(e.id, f'Loading cargo')
        self.time_forward(e.time)
        self.dock_arrivals[e.id] = e.time
        self.docks -= 1
        self.tugboat_blocked = False
        self.info('TUGBOAT', 'Free')
        time = self.load_time(self.size[e.id])
        self.events.append(Event(time, e.id, self.ready))

        return True

    def ready(self, e):
        '''
        Finish to load the ship cargo
        and wait for it's departure
        '''
        self.info(e.id, f'Loaded')
        self.time_forward(e.time)
        self.events.append(Event(self.time, e.id, self.do_departure))

        return True

    def do_departure(self, e):
        '''
        Move a ship out of the docks
        '''
        if self.tugboat_blocked:
            self.error(e.id, f'Tugboat is bussy, should wait at dock')
            return False
        self.info(e.id, f'Moving back to the port')
        self.update_tugboat_state(0)
        self.docks += 1
        self.tugboat_blocked = True
        time = self.time + self.exp(self.TUGBOAT_MOVE_SHIP_OUT_TIME_LAMBDA) * 60
        self.events.append(Event(time, e.id, self.done))

        return True

    def done(self, e):
        '''
        Finish to service a ship
        '''
        self.info(e.id, f'Leaving the harbor')
        self.tugboat_blocked = False
        self.time_forward(e.time)
        self.departures[e.id] = self.time
        self.dock_departures[e.id] = e.time
        
        return True          

    def update_tugboat_state(self, nstate):
        '''
        Move the tugboat to <pos>.
        1 implies the port,
        0 implies the docks.
        '''
        if nstate != self.tugboat_state:
            location = 'port' if nstate else 'dock'
            self.info('TUGBOAT', f'Moving to {location}')
            self.time += self.exp(self.TUGBOAT_MOVE_TIME_LAMBDA)
        self.tugboat_state = 1 - nstate

    def load_time(self, id):
        '''
        Get the ith size ship load cargo
        '''
        u, o = self.SHIP_CARGO_TIME_PARAMS[id]
        return self.time + self.normal(u, o) * 60

    def time_in_harbor(self, id):
        '''
        Get the time elapsed in harbor for ship id
        '''
        return self.departures[id] - self.arrivals[id]

    def time_in_dock(self, id):
        '''
        Get the time elapsed in dock for ship id
        '''
        return self.dock_departures[id] - self.dock_arrivals[id]

    def loop(self):
        self.do_arrival()

        while self.events:
            for i in range(len(self.events)):
                e = self.events[i]
                if e.next(e):
                    self.events.pop(i)
                    break

        self.info('---', 'FINISHED')

