from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from EditorialModel.randomem import RandomEm
from EditorialModel.backend.json_backend import EmBackendJson
from EditorialModel.backend.dummy_backend import EmBackendDummy
from EditorialModel.backend.graphviz import EmBackendGraphviz


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--no-classes',
            action='store',
            dest='classtype',
            default = 0,
            help='Chances for a classtype to be empty',
            type="int",
            metavar="INT",
        ),
        make_option('--max-classes',
            action='store',
            dest='nclass',
            default = 3,
            help='Maximum number of classes per classtype',
            type="int",
            metavar="INT",
        ),
        make_option('--no-fieldgroup',
            action='store',
            dest='nofg',
            default = 10,
            help='Chances for a class to have no fieldgroup',
            type="int",
            metavar="INT",
        ),
        make_option('--no-types',
            action='store',
            dest='notype',
            default = 10,
            help='Chances for a class to have no types',
            type="int",
            metavar="INT",
        ),
        make_option('--max-types',
            action='store',
            dest='ntype',
            default = 8,
            help='Maximum number of types in a class',
            type="int",
            metavar="INT",
        ),
        make_option('--sel-opt-field',
            action='store',
            dest='seltype',
            default = 2,
            help='Chances for type to select an optionnal field',
            type="int",
            metavar="INT",
        ),
        make_option('--superiors',
            action='store',
            dest='ntypesuperiors',
            default = 2,
            help='Chances for a type to link with other types (superiors)',
            type="int",
            metavar="INT",
        ),
        make_option('--no-fields',
            action='store',
            dest='nofields',
            default = 10,
            help='Chances for a fieldgroup to be empty',
            type="int",
            metavar="INT",
        ),
        make_option('--max-fields',
            action='store',
            dest='nfields',
            default = 8,
            help='Maxmimum number of fields per fieldgroup',
            type="int",
            metavar="INT",
        ),
        make_option('--rel-to-type-attr',
            action='store',
            dest='rfields',
            default = 5,
            help='Maximum number of relation-to-type attribute fields',
            type="int",
            metavar="INT",
        ),
        make_option('--opt-field',
            action='store',
            dest='optfield',
            default = 2,
            help='Chances for a field to be optionnal',
            type="int",
            metavar="INT",
        ),
        make_option('-o',
            '--output',
            action='store',
            dest='output',
            default = 'random_me.json',
            help='json output file for the me',
            type="string",
            metavar="FILENAME",
        ),
        make_option('-d',
            '--output-dot',
            action='store',
            dest='dotout',
            default = False,
            help='graphviz output file for the me',
            type="string",
            metavar="FILENAME",
        ),


    )
    help = 'Randomly generate an EditorialModel'

    def handle(self, *args, **options):
        anames = ['classtype','nclass', 'nofg', 'notype', 'ntype', 'seltype', 'ntypesuperiors', 'nofields', 'nfields', 'optfield']
        chances = dict()
        for n in anames:
            chances[n] = options[n]
        
        bj = EmBackendJson(options['output'])

        em = RandomEm.random_em(EmBackendDummy())
        bj.save(em)

        if options['dotout']:
            gvb = EmBackendGraphviz(options['dotout'])
            gvb.save(em)


