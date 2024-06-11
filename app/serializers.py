from rest_framework import serializers
from .models import *

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data['email'].lower(),
            firstname = validated_data['firstname'],
            lastname = validated_data['lastname'], password = None)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def to_representation(self, instance):
        data = {}
        data['id'] = instance.id
        data['name'] = instance.firstname + ' ' + instance.lastname
        data['email'] = instance.email
        return {'statusCode': '201', 'data': data}

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ['email', 'password']

class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'firstname', 'lastname']

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['sender', 'receiver']

    def validate(self, data):
        if data['sender'] == data['receiver']:
            raise serializers.ValidationError('You cannot send a friend request to yourself.')
        if FriendRequest.objects.filter(sender=data['sender'], receiver=data['receiver'], status='pending').exists():
            raise serializers.ValidationError('A pending friend request already exists between these users.')
        if Friendship.objects.filter(user1=data['sender'], user2=data['receiver']).exists() or Friendship.objects.filter(user1=data['receiver'], user2=data['sender']).exists():
            raise serializers.ValidationError('Friendship already exists between these users.')
        return data
    
class FriendRequestActionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    status = serializers.ChoiceField(choices=['accepted', 'rejected'], required=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'receiver', 'status']

    def validate(self, data):
        id = data.get('id')
        receiver = data.get('receiver')
        status = data.get('status')

        friend_request = FriendRequest.objects.filter(id=id, receiver=receiver, status='pending').first()
        if not friend_request:
            raise serializers.ValidationError('Friend request not found.')

        if Friendship.objects.filter(user1=receiver, user2=friend_request.sender).exists() or Friendship.objects.filter(user1=friend_request.sender, user2=receiver).exists():
            raise serializers.ValidationError('Friendship already exists between these users.')

        return data

class FriendListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.firstname + ' ' + obj.lastname
    
class PendingFriendRequests(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'name']

    def get_name(self, obj):
        return obj.sender.firstname + ' ' + obj.sender.lastname