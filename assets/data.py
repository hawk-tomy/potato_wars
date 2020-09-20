class BaseMember:
    def __init__(self,**kwargs):
        if set(kwargs.keys()) >= {'id'}:
            self.id = kwargs['id']
        else:
            raise TypeError('missing argument')

    def __eq__(self,other):
        return isinstance(other,BaseMember) and self.id == other.id

    def __ne__(self,other):
        return not self.__eq__(other)

    def __int__(self):
        return self.id

    def __repr__(self):
        return f'BaseMember(**{self.return_dict()})'

    def __str__(self):
        return f'<BaseMember id:{self.id}>'

    def __bool__(self):
        return bool(self.id)

    def return_dict(self):
        return {'id':self.id,'is_sub': False}

class Country:
    """
    id -> int
    name -> str
    header -> int(dicord_id)
    members -> dict
    deleted -> boolen
    """
    def __init__(self,**kwargs):
        if set(kwargs.keys()) >= {'id','name','header','members','deleted'}:
            self.id = kwargs['id']
            self.name = kwargs['name']
            self.header = kwargs['header']
            self.members = kwargs['members']
            self.deleted = kwargs['deleted']
        else:
            raise TypeError('missing argument')

    def __eq__(self,other):
        return isinstance(other, Country) and self.id == other.id

    def __ne__(self,other):
        return not self.__eq__(other)

    def __int__(self):
        return self.id

    def __repr__(self):
        return f'Country(**{self.return_dict()})'

    def __str__(self):
        return f'<Country name:{self.name},id:{self.id},members:{self.members},header:{self.header},deleted:{self.deleted}>'

    def __bool__(self):
        return bool(self.members)

    def __len__(self):
        return len(self.members)

    def add_member(self,id):
        if id in self.members:
            return
        self.members[id] ={'role':'normal'}

    def remove_member(self,member_id):
        if member_id in self.members:
            self.members.remove(member_id)

    def delete(self):
        self.deleted = True
        for member_id in list(self.members.keys()):
            self.remove_member(member_id)

    def return_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'deleted':self.deleted,
            'members':self.members,
            'header':self.header,
        }

class SessionMember(BaseMember):
    """
    id -> int
    has_sub -> boolen
    sub_id -> int
    country -> dict
    """
    def __init__(self,**kwargs):
        if set(kwargs.keys()) >= {'id','has_sub','sub_id','country'}:
            super().__init__(**kwargs)
            self.has_sub = kwargs['has_sub']
            self.sub_id = kwargs['sub_id']
            self.country = kwargs['country']
            self.is_sub = False
            if ((self.has_sub and self.sub_id is None) or
                (not self.has_sub and self.sub_id is not None)):
                raise ValueError(f'has_sub is {self.has_sub}. but sub_id is {self.sub_id}')
        else:
            raise ValueError('missing argument')

    def __repr__(self):
        return f'Member(**{str(self.return_dict())})'

    def return_dict(self):
        return {
            'id':self.id,
            'has_sub':self.has_sub,
            'sub_id':self.sub_id,
            'is_sub':False,
            'country':self.country,
        }

    def set_sub(self,id):
        self.has_sub = True
        self.sub_id = id

    def set_country(self,id,role):
        self.country = {'id':id,'role':role}

    def remove_country(self):
        self.country = None

class SubMember(BaseMember):
    def __init__(self,**kwargs):
        if set(kwargs.keys()) >= {'id','main_id'}:
            self.id = kwargs['id']
            self.main_id = kwargs['main_id']
            self.is_sub = True
        else:
            raise TypeError('missing argument')

    def __repr__(self):
        return f'SubMember(**{self.return_dict()})'

    def return_dict(self):
        return {'id':self.id, 'main_id':self.main_id, 'is_sub':True}

class Session:
    """
    id -> int
    country -> list
    members -> list
    """
    def __init__(self,**kwargs):
        if set(kwargs.keys()) >= {'id','country','members'}:
            self.id = kwargs['id']
            self.country = [Country(**c) for c in kwargs['country']]
            self.members = [SubMember(**m) if m['is_sub'] else SessionMember(**m) for m in kwargs['members']]
        else:
            raise TypeError('missing argument')

    def __eq__(self,other):
        return isinstance(other,Session) and self.id == other.id

    def __ne__(self,other):
        return not self.__eq__(other)

    def __int__(self):
        return self.id

    def __repr__(self):
        return f"Session(**{{'id':{self.id},'country':{self.country},'members':{self.members}}})"

    def __str__(self):
        c_list = [str(c) for c in self.country]
        m_list = [str(m) for m in self.members]
        return f'<id:{self.id},country:{c_list},members:{m_list}>'

    def __bool__(self):
        return bool(self.id)

    def return_dict(self):
        return {
            'id':self.id,
            'country':[c.return_dict() for c in self.country],
            'members':[m.return_dict() for m in self.members],
        }

    def get_country_dict(self):
        return {c.id: c for c in self.country if not c.deleted}

    def get_country_by_id(self,id):
        c = self.get_country_dict()
        return c[id]

    def get_member_dict(self):
        return {m.id: m for m in self.members}

    def get_member_by_id(self,id):
        m = self.get_member_dict()
        return m[id]

    def country_create(self,**kwargs):
        if set(kwargs.keys()) >= {'name','roles','members'}:
            id_ = len(self.country)
            self.country.append(Country(**{'id':id_},**kwargs))
            return id_
        else:
            raise TypeError('missing argment')

    def country_delete(self,country_id):
        self.get_country_by_id(country_id).delete()
        for m in self.members:
            if m.is_sub:
                continue
            elif m.country is not None and m.country['id'] == country_id:
                m.country = None

    def country_add_members(self,country_id,*members_id):
        for member_id in members_id:
            self.get_country_by_id(country_id).add_member(member_id)
            self.get_member_by_id(member_id).set_country(country_id,'normal')

    def member_add(self,**kwargs):
        self.members.append(SessionMember(**kwargs))

    def member_set_sub(self,member_id,sub_id):
        if sub_id in self.get_member_dict():
            self.get_member_by_id(member_id).set_sub(sub_id)
            for m in self.members:
                if m.id == sub_id:
                    m = SubMember(**{'id':sub_id,'main_id':main_id})
