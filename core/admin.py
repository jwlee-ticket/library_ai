from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Company, UserProfile

User = get_user_model()


# 기존 User 어드민 등록 해제
admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """커스텀 User 어드민 - 이름 필드 추가"""
    
    # 사용자 추가 폼에 이름 필드 추가
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'password1', 'password2'),
        }),
    )
    
    # 사용자 수정 폼에 이름 필드 추가
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('개인 정보', {'fields': ('first_name', 'email')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요한 날짜', {'fields': ('last_login', 'date_joined')}),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """폼에서 first_name 라벨을 '이름'으로 변경"""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['first_name'].label = '이름'
        return form


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """회사 어드민"""
    list_display = ['name', 'name_en', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'name_en']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'name_en')
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """사용자 프로필 어드민"""
    list_display = ['user', 'company', 'created_at']
    list_filter = ['company', 'created_at']
    search_fields = ['user__username', 'user__email', 'company__name']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['user', 'company']
    
    fieldsets = (
        ('사용자 정보', {
            'fields': ('user', 'company')
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
