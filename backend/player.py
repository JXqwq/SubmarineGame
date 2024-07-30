import socket
import json
import random

# Player Status Sent to Server:
# {
#    attack: (x, y)
#    move: str
#    hps: dict
#    dead: T/F
#
# }
class player:
    def __init__(self, port):
        self.hps = {'s':1, 'c':2, 'w':3}
        self.positions = {'s':None, 'c':None, 'w':None}
        self.enemy_attack = None
        self.enemy_move = None
        self.enemy_hps = {'s':1, 'c':2, 'w':3}
        self.dead = False
        self.port = port

    def connect(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(("localhost", self.port))
            return client
        except Exception as e:
            print("Connection to Server Failed:(")
            raise e


    def receive_data(self, another_player, client):
        
        self.enemy_attack = another_player["attack"]
        self.enemy_move =  another_player["move"]
        self.enemy_hps = another_player["hps"]

        if another_player["dead"] == True:
            return "Win"
            
        if self.enemy_attack != None:
            self._handle_attack(self.enemy_attack)

        if self.hps['s'] == 0 and self.hps['c'] == 0 and self.hps['w'] == 0:
            self.dead = True
            if client != None:
                client.sendall(json.dumps(self._create_data(None,None,{'s':0, 'c':0, 'w':0}, True)).encode('utf-8'))
            return "Lose"
    
    def send_data(self, client, move:str=None, attack:tuple=None):
        data = self._create_data(attack,move,self.hps,self.dead)
        data_bytes = json.dumps(data).encode('utf-8')
        client.sendall(data_bytes)
    
    def update_positions(self,pos):
        self.positions['s'] = pos[0]
        self.positions['c'] = pos[1]
        self.positions['w'] = pos[2]

        
    
    def _handle_attack(self, attack: tuple):
        for key, values in self.positions.items():
            if values != None:
                if attack[0] == values[0] and attack[1] == values[1]:
                    self.hps[key] -= 1

        for key, values in self.hps.items():
            if values == 0:
                self.positions[key] = None

    def _create_data(self, attack, move, hps, dead):
        return {"attack": attack, "move": move, "hps": hps, "dead": dead}
            


class randomPlayer(player):
    def __init__(self, seed=0):
        super().__init__(None)
        random.seed(seed)
        self.field = [(i, j) for i in range(5)
                        for j in range(5)]
        ps = random.sample(self.field, 3)
        self.positions = {'s': ps[0], 'c': ps[1], 'w': ps[2]}

    def can_reach(self, pos, to):
        if pos[0] == to[0] or pos[1] == to[1]:
            return True
        return False
    
    def can_attack(self, pos, to):
        if abs(pos[0]-to[0]) <= 1 and abs(pos[1] - to[1]) <= 1:
            return True
        return False
    
    def action(self):
        pos = None
        dead = 0

        dead = sum(value == None for value in self.positions.values())
        if dead == 3:
            return self._create_data(None, None, self.hps, True)

        while pos == None:
            act = random.choice(["move", "attack"])
            ship = random.choice(list(self.positions.keys()))
            pos = self.positions[ship]

        if act == "move":
            to = random.choice(self.field)
            while not self.can_reach(pos, to):
                to = random.choice(self.field)
            print(f"Bot moved {ship} from {pos} to {to}")
            self.positions[ship] = to
            print(list(self.positions.items()))
            return self._create_data(None, f"Player 2 moved {ship} by {pos[0]-to[0]}, {pos[1]-to[1]}", self.hps, False)
        
        elif act == "attack":
            to = random.choice(self.field)
            while not self.can_attack(pos,to):
                to = random.choice(self.field)
            print(f"Bot attacked {to}")
            print(list(self.positions.items()))
            return self._create_data(to, None, self.hps, False)
    
    
    
            
             







