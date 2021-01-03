from flask import Flask,render_template
from flask_flatpages import FlatPages

app = Flask(__name__, template_folder='templates')
FLATPAGES_EXTENSION = '.md'

pages = FlatPages(app)
app.config['FLATPAGES_EXTENSION'] = FLATPAGES_EXTENSION

@app.route('/<path:path>.html')
def page(path):
    page = pages.get_or_404(path)
    return render_template('page.html', page=page)

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')


