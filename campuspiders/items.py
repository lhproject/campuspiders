# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class JWNewsItem(Item):
    title = Field()
    ctime = Field()
    content = Field()
    author = Field()
    publisher = Field()
    url = Field()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
