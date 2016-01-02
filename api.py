# Cloud Endpoints Libraries
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

# allow for HTTP Headers
from google.appengine.ext.endpoints import api_config
AUTH_CONFIG = api_config.ApiAuth(allow_cookie_auth=True)

api_version = "1.00"


#import Datastore models
from models import *


'''
	Users API
'''


class Error(messages.Message):
    error = messages.StringField(1)

class Response(messages.Message):
    message = messages.StringField(1)
    success = messages.BooleanField(2)
    errors = messages.StringField(3)
    token = messages.StringField(4)

class UserObject(messages.Message):
    email = messages.StringField(1)
    password = messages.StringField(2)
    first_name = messages.StringField(3)
    last_name = messages.StringField(4)

class GetUserObject(messages.Message):
    token = messages.StringField(1)

@endpoints.api(name = 'users', version = api_version, auth=AUTH_CONFIG,
               description = 'User Resources')
class UsersApi(remote.Service):



    @endpoints.method(UserObject, Response,
                        name = 'create',
                        path = 'create',
                        http_method = 'POST')
    def create(self, request):
        response = Users.create_user(request)
        if response:
            u = response[0]
            t = response[1]
            return Response(message = "User created successfully", success = True, errors = "", token = t)
        return Response(message = "That email address already exists in our system", success = False)


    @endpoints.method(UserObject, Response,
                        name = 'login',
                        path = 'login',
                        http_method = 'POST')
    def login(self, request):
        #basic_auth = self.request_state.headers.get('authorization')
        auth_values = Users.login(request.email, request.password)
        u = auth_values[0]
        t = auth_values[1]
        if u:
            return Response(message = u.first_name + " has successfully logged in!", success = True, errors = "", token = t)
        return Response(message = "Email or password is incorrect.", success = False, errors = "", token = "")

    @endpoints.method(GetUserObject, UserObject,
                        name = 'get_user',
                        path = 'get_user',
                        http_method = 'GET')
    def get_user(self, request):
        u = Users.by_token(request.token)
        if u:
            return UserObject(email=u.email, first_name=u.first_name, last_name=u.last_name)
        return UserObject(email="", first_name="", last_name="")


    @endpoints.method(UserObject, Response,
                        name = 'check_user_exists',
                        path = 'check_user_exists',
                        http_method = 'GET')
    def check_user_exists(self, request):
        u = Users.by_email(request.email)
        if u:
            return Response(success = True)
        return Response(success = False)


class FieldObject(messages.Message):
    name = messages.StringField(1)
    slug = messages.StringField(2)
    icon = messages.StringField(3)

class FieldObjects(messages.Message):
    fields = messages.MessageField(FieldObject, 1, repeated = True)

@endpoints.api(name = 'fields', version = 'v1',
               description = 'Field Management Resources')
class FieldsApi(remote.Service):

    @endpoints.method(FieldObject, Response,
                        name = 'create_field',
                        path = 'create_field',
                        http_method = 'POST')
    def create_field(self, request):
        f = Fields(name = request.name, slug = request.slug, icon = request.icon)
        f.put()
        return Response(message = "Field created successfully", success = True)

    @endpoints.method(message_types.VoidMessage, FieldObjects,
                        name = 'get_fields',
                        path = 'get_fields',
                        http_method = 'GET')
    def get_fields(self, request):
        fields = Fields.query().order(Fields.name)
        all_fields = [FieldObject(name = f.name, slug = f.slug, icon = f.icon) for f in fields]
        return FieldObjects(fields = all_fields)

class ProfessionObject(messages.Message):
    name = messages.StringField(1)
    slug = messages.StringField(2)
    field_slug = messages.StringField(3)

class ProfessionObjects(messages.Message):
    professions = messages.MessageField(ProfessionObject, 1, repeated = True)


@endpoints.api(name = 'professions', version = 'v1',
               description = 'Profession Management Resources')
class ProfessionsApi(remote.Service):

    @endpoints.method(ProfessionObject, Response,
                        name = 'create_profession',
                        path = 'create_profession',
                        http_method = 'POST')
    def create_profession(self, request):
        f = Fields.query(Fields.slug == request.field_slug).get()
        p = Professions(name = request.name, slug = request.slug, field = f.key)
        p.put()
        return Response(message = "Profession created successfully", success = True)

    @endpoints.method(message_types.VoidMessage, ProfessionObjects,
                        name = 'get_professions',
                        path = 'get_professions',
                        http_method = 'GET')
    def get_professions(self, request):
        professions = Professions.query().order(Professions.name)
        all_professions = [ProfessionObject(name = p.name, slug = p.slug) for p in professions]
        return ProfessionObjects(professions = all_professions)


class ProjectObject(messages.Message):
    title = messages.StringField(1)
    description = messages.StringField(2)
    founder = messages.StringField(3)
    project_type = messages.StringField(4)
    field = messages.StringField(5)
    professions = messages.StringField(6)
    token = messages.StringField(7)
    created = messages.StringField(8)

class ProjectObjects(messages.Message):
    projects = messages.MessageField(ProjectObject, 1, repeated = True)

@endpoints.api(name = 'projects', version = 'v1',
               description = 'Projects Management Resources')
class ProjectsApi(remote.Service):

    @endpoints.method(ProjectObject, Response,
                        name = 'create_project',
                        path = 'create_project',
                        http_method = 'POST')
    def create_project(self, request):
        u = Users.by_token(request.token)
        if u:
            p = Projects()
            p.title = request.title
            p.description = request.description
            p.founder = u.key
            p.project_type = ProjectTypes.query(ProjectTypes.name == request.project_type).get().key
            p.field = Fields.query(Fields.name == request.field).get().key
            profession_keys = []
            professions = request.professions.split(", ")
            print professions
            for i in professions:
                if i != "":
                    p_key = Professions.query(Professions.name == i).get()
                    profession_keys.append(p_key.key)
            p.professions = profession_keys
            p.put()
            return Response(message = "Project created successfully", success = True)
        return Response(message = "Failed to create a project", success = False)


    @endpoints.method(message_types.VoidMessage, ProjectObjects,
                        name = 'get_projects',
                        path = 'get_projects',
                        http_method = 'GET')
    def get_projects(self, request):
        projects = Projects.query().order(-Projects.created)
        all_projects = [ProjectObject(title = p.title, created = p.created.strftime("%B %d, %Y"), project_type = p.project_type.get().name, field = p.field.get().name, founder = p.founder.get().first_name + " " + p.founder.get().last_name) for p in projects]
        return ProjectObjects(projects = all_projects)


application = endpoints.api_server([UsersApi, FieldsApi, ProfessionsApi, ProjectsApi])