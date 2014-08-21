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
        plt.show()
    def next_state(self):
        temp = [0]*2 + self.values + [0]*2
        new_values = []
        for idx in range(1, len(temp)-1):
            new_values.append(self.rule[self._eval_pattern(temp[idx-1:idx+2])])
        new_state = State(self.rule, new_values)
        return new_state

    def _eval_pattern(self, pattern):
        return sum([x*2**idx for (idx, x) in enumerate(reversed(pattern))])

class Totalistic_State(State):
    def __init__(self, rule=0, values=[0], k=3):
        self.k = k
        self.nvalues = 3*k-2
        self.set_rule(rule)
        self.values = values
    def _rule_from_int(self, value):
        rule = dict()
        for i in range(self.nvalues):
            rule[i] = value % self.k
            value /= self.k
        return rule
    def next_state(self):
        temp = [0]*2 + self.values + [0]*2
        new_values = []
        for idx in range(1, len(temp)-1):
            new_values.append(self.rule[self._eval_pattern(temp[idx-1:idx+2])])
        new_state = Totalistic_State(self.rule, new_values, self.k)
        return new_state
    def _eval_pattern(self, pattern):
        return sum(pattern)

class Machine:
    def __init__(self, rule=0, values=[0], type='binary', k=3, layers=1):
        self.states = []
        self.rule = rule 
        self.values = values
        self.layers = layers
        self.type=type
        self.k = k
        if self.type=='binary':
            self.base_state = State(self.rule, self.values)
        elif self.type=='totalistic':
            self.base_state = Totalistic_State(self.rule, self.values, self.k)
        self.states.append(self.base_state)
        for i in range(self.layers-1):
            self._add_layer()
        self.fig = None
        self.im = None
        self.state_idx = 0
        self.anim_dim = 2
    def _add_layer(self):
        self.states.append(self.states[-1].next_state())
    def add_layer(self, n=1):
        return Machine(self.rule, self.values, self.type, self.k, self.layers+n)
    def __str__(self):
        return str(map(str, self.states))
    def _gen_image(self):
        image = []
        for idx, state in enumerate(self.states):
            pad = self.layers - idx
            image.append(state.get_values(pad))
        self.array = np.zeros(np.array(image).shape)
        if self.anim_dim == 1:
            return plt.imshow(image[0:1], cmap=plt.cm.gray_r, interpolation='none')
        else:
            return plt.imshow(image, cmap=plt.cm.gray_r, interpolation='none')
    def display(self):
        self._gen_image()
        plt.show()
    def init_anim(self):
        self.array = np.zeros(self.array.shape)
        if self.anim_dim == 1:
            self.im.set_array(self.array[0:1, :])
        else:
            self.im.set_array(self.array)
        return self.im,

    def update_fig(self, *args):
        if self.state_idx == 0:
            self.array = np.zeros(self.array.shape)
        pad = self.layers - self.state_idx
        self.array[self.state_idx, :] = self.states[self.state_idx].get_values(pad)
        if self.anim_dim == 1:
            self.im.set_array(self.array[self.state_idx:self.state_idx+1, :])
        else:
            self.im.set_array(self.array)
        self.state_idx = (self.state_idx + 1) % self.layers
        return self.im,

    def animate(self, dim=2, interval=50):
        #recommend longer interval for dim=1
        self.anim_dim = dim
        self.fig = plt.figure()
        self.im = self._gen_image() 
        self.ani = anim.FuncAnimation(self.fig, self.update_fig, init_func=self.init_anim, interval=interval, blit=True)
        plt.show()
    def save_animation(self):
        #self.ani.save('automata_rule:{0}_layers{1}.mp4'.format(self.rule, self.layers), fps=30)
        self.ani.save("automata.mp4", fps=30)


def test():
    machine = Machine(rule=30, values=[1])
    machine = machine.add_layer(16)
    machine.animate()
    machine.save_animation()
    return machine

if __name__ == "__main__":
    test()
