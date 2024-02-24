import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from myapp.models import PlaceModel
from django.contrib.auth import get_user_model
from myapp.models import AppUser
from graphql_jwt.decorators import login_required


class AppUserType(DjangoObjectType): 
    class Meta:
        model = get_user_model()
        exclude = ('password', )

class PlaceType(DjangoObjectType):
    class Meta:
        model = PlaceModel
    
class Query(graphene.ObjectType):
    app_users = graphene.List(AppUserType)
    logged_in = graphene.Field(AppUserType)
    
    def resolve_app_users(self, info):
        return get_user_model().objects.all()
    
    @login_required
    def resolve_logged_in(self, info):
        return info.context.user
    
    places = graphene.List(PlaceType)
    place = graphene.Field(PlaceType, id=graphene.ID())
    
    def resolve_places(self, info):
        return PlaceModel.objects.all()
    
    def resolve_place(self, info, id):
        return PlaceModel.objects.get(pk=id)
           

class CreateAppUser(graphene.Mutation):
    app_user = graphene.Field(AppUserType)
    class Arguments:
        email = graphene.String(required=True)
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        
    def mutate(self, info, email, username, password):
        app_user = get_user_model()
        new_user = app_user(email=email, username=username)
        new_user.set_password(password)
        new_user.save()
        return CreateAppUser(app_user=new_user)

class CreatePlace(graphene.Mutation):
    id = graphene.Int()
    place_name = graphene.String()
    place_distance = graphene.Int()
    place_date = graphene.String()
    place_star = graphene.Float()
    place_price = graphene.Int()
    place_img = graphene.JSONString()
    place_des = graphene.String()

    class Arguments:
        place_name = graphene.String()
        place_distance = graphene.Int()
        place_date = graphene.String()
        place_star = graphene.Float()
        place_price = graphene.Int()
        place_img = graphene.JSONString()
        place_des = graphene.String()
        
    def mutate(self, info, place_name, place_distance, place_date, place_star, place_price, place_img, place_des):
        place = PlaceModel(place_name=place_name, place_distance=place_distance, place_date=place_date, place_star=place_star, place_price=place_price, place_img=place_img, place_des=place_des)
        place.save()
        
        return CreatePlace(
            id = place.id,
            place_name = place.place_name,
            place_distance = place.place_distance,
            place_date = place_date,
            place_star = place_star,
            place_price = place_price,
            place_img = place_img,
            place_des = place_des
        )

class DeleteItemMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        try:
            item = PlaceModel.objects.get(pk=id)
            item.delete()
            return DeleteItemMutation(success=True, message=f"Item with ID {id} deleted successfully.")
        except PlaceModel.DoesNotExist:
            return DeleteItemMutation(success=False, message=f"Item with ID {id} does not exist.")
 
      
class Mutation(graphene.ObjectType):
    create_place = CreatePlace.Field()
    delete_place = DeleteItemMutation.Field()
    create_app_user = CreateAppUser.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
