import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim

import time

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
        #plt.imshow([[0]*pad+self.values+[0]*pad], cmap=plt.cm.gray_r, interpolation='none')
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
        self.fig = None
        self.im = None
        self.state_idx = 0
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
        self.array = np.zeros(np.array(image).shape)
        return plt.imshow(image, cmap=plt.cm.gray_r, interpolation='none')
    def display(self):
        self._gen_image()
        plt.show()

    def update_fig(self, *args):
        if self.state_idx == 0:
            self.array = np.zeros(self.array.shape)
        pad = self.layers - self.state_idx
        self.array[self.state_idx, :] = self.states[self.state_idx].get_values(pad)
        self.im.set_array(self.array)
        self.state_idx = (self.state_idx + 1) % self.layers
        return self.im,

    def animate(self):
        #if isinstance(self.fig, None):
        #if self.fig is None:
        self.fig = plt.figure()
        #if isinstance(self.im, None):
        #if self.im is None:
        self.im = self._gen_image() 
        animation = anim.FuncAnimation(self.fig, self.update_fig, interval=50, frames=200, blit=True)
        plt.show()


def test():
    machine = Machine(rule=30, values=[1])
    machine = machine.add_layer(20)
    machine.animate()
    return machine

if __name__ == "__main__":
    test()
