# LAU LE - https://levanlau.net
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# 
from flask_graphql import GraphQLView
import graphene
from graphene import relay, Field
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType

app = Flask(__name__)
app.secret_key = 'my_secret_key'

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(    
    os.environ.get('DB_USER', 'your_user'),
    os.environ.get('DB_PASS', 'your_password'),
    os.environ.get('DB_HOST', 'db'),
    os.environ.get('DB_NAME', 'your_db')
)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)

    def __repr__(self):
        return self.name

# end database

# graphQL
class CustomNode(graphene.Node):
    class Meta:
        name = 'myNode'

    @staticmethod
    def to_global_id(type, id):
        return id

class UserSchema(SQLAlchemyObjectType):    
    class Meta:
        model = User
        interfaces = (CustomNode,)

class Query(graphene.ObjectType):
    node = relay.Node.Field()    

    all_users = SQLAlchemyConnectionField(UserSchema.connection)
    getUserById = Field(UserSchema, user_id=graphene.Int(required=True))    

    def resolve_getUserById(self, info, user_id):
        user = User.query.filter_by(id=user_id).first()
        return user

class AddUserMutation(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)

    user = graphene.Field(lambda: UserSchema)

    def mutate(self, info, name, email):
        user = User(
            name=name,
            email=email
        )

        db.session.add(user)
        db.session.commit()

        return AddUserMutation(user=user)

class DeleteUserMutation(graphene.Mutation):

    class Arguments:
        user_id = graphene.Int(required=True)        

    user = graphene.Field(lambda: UserSchema)

    def mutate(self, info, user_id):
        user = User.query.filter_by(id=user_id).first()

        db.session.delete(user)
        db.session.commit()

        return DeleteUserMutation(user=user)

class UpdateUserMutation(graphene.Mutation):

    class Arguments:
        user_id = graphene.Int(required=True) 
        name = graphene.String(required=True)
        email = graphene.String(required=True)

    user = graphene.Field(lambda: UserSchema)

    def mutate(self, info, user_id, name, email):
        user = User.query.filter_by(id=user_id).first()
        user.name = name
        user.email = email
        db.session.commit()

        return UpdateUserMutation(user=user)

class Mutation(graphene.ObjectType):
    addUser = AddUserMutation.Field()
    deleteUser = DeleteUserMutation.Field()
    updateUser = UpdateUserMutation.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=schema,
        graphiql=True
    ),
)
# end graphQL

@app.route('/')
def hello_world():
    return "Hello Flask framework"   

if __name__ == '__main__':
    app.run(debug=True)
