from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import EditorialModel

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--silent',
            action='store_true',
            dest='silent',
            default=False,
            help='Only display field types name and hide the help text'),
    )
    help = 'List all the possible field types'

    def handle(self, *args, **options):
        ftl = EditorialModel.fields.EmField.fieldtypes_list()
        ftl.sort()
        if options['silent']:
            for ftype in ftl:
                self.stdout.write("%s\n"%ftype)
        else:
            self.stdout.write("Field types list : ")
            for ftype in ftl:
                self.stdout.write("\t{0:15} {1}".format(ftype, EditorialModel.fieldtypes.generic.GenericFieldType.from_name(ftype).help))
