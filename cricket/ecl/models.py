from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    team_name = models.CharField(max_length=50)
    # team_owner_code = models.CharField(max_length=20)


class Tournament(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    tournament_name = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='inactive')
# Query for SQL object creation : tobj = Tournament(id= 'abc', tournament_name = 'App tst', status='active')


class Matches(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team2')
    match_date = models.DateTimeField(auto_now_add=True, blank=True)
    played = models.CharField(max_length=5)
    result = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='result')
# Query for SQL object creation : m1 = Matches(id= 'abc', tournament_name = 'App tst', status='active')


class League(models.Model):
    league_name = models.CharField(max_length=50)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    league_code = models.CharField(max_length=50)
    league_admin = models.ForeignKey(User, on_delete=models.CASCADE)


class UserDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    match = models.ForeignKey(Matches, on_delete=models.CASCADE)
    result = models.CharField(max_length=5)
    team_selected = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_selected', default='N')


# Query for creation of SQL objects
# t =
