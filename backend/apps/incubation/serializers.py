from rest_framework import serializers
from .models import StartupProfile, IncubationApplication, ApplicationNote, FundingRound


class ApplicationNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = ApplicationNote
        fields = ['id', 'content', 'is_internal', 'author', 'author_name', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def validate_is_internal(self, value):
        user = self.context['request'].user
        if value and not user.is_super_admin:
            raise serializers.ValidationError("Only Super Admins can create internal notes.")
        return value


class StartupProfileSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = StartupProfile
        fields = [
            'id', 'company', 'company_name', 'startup_name', 'tagline',
            'description', 'founded_date', 'industry', 'stage', 'team_size',
            'website', 'linkedin_url', 'twitter_url', 'logo', 'pitch_deck',
            'business_plan', 'applications_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_applications_count(self, obj):
        return obj.applications.count()

    def validate_company(self, value):
        user = self.context['request'].user
        if not user.is_super_admin and user.company != value:
            raise serializers.ValidationError(
                "You can only create a startup profile for your own company."
            )
        return value


class IncubationApplicationSerializer(serializers.ModelSerializer):
    startup_name = serializers.CharField(source='startup.startup_name', read_only=True)
    company_name = serializers.CharField(source='startup.company.name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    notes_count = serializers.SerializerMethodField()
    visible_notes = serializers.SerializerMethodField()

    class Meta:
        model = IncubationApplication
        fields = [
            'id', 'startup', 'startup_name', 'company_name', 'cohort', 'status',
            'problem_statement', 'solution', 'market_size', 'traction',
            'funding_ask', 'funding_type',
            'submitted_at', 'reviewed_by', 'reviewed_by_name', 'reviewed_at',
            'rejection_reason', 'notes_count', 'visible_notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'submitted_at', 'reviewed_by', 'reviewed_at',
            'rejection_reason', 'created_at', 'updated_at',
        ]

    def get_notes_count(self, obj):
        return obj.notes.count()

    def get_visible_notes(self, obj):
        user = self.context['request'].user
        qs = obj.notes.select_related('author').all()
        if not user.is_super_admin:
            qs = qs.filter(is_internal=False)
        return ApplicationNoteSerializer(qs, many=True, context=self.context).data

    def validate_startup(self, value):
        user = self.context['request'].user
        if not user.is_super_admin and value.company != user.company:
            raise serializers.ValidationError(
                "You can only apply for your own company's startup."
            )
        return value


class RejectApplicationSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default='')


class FundingRoundSerializer(serializers.ModelSerializer):
    startup_name = serializers.CharField(source='startup.startup_name', read_only=True)

    class Meta:
        model = FundingRound
        fields = [
            'id', 'startup', 'startup_name', 'funding_type', 'amount_sought',
            'amount_raised', 'currency', 'status', 'target_date', 'investors',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_startup(self, value):
        user = self.context['request'].user
        if not user.is_super_admin and value.company != user.company:
            raise serializers.ValidationError(
                "You can only manage funding rounds for your own startup."
            )
        return value
