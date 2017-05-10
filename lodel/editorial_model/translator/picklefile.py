#-*- coding: utf-8 -*-
##@package lodel.editorial_model.translator.picklefile
# This module handles the file storage of an editorial model

import pickle

##@brief Saves a model in a file
# @param model EditorialModel : the model to save
# @param filename str|None : if None return the model as pickle bytes (by default : None)
# @return None if filename is a string, else returns bytes representation of model
def save(model, filename = None):
    with open(filename, 'w+b') as ffd:
        pickle.dump(model, ffd)
    return filename

##@brief Loads a model from a file
# @param filename str : the filename to use to load the model
# @return EditorialModel
def load(filename):
    with open(filename, 'rb') as ffd:
        edmod = pickle.load(ffd)
    return edmod
