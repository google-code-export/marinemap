from django import template
register = template.Library()

@register.tag(name="tabpanel")
def do_tabpanel(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument. You must give your tabpanel a title." % token.contents.split()[0]
    if not (title[0] == title[-1] and title[0] in ('"', "'")):
            raise template.TemplateSyntaxError, "%r title should be in quotes" % tag_name
    nodelist = parser.parse(('endtabpanel',))
    parser.delete_first_token()
    return TabPanelNode(nodelist, title[1:-1])

class TabPanelNode(template.Node):
    def __init__(self, nodelist, title):
        self.nodelist = nodelist
        self.title = title
        self.tab_id = title.replace(' ', '')
    
    def render(self, context):
        # print self.nodelist
        output = self.nodelist.render(context)
        list_items = ''
        for node in self.nodelist:
            if node.__class__.__name__ is 'TabNode':
                list_items += """
                    <li><a href="#%s">%s</a></li>
                """ % (node.tab_id, node.title)
        return """<div class="sidebar-panel">
            <div class="sidebar-header">
                <h1>%s</h1>
            </div>
            <ul class="tabs">
                %s
            </ul>
            <div class="sidebar-body">
                <div class="sidebar-wrapper">
                    %s
                </div>
            </div>
        </div>
        """ % (self.title, list_items, output)