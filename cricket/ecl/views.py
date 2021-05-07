from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserRegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import League, Matches, UserDetails, Team
from datetime import datetime, timedelta
from django.utils import timezone


def register_user(request):
    form = UserRegistrationForm()
    # print("Entered register method")
    context = {'form': form, 'errors': []}
    return render(request, 'ecl/register.html', context)


def register_success(request):
    # print("Entered register Success mode")
    context = {}
    if request.method == 'POST':
        # print("Entered post method")
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            context = {'form': form}
            return render(request, 'ecl/register_success.html', context)
        else:
            list_all_errors = []
            for k in form.error_messages.keys():
                list_all_errors.append(k)
            context = {'form': form, 'errors': list_all_errors}
            return render(request, 'ecl/register.html', context)


def login_page(request):
    context = {}
    if request.user.is_authenticated:
        #print('redirecting from login to home page')
        response = redirect('home')
        return response
    return render(request, 'ecl/login_page.html', context)


def login_auth(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # print(User.first_name)
            response = redirect('home')
            return response
        else:
            response = redirect('inv_login')
            return response
    except Exception as e:
        # print("Redirecting to home page")
        response = redirect('home')
        return response


def invalid_login(request):
    # print('Invalid Login')
    context = {}
    if request.user.is_authenticated:
        # print('redirecting from login to home page')
        response = redirect('login_auth/home/')
        return response
    return render(request, 'ecl/invalid_login_page.html', context)


@login_required(login_url='')
def home_view(request):
    # print(request.user)
    list_performance_data = []
    login_user_rec = User.objects.filter(username=request.user)
    login_user_id = login_user_rec[0].id

    list_league_players_perf = []
    list_existing_user_matches_rec = UserDetails.objects.filter(user=login_user_id)

    list_all_active_leagues = [i.league for i in list_existing_user_matches_rec if i.league.tournament.status == 'active']
    if len(list_all_active_leagues) > 0:
        list_all_active_leagues = list(set(list_all_active_leagues))

        for indv_league in list_all_active_leagues:
            list_filtered_victory_rec = list_existing_user_matches_rec.filter(league=indv_league.id, result='Won')
            int_total_game_won = len(list_filtered_victory_rec)
            str_tournament_id = indv_league.tournament.id
            list_all_matches_for_this_league = Matches.objects.filter(tournament=str_tournament_id).exclude(result='RP')
            int_total_number_of_matches = len(list_all_matches_for_this_league)
            int_total_game_lost = int_total_number_of_matches - int_total_game_won
            str_league_name = indv_league.league_name
            str_league_unique_key = str_league_name.split()[0] + str(indv_league.id)
            dict_performance_stats = {
                'league_name': indv_league.league_name,
                'total_games': int_total_number_of_matches,
                'won_games': int_total_game_won,
                'lost_games': int_total_game_lost,
                'modal_id': '#' + str_league_unique_key,
            }
            list_performance_data.append(dict_performance_stats)

            list_all_players_this_league_rec = UserDetails.objects.filter(league=indv_league.id)
            list_all_users_rec = list(
                                      set([i.user for i in list_all_players_this_league_rec if i.user.id != login_user_id])
                                )
            # print(login_user_id)
            # print(list_all_users_rec)
            list_league_stats_recs = [
                [login_user_rec[0].get_full_name(), int_total_game_won, int_total_game_lost, ]
            ]

            for ind_user_rec in list_all_users_rec:
                list_matches_rec = list_all_players_this_league_rec.filter(user=ind_user_rec.id, result='Won')
                int_indv_user_win_count = len(list_matches_rec)
                int_indv_user_loss_count = int_total_number_of_matches - int_indv_user_win_count

                list_single_row = [
                    ind_user_rec.get_full_name(), int_indv_user_win_count, int_indv_user_loss_count,
                ]
                list_league_stats_recs.append(list_single_row)
            dict_league_players_stats = {
                                            "modal_id": str_league_unique_key,
                                            "data": list_league_stats_recs,
            }
            list_league_players_perf.append(dict_league_players_stats)
            # print(list_league_players_perf)

    context = {'performance_data': list_performance_data, 'all_players_performance': list_league_players_perf}
    return render(request, 'ecl/home.html', context)


@login_required(login_url='')
def join_match_view(request):
    context = {'alert_msg': "", 'alert_type': 0}
    return render(request, 'ecl/join_match.html', context)


@login_required(login_url='')
def join_match_processing(request):
    context = {}
    # print(request.user)
    login_user_rec = User.objects.filter(username=request.user)
    login_user_id = login_user_rec[0].id
    str_league_code = request.POST['league_code']
    # print("League Code : " + str_league_code)
    list_filtered_leagues = League.objects.filter(league_code=str_league_code)
    if len(list_filtered_leagues) == 0:
        str_submission_msg = "Invalid League Code"
        int_type_code = 3   # Number 3 refers to Warning alert of invalid league code
        context = {'alert_msg': str_submission_msg, 'alert_type': int_type_code}
        return render(request, 'ecl/join_match.html', context)
    else:
        # print("League Code exist")
        # print("league length : " + str(len(list_filtered_leagues)))
        tournament_rec = list_filtered_leagues[0].tournament
        league_id = list_filtered_leagues[0].id
        # print("tournament id : " + str(tournament_rec.id))

        list_existing_matches_rec = UserDetails.objects.filter(user=login_user_id, league=league_id)
        list_existing_matches_rec_ids = [league_rec.match_id for league_rec in list_existing_matches_rec]

        list_filtered_matches = Matches.objects.filter(tournament=tournament_rec.id, played='No')
        list_filtered_matches_rec_ids = [league_filtered_rec.id for league_filtered_rec in list_filtered_matches]

        list_new_matches_rec_ids = list(set(list_filtered_matches_rec_ids) - set(list_existing_matches_rec_ids))
        # print("New matches record length : "+str(len(list_new_matches_rec_ids)))

        if len(list_new_matches_rec_ids) > 0:
            for row in list_filtered_matches:
                if row.id in list_new_matches_rec_ids:
                    str_result = "TBD"
                    ud_obj = UserDetails(user=login_user_rec[0], league=list_filtered_leagues[0], match=row,
                                         result=str_result)
                    ud_obj.save()

            str_submission_msg = list_filtered_leagues[0].league_name
            list_submission_msg = [str_submission_msg, league_id]
            int_type_code = 4  # Number 4 refers to paragraph with hyperlink to league matches
            context = {'alert_msg': list_submission_msg, 'alert_type': int_type_code}
            return render(request, 'ecl/join_match.html', context)

        elif len(list_new_matches_rec_ids) == 0:
            str_submission_msg = "You already used this code"
            int_type_code = 2  # Number 2 refers to info about you have already joined the league
            context = {'alert_msg': str_submission_msg, 'alert_type': int_type_code}
            return render(request, 'ecl/join_match.html', context)


def get_list_of_all_matches_data(request, filter_var=None):
    login_user_rec = User.objects.filter(username=request.user)
    login_user_id = login_user_rec[0].id
    if filter_var:
        if len(filter_var) == 1:
            str_filter_field = list(filter_var.keys())[0]
            str_filter_value = list(filter_var.values())[0]
            if str_filter_field == 'league_id':
                list_existing_matches_rec = UserDetails.objects.filter(user=login_user_id, league=str_filter_value)
            else:
                list_existing_matches_rec = UserDetails.objects.filter(user=login_user_id)
        else:
            list_existing_matches_rec = UserDetails.objects.filter(user=login_user_id)
    else:
        list_existing_matches_rec = UserDetails.objects.filter(user=login_user_id)

    if len(list_existing_matches_rec) == 0:
        list_data = []
        return list_data
    else:
        list_all_league_ids = [indv_match.league for indv_match in list_existing_matches_rec]
        list_all_league_ids = list(set(list_all_league_ids))
        list_final_league_ids = []

        # Checking whether league is active
        for i in list_all_league_ids:
            if i.tournament.status == 'active':
                list_final_league_ids.append(i)

        list_output_data = []

        for indv_league in list_final_league_ids:
            dict_indv_rec = {}
            list_all_matches_data = []
            list_indv_user_details_rec = list_existing_matches_rec.filter(league=indv_league).order_by('id')
            str_league_name = indv_league.league_name
            dict_indv_rec['league_name'] = str_league_name
            for j in list_indv_user_details_rec:
                match_date = j.match.match_date
                str_team_1 = j.match.team1.team_name
                str_team_2 = j.match.team2.team_name
                str_team_1_id = j.match.team1.id
                str_team_2_id = j.match.team2.id
                str_selected_team_id = j.team_selected.id
                match_deadline_date = match_date + timedelta(minutes=10)
                # match_status value 0 for not played, value 1 for match status changed from not played to played,
                # value 2 for match played and result pending, value 3 for matched played with result
                str_winner_team_id = ""
                if timezone.now() > match_deadline_date:
                    # print("Deadline Passed")
                    list_indv_match_data = Matches.objects.filter(id=j.match.id)
                    indv_match_obj = list_indv_match_data[0]
                    if indv_match_obj.played == "No":
                        indv_match_obj.played = "Yes"
                        indv_match_obj.save()
                        match_status = 1
                        # print('Status 1')
                    else:
                        if indv_match_obj.result.id == 'RP':
                            match_status = 2
                            # print('Status 2')
                        else:
                            match_status = 3
                            str_winner_team_id = indv_match_obj.result.id
                            if j.result == "TBD":
                                if str_selected_team_id == str_winner_team_id:
                                    # print('you won')
                                    j.result = "Won"
                                else:
                                    # print('you lose')
                                    j.result = "Lose"
                                j.save()

                            # print('Status 3')
                else:
                    match_status = 0
                    # print('Status 0')

                if str_selected_team_id == 'N':
                    selection_status = ""
                else:
                    selection_status = str_selected_team_id

                match_date = match_date + timedelta(hours=5, minutes=30)
                str_match_date = match_date.date().strftime("%d %B %Y")
                str_match_time = match_date.time().strftime("%H : %M")

                match_deadline_date = match_deadline_date + timedelta(hours=5, minutes=30)
                str_match_deadline_date = match_deadline_date.date().strftime("%d %B %Y")
                str_match_deadline_time = match_deadline_date.time().strftime("%H : %M")

                list_match_values = [str_match_date, str_match_time, str_team_1, str_team_2, str_team_1_id,
                                     str_team_2_id, j.id, selection_status, str_match_deadline_date,
                                     str_match_deadline_time, match_status, str_winner_team_id]
                # print(list_match_values)
                list_all_matches_data.append(list_match_values)
            dict_indv_rec['list_matches'] = list_all_matches_data
            list_output_data.append(dict_indv_rec)

    return list_output_data


@login_required(login_url='')
def my_matches_list_view(request):
    # print("All league matches view")
    context = {}
    list_output_data = get_list_of_all_matches_data(request)

    if len(list_output_data) > 0:
        context = {'all_data': list_output_data, 'alert_msg': ""}
        return render(request, 'ecl/all_leagues_view.html', context)
    else:
        context = {'alert_msg': "You have not joined any league. Please select 'Join League' option from the top and join a league by passing league code."}
        return render(request, 'ecl/no_league_found.html', context)


@login_required(login_url='')
def match_value_submission(request):
    context = {}
    form_data = request.POST
    list_form_data = list(form_data.values())

    str_selected_team_id = list_form_data[1]
    str_selected_match_id = list_form_data[2]
    # print(str_selected_team_id)
    # print(str_selected_match_id)
    list_user_details_recs = UserDetails.objects.filter(id=int(str_selected_match_id))
    user_details_rec = list_user_details_recs[0]

    # Checking whether submission is before deadline
    match_play_datetime = user_details_rec.match.match_date
    match_played_status = user_details_rec.match.played
    match_deadline_datetime = match_play_datetime + timedelta(minutes=10)
    curr_datetime = timezone.now()

    if curr_datetime <= match_deadline_datetime and match_played_status == "No":
        selected_team = Team.objects.filter(id=str_selected_team_id)
        user_details_rec.team_selected = selected_team[0]
        user_details_rec.save()
    elif curr_datetime > match_deadline_datetime and match_played_status == "No":
        context = {
            'alert_msg': "Oops!! You have missed the deadline. You need to submit before " + match_deadline_datetime.time().strftime("%H : %M") + " IST"
        }
        return render(request, 'ecl/no_league_found.html', context)

    list_output_data = get_list_of_all_matches_data(request)
    str_submission_msg = "You have Successfully chosen team : " + selected_team[0].team_name

    if len(list_output_data) > 0:
        context = {'all_data': list_output_data, 'alert_msg': str_submission_msg}
        return render(request, 'ecl/all_leagues_view.html', context)
    else:
        context = {'alert_msg': "You have not joined any league. Please select 'Join League' option from the top and join a league by passing league code."}
        return render(request, 'ecl/no_league_found.html', context)


@login_required(login_url='')
def single_league_matches_view(request, league_id):
    dict_filter = {'league_id': league_id}
    list_output_data = get_list_of_all_matches_data(request, filter_var=dict_filter)

    if len(list_output_data) > 0:
        context = {'all_data': list_output_data, 'alert_msg': ""}
        return render(request, 'ecl/all_leagues_view.html', context)
    elif len(list_output_data) == 0:
        context = {'alert_msg': "Incorrect inputs have been provided, please verify the URL which you have given."}
        return render(request, 'ecl/no_league_found.html', context)


@login_required(login_url='')
def my_profile_view(request):
    context = {}
    str_user_name = request.user
    list_user_data = User.objects.filter(username=str_user_name)
    user_obj = list_user_data[0]
    str_full_name = user_obj.get_full_name()
    str_email_id = user_obj.email
    user_values = {
        'user_name': str_user_name,
        'full_name': str_full_name,
        'email_id': str_email_id,
    }
    context['user_details'] = user_values
    return render(request, 'ecl/profile_view.html', context)


def logout_view(request):
    # print("Logging Out")
    context = {}
    logout(request)
    # return HttpResponse("<h3>Successful Logout" + "</h3>")
    return render(request, 'ecl/logout_page.html', context)
