# Generated manually for adding QQ UnionID support
# Date: 2025-11-08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_add_fusion_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='qquser',
            name='unionid',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='QQ 互联 UnionID，用于跨应用识别同一用户',
                max_length=100,
                null=True,
                verbose_name='QQ UnionID'
            ),
        ),
        migrations.AddIndex(
            model_name='qquser',
            index=models.Index(fields=['unionid'], name='qquser_unionid_idx'),
        ),
    ]

