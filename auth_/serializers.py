from rest_framework import serializers
from api.models import Product
from .models import User, Seller, Profile
from django.core.validators import validate_email


class CategorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)


class ProductSimplestSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price']


class UserSimplestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class UserSimpleSerializer(UserSimplestSerializer):
    class Meta:
        model = User
        fields = UserSimplestSerializer.Meta.fields + ['location', 'is_seller']


class UserSerializer(UserSimpleSerializer):
    class Meta:
        model = User
        fields = UserSimpleSerializer.Meta.fields + ['age', 'gender']


class SellerSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['shopName', 'location', 'shopEmail', 'is_active']


class SellerSerializer(SellerSimpleSerializer):
    user = UserSimpleSerializer()

    class Meta:
        model = Seller
        fields = SellerSimpleSerializer.Meta.fields + ['user']


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'age', 'gender', 'cardDetails', 'location')

    def validate(self, attrs):
        password = attrs['password']
        if not attrs.__contains__('email'):
            raise serializers.ValidationError('email is required')
        email = attrs['email']
        if not attrs.__contains__('location'):
            raise serializers.ValidationError('location is required')
        if not attrs.__contains__('age'):
            raise serializers.ValidationError('age is required')
        if not attrs.__contains__('gender'):
            raise serializers.ValidationError('gender is required')
        if not attrs.__contains__('cardDetails'):
            raise serializers.ValidationError('cardDetails is required')
        if len(password) < 8:
            raise serializers.ValidationError('Password is too short, minimum length is 8')
        try:
            validate_email(email)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(f"bad email, details: {e}")
        return attrs

    def create(self, validated_data):
        user = User.users.create_user(username=validated_data['username'],
                                      password=validated_data['password'],
                                      email=validated_data['email'],
                                      location=validated_data['location'],
                                      age=validated_data['age'],
                                      gender=validated_data['gender'],
                                      cardDetails=validated_data['cardDetails'],
                                      is_seller=False)
        return user


class RegisterSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ('shopEmail', 'shopName', 'location')

    def validate(self, attrs):
        if not attrs.__contains__('shopName'):
            raise serializers.ValidationError('email is required')
        shopName = attrs['shopName']
        if not attrs.__contains__('shopEmail'):
            raise serializers.ValidationError('location is required')
        shopEmail = attrs['shopEmail']
        if not attrs.__contains__('location'):
            raise serializers.ValidationError('age is required')
        if len(shopName) < 4:
            raise serializers.ValidationError('Shop Name is too short, minimum length is 8')
        try:
            validate_email(shopEmail)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(f"Bad email, details: {e}")
        return attrs

    def create(self, validated_data):
        user_obj = self.context['request'].user
        seller = Seller.objects.create(user=user_obj,
                                       shopName=validated_data['shopName'],
                                       shopEmail=validated_data['shopEmail'],
                                       location=validated_data['location'])
        user_obj.is_seller = True
        user_obj.save()
        return seller


class ProfileSerializer(serializers.ModelSerializer):
    products = ProductSimplestSerializer(read_only=True, many=True)
    img = serializers.ImageField()

    class Meta:
        model = Profile
        fields = ['products', 'img']


class EditProfile(serializers.ModelSerializer):
    img = serializers.ImageField()

    class Meta:
        model = Profile
        fields = ['img']

    def update(self, instance, validated_data):
        instance.img = validated_data.get('image', instance.img)
        instance.save()
        return instance
