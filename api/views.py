from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from requests import Response
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
import json
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from auth_.serializers import UserSerializer, ProfileSerializer
from .models import Product, Comment, Order, Category, ShippingAddress
from .serializers import ProductSerializer, ProductCreateSerializer, ProductUpdateSerializer, CommentSerializer, \
    CommentCreateSerializer, CategorySerializer, OrderSerializer, OrderCreateSerializer
from auth_.models import User, Profile, Seller
from auth_.roles import SellerPermission
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import ProductFilter
from rest_framework.pagination import PageNumberPagination
from auth_.roles import SellerPermission, CustomerPermission
import logging
logger = logging.getLogger('api')


class ProfileBasket(viewsets.ViewSet,):
    queryset = Profile.objects.prefetch_related('products')
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    @action(detail=False, methods=['get'], url_path='view')
    def my_basket(self, request):
        ser = self.serializer_class(self.request.user.profile)
        return JsonResponse(ser.data, safe=False)

    @action(detail=True, methods=['post'], url_path='add')
    def add_to_basket(self, request, pk, *args, **kwargs):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist as e:
            return JsonResponse({'error': 'Product does not exist'})
        user = request.user
        try:
            if not user.profile.products.get(id=product.id) == Product.DoesNotExist:
                return JsonResponse({'error': 'This product is already on your tour list'})
        except Product.DoesNotExist as e:
            user.profile.products.add(product)
            logger.info(f"{user} added {product} to his profile")
            user.profile.save()
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        ser = self.serializer_class(self.request.user.profile)
        return JsonResponse(ser.data, safe=False)

    @action(methods=['delete'], detail=True, url_path='remove')
    def remove_from_basket(self, request, pk=None, *args, **kwargs):
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist as e:
            return JsonResponse({'error': 'Product does not exist'})
        user = request.user
        try:
            if user.profile.products.get(id=product.id) == Product.DoesNotExist:
                return JsonResponse({'error': 'This product is not on your tour list'})
            user.profile.products.remove(product)
            logger.info(f"{user} removed {product} from his profile")
            user.profile.save()
        except Product.DoesNotExist as e:
            return JsonResponse({'error': 'Product not found on your list'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        ser = self.serializer_class(self.request.user.profile)
        return JsonResponse(ser.data, safe=False)


class ProductViewSet(
                    # mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = (AllowAny,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter
    pagination_class = PageNumberPagination

    @action(methods=["GET", ], url_path='all', detail=False)
    def all(self, request, *args, **kwargs):
        serializer = ProductSerializer(Product.objects.all(), many=True)
        data = serializer.data
        return JsonResponse(data, safe=False)

    def list(self, request, *args, **kwargs):
        serializer = ProductSerializer(Product.objects.actual(), many=True)
        data = serializer.data
        return JsonResponse(data, safe=False)

    def retrieve(self, request, *args, **kwargs):
        try:
            serializer = ProductSerializer(self.get_object())
            data = serializer.data
            return JsonResponse(data, safe=False)
        except Product.DoesNotExist as e:
            return JsonResponse({'error': 'Product does not exist'})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    @action(methods=['POST'], detail=False, url_path='add', url_name='create',
            permission_classes=(SellerPermission,))
    def post_product(self, request):
        try:
            data = self.request.data
            serializer = ProductCreateSerializer(data=data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                logger.info(f"{request.user} created {serializer.data['name']}")
                return JsonResponse(serializer.data, status=status.HTTP_200_OK)
            else:
                logger.error(f"{request.user} try to post product with bad request")
                return HttpResponse('Invalid Product', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"{e}")
            return HttpResponse(e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['PUT', 'DELETE'], detail=True, url_path='edit', url_name='update',
            permission_classes=(IsAuthenticated, SellerPermission))
    def update_product(self, request, pk):
        if request.method == "PUT":
            product = Product.objects.get(id=pk)
            serializer = ProductUpdateSerializer(instance=product, data=self.request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                logger.info(f"{request.user} updated {product}")
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.data)
        elif request.method == "DELETE":
            product = self.queryset.get(id=pk)
            if product.seller == request.user.seller:
                logger.info(f"{request.user} deleted {product}")
                product.delete()
                return HttpResponse('deleted')
            else:
                return HttpResponse('You can delete only your products!')

    # @action(methods=['POST'], detail=False, url_path='category', url_name='create-category',
    #         permission_classes=(SellerPermission,))
    # def post_category(self, request):
    #     data = self.request.data
    #     serializer = CategorySerializer(data=data, context={'request': request})
    #     if serializer.is_valid():
    #         serializer.save()
    #         logger.info(f"{request.user} posted new category")
    #         return JsonResponse(serializer.data)
    #     return JsonResponse({'error': "Category name is not valid!"})


class CommentView(APIView):
    serializer_class = CommentSerializer

    def get(self, request, pk, *args, **kwargs):
        product = Product.objects.get(id=pk)
        serializer = CommentSerializer(product.comments.all(), many=True)
        return JsonResponse(serializer.data, safe=False)

    @permission_classes([IsAuthenticated, ])
    def post(self, request, pk, *args, **kwargs):
        data = self.request.data
        product = Product.objects.get(id=pk)
        serializer = CommentCreateSerializer(data=data, context={'request': request, 'product': product})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            logger.info(f"{request.user} posted comment on {product}")
            return JsonResponse(serializer.data)
        return HttpResponse("Comment is not valid!")
    # @action(methods=['POST'], detail=True, url_path='add', url_name='create',
    #         permission_classes=(IsAuthenticated,))
    # def post_comment(self, request):
    #     data = self.request.data
    #     serializer = CommentCreateSerializer(data=data, context={'request': request})
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #         return JsonResponse(serializer.data)
    #     else:
    #         return HttpResponse('Invalid Product')


class CategoryView(APIView):

    @permission_classes(SellerPermission,)
    def post(self, request, *args, **kwargs):
        data = self.request.data
        serializer = CategorySerializer(data=data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            logger.info(f"{request.user} posted new category")
            return JsonResponse(serializer.data)
        return JsonResponse({'error': "Category name is not valid!"})

    @permission_classes(AllowAny)
    def get(self, request, *args, **kwargs):
        serializer = CategorySerializer(Category.objects.all(), many=True)
        return JsonResponse(serializer.data, safe=False)


class Orders(viewsets.GenericViewSet,
             mixins.ListModelMixin,
             ):
    queryset = Order.orders.prefetch_related('customer')
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self, pk=0):
        if pk > 0:
            return self.request.user.customer_order.all()[int(pk)-1]
        return self.request.user.customer_order.all()

    def list(self, request, *args, **kwargs):
        serializer = OrderSerializer(self.get_queryset(), many=True)
        return JsonResponse(serializer.data, safe=False)

    def retrieve(self, request, pk, *args, **kwargs):
        try:
            serializer = OrderSerializer(self.get_queryset(pk=int(pk)))
            data = serializer.data
            return JsonResponse(data, safe=False)
        except Order.DoesNotExist as e:
            return JsonResponse({'error': 'Order does not exist'})
        except IndexError as e:
            return JsonResponse({'error': 'Order does not exist'})
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)})

    @action(methods=['POST'], detail=False, url_path='make',
            permission_classes=(IsAuthenticated,))
    def make_order(self, request):
        try:
            prods = self.request.user.profile.products.all()
            if len(prods) < 1:
                return JsonResponse({'error': 'Add products to your basket'})
            address = request.data['address']
            total = 0
            for prod in prods:
                total = prod.price + total
            try:
                add = ShippingAddress.objects.get(address=address)
            except ShippingAddress.DoesNotExist:
                add = ShippingAddress.objects.create(address=address, region=request.user.location)
            order_data = {
                'customer': self.request.user,
                'products': prods,
                'shipping_address': add,
                'total': total
            }
            ser = OrderCreateSerializer(data=order_data)
            ser.create(validated_data=order_data)
            if ser.is_valid(raise_exception=True):
                profile = request.user.profile
                profile.products.set([])
                profile.save()
                logger.info(f"{request.user} created order")
                return JsonResponse({'message': 'Order create success!'}, safe=False)
            return JsonResponse({'error': str(ser.errors)})
        except Exception as e:
            logger.error(str(e))
        return JsonResponse({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def category_products(request, pk):
    try:
        cat = Category.objects.get(id=pk)
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category does not exist'})
    ser = ProductSerializer(cat.cat_products, many=True)
    return JsonResponse(ser.data, safe=False)
