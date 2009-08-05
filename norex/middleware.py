from django.conf import settings
import re


class mobile(object):
    """
    If the Middleware detects an iPhone/iPod the template dir changes to the
    iPhone template folder.
    """

    def __init__(self):
        
        self.normal_templates = settings.TEMPLATE_DIRS
        
        #p = re.compile('mobile', re.IGNORECASE)
        #if p.search(self.normal_templates[0]):
        #    self.normal_templates = (self.normal_templates[1],) + self.normal_templates
        self.iphone_templates = (self.normal_templates[0] + '/mobile',) + self.normal_templates
        self.mobile_templates = (self.normal_templates[0] + '/mobile',) + self.normal_templates

    def process_request(self, request):
        #p = re.compile('iPhone|iPod|BlackBerry|Android|Nokia|webOS', re.IGNORECASE)
        p = re.compile('iPhone|iPod|Android|webOS', re.IGNORECASE)
        if p.search(request.META['HTTP_USER_AGENT']):
            # user agent looks like iPhone or iPod
            settings.TEMPLATE_DIRS = self.iphone_templates
        else:
            p = re.compile('BlackBerry|Nokia|Mobile', re.IGNORECASE)
            if p.search(request.META['HTTP_USER_AGENT']):
                # less cool mobile agents
                settings.TEMPLATE_DIRS = self.mobile_templates
            else:
                # other standard user agents
                settings.TEMPLATE_DIRS = self.normal_templates
        return
