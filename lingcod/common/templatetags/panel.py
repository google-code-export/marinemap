from django import template
register = template.Library()

@register.tag(name="panel")
def do_panel(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument. You must give your panel a title." % token.contents.split()[0]
    if not (title[0] == title[-1] and title[0] in ('"', "'")):
            raise template.TemplateSyntaxError, "%r title should be in quotes" % tag_name
    nodelist = parser.parse(('endpanel',))
    parser.delete_first_token()
    return PanelNode(nodelist, title[1:-1])

class PanelNode(template.Node):
    def __init__(self, nodelist, title):
        self.nodelist = nodelist
        self.title = title
    def render(self, context):
        print self.nodelist
        output = self.nodelist.render(context)
        return """<div class="sidebar-panel">
            <div class="sidebar-header">
                <h1>%s</h1>
            </div>
            <div class="sidebar-body">
                <div class="sidebar-wrapper">
                    %s
                </div>
            </div>
        </div>
        """ % (self.title, output)