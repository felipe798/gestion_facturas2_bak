from rest_framework import serializers
from .models import Usuario
from .models import Cliente, Proveedor, Factura

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nombre', 'rol', 'password', 'fecha_creacion']

    def create(self, validated_data):
        """
        Sobrescribe el método de creación para manejar contraseñas correctamente.
        """
        password = validated_data.pop('password', None)
        usuario = Usuario(**validated_data)
        if password:
            usuario.set_password(password)  # Encripta la contraseña
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        """
        Sobrescribe el método de actualización para manejar contraseñas y otros campos.
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)  # Actualiza la contraseña encriptada
        instance.save()
        return instance

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'email']


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre', 'email']


class FacturaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)  # Agregado para el nombre del proveedor

    class Meta:
        model = Factura
        fields = [
            'id', 'numero_factura', 'proveedor', 'proveedor_nombre',  # Agregado proveedor_nombre
            'cliente', 'cliente_nombre',
            'fecha_emision', 'fecha_vencimiento', 'monto_total', 'estado', 'penalizacion'
        ]
