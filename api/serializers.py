from datetime import datetime
from rest_framework import serializers
from auth_.models import Seller, User
from auth_.serializers import SellerSerializer, UserSimpleSerializer, SellerSimpleSerializer, UserSimplestSerializer
from .models import Product, ShippingAddress, Category, Comment, Order


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=100)

    def validate(self, attrs):
        if not attrs.__contains__('name'):
            raise serializers.ValidationError('Name field is required')
        try:
            Category.objects.get(name=attrs['name'])
        except Category.DoesNotExist:
            return attrs
        raise serializers.ValidationError('Category with that name already exists')
        # return attrs

    def create(self, validated_data):
        return Category.objects.create(**validated_data)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['address']


class ProductSellerSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer()

    class Meta:
        model = Seller
        fields = ['user', 'shopName', 'location', 'shopEmail', 'is_active']


class ProductSerializer(serializers.ModelSerializer):
    location = serializers.IntegerField()
    seller = ProductSellerSerializer(read_only=True)
    is_active = serializers.BooleanField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'description', 'price', 'amount', 'location', 'seller', 'is_active']


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'is_active']


class ProductSimpleSerializer(OrderProductSerializer):
    seller = SellerSimpleSerializer()

    class Meta:
        model = Product
        fields = OrderProductSerializer.Meta.fields + ['seller']


class ProductUpdateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    location = serializers.IntegerField(required=False)
    is_active = serializers.BooleanField(required=False)
    price = serializers.IntegerField(required=False)
    amount = serializers.IntegerField(required=False)

    class Meta:
        model = Product
        fields = ['description', 'price', 'amount', 'location', 'is_active']

    def validate(self, attrs):
        if not attrs.__contains__('description') and not attrs.__contains__('price') and\
                not attrs.__contains__('amount') and not attrs.__contains__('location') \
                and not attrs.__contains__('is_active'):
            raise serializers.ValidationError('No data to update')

        return attrs

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.location = validated_data.get('location', instance.location)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance

    def delete(self, instance):
        print('delete', instance)
        return instance


class ProductCreateSerializer(serializers.ModelSerializer):
    location = serializers.IntegerField()
    seller = SellerSimpleSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'amount', 'location', 'seller']

    def validate(self, attrs):
        if not attrs.__contains__('name'):
            raise serializers.ValidationError('Name is required')
        if not attrs.__contains__('category'):
            raise serializers.ValidationError('Category is required')
        if not attrs.__contains__('description'):
            raise serializers.ValidationError('Description is required')
        if not attrs.__contains__('price'):
            raise serializers.ValidationError('Price is required')
        if not attrs.__contains__('amount'):
            raise serializers.ValidationError('Amount is required')
        if not attrs.__contains__('location'):
            raise serializers.ValidationError('Location is required')
        return attrs

    def create(self, validated_data):
        return Product.objects.create(
            name=validated_data['name'],
            category=validated_data['category'],
            description=validated_data['description'],
            price=validated_data['price'],
            amount=validated_data['amount'],
            location=validated_data['location'],
            seller=self.context['request'].user.seller
        )


class CommentSerializer(serializers.ModelSerializer):
    user = UserSimplestSerializer(read_only=True)
    # product = ProductSimpleSerializer(read_only=True)
    published = serializers.DateField()

    class Meta:
        model = Comment
        fields = ['user', 'title', 'body', 'published']


class CommentCreateSerializer(serializers.ModelSerializer):
    user = UserSimplestSerializer(read_only=True)
    product = ProductSimpleSerializer(read_only=True)
    published = serializers.DateField(required=False)
    title = serializers.CharField()
    body = serializers.CharField()

    class Meta:
        model = Comment
        fields = ['user', 'product', 'published', 'title', 'body']

    def validate(self, attrs):
        if not attrs.__contains__('title'):
            raise serializers.ValidationError('Title is required')
        title = attrs['title']
        if not attrs.__contains__('body'):
            raise serializers.ValidationError('Body of comment is required')
        if len(title) < 3:
            raise serializers.ValidationError('Title is too short')
        return attrs

    def create(self, validated_data):
        comment = Comment.objects.create(
            user=self.context['request'].user,
            product=self.context['product'],
            title=validated_data['title'],
            body=validated_data['body'],
        )
        comment.save()
        return comment


class ShippingAddressSerializer(serializers.Serializer):
    address = serializers.CharField()

    class Meta:
        model = ShippingAddress
        fields = ['address']


class OrderSerializer(serializers.ModelSerializer):
    shipping_address = ShippingAddressSerializer(read_only=True)
    products = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'products', 'total', 'date_created', 'shipping_address']


class OrderCreateSerializer(serializers.ModelSerializer):
    customer = UserSimplestSerializer(read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)
    products = ProductSimpleSerializer(read_only=True, many=True)
    total = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ['customer', 'products', 'total', 'shipping_address']

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        customer = validated_data['customer']
        add = validated_data['shipping_address']
        products = validated_data['products']
        total = validated_data['total']
        order = Order.orders.create(
            customer=customer,
            products=products,
            address=add,
            total=total)
        order.products.set(products)
        return order
