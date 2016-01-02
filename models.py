'''
	Models
'''

# NDB Model Libraries
from google.appengine.ext import ndb

# user auth
from user_authentication import *


# token libraries
import uuid
import hmac

try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha


class BaseModel(ndb.Model):
	'''
		BaseModel - inherited by all other models.
	'''

	created = ndb.DateTimeProperty(auto_now_add = True)
	updated = ndb.DateTimeProperty(auto_now = True)

class Roles(ndb.Model):
	pass


class Users(BaseModel):
	'''
		Contains user information.
	'''

	email = ndb.StringProperty(required = True)
	password_hash = ndb.StringProperty(required = True)
	first_name = ndb.StringProperty(required = True)
	last_name = ndb.StringProperty(required = True)
	active = ndb.BooleanProperty(default = True)
	profile_image = ndb.KeyProperty(kind = 'Images')
	profile_cover_image = ndb.KeyProperty(kind = 'Images')
	profession = ndb.KeyProperty(kind = 'Professions')
	friends = ndb.KeyProperty(kind = 'Users', repeated = True)

	@classmethod
	def by_email(cls, email):
		user = cls.query(cls.email == email).get()
		return user

	@classmethod
	def by_token(cls, token):
		t = Tokens.query(Tokens.token == token).get()
		if t:
			u = Users
			return t.user.get()
		return False

	@classmethod
	def login(cls, email, password):
		# returns a user and a token value
		user = cls.by_email(email)
		if user and valid_pw(email, password, user.password_hash):
			t = Tokens()
			t.user = user.key
			t.token = t.generate_key()
			t.put()
			return [user, t.token]

	@classmethod
	def create_user(cls, user):
		u = cls.by_email(user.email)
		if not u:
			u = Users()
			u.email = user.email
			u.password_hash = make_pw_hash(user.email, user.password)
			u.first_name = user.first_name
			u.last_name = user.last_name
			u.put()
			t = Tokens()
			t.user = u.key
			t.token = t.generate_key()
			t.put()
			return [u, t.token]

	@classmethod
	def add_friend(cls, friend1_id, friend2_id):
		friend1 = cls.get_by_id(int(friend1_id))
		friend2 = cls.get_by_id(int(friend2_id))
		if friend1.key not in friend2.friends:
			friend1.friends.append(friend2.key)
			friend2.friends.append(friend1.key)
			friend1.put()
			friend2.put()
			return True
		return False

	@classmethod
	def remove_friend(cls, friend1_id, friend2_id):
		friend1 = cls.get_by_id(int(friend1_id))
		friend2 = cls.get_by_id(int(friend2_id))
		if friend1.key in friend2.friends:
			friend1.friends.remove(friend2.key)
			friend2.friends.remove(friend1.key)
			friend1.put()
			friend2.put()
			return True
		return False

class Tokens(BaseModel):
	'''
		Contains tokens for authentication.
	'''

	token = ndb.StringProperty(required = True)
	user = ndb.KeyProperty(kind = 'Users', required = True)
	lifespan = ndb.DateTimeProperty()

	def generate_key(self):
		new_uuid = uuid.uuid4()
		# Hmac that beast.
		return hmac.new(str(new_uuid), digestmod=sha1).hexdigest()


class Projects(BaseModel):
	'''
		Contains project information.
	'''
	title = ndb.StringProperty(required = True)
	description = ndb.TextProperty(required = True)
	founder = ndb.KeyProperty(kind = 'Users', required = True)
	contributors = ndb.KeyProperty(kind = 'Users', repeated = True)
	managers = ndb.KeyProperty(kind = 'Users', repeated = True)
	field = ndb.KeyProperty(kind = 'Fields')
	professions = ndb.KeyProperty(kind = 'Professions', repeated = True)
	card = ndb.KeyProperty(kind = 'Images')
	votes = ndb.IntegerProperty(default = 0)
	visits = ndb.IntegerProperty(default = 0)
	project_type = ndb.KeyProperty(kind = "ProjectTypes")
	request_to_join = ndb.KeyProperty(kind = 'Users', repeated = True)


class ProjectTypes(BaseModel):
	name = ndb.StringProperty(required = True)
	slug = ndb.StringProperty(required = True)


class ProjectPages(BaseModel):
	'''
		Contains the project advert page, 
		that is available to the public.
	'''
	content = ndb.TextProperty(required = True)
	images = ndb.KeyProperty(kind = 'Images', repeated = True)
	project = project_type = ndb.KeyProperty(kind = "Projects")


class Fields(BaseModel):
	'''
		Stores fields (i.e. Software, AI, Biology,
		Medicine, etc...)
	'''
	name = ndb.StringProperty(required = True)
	slug = ndb.StringProperty(required = True)
	icon = ndb.StringProperty()  

class Professions(BaseModel):
	'''
		Stores professions (i.e. Software Engineer, 
		Graphic Artist, etc...)
	'''
	name = ndb.StringProperty(required = True)
	slug = ndb.StringProperty(required = True)
	icon = ndb.StringProperty()
	field = ndb.KeyProperty(kind = 'Fields')

class Images(BaseModel):
	'''
		Stores images - obviously.
	'''
	image = ndb.BlobProperty(required = True)

class Invitations(BaseModel):
	'''
		Invitations to projects.
		Users are popped off as actions are taken.
	'''
	project = ndb.KeyProperty(kind = 'Projects')
	invited_user = ndb.KeyProperty(kind = 'Users')

class FriendsPending(BaseModel):
	'''
		Contains pending friend requests.
	'''
	requester = ndb.KeyProperty(kind = 'Users')
	reciever = ndb.KeyProperty(kind = 'Users')

	@classmethod
	def send_request(cls, requester, reciever):
		check = cls.query(cls.requester == requester.key, cls.reciever == reciever.key)
		if check.count() > 0:
			return False
		f = cls(requester = requester.key, reciever = reciever.key)
		f.put()
		m = Messages(message = "Friend Request", to_user = reciever.key, from_user = null)
		m.put()

	@classmethod
	def accept_request(cls, requester, reciever):
		check = cls.query(cls.requester == requester.key, cls.reciever == reciever.key)
		print check.count()
		if check.count() > 0:
			if Friends.add_friend(reciever, requester) == False:
				return False
			check.get().key.delete()
			return True
		return False