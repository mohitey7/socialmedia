from .models import *
from .serializers import *
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from django.db.models import Q, Case, When
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle


class UserSignup(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if not serializer.is_valid():
            response = {"statusCode" : 400, "message" : serializer.errors}
            return Response(response, status=400)
        serializer.save()
        return Response(serializer.data, status=201)
    
class UserLogin(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            response = {"statusCode" : 400, "message" : serializer.errors}
            return Response(response, status=400)
        
        email = serializer.validated_data['email'].lower()
        password = serializer.validated_data['password']

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'statusCode': '404', 'message': 'User does not exist'}, status=404)
        
        if not check_password(password, user.password):
            return Response({'statusCode': '400', 'message': 'Invalid password'}, status=400)
        
        token, _ = Token.objects.get_or_create(user=user)
        data = {'id': user.id, 'email': user.email, 'token': token.key}
        return Response({'statusCode': '200', 'data': data}, status=200)
    
class UserLogout(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        request.user.auth_token.delete()
        response = {
            "statusCode" : 200,
            "message" : "Logout successful"
        }
        return Response(response, status=200)
    

class UserSearch(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    class CustomPagination(PageNumberPagination):
        page_size = 10
        page_size_query_param = 'page_size'
        max_page_size = 10

        def get_paginated_response(self, data):
            return Response({
                'statusCode': 200,
                'records': self.page.paginator.count,
                'data': data,
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages
            })
        
    pagination_class = CustomPagination

    def post(self, request):
        search = request.data.get('search_key')
        if search is None:
            return Response({'statusCode': '400', 'message': 'Please provide search_key parameter'}, status=400)

        user = User.objects.filter(email=search.lower()).first()
        if user:
            return Response({'statusCode': '200', 'data': UserSearchSerializer(user).data}, status=200)
        
        users = User.objects.filter(Q(firstname__icontains=search) | Q(lastname__icontains=search))
        if users:
            paginator = self.pagination_class()
            paginated_users = paginator.paginate_queryset(users, request)
            serializer = UserSearchSerializer(paginated_users, many=True)
            return paginator.get_paginated_response(serializer.data)
            # return Response({'statusCode': '200', 'data': UserSearchSerializer(users, many=True).data}, status=200)
        
        return Response({'statusCode': '404', 'message': 'No user found'}, status=404)

class FriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    class CustomThrottle(UserRateThrottle):
        rate = '3/minute'

    throttle_classes = [CustomThrottle]

    def post(self, request):
        data = request.data
        data['sender'] = request.user.id
        serializer = FriendRequestSerializer(data=data)
        if not serializer.is_valid():
            return Response({'statusCode': 400, 'message': serializer.errors}, status=400)
        object = serializer.save()
        data = {
            'request_id': object.id,
            'sender': {
                'id': object.sender.id,
                'sender_name': object.sender.firstname + ' ' + object.sender.lastname
             }, 'receiver': {
                 'id': object.receiver.id,
                 'receiver_name': object.receiver.firstname + ' ' + object.receiver.lastname}
            }
        return Response({'statusCode': 201, 'message': 'Friend request sent successfully', 'data': data}, status=201)
    
class FriendRequestAction(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def post(self, request):
        data = request.data
        data['receiver'] = request.user.id
        serializer = FriendRequestActionSerializer(data=data)

        if not serializer.is_valid():
            return Response({'statusCode': 400, 'message': serializer.errors}, status=400)
        
        friend_request = FriendRequest.objects.get(id=data['id'])
        friend_request.status = data['status']
        friend_request.save()

        if data['status'] == 'accepted':
            Friendship.objects.create(user1=friend_request.sender, user2=friend_request.receiver, friend_request=friend_request)
        return Response({'statusCode': 200, 'message': 'Friend request updated successfully'}, status=200)
    
class FriendList(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user
        friend_ids = Friendship.objects.filter(Q(user1=user) | Q(user2=user)).annotate(
            friend_id=Case(
                When(user1=user, then='user2_id'),
                default='user1_id',
            )
        ).values_list('friend_id', flat=True)
        friends = User.objects.filter(id__in=friend_ids)
        serializer = FriendListSerializer(friends, many=True)
        return Response({'statusCode': 200, 'data': serializer.data}, status=200)
    
class PendingRequests(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        user = request.user
        pending_requests = FriendRequest.objects.filter(receiver=user, status='pending')
        serializer = PendingFriendRequests(pending_requests, many=True)
        return Response({'statusCode': 200, 'data': serializer.data}, status=200)