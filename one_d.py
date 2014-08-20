import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim

class State:
    def __init__(self, rule=0, values=[0]):
        self.set_rule(rule)
        self.values = values
    def set_rule(self, rule):
        if isinstance(rule, int):
            self.rule = self._rule_from_int(rule)
        elif isinstance(rule, dict):
            self.rule = rule
        else:
            print "invalid rule type"
    def _rule_from_int(self, value):
        results = reversed(bin(value)[2:].zfill(8))
        rule = dict()
        for idx, result in enumerate(results):
            rule[idx] = int(result)
        return rule
    def get_values(self, pad=0):
        return [0]*pad+self.values+[0]*pad
    def set_values(self, values):
        self.values = values
    def __str__(self):
        return str(self.values)
    def display(self, pad=0):
        plt.imshow([[0]*pad+self.values+[0]*pad], cmap=plt.cm.gray_r, interpolation='none')
        plt.show()
    def next_state(self):
        temp = [0]*2 + self.values + [0]*2
        new_values = []
        for idx in range(1, len(temp)-1):
            new_values.append(self.rule[self._eval_pattern(temp[idx-1:idx+2])])
        new_state = State(self.rule, new_values)
        return new_state

    def _eval_pattern(self, pattern):
        return sum([x*2**idx for (idx, x) in enumerate(pattern)])

class Machine:
    def __init__(self, rule=0, values=[0], layers=1):
        self.states = []
        self.rule = rule 
        self.values = values
        self.layers = layers
        self.base_state = State(self.rule, self.values)
        self.states.append(self.base_state)
        for i in range(self.layers-1):
            self._add_layer()
        self.im = self._gen_image() 
    def _add_layer(self):
        self.states.append(self.states[-1].next_state())
    def add_layer(self, n=1):
        return Machine(self.rule, self.values, self.layers+n)
    def __str__(self):
        return str(map(str, self.states))
    def _gen_image(self):
        image = []
        for idx, state in enumerate(self.states):
            pad = self.layers - idx
            image.append(state.get_values(pad))
        return plt.imshow(image, cmap=plt.cm.gray_r, interpolation='none')
    def display(self):
        self._gen_image()
        plt.show()
    def updatefig():
        array = self.im
        self.im.set_array(

    def get_state(self, i):
        pad = self.layers - i
        return plt.imshow([self.states[i].get_values(pad)], cmap=plt.cm.gray_r, interpolation='none')
    def animate(self):
        fig = plt.figure()
        animation = anim.FuncAnimation(fig, self.get_state, frames=200, interval=20, blit=True)
        plt.show()


def test():
    machine = Machine(rule=30, values=[1])
    machine = machine.add_layer(10)
    machine.animate()
    return machine
