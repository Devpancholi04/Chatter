from django.shortcuts import render
from django.http import HttpResponse

from community.models import Community, CommunityMember
# Create your views here.

def home_page(request):
    user = request.user

    get_member_in_community = CommunityMember.objects.filter(member = user).values_list('community__community_id', flat=True)

    non_member_community = Community.objects.exclude(community_id__in=get_member_in_community)
    print(non_member_community)
    params = {
        'non_member_community' : non_member_community,
    }
    


    return render(request, "home/home_page.html", params) 