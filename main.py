from flask import Flask

import exchange_rate_scraper
from utils.files import read_log_file

app = Flask(__name__)


@app.route('/')
def hello_world():
    exchange_rate_scraper.main()
    log_content = read_log_file('log/exchange_rate_scraper.log')
    print(log_content)
    return 'Hello, World! 888'+log_content

if __name__ == '__main__':
    app.run(debug=True)
