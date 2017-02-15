#python 2.x
import web
import web.form as form
import ticket_update_summary
urls = (
  '/', 'Index'
)
render = web.template.render('templates/')

app = web.application(urls, globals())
jql_query = form.Form(
    form.Textarea('JQL', rows=2, cols=200, value = 'project = "CNN Android Titan Project" and status != Done and status != QA order by updated desc')
)

class Index(object):
    def GET(self):
        return render.jqlquery(jql_query())

    def POST(self):
        f = jql_query()
        q = web.input().JQL
        print 'query is ' + q
        ret = ticket_update_summary.query(q)
#        print ret
        return ret

class MyApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

if __name__ == "__main__":
    app = MyApplication(urls, globals())
    app.run(port=8888)

