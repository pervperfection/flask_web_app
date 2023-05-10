from waitress import serve
import main
import logging


def serving():
    serve(main.app, host='10.8.8.106', port=8080)
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO) 

serving()