import tornado.ioloop
from insight.services.main_handler import MainHandler, MonitorHandler


def make_app():

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/monitor", MonitorHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(9999)
    tornado.ioloop.IOLoop.current().start()