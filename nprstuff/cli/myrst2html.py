from docutils import core, nodes
from docutils.core import publish_cmdline
from docutils.utils.math import unichar2tex
from docutils.writers.html4css1 import Writer, HTMLTranslator

class MyHTMLTranslator(HTMLTranslator):
    mathjax_script = '<script type="text/javascript" src="{}"></script>\n'
    mathjax_url = 'https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'

    def visit_math(self, node, math_env=''):
        if self.math_output != 'mathjax':
            super().visit_math(node, math_env)
            return

        if self.math_output == 'mathjax' and not self.math_header:
            if self.math_output_options:
                self.mathjax_url = self.math_output_options[0]
            self.math_header = [self.mathjax_script.format(self.mathjax_url)]

        math_code = node.astext().translate(unichar2tex.uni2tex_table)
        math_code = self.encode(math_code)
        # Don't wrap the mathematics with div or span
        if math_env:
            self.body.append('\[{}\]\n'.format(math_code))
        else:
            self.body.append('\({}\)'.format(math_code))
        raise nodes.SkipNode

def _main( ):
    htmlwriter = Writer()
    htmlwriter.translator_class = MyHTMLTranslator
    publish_cmdline(writer=htmlwriter)
