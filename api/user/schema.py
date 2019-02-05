import graphene
from graphene_sqlalchemy import (SQLAlchemyObjectType)
from sqlalchemy import func
from graphql import GraphQLError

from api.user.models import User as UserModel
from api.notification.models import Notification as NotificationModel
from helpers.auth.user_details import get_user_from_db
from helpers.auth.authentication import Auth
from utilities.validator import verify_email
from helpers.pagination.paginate import Paginate, validate_page
from helpers.auth.error_handler import SaveContextManager
from helpers.email.email import email_invite
from helpers.user_filter.user_filter import user_filter
from utilities.utility import update_entity_fields
from api.role.schema import Role
from api.role.models import Role as RoleModel


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel


class CreateUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        location = graphene.String(required=False)
        name = graphene.String(required=True)
        picture = graphene.String()

    user = graphene.Field(User)

    def mutate(self, info, **kwargs):
        user = UserModel(**kwargs)
        if not verify_email(user.email):
            raise GraphQLError("This email is not allowed")
        with SaveContextManager(user, kwargs.get('email'), 'User email'):
            notification_settings = NotificationModel(user_id=user.id)
            notification_settings.save()
            return CreateUser(user=user)


class PaginatedUsers(Paginate):
    users = graphene.List(User)

    def resolve_users(self, info):
        page = self.page
        per_page = self.per_page
        query = User.get_query(info)
        active_user = query.filter(UserModel.state == "active")
        exact_query = user_filter(active_user, self.filter_data)
        if not page:
            return exact_query.order_by(func.lower(UserModel.email)).all()
        page = validate_page(page)
        self.query_total = exact_query.count()
        result = exact_query.order_by(
            func.lower(UserModel.name)).limit(per_page).offset(page * per_page)
        if result.count() == 0:
            return GraphQLError("No users found")
        return result


class Query(graphene.ObjectType):
    users = graphene.Field(
        PaginatedUsers,
        page=graphene.Int(),
        per_page=graphene.Int(),
        location_id=graphene.Int(),
        role_id=graphene.Int(),
    )
    user = graphene.Field(
        lambda: User,
        email=graphene.String())

    def resolve_users(self, info, **kwargs):
        response = PaginatedUsers(**kwargs)
        return response

    def resolve_user(self, info, email):
        query = User.get_query(info)
        return query.filter(UserModel.email == email).first()


class DeleteUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        state = graphene.String()

    user = graphene.Field(User)

    @Auth.user_roles('Admin')
    def mutate(self, info, email, **kwargs):
        query_user = User.get_query(info)
        active_user = query_user.filter(UserModel.state == "active")
        exact_query_user = active_user.filter(UserModel.email == email).first()
        user_from_db = get_user_from_db()
        if not verify_email(email):
            raise GraphQLError("Invalid email format")
        if not exact_query_user:
            raise GraphQLError("User not found")
        if user_from_db.email == email:
            raise GraphQLError("You cannot delete yourself")
        update_entity_fields(exact_query_user, state="archived", **kwargs)
        exact_query_user.save()
        return DeleteUser(user=exact_query_user)


class ChangeUserRole(graphene.Mutation):
    class Arguments:

        email = graphene.String(required=True)
        role_id = graphene.Int()

    user = graphene.Field(User)

    @Auth.user_roles('Admin')
    def mutate(self, info, email, **kwargs):
        query_user = User.get_query(info)
        active_user = query_user.filter(UserModel.state == "active")
        exact_user = active_user.filter(UserModel.email == email).first()
        if not exact_user:
            raise GraphQLError("User not found")

        if not exact_user.roles:
            raise GraphQLError('user has no role')

        new_role = RoleModel.query.filter_by(id=kwargs['role_id']).first()
        if not new_role:
            raise GraphQLError('invalid role id')

        exact_user.roles[0] = new_role
        exact_user.save()
        return ChangeUserRole(user=exact_user)


class CreateUserRole(graphene.Mutation):

    class Arguments:
        user_id = graphene.Int(required=True)
        role_id = graphene.Int(required=True)
    user_role = graphene.Field(User)

    def mutate(self, info, **kwargs):
        user = User.get_query(info)
        exact_user = user.filter_by(id=kwargs['user_id']).first()

        if not exact_user:
            raise GraphQLError('User not found')

        role = Role.get_query(info)
        exact_role = role.filter_by(id=kwargs['role_id']).first()

        if not exact_role:
            raise GraphQLError('Role id does not exist')

        if exact_user.roles:
            raise GraphQLError('user already has a role')

        exact_user.roles.append(exact_role)
        exact_user.save()

        return CreateUserRole(user_role=exact_user)


class InviteToConverge(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    email = graphene.String()

    @Auth.user_roles('Admin')
    def mutate(self, info, email):
        query_user = User.get_query(info)
        active_user = query_user.filter(UserModel.state == "active")
        user = active_user.filter(UserModel.email == email).first()
        if user:
            raise GraphQLError("User already joined Converge")
        admin = get_user_from_db()
        email_invite(email, admin.__dict__["name"])
        return InviteToConverge(email=email)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    delete_user = DeleteUser.Field()
    change_user_role = ChangeUserRole.Field()
    invite_to_converge = InviteToConverge.Field()
    create_user_role = CreateUserRole.Field()
