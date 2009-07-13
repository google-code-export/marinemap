from django import template
register = template.Library()

@register.tag(name="footer")
def do_footer(parser, token):
    nodelist = parser.parse(('endfooter',))
    parser.delete_first_token()
    return FooterNode(nodelist)

class FooterNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        print self.nodelist
        output = self.nodelist.render(context)
        return '<div class="sidebar-footer">%s</div>' % (output,)