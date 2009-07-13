from django import template
register = template.Library()

@register.tag(name="printable")
def do_printable(parser, token):
    return PrintableNode()

class PrintableNode(template.Node):
    
    def render(self, context):
        return """
            <a class="printable" href="#" target="_blank">Print View</a>
        """