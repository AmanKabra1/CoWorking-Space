from django.contrib import admin
from django.utils import timezone
from .models import StartupProfile, IncubationApplication, ApplicationNote, FundingRound


class ApplicationNoteInline(admin.TabularInline):
    model = ApplicationNote
    extra = 0
    readonly_fields = ['author', 'created_at']


class FundingRoundInline(admin.TabularInline):
    model = FundingRound
    extra = 0
    fields = ['funding_type', 'amount_sought', 'amount_raised', 'status', 'target_date']


@admin.register(StartupProfile)
class StartupProfileAdmin(admin.ModelAdmin):
    list_display = ['startup_name', 'company', 'industry', 'stage', 'team_size', 'created_at']
    list_filter = ['industry', 'stage']
    search_fields = ['startup_name', 'company__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [FundingRoundInline]


@admin.register(IncubationApplication)
class IncubationApplicationAdmin(admin.ModelAdmin):
    list_display = ['startup', 'cohort', 'status', 'submitted_at', 'reviewed_by', 'reviewed_at']
    list_filter = ['status', 'cohort', 'funding_type']
    search_fields = ['startup__startup_name', 'startup__company__name']
    readonly_fields = ['submitted_at', 'reviewed_at', 'created_at', 'updated_at']
    inlines = [ApplicationNoteInline]
    actions = ['mark_under_review', 'mark_accepted', 'mark_rejected']

    def mark_under_review(self, request, queryset):
        updated = queryset.filter(status='submitted').update(status='under_review')
        self.message_user(request, f'{updated} application(s) moved to Under Review.')
    mark_under_review.short_description = 'Move selected to Under Review'

    def mark_accepted(self, request, queryset):
        updated = queryset.filter(
            status__in=['submitted', 'under_review']
        ).update(status='accepted', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f'{updated} application(s) accepted.')
    mark_accepted.short_description = 'Accept selected applications'

    def mark_rejected(self, request, queryset):
        updated = queryset.filter(
            status__in=['submitted', 'under_review']
        ).update(status='rejected', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f'{updated} application(s) rejected.')
    mark_rejected.short_description = 'Reject selected applications'


@admin.register(ApplicationNote)
class ApplicationNoteAdmin(admin.ModelAdmin):
    list_display = ['application', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal']
    readonly_fields = ['created_at']


@admin.register(FundingRound)
class FundingRoundAdmin(admin.ModelAdmin):
    list_display = ['startup', 'funding_type', 'amount_sought', 'amount_raised', 'status', 'target_date']
    list_filter = ['status', 'funding_type', 'currency']
    search_fields = ['startup__startup_name']
    readonly_fields = ['created_at', 'updated_at']
