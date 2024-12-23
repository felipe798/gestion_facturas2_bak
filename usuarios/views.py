import csv
from io import BytesIO
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Usuario, Cliente, Proveedor, Factura
from .serializers import UsuarioSerializer, ClienteSerializer, ProveedorSerializer, FacturaSerializer
from .models import Factura, Proveedor
from io import TextIOWrapper
from .models import Proveedor, Factura
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from datetime import date








class RegistroView(APIView):
    def post(self, request):
        data = request.data
        if data.get('rol') != 'Administrador':
            return Response({'error': 'Solo se pueden registrar administradores'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UsuarioSerializer(data=data)
        if serializer.is_valid():
            Usuario.objects.create_user(
                email=data['email'],
                nombre=data['nombre'],
                password=data['password'],
                rol=data['rol']
            )
            return Response({'mensaje': 'Usuario creado exitosamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'rol': user.rol
            })
        return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_401_UNAUTHORIZED)


class UsuarioCRUDView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.rol != 'Administrador':
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.rol != 'Administrador':
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            Usuario.objects.create_user(
                email=request.data['email'],
                nombre=request.data['nombre'],
                password=request.data['password'],
                rol=request.data.get('rol', 'Contador')  # Rol por defecto
            )
            return Response({'mensaje': 'Usuario creado exitosamente'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if request.user.rol != 'Administrador':
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validar y actualizar usuario
        serializer = UsuarioSerializer(usuario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.rol != 'Administrador':
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        try:
            usuario = Usuario.objects.get(pk=pk)
            usuario.delete()
            return Response({'mensaje': 'Usuario eliminado correctamente'}, status=status.HTTP_200_OK)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)



class ClienteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        clientes = Cliente.objects.all()
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProveedorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        proveedores = Proveedor.objects.all()
        serializer = ProveedorSerializer(proveedores, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProveedorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacturaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        facturas = Factura.objects.all()
        serializer = FacturaSerializer(facturas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FacturaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            factura = Factura.objects.get(pk=pk)
        except Factura.DoesNotExist:
            return Response({'error': 'Factura no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FacturaSerializer(factura, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ExportarPDF(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            factura = Factura.objects.get(pk=pk)
            
            # Calcular penalización basado en la fecha de vencimiento
            today = date.today()
            dias_vencidos = 0
            penalizacion = 0

            if factura.fecha_vencimiento < today:
                dias_vencidos = (today - factura.fecha_vencimiento).days
                penalizacion = float(factura.monto_total) * 0.01 * dias_vencidos

            # Actualizar estado basado en la fecha de vencimiento
            if factura.estado != 'Pagada':
                factura.estado = 'Vencida' if dias_vencidos > 0 else 'Pendiente'

            factura.save()  # Guardar cambios en el estado

            # Preparar contexto para el PDF
            context = {
                'factura': factura,
                'penalizacion': penalizacion,
                'monto_total_actualizado': float(factura.monto_total) + penalizacion
            }

            template = get_template('factura_pdf.html')
            html = template.render(context)

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Factura-{factura.numero_factura}.pdf"'

            pisa_status = pisa.CreatePDF(html.encode('utf-8'), dest=response, encoding='utf-8')
            if pisa_status.err:
                return HttpResponse('Error al generar PDF', status=500)
            return response

        except Factura.DoesNotExist:
            return HttpResponse('Factura no encontrada', status=404)





class ImportarCSV(APIView):
    def post(self, request):
        try:
            archivo_csv = request.FILES['archivo']
            data = TextIOWrapper(archivo_csv.file, encoding='utf-8')
            reader = csv.DictReader(data)

            for row in reader:
                proveedor, _ = Proveedor.objects.get_or_create(nombre=row['proveedor'])
                Factura.objects.create(
                    numero_factura=row['numero_factura'],
                    proveedor=proveedor,
                    fecha_emision=row['fecha_emision'],
                    fecha_vencimiento=row['fecha_vencimiento'],
                    monto_total=row['monto_total'],
                    estado=row['estado']
                )

            return Response({'message': 'Facturas importadas correctamente'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ImportarFacturasProveedoresCSV(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('archivo')
        if not file:
            return Response({'error': 'No se proporcionó ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            required_columns = {'numero_factura', 'proveedor', 'fecha_emision', 'fecha_vencimiento', 'monto_total', 'estado'}
            if not required_columns.issubset(reader.fieldnames):
                return Response({'error': 'El archivo CSV no contiene las columnas requeridas'}, status=status.HTTP_400_BAD_REQUEST)

            errores = []
            for row_number, row in enumerate(reader, start=1):
                try:
                    # Asociar la factura con un proveedor
                    proveedor = Proveedor.objects.filter(nombre=row['proveedor']).first()
                    if not proveedor:
                        errores.append(f"Fila {row_number}: Proveedor '{row['proveedor']}' no encontrado")
                        continue

                    # Crear la factura asociada al proveedor
                    Factura.objects.create(
                        numero_factura=row['numero_factura'],
                        proveedor=proveedor,
                        fecha_emision=row['fecha_emision'],
                        fecha_vencimiento=row['fecha_vencimiento'],
                        monto_total=float(row['monto_total']),
                        estado=row.get('estado', 'Pendiente'),
                    )
                except Exception as e:
                    errores.append(f"Fila {row_number}: {str(e)}")

            if errores:
                return Response({'error': 'Errores al procesar el archivo', 'detalles': errores}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'mensaje': 'Facturas importadas correctamente'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Error procesando el archivo CSV: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

class FacturasPorProveedorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        proveedores = Proveedor.objects.prefetch_related('factura_set').all()
        data = [
            {
                'proveedor': proveedor.nombre,
                'facturas': FacturaSerializer(proveedor.factura_set.all(), many=True).data
            }
            for proveedor in proveedores
        ]
        return Response(data, status=status.HTTP_200_OK)
    
    
# views.py
class ActualizarEstadoFacturaProveedor(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            factura = Factura.objects.get(pk=pk, proveedor__isnull=False)  # Solo facturas de proveedores
        except Factura.DoesNotExist:
            return Response({'error': 'Factura no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        nuevo_estado = request.data.get('estado')
        if nuevo_estado not in ['Pendiente', 'Pagada', 'Vencida']:
            return Response({'error': 'Estado inválido'}, status=status.HTTP_400_BAD_REQUEST)

        factura.estado = nuevo_estado
        factura.save()
        return Response({'mensaje': 'Estado actualizado correctamente'}, status=status.HTTP_200_OK)






class NotificacionesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Validar si el usuario tiene permiso para acceder a las notificaciones
        if request.user.rol not in ['Contador', 'Administrador']:
            return Response({'error': 'No autorizado. Solo los contadores y administradores pueden acceder.'},
                            status=status.HTTP_403_FORBIDDEN)
        
        today = timezone.now()

        # Filtrar todas las facturas vencidas
        facturas_vencidas = Factura.objects.filter(
            fecha_vencimiento__lt=today,
            estado='Pendiente'
        )

        # Enviar solo la cantidad de facturas vencidas
        return Response({'facturas_vencidas_count': facturas_vencidas.count()}, status=status.HTTP_200_OK)


    

class ObtenerRolUsuarioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'rol': request.user.rol}, status=200)
    

    
class EstadisticasDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Validar permisos
        if request.user.rol not in ['Administrador', 'Gerente']:
            return Response({'error': 'No autorizado. Solo Administradores y Gerentes pueden acceder.'},
                            status=status.HTTP_403_FORBIDDEN)

        today = date.today()
        inicio_mes = today.replace(day=1)

        # Facturas pagadas por clientes y proveedores
        facturas_pagadas_clientes = Factura.objects.filter(cliente__isnull=False, estado='Pagada').count()
        facturas_pagadas_proveedores = Factura.objects.filter(proveedor__isnull=False, estado='Pagada').count()

        facturas_pagadas = (
            Factura.objects.filter(estado='Pagada')
            .values('fecha_emision__month')
            .annotate(total_pagadas=Count('id'), monto_pagado=Sum('monto_total'))
        )
        facturas_vencidas = (
            Factura.objects.filter(estado='Vencida', fecha_vencimiento__month=today.month)
            .count()
        )
        comparacion_pagos = {
            "pagos": Factura.objects.filter(proveedor__isnull=False, estado='Pagada')
                .aggregate(total=Sum('monto_total'))['total'] or 0,
            "cobros": Factura.objects.filter(cliente__isnull=False, estado='Pagada')
                .aggregate(total=Sum('monto_total'))['total'] or 0,
        }

        return Response({
            'facturas_pagadas': list(facturas_pagadas),
            'facturas_vencidas': facturas_vencidas,
            'comparacion_pagos': comparacion_pagos,
            'facturas_pagadas_clientes': facturas_pagadas_clientes,
            'facturas_pagadas_proveedores': facturas_pagadas_proveedores,
        })


class FacturasVencidasCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Obtiene el número de facturas vencidas"""
        today = timezone.now().date()  # Fecha actual

        # Filtra las facturas que están vencidas
        facturas_vencidas_count = Factura.objects.filter(
            fecha_vencimiento__lt=today,  # Fecha vencida
            estado="Pendiente"  # Solo facturas pendientes que están vencidas
        ).count()

        return Response({"facturas_vencidas_count": facturas_vencidas_count}, status=200)