from django import template
register = template.Library()

@register.tag(name="tab")
def do_tab(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument. You must give your tab a title." % token.contents.split()[0]
    if not (title[0] == title[-1] and title[0] in ('"', "'")):
            raise template.TemplateSyntaxError, "%r title should be in quotes" % tag_name
    nodelist = parser.parse(('endtab',))
    parser.delete_first_token()
    return TabNode(nodelist, title[1:-1])

class TabNode(template.Node):
    def __init__(self, nodelist, title):
        self.nodelist = nodelist
        self.title = title
        self.tab_id = title.replace(' ', '')
    def render(self, context):
        print self.nodelist
        output = self.nodelist.render(context)
        return """<div id="%s" class="sidebar-body">
            <div class="sidebar-wrapper">
                %s
            </div>
        </div>
        """ % (self.tab_id, output)