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

        self.exp = RandomVariable("exp")
        self.normal = RandomVariable("normal")

        self.verbose = verbose

    def time_forward(self, ntime):
        self.time = max(self.time, ntime)

    def print(self, color, msg):
        '''
        Print if self.verbose=True
        '''
        if (self.verbose):
           cprint(color, msg) 

    def do_arrival(self):
        '''
        Generate a new arrival
        '''
        if self.s_counter < self.n:
            self.print(BColors.OKBLUE, f"Generating the arrival time of ship number {self.s_counter}")
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
        self.print(BColors.OKBLUE, f'Ship number {e.id} arrive to the port')
        self.events.append(Event(self.time, e.id, self.move))
        
        return self.do_arrival()

    def move(self, e):
        '''
        Move a ship to a dock
        '''
        if (self.docks == 0) or self.tugboat_blocked:
            self.print(BColors.FAIL, f'Imposible to move ship number {e.id} at this moment')
            return False
        self.update_tugboat_state(1)
        self.print(BColors.OKBLUE, f'Ship number {e.id} is being moved to a dock')
        self.tugboat_blocked = True
        time = self.time + self.exp(self.TUGBOAT_MOVE_SHIP_TIME_LAMBDA) * 60
        self.events.append(Event(time, e.id, self.dock))

        return True

    def dock(self, e):
        '''
        Start load the cargo of a ship
        '''
        self.print(BColors.OKBLUE, f'Ship number {e.id} is loading its cargo')
        self.time_forward(e.time)
        self.docks -= 1
        self.tugboat_blocked = False
        time = self.load_time(self.size[e.id])
        self.events.append(Event(time, e.id, self.ready))

        return True

    def ready(self, e):
        '''
        Finish to load the ship cargo
        and wait for it's departure
        '''
        self.print(BColors.OKBLUE, f'Ship number {e.id} is already loaded')
        self.time_forward(e.time)
        self.events.append(Event(self.time, e.id, self.do_departure))

        return True

    def do_departure(self, e):
        '''
        Move a ship out of the docks
        '''
        if self.tugboat_blocked:
            self.print(BColors.FAIL, f'Tugboat is bussy, ship number {e.id} stay at dock')
            return False
        self.print(BColors.OKBLUE, f'Ship number {e.id} is being moved back to the port')
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
        self.print(BColors.OKBLUE, f'Ship number {e.id} is leaving the harbor')
        self.tugboat_blocked = False
        self.time_forward(e.time)
        self.departures[e.id] = self.time
        
        return True          

    def update_tugboat_state(self, nstate):
        '''
        Move the tugboat to <pos>.
        1 implies the port,
        0 implies the docks.
        '''
        if nstate != self.tugboat_state:
            name = ['docks', 'port'][nstate]
            self.print(BColors.OKBLUE, f'Moving the tugboat to the {name}')
            self.time += self.exp(self.TUGBOAT_MOVE_TIME_LAMBDA)
        self.tugboat_state = 1 - nstate

    def load_time(self, id):
        '''
        Get the ith size ship load cargo
        '''
        u, o = self.SHIP_CARGO_TIME_PARAMS[id]
        return self.time + self.normal(u, o) * 60

    def elapsed(self, id):
        '''
        Get the time elapsed for ship id
        '''
        return self.departures[id] - self.arrivals[id]

    def loop(self):
        self.do_arrival()

        while self.events:
            for i in range(len(self.events)):
                e = self.events[i]
                if e.next(e):
                    self.events.pop(i)
                    break

        self.print(BColors.OKBLUE, 'FINISHED')

