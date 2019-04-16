import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import authorized_userid, remember, check_authorized, forget, check_permission
from backend.security.db_auth import check_credentials


class LoginRouter:

    @aiohttp_jinja2.template('pages/login.html')
    async def index(self, request):
        username = await authorized_userid(request)
        if username:
            res = {'message': 'Hey, ' + username}
        else:
            res = {'message': 'You need to login'}
        return res

    async def login(self, request):
        response = web.HTTPFound('/security')
        form = await request.post()
        login = form.get('email')
        password = form.get('password')
        db_engine = request.app['db']
        if await check_credentials(db_engine, login, password, 'admin'):
            await remember(request, response, login)
            raise response

        raise web.HTTPUnauthorized(
            body=b'Invalid username/password combination')

    async def logout(self, request):
        await check_authorized(request)
        response = web.HTTPFound('/security')
        await forget(request, response)
        return response

    async def admin_page(self, request):
        await check_permission(request, 'admin')
        context = {
            'message': 'this is admin page'
        }
        response = aiohttp_jinja2.render_template('pages/login.html', request, context)
        return response

    async def protected_page(self, request):
        await check_authorized(request)
        context = {
            'message': 'you are authorized'
        }
        response = aiohttp_jinja2.render_template('pages/login.html', request, context)
        return response

    def configure(self, app):
        router = app.router
        router.add_route('GET', '/security', self.index, name='security')
        router.add_route('POST', '/login', self.login, name='login')
        router.add_route('GET', '/logout', self.logout, name='logout')
        router.add_route('GET', '/admin', self.admin_page, name='admin')
        router.add_route('GET', '/protected', self.protected_page,
                         name='protected')
