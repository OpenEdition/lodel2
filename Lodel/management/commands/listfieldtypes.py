from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from EditorialModel.fields import EmField

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
        if options['silent']:
            for ftype in EmField.fieldtypes_list():
                self.stdout.write("\t%s\n"%ftype)
        else:
            self.stdout.write("Field types list : ")
            for ftype in EmField.fieldtypes_list():
                self.stdout.write("\t{0:15} {1}".format(ftype, EmField.get_field_class(ftype).help))
