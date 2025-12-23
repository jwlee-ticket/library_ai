from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class CompanyFilterMixin(LoginRequiredMixin):
    """회사별 데이터 필터링 Mixin
    
    Admin 사용자는 모든 데이터 접근 가능
    일반 사용자는 자신의 회사 데이터만 접근 가능
    """
    
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
        """단일 객체 접근 시에도 회사 필터링"""
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


