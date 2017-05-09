from flask_script import Command
from lodel.editorial_model.model import EditorialModel

class LodelCommand(Command):

    def run(self, model_file, translator):
        em = EditorialModel('LodelSites', 'LodelSites editorial model')
        
        base_group = em.new_group('base_group', display_name='Base group', help_text='Base group that implements base EM features (like classtype)')
        
        em_lodel_site = em.new_class('LodelSite', group=base_group)
        em_lodel_site.new_field('name', display_name='lodelSiteName', help_text='Lodel site full name', group=base_group, data_handler='varchar')
        em_lodel_site.new_field('shortname', display_name='lodelSiteShortName', help_text='Lodel site short string identifier', group=base_group, data_handler='varchar', max_length=5, uniq=True)
        em_lodel_site.new_field('extensions', display_text='lodeSiteExtensions', help_text='Lodel site extensions', group=base_group, data_handler='varcharlist', delimiter=' ')
        em_lodel_site.new_field('em_groups', display_text = 'lodelSiteEmGroups', help_text = 'Lodel site EM groups', group = base_group, data_handler = 'text',)
        
        pickle_file_path = 'examples/lodelsites_em.pickle'
        xml_file_path = 'examples/lodelsites_em.xml'

        em.save('xmlfile', filename=xml_file_path)
        em.save('picklefile', filename=pickle_file_path)
        print('The %s (XML) and %s (Pickle) files are created' % (xml_file_path, pickle_file_path))
