# Custom migration: convert tipo CharField to ForeignKey(TipoActivo)

import django.db.models.deletion
from django.db import migrations, models


# Estos son los tipos que existían como choices en TIPO_ACTIVO
TIPOS_ORIGINALES = [
    ('LAPTOP', 'Laptop'),
    ('PC', 'Computador de escritorio'),
    ('MONITOR', 'Monitor'),
    ('IMPRESORA', 'Impresora'),
    ('SWITCH', 'Switch'),
    ('ROUTER', 'Router'),
    ('SERVER', 'Servidor'),
    ('CELULAR', 'Celular'),
    ('OTRO', 'Otro'),
]


def crear_tipos_y_migrar_datos(apps, schema_editor):
    """Crear TipoActivo por cada choice anterior y mapear los activos existentes."""
    TipoActivo = apps.get_model('catalogos', 'TipoActivo')
    Activo = apps.get_model('inventario', 'Activo')

    # Crear registros de TipoActivo a partir de los choices originales
    tipo_map = {}
    for codigo, nombre in TIPOS_ORIGINALES:
        obj, _ = TipoActivo.objects.get_or_create(nombre=nombre)
        tipo_map[codigo] = obj

    # Asignar FK temporal a cada activo basándose en el valor de texto
    for activo in Activo.objects.all():
        tipo_texto = activo.tipo_old
        if tipo_texto in tipo_map:
            activo.tipo_new = tipo_map[tipo_texto]
        else:
            # Si hay un valor inesperado, asignar "Otro"
            activo.tipo_new = tipo_map.get('OTRO') or TipoActivo.objects.get_or_create(nombre='Otro')[0]
        activo.save(update_fields=['tipo_new'])


def revertir_datos(apps, schema_editor):
    """Revertir: copiar de FK a texto."""
    TipoActivo = apps.get_model('catalogos', 'TipoActivo')
    Activo = apps.get_model('inventario', 'Activo')

    # Crear mapa inverso nombre -> código
    nombre_a_codigo = {nombre: codigo for codigo, nombre in TIPOS_ORIGINALES}

    for activo in Activo.objects.select_related('tipo_new').all():
        if activo.tipo_new:
            activo.tipo_old = nombre_a_codigo.get(activo.tipo_new.nombre, 'OTRO')
            activo.save(update_fields=['tipo_old'])


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0002_tipoactivo'),
        ('inventario', '0002_alter_activo_codigo_alter_activo_fecha_compra_and_more'),
    ]

    operations = [
        # 1. Renombrar la columna vieja de texto
        migrations.RenameField(
            model_name='activo',
            old_name='tipo',
            new_name='tipo_old',
        ),
        # 2. Añadir nueva columna FK (nullable temporalmente)
        migrations.AddField(
            model_name='activo',
            name='tipo_new',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='catalogos.tipoactivo',
            ),
        ),
        # 3. Migrar datos de texto a FK
        migrations.RunPython(crear_tipos_y_migrar_datos, revertir_datos),
        # 4. Eliminar la columna vieja de texto
        migrations.RemoveField(
            model_name='activo',
            name='tipo_old',
        ),
        # 5. Renombrar tipo_new -> tipo
        migrations.RenameField(
            model_name='activo',
            old_name='tipo_new',
            new_name='tipo',
        ),
        # 6. Hacer la FK no nullable
        migrations.AlterField(
            model_name='activo',
            name='tipo',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to='catalogos.tipoactivo',
            ),
        ),
    ]
