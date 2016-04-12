#-*- coding: utf-8 -*-

import pickle
from pickle import Pickler

##@brief Save a model in a file
# @param model EditorialModel : the model to save
# @param filename str|None : if None return the model as pickle bytes
# @return None if filename is a string, else returns bytes representation of model
def save(model, filename = None):
    with open(filename, 'w+b') as ffd:
        pickle.dump(model, ffd)
    return filename

##@brief Load a model from a file
# @param filename str : the filename to use to load the model
def load(filename):
    with open(filename, 'rb') as ffd:
        edmod = pickle.load(ffd)
    return edmod
