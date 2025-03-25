from django.contrib import admin

from .models import Film, Actor


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    
    def get_actors(self, obj):
        return ", ".join([actor.name for actor in obj.actors.all()])
    
    get_actors.short_description = "Actors"
    
    list_display = ("kinopoisk_id", "name", "year", "get_actors", "created_or_updated_at",)


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    
    list_display = ("staff_id", "name", "poster_url", "profession", "created_or_updated_at",)
