import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import matplotlib.colors as clr

import time

class State:
    def __init__(self, rule=0, values=[0]):
        self.set_rule(rule)
        self.values = values
        self.norm = None
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
        self.norm = self.base_state.norm
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
            return plt.imshow(image[0:1], norm=self.norm, cmap=plt.cm.gray_r, interpolation='none')
        else:
            return plt.imshow(image, norm=self.norm, cmap=plt.cm.gray_r, interpolation='none')
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

    def animate(self, dim=2, interval=50, display=True, repeat=True, repeat_delay=1000, figure=None, subplot=None):
        #recommend longer interval for dim=1
        self.anim_dim = dim
        if figure == None:
            self.fig = plt.figure()
        else:
            self.fig = figure
        if subplot != None:
            self.fig.add_subplot(*subplot)
        self.im = self._gen_image() 
        self.ani = anim.FuncAnimation(self.fig, self.update_fig, init_func=self.init_anim, interval=interval, blit=True, frames=self.layers, repeat=repeat, repeat_delay=repeat_delay)
        if display:
            plt.show()
    def save_animation(self, path):
        self.ani.save(path+'automata_rule:{0:03d}_layers{1:03d}.mp4'.format(self.rule, self.layers), fps=30)
        
        #self.ani.save("automata.mp4", fps=30)
    def del_animation(self):
        plt.close(self.fig)
        del self.ani


def test_binary():
    for i in range(256):
        machine = Machine(rule=i, values=[1])
        machine = machine.add_layer(20)
        machine.animate(display=False)
        machine.save_animation(path="animations/")
        machine.del_animation()
    return machine

def test_trinary():
    figure = plt.figure()
    nfigs = 10
    nrows = int(np.sqrt(nfigs)); ncols = (nfigs + nrows - 1)/nrows 
    for i in range(nfigs):
        subplot = (nrows, ncols, i+1)
        print subplot
        machine = Machine(rule=i, values=[1], type='totalistic')
        machine = machine.add_layer(50)
        machine.animate(display=False, repeat=True, figure=figure, subplot=subplot)
        #machine.del_animation() 
        print "rule {0}".format(i)
    plt.show()

if __name__ == "__main__":
    test_trinary()
    time.sleep(2)
