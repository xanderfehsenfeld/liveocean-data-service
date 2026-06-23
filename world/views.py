from datetime import datetime

from django.http import JsonResponse, HttpResponse, Http404
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from .models import LiveOceanDrifterForecast


# def worldborder_list(request):
#     """List WorldBorder objects.

#     Query params:
#     - format=geojson to return GeoJSON (Content-Type: application/geo+json)
#     - limit, offset for simple pagination
#     """
#     fmt = request.GET.get('format', 'json').lower()
#     limit = request.GET.get('limit')
#     offset = request.GET.get('offset', 0)
#     qs = WorldBorder.objects.all().order_by('id')
#     # apply simple slicing if provided
#     if limit:
#         try:
#             limit = int(limit)
#             offset = int(offset)
#             qs = qs[offset:offset + limit]
#         except ValueError:
#             pass

#     if fmt == 'geojson':
#         geojson = serialize('geojson', qs, geometry_field='mpoly', fields=('name', 'area', 'pop2005', 'iso2', 'iso3', 'lon', 'lat'))
#         return HttpResponse(geojson, content_type='application/geo+json')

#     # default JSON response with selected fields
#     data = []
#     for o in qs:
#         data.append({
#             'id': o.id,
#             'name': o.name,
#             'area': o.area,
#             'pop2005': o.pop2005,
#             'iso2': o.iso2,
#             'iso3': o.iso3,
#             'lon': o.lon,
#             'lat': o.lat,
#         })

#     return JsonResponse({'count': WorldBorder.objects.count(), 'results': data})


# def worldborder_detail(request, pk):
#     """Retrieve a single WorldBorder by primary key."""
#     fmt = request.GET.get('format', 'json').lower()
#     obj = get_object_or_404(WorldBorder, pk=pk)

#     if fmt == 'geojson':
#         geo = serialize('geojson', [obj], geometry_field='mpoly', fields=('name', 'area', 'pop2005', 'iso2', 'iso3', 'lon', 'lat'))
#         return HttpResponse(geo, content_type='application/geo+json')

#     data = {
#         'id': obj.id,
#         'name': obj.name,
#         'area': obj.area,
#         'pop2005': obj.pop2005,
#         'iso2': obj.iso2,
#         'iso3': obj.iso3,
#         'lon': obj.lon,
#         'lat': obj.lat,
#     }
#     return JsonResponse(data)



def forecast_drifters(request):


    current_date = datetime.now().date()

    result = LiveOceanDrifterForecast.objects.filter(date_of_query=current_date).first()

    if (result is None):
        ## make http get request to get drifter data
    else:
        return JsonResponse(result)





