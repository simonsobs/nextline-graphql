import strawberry

from nextlinegraphql.plugins.ctrl.schema import Mutation, Query, Subscription

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)
