# -*- coding: utf-8 -*-

import scrapy
from syllascrape.items import PageItem 

class PSUSpider(scrapy.spiders.Spider):
    name = "psu"
    allowed_domains = ["psu.edu"]

    def start_requests(self):
        start_url = "http://www.altoona.psu.edu/syllabi/"

        def start_form_requests(response):
            view1_url = "http://www.altoona.psu.edu/syllabi/view1.php"

            course_abbreviations = response.css("#course_abbr option::text").extract()
            for course in course_abbreviations:
                yield scrapy.FormRequest(
                    view1_url,
                    formdata={
                        "course_abbr": course,
                    },
                    method='POST',
                    meta={
                        "depth": 1,
                        "hops_from_seed": 1,
                        "source_url": start_url,
                        "source_anchor": "",
                    },
                    callback=self.get_semester_urls
                )


        yield scrapy.Request(start_url, callback=start_form_requests)

    def get_semester_urls(self, response):
        semester_tags = response.css("#main ul li a")
        for tag in semester_tags:
            relative_url = tag.css("a::attr(href)").extract_first()
            url = response.urljoin(relative_url)
            anchor = tag.css("a::text").extract_first()
            yield scrapy.Request(
                url,
                meta={
                    'source_url': response.url,
                    'source_anchor': anchor,
                    'depth': response.meta['depth'] + 1,
                    'hops_from_seed': response.meta['hops_from_seed'] + 1,
                }
            )

    def parse(self, response):
        file_urls = []

        title_tags = response.css("table.data tbody td:nth-child(3) a")
        for tag in title_tags:
            relative_url = tag.css("a::attr(href)").extract_first()
            url = response.urljoin(relative_url)
            anchor = tag.css("a::text").extract_first()

            meta = {
                'source_url': response.url,
                'source_anchor': anchor,
                'depth': response.meta['depth'] + 1,
                'hops_from_seed': response.meta['hops_from_seed'] + 1,
            }

            file_urls.append((url, meta))

        yield PageItem(
            url=response.url,
            content=response.body,
            headers=response.headers,
            status=response.status,
            source_url=response.meta.get('source_url'),
            source_anchor=response.meta.get('source_anchor'),
            depth=response.meta.get('depth'),
            hops_from_seed=response.meta.get('hops_from_seed'),
            file_urls=file_urls,
        )

# http://www.altoona.psu.edu/syllabi/ Needs custom scraper

# http://hhd.psu.edu/rptm/courses-and-syllabi Requires permissions
# http://sip.la.psu.edu/blp/courses/syllabi-and-policies Handled by syllascrape
# http://forensics.psu.edu/program/undergraduate-degree-program/undergraduate-course-syllabi Handled by syllascrape
# http://chem.psu.edu/undergrad/courses/syllabi Handled by syllascrape
# http://stat.psu.edu/education/syllabi/previous-semester-courses Handled by syllascrape
# http://stat.psu.edu/education/undergraduate-program/spring-2013-syllabi-folder/spring-2013-syllabi-links Handled by syllascrape
# http://sip.la.psu.edu/undergraduate/italian/courses-syllabi-and-more/syllabi Handled by syllascrape
# https://ed.psu.edu/eps/edldr/downloads-forms/schafft-syllabi Handled by syllascrape
# http://lser.la.psu.edu/gwr/resources-1/course-syllabi Handled by syllascrape
# http://nursing.psu.edu/undergraduate/syllabus Requires permissions
# https://www.courses.psu.edu/art/ Handled by syllascrape, but syllabi are HTML
# http://bulletins.psu.edu/undergrad/campuses/details/28/BB%20H No syllabi found
# http://bio.psu.edu/undergraduate-portal/our-curriculum/syllabi Handled by syllascrape, but syllabi are HTML
# http://www.met.psu.edu/academics/undergraduate-studies/undergraduate-courses/course-syllabi Handled by syllascrape, but no syllabi found
# http://www.phys.psu.edu/undergraduate/courses/syllabi Handled by syllascrape, but syllabi are HTML
# http://bmb.psu.edu/undergraduate/courses/sp16-syllabi Handled by syllascrape, but syllabi are HTML
# http://phys23p.sl.psu.edu/syll/ Handled by syllascrape
# http://www.personal.psu.edu/~j5j/courses.html Handled by syllascrape
# http://nursing.psu.edu/undergraduate/syllabus Requires permissions
