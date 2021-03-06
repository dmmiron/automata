import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import matplotlib.colors as clr

import time
import sys
import random as rand

class State:
    def __init__(self, rule=0, values=[0]):
        self.set_rule(rule)
        self.values = values
        self.norm = None
    def set_rule(self, rule):
        if isinstance(rule, int) or isinstance(rule, long):
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
        plt.imshow([self.values], cmap=plt.cm.gray_r, interpolation='none') 
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
        self.norm = clr.Normalize(vmax=k-1)
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
    def __init__(self, rule=0, values=[0], state_type='binary', k=3, layers=1):
        self.states = []
        self.rule = rule 
        self.values = values
        self.layers = layers
        self.state_type=state_type
        self.k = k
        if self.state_type=='binary':
            self.base_state = State(self.rule, self.values)
        elif self.state_type=='totalistic':
            self.base_state = Totalistic_State(self.rule, self.values, self.k)
        self.norm = self.base_state.norm
        self.states.append(self.base_state)
        for i in range(self.layers-1):
            self._add_layer()
        self.fig = None
        self.subplot = None
        self.im = None
        self.state_idx = 0
        self.anim_dim = 2
        self.cmap = 'gray_r'
    def _add_layer(self):
        self.states.append(self.states[-1].next_state())
    def add_layer(self, n=1):
        return Machine(self.rule, self.values, self.state_type, self.k, self.layers+n)
    def __str__(self):
        return str(map(str, self.states))
    def _gen_image(self, static=False):
        image = []
        for idx, state in enumerate(self.states):
            pad = self.layers - idx
            image.append(state.get_values(pad))
        self.array = np.zeros(np.array(image).shape)
        if static:
            return plt.imshow(image, norm=self.norm, cmap=self.cmap, interpolation='none')
        if self.anim_dim == 1:
            return self.subplot.imshow(image[0:1], norm=self.norm, cmap=self.cmap, interpolation='none')
        else:
            return self.subplot.imshow(image, norm=self.norm, cmap=self.cmap, interpolation='none')
    def display(self, cmap='gray_r'):
        self.cmap=cmap
        self._gen_image(static=True)
        plt.show()

    def init_anim(self):
        self.im = self._gen_image()
        self.array = np.zeros(self.array.shape)
        if self.anim_dim == 1:
            self.im.set_array(self.array[0:1, :])
        else:
            self.im.set_array(self.array)
        return self.im,

    def update_fig(self, subplot=None, *args):
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

    def animate(self, dim=2, interval=50, display=True, repeat=True, repeat_delay=1000, figure=None, subplot=(1, 1, 1), cmap='gray_r'):
        #recommend longer interval for dim=1
        self.anim_dim = dim
        self.cmap = cmap
        if figure == None:
            self.fig = plt.figure()
        else:
            self.fig = figure
        self.subplot = self.fig.add_subplot(*subplot)
        self.subplot.set_title("Rule {0}, k={1}".format(self.rule, self.k))

        self.ani = anim.FuncAnimation(self.fig, self.update_fig, init_func=self.init_anim, interval=interval, blit=True, frames=self.layers, repeat=repeat, repeat_delay=repeat_delay)

        if display:
            plt.show()

    def save_animation(self, path):
        self.ani.save(path+'automata_rule:{0:03d}_layers{1:03d}.mp4'.format(self.rule, self.layers), fps=30)
        
    def del_animation(self):
        plt.close(self.fig)
        del self.ani

def test_binary():
    fig = plt.figure()
    nfigs = 16
    ncols = int(np.sqrt(nfigs)); nrows = (nfigs + ncols - 1)/ncols 
    machines = []
    for i in range(nfigs):
        subplot = (nrows, ncols, i+1)
        machine = Machine(rule=i, values=[1])
        machine = machine.add_layer(20)
        machine.animate(dim=2, display=False, figure=fig, subplot=subplot)
        machines.append(machine)
        #machine.save_animation(path="animations/")
        #machine.del_animation()
    plt.show()
    return machine

def test_trinary():
    nfigs = 2 

    ncols = int(np.sqrt(nfigs)); nrows = (nfigs + ncols - 1)/ncols 
    colormaps = plt.colormaps()[::2]
    colormaps = ['hsv', 'gray_r']
    for k in range(3, 64):
        for cm in colormaps:
            exp = 3*k-2
            rules = [long(rand.randint(0, k**exp)) for x in range(nfigs)]
            
            figure = plt.figure()
            machines = []
            for idx, rule in enumerate(rules):
                subplot = (nrows, ncols, idx+1)
                machine = Machine(rule=rule, values=[1], state_type='totalistic', k=k)
                machine = machine.add_layer(20)
                machines.append(machine)
                machine.animate(dim=2, display=False, figure=figure, subplot=subplot, cmap=cm)
                #machine.del_animation() 
            plt.show()

if __name__ == "__main__":
    machine = Machine(rule=912, state_type='totalistic', values=[1])
    machine = machine.add_layer(100)
    #machine.animate(interval=2)
    machine.display()
    machine.display(cmap='hsv')
    #test_binary()
    #test_trinary()
