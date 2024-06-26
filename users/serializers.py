from django.contrib.auth.models import User
from backend.models import StaffPermission, Warehouse
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.exceptions import ValidationError
from warehouses.serializers import WarehouseSerializer




class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    role = serializers.CharField(write_only=True, required=False)
    warehouse_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'confirm_password', 'role', 'warehouse_id')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        role = validated_data.pop('role', 'customer')
        warehouse_id = validated_data.pop('warehouse_id', None)
        user = User.objects.create_user(
            **validated_data,
            is_staff=(role == 'staff' or role == 'admin'),
            is_superuser=(role == 'admin'),
        )
        if warehouse_id and role == 'staff':
            warehouse = Warehouse.objects.get(id=warehouse_id)
            StaffPermission.objects.create(user=user, warehouse=warehouse, is_permitted=True)
        return user


UserModel = get_user_model()

class CustomAuthTokenSerializer(serializers.Serializer):
    
    username_or_email = serializers.CharField(label="Username or Email")
    password = serializers.CharField(label="Password", style={'input_type': 'password'})

    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')

        user = None

        # Check if the input is an email
        if '@' in username_or_email:
            try:
                user = UserModel.objects.get(email=username_or_email)
            except UserModel.DoesNotExist:
                pass  

        if not user:
            user = authenticate(request=self.context.get('request'), username=username_or_email, password=password)

        if not user:
            raise serializers.ValidationError({'detail':'Unable to log in with provided credentials.'})

        attrs['user'] = user
        return attrs

class UserLoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()
    user = serializers.DictField(child=serializers.CharField())

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user']['date_joined'] = instance.user.date_joined.isoformat()
        return representation


class CustomUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}  
    def get_role(self, obj):
        if obj.is_superuser:
            return 'admin'
        elif obj.is_staff:
            return 'staff'
        else:
            return 'customer'

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class StaffSerializer(serializers.ModelSerializer):
    is_staff_permitted = serializers.SerializerMethodField()
    permitted_warehouse = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_staff_permitted', 'permitted_warehouse']

    def get_is_staff_permitted(self, obj):
        try:
            staff_permission = StaffPermission.objects.get(user=obj)
            return staff_permission.is_permitted
        except StaffPermission.DoesNotExist:
            return False

    def get_permitted_warehouse(self, obj):
        try:
            staff_permission = StaffPermission.objects.get(user=obj)
            warehouse = staff_permission.warehouse
            return WarehouseSerializer(warehouse).data
        except StaffPermission.DoesNotExist:
            return None


class CustomerSerializer(serializers.ModelSerializer):
    is_staff_permitted = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def validate(self, data):
        username = data.get('username')
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise serializers.ValidationError("Username is already in use.")

        email = data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise serializers.ValidationError("Email is already in use.")

        return data


# class StaffPermissionSerializer(serializers.ModelSerializer):
#     warehouse_id = serializers.IntegerField()

#     class Meta:
#         model = StaffPermission
#         fields = ['warehouse_id']

#     def validate(self, data):
#         if 'warehouse_id' not in data:
#             raise serializers.ValidationError("Warehouse ID is required.")
        
#         user = self.context['request'].user
#         if not user.is_staff:
#             raise serializers.ValidationError("Only staff members can be assigned permissions.")
        
#         return data
