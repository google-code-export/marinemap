from django import template
register = template.Library()

@register.tag(name="home_link")
def do_home_link(parser, token):
    tokens = token.split_contents()
    print tokens
    if len(tokens) == 1:
        href = "#"
        text = "Back Home"
    elif len(tokens) == 2:
        href = "#"
        text = tokens[1]
    elif len(tokens) == 3:
        text = tokens[1]
        href = '#' + tokens[2].replace(' ', '')
    else:
        raise template.TemplateSyntaxError, "%r tag accepts no more than 2 arguments." % token.contents.split()[0]
    return HomeLinkNode(href, text)

class HomeLinkNode(template.Node):
    def __init__(self, href, text):
        self.href = href
        self.text = text
    
    def render(self, context):
        return """
            <a class="back_link" href="%s">%s</a>
        """ % (self.href, self.text)