import scrapy.spiders

class Spider(scrapy.spiders.Spider):
    """Base class for syllascrape spiders

    :cvar int version: a version number for the spider. This should be incremented by the developer for each version of code deployed to production
    """

    @property
    def version_string(self):
        """return the name/version"""
        return "%s/%d" % (self.name, self.version)

