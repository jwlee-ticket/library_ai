# 멀티 테넌트 구현 계획

## 목표
- 회사별로 데이터를 분리하여 관리
- 각 사용자는 자신의 회사 데이터만 접근 가능
- Admin 사용자는 모든 회사 데이터 접근 가능

## 구현 단계

### 1단계: Company 모델 생성

**파일**: `core/models.py` 또는 `performance/models.py`

```python
class Company(models.Model):
    """회사 모델"""
    name = models.CharField(max_length=200, verbose_name='회사명', unique=True)
    name_en = models.CharField(max_length=200, blank=True, verbose_name='회사명(영문)')
    
    # 메타 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        verbose_name = '회사'
        verbose_name_plural = '회사들'
        ordering = ['name']
    
    def __str__(self):
        return self.name
```

### 2단계: User 모델 확장

**방법 1: OneToOne 관계 (권장)**
- 기존 User 모델 유지
- UserProfile 모델 생성하여 company 연결

**파일**: `core/models.py`

```python
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    """사용자 프로필 모델"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='소속 회사')
    
    class Meta:
        verbose_name = '사용자 프로필'
        verbose_name_plural = '사용자 프로필들'
    
    def __str__(self):
        return f'{self.user.username} - {self.company.name if self.company else "No Company"}'
```

**방법 2: AbstractUser 확장**
- User 모델을 직접 확장 (더 복잡하지만 더 깔끔)

### 3단계: 모든 모델에 company 필드 추가

**변경이 필요한 모델들:**
1. `Performance` - 공연
2. `Person` - 인물 (아티스트, 제작진)
3. `SeatGrade` - 좌석 등급 (Performance를 통해 간접적으로)
4. `BookingSite` - 예매처 (Performance를 통해 간접적으로)
5. `DiscountType` - 할인권종 (Performance를 통해 간접적으로)
6. `CastingRole` - 캐스팅 (Performance를 통해 간접적으로)
7. `CrewRole` - 제작진 (Performance를 통해 간접적으로)

**접근 방식:**
- `Performance`와 `Person`에 직접 `company` 필드 추가
- 나머지는 `Performance`를 통해 간접적으로 company 접근

**파일**: `performance/models.py`

```python
# Performance 모델에 추가
company = models.ForeignKey(
    'core.Company',  # 또는 'Company' (같은 앱에 있다면)
    on_delete=models.CASCADE,
    related_name='performances',
    verbose_name='회사',
    null=True,  # 마이그레이션을 위해 임시로 null=True
    blank=True
)

# Person 모델에 추가
company = models.ForeignKey(
    'core.Company',
    on_delete=models.CASCADE,
    related_name='persons',
    verbose_name='회사',
    null=True,  # 마이그레이션을 위해 임시로 null=True
    blank=True
)
```

### 4단계: 마이그레이션 생성 및 적용

```bash
python manage.py makemigrations
python manage.py migrate
```

**주의사항:**
- 기존 데이터가 있다면 마이그레이션 전에 기본 Company 생성 필요
- 기존 데이터에 company 할당하는 데이터 마이그레이션 필요

### 5단계: 쿼리 필터링 로직 추가

**Base View Mixin 생성**

**파일**: `core/mixins.py` (새로 생성)

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class CompanyFilterMixin(LoginRequiredMixin):
    """회사별 데이터 필터링 Mixin"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Admin은 모든 데이터 접근 가능
        if self.request.user.is_superuser:
            return queryset
        
        # 일반 사용자는 자신의 회사 데이터만
        user_profile = getattr(self.request.user, 'profile', None)
        if user_profile and user_profile.company:
            return queryset.filter(company=user_profile.company)
        
        # 회사가 없는 사용자는 빈 쿼리셋
        return queryset.none()
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Admin은 모든 객체 접근 가능
        if self.request.user.is_superuser:
            return obj
        
        # 일반 사용자는 자신의 회사 객체만 접근 가능
        user_profile = getattr(self.request.user, 'profile', None)
        if user_profile and user_profile.company:
            if obj.company != user_profile.company:
                raise PermissionDenied("이 데이터에 접근할 권한이 없습니다.")
        
        return obj
```

### 6단계: 모든 View에 Mixin 적용

**파일**: `performance/views.py`

```python
from core.mixins import CompanyFilterMixin

class PerformanceListView(CompanyFilterMixin, ListView):
    """공연 목록 뷰"""
    model = Performance
    # ... 기존 코드

class PerformanceCreateView(CompanyFilterMixin, CreateView):
    """공연 생성 뷰"""
    model = Performance
    
    def form_valid(self, form):
        # 회사 자동 할당
        user_profile = getattr(self.request.user, 'profile', None)
        if user_profile and user_profile.company:
            form.instance.company = user_profile.company
        return super().form_valid(form)
```

### 7단계: Form에서 company 필드 제거 및 자동 설정

**파일**: `performance/forms.py`

```python
class PerformanceForm(forms.ModelForm):
    class Meta:
        model = Performance
        exclude = ['company', 'created_at', 'updated_at']  # company 제외
        # ... 기존 필드들
```

### 8단계: Person 관련 쿼리 필터링

**파일**: `performance/views.py`

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    # Person 쿼리셋 필터링
    if self.request.user.is_superuser:
        person_queryset = Person.objects.all()
    else:
        user_profile = getattr(self.request.user, 'profile', None)
        if user_profile and user_profile.company:
            person_queryset = Person.objects.filter(company=user_profile.company)
        else:
            person_queryset = Person.objects.none()
    
    context['person_choices'] = person_queryset.order_by('name')
    return context
```

### 9단계: Admin 설정

**파일**: `performance/admin.py`

```python
from django.contrib import admin
from .models import Performance, Person, Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'created_at']
    search_fields = ['name', 'name_en']

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'genre', 'performance_start']
    list_filter = ['company', 'genre', 'performance_start']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Admin도 회사별 필터링 가능하도록 (선택사항)
        return qs

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'company']
    list_filter = ['company']
    search_fields = ['name', 'name_en']
```

### 10단계: 기존 데이터 마이그레이션

**데이터 마이그레이션 파일 생성**

```python
# performance/migrations/XXXX_assign_default_company.py

from django.db import migrations

def assign_default_company(apps, schema_editor):
    Company = apps.get_model('core', 'Company')
    Performance = apps.get_model('performance', 'Performance')
    Person = apps.get_model('performance', 'Person')
    
    # 기본 회사 생성 (또는 기존 회사 사용)
    default_company, created = Company.objects.get_or_create(
        name='라이브러리컴퍼니',
        defaults={'name_en': 'Library Company'}
    )
    
    # 기존 Performance에 company 할당
    Performance.objects.filter(company__isnull=True).update(company=default_company)
    
    # 기존 Person에 company 할당
    Person.objects.filter(company__isnull=True).update(company=default_company)

def reverse_assign_default_company(apps, schema_editor):
    # 역방향 마이그레이션 (필요시)
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('performance', 'XXXX_previous_migration'),
    ]
    
    operations = [
        migrations.RunPython(assign_default_company, reverse_assign_default_company),
    ]
```

### 11단계: User Profile 생성 및 관리

**시그널을 사용하여 자동 생성**

**파일**: `core/signals.py` (새로 생성)

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
```

**파일**: `core/apps.py`

```python
class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        import core.signals  # 시그널 등록
```

## 구현 순서 요약

1. ✅ Company 모델 생성
2. ✅ UserProfile 모델 생성 (User와 OneToOne)
3. ✅ Performance, Person 모델에 company 필드 추가
4. ✅ 마이그레이션 생성 및 적용
5. ✅ CompanyFilterMixin 생성
6. ✅ 모든 View에 Mixin 적용
7. ✅ Form에서 company 필드 제거
8. ✅ Person 쿼리 필터링 추가
9. ✅ Admin 설정 업데이트
10. ✅ 기존 데이터 마이그레이션
11. ✅ User Profile 자동 생성 시그널 추가

## 주의사항

1. **기존 데이터 처리**: 마이그레이션 전에 기본 Company를 생성하고 기존 데이터에 할당해야 함
2. **null=True 제거**: 마이그레이션 완료 후 company 필드의 null=True를 제거해야 함
3. **Admin 권한**: Admin 사용자는 모든 데이터 접근 가능하도록 처리
4. **Person 공유**: Person이 여러 회사에서 공유될 수 있는지 결정 필요 (현재는 회사별로 분리)
5. **테스트**: 각 단계마다 테스트하여 데이터 격리가 제대로 작동하는지 확인

## 추가 고려사항

- **Person 공유**: 아티스트가 여러 회사에서 활동할 수 있다면 ManyToMany 관계 고려
- **데이터 백업**: 마이그레이션 전 데이터 백업 필수
- **권한 관리**: 더 세밀한 권한 관리가 필요하다면 django-guardian 등 라이브러리 고려

