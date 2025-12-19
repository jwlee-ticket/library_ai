from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    """회사 모델"""
    name = models.CharField(max_length=200, verbose_name='회사명', unique=True)
    name_en = models.CharField(max_length=200, blank=True, verbose_name='회사명(영문)', help_text='회사명 영문')
    
    # 메타 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        verbose_name = '회사'
        verbose_name_plural = '회사들'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """사용자 프로필 모델"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='사용자'
    )
    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_profiles',
        verbose_name='소속 회사',
        help_text='사용자가 소속된 회사'
    )
    
    # 메타 필드
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        verbose_name = '사용자 프로필'
        verbose_name_plural = '사용자 프로필들'
        indexes = [
            models.Index(fields=['company']),
        ]
    
    def __str__(self):
        company_name = self.company.name if self.company else "No Company"
        return f'{self.user.username} - {company_name}'
