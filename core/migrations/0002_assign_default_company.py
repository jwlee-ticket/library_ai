# Generated manually for data migration

from django.db import migrations


def assign_default_company_and_profiles(apps, schema_editor):
    """기본 회사 생성 및 기존 데이터에 할당"""
    Company = apps.get_model('core', 'Company')
    UserProfile = apps.get_model('core', 'UserProfile')
    User = apps.get_model('auth', 'User')
    Performance = apps.get_model('performance', 'Performance')
    Person = apps.get_model('performance', 'Person')
    
    # 1. 기본 회사 생성 (라이브러리컴퍼니)
    default_company, created = Company.objects.get_or_create(
        name='라이브러리컴퍼니',
        defaults={'name_en': 'Library Company'}
    )
    
    # 2. 기존 Performance, Person에 company 할당
    Performance.objects.filter(company__isnull=True).update(company=default_company)
    Person.objects.filter(company__isnull=True).update(company=default_company)
    
    # 3. 기존 User들에게 UserProfile 생성 및 Company 할당
    for user in User.objects.all():
        profile, profile_created = UserProfile.objects.get_or_create(user=user)
        if profile_created:
            # 일반 사용자는 기본 회사 할당
            if not user.is_superuser:
                profile.company = default_company
                profile.save()
            # admin은 superuser이므로 company 없이도 모든 데이터 접근 가능
            # 필요시 나중에 할당 가능


def reverse_assign_default_company(apps, schema_editor):
    """역방향 마이그레이션 (필요시)"""
    # 역방향 마이그레이션은 선택사항
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('performance', '0011_performance_company_person_company_and_more'),
    ]

    operations = [
        migrations.RunPython(assign_default_company_and_profiles, reverse_assign_default_company),
    ]


