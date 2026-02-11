from django.contrib import admin

from . import models


@admin.register(models.Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "short_name",
        "name",
        "admin",
        "created_at",
        "frozen_at",
        "archived_at",
        "private_p",
    )
    list_filter = ("private_p",)
    search_fields = ("uuid", "short_name", "name")
    raw_id_fields = ("admin",)


@admin.register(models.Trustee)
class TrusteeAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "name", "email", "election")
    search_fields = ("uuid", "name", "email")
    raw_id_fields = ("election",)


@admin.register(models.Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "voter_login_id", "voter_email", "voter_name", "election", "cast_at")
    search_fields = ("uuid", "voter_login_id", "voter_email", "voter_name")
    raw_id_fields = ("election", "user")


@admin.register(models.VoterFile)
class VoterFileAdmin(admin.ModelAdmin):
    list_display = ("id", "election", "uploaded_at", "num_voters", "processing_started_at", "processing_finished_at")
    raw_id_fields = ("election",)


@admin.register(models.CastVote)
class CastVoteAdmin(admin.ModelAdmin):
    def election(self, obj):
        return obj.voter.election
    election.admin_order_field = "voter__election"

    list_display = ("id", "voter", "election", "cast_at", "verified_at", "invalidated_at", "quarantined_p")
    list_filter = ("quarantined_p",)
    raw_id_fields = ("voter",)


@admin.register(models.AuditedBallot)
class AuditedBallotAdmin(admin.ModelAdmin):
    list_display = ("id", "election", "vote_hash", "added_at")
    search_fields = ("vote_hash",)
    raw_id_fields = ("election",)


@admin.register(models.ElectionLog)
class ElectionLogAdmin(admin.ModelAdmin):
    list_display = ("id", "election", "at")
    raw_id_fields = ("election",)


@admin.register(models.EmailOptOut)
class EmailOptOutAdmin(admin.ModelAdmin):
    list_display = ("id", "email_hash", "opted_out_at", "ip_address")
    search_fields = ("email_hash",)
    list_filter = ("opted_out_at",)
