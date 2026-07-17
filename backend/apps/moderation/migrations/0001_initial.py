import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('reason', models.CharField(
                    choices=[('spam', 'Спам'), ('hate', 'Ненависть / образи'),
                             ('misleading', 'Дезінформація'), ('nsfw', 'Небажаний контент'), ('other', 'Інше')],
                    default='other', max_length=20
                )),
                ('comment', models.TextField(blank=True, max_length=500)),
                ('status', models.CharField(
                    choices=[('pending', 'На розгляді'), ('resolved',
                                                          'Вирішено — видалено'), ('rejected', 'Відхилено — залишено')],
                    default='pending', max_length=20
                )),
                ('admin_note', models.TextField(blank=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='reports_sent', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                 related_name='reports_reviewed', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
                'db_table': 'reports',
                'ordering': ['-created_at'],
                'unique_together': {('reporter', 'content_type', 'object_id')},
            },
        ),
        migrations.AddIndex(
            model_name='report',
            index=models.Index(
                fields=['status', '-created_at'], name='reports_status_idx'),
        ),
        migrations.AddIndex(
            model_name='report',
            index=models.Index(
                fields=['content_type', 'object_id'], name='reports_content_idx'),
        ),
    ]
