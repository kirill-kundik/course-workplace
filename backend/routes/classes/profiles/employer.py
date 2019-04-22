import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import check_permission, authorized_userid
from passlib.handlers.sha2_crypt import sha256_crypt

from db import db


class EmployerRouter:

    async def index(self, request):
        await check_permission(request, 'employer')
        username = await authorized_userid(request)
        context = {
            'username': username,
            'title': 'Profile page',
            'profile_link': 'employer',
            'employer': True
        }

        async with request.app['db'].acquire() as conn:
            res = await db.get_employer(conn, username)
            context.update(res)

        response = aiohttp_jinja2.render_template('pages/profiles/employer.html', request, context)
        return response

    async def update_employer(self, request):
        await check_permission(request, 'employer')
        username = await authorized_userid(request)
        form = await request.post()

        employer_update = {
            'email': form.get('email'),
            'password': sha256_crypt.hash(form.get('password')),
            'first_name': form.get('first_name'),
            'last_name': form.get('last_name'),
            'phone': form.get('phone'),

            'image_url': form.get('image_url'),
            'tg_link': form.get('tg_link'),
            'fb_link': form.get('fb_link'),
            'skype_link': form.get('skype_link'),
            'city': form.get('city'),
            'date_of_birth': form.get('date_of_birth'),
        }

        async with request.app['db'].acquire() as conn:
            await db.update_employer(conn, employer_update, username)

        return web.HTTPFound('/employer')

    def configure(self, app):
        router = app.router

        router.add_route('GET', '/employer', self.index, name='employer')
        router.add_route('POST', '/employer', self.update_employer, name='employer')