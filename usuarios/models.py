from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from datetime import date, timedelta

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password=None, rol=None):
        if not email:
            raise ValueError("El usuario debe tener un correo electrónico")
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, rol=rol)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, password):
        return self.create_user(email, nombre, password, rol="Administrador")

class Usuario(AbstractBaseUser):
    ROL_CHOICES = [
        ('Administrador', 'Administrador'),
        ('Contador', 'Contador'),
        ('Gerente', 'Gerente'),
    ]
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    rol = models.CharField(max_length=50, choices=ROL_CHOICES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.rol})"




class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.nombre


class Factura(models.Model):
    ESTADO_CHOICES = [
        ('Pagada', 'Pagada'),
        ('Pendiente', 'Pendiente'),
        ('Vencida', 'Vencida'),
    ]

    numero_factura = models.CharField(max_length=50, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, blank=True, null=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    penalizacion = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def actualizar_estado(self):
        """Actualiza el estado y calcula penalizaciones si está vencida."""
        if self.estado == 'Pagada':
            return
        hoy = date.today()
        if hoy > self.fecha_vencimiento:
            self.estado = 'Vencida'
            dias_vencidos = (hoy - self.fecha_vencimiento).days
            self.penalizacion = self.monto_total * 0.10 * dias_vencidos
        else:
            self.estado = 'Pendiente'
        self.save()

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.estado}"
    

    