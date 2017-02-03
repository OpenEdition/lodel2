from lodel.context import LodelContext

LodelContext.expose_modules(globals(), {
    'lodel.exceptions': ['LodelFatalError'],
})

def save(model, filename= None):
    raise LodelFatalError('Not allowed to save an EM. EM are handled \
externally')

def load(filename):
    raise LodelFatalError('Not allowed to load an EM : EM are handled \
externally')
