
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class MonitorHandler(tornado.web.RequestHandler):
    def post(self):
        event_data = self.get_body_argument('data')
        print(event_data)