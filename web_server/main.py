import inspect

from flask import Flask,render_template
from flask_flatpages import FlatPages, pygments_style_defs
from jinja2 import Environment


from lessons.one import first_data_pipeline


app = Flask(__name__, template_folder='templates')
FLATPAGES_EXTENSION = '.md'
ZERO_WIDTH_SPACE = '\u00a0' # Add zero breaking space to trick markdown into rendering code correctly
pages = FlatPages(app)
app.config['FLATPAGES_EXTENSION'] = FLATPAGES_EXTENSION
JINGA_ENV = Environment()
JINGA_ENV.lstrip_blocks= True
JINGA_ENV.trim_blocks = True


def template_markdown(markdown, **kwargs):
    '''
        Render in functions from lessons
    '''
    template = JINGA_ENV.from_string(markdown)
    template_processed_markdown = template.render(**kwargs)
    return template_processed_markdown


def get_lesson_source_code(path):
    full_code = { 'full_code' : inspect.getsource(eval(path))}
    functions = { func : inspect.getsource(eval(f'{path}.{func}')) for func, _ in inspect.getmembers(eval(path), inspect.isfunction)}
    # Add zero breaking space to trick markdown
    for lines in functions.values():
        for line in lines:
            if line.isspace():

                line += ZERO_WIDTH_SPACE
    return {**full_code, **functions}


@app.route('/<path:path>.html')
def page(path):
    page = pages.get_or_404(path)
    code = get_lesson_source_code(path)
    page.body = template_markdown(page.body, **code)
    return render_template('page.html', page=page)

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/pygments.css')
def pygments_css():
    return pygments_style_defs('tango'), 200, {'Content-Type':"text/css"}


if __name__ == '__main__':
    app.run(host='0.0.0.0')


