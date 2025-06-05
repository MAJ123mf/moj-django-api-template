#Django imports
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.forms.models import model_to_dict
from django.contrib.auth.mixins import LoginRequiredMixin

#Geoss
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import SnapToGrid

#rest_framework imports
from rest_framework import viewsets
from rest_framework import permissions

#My imports
from core.myLib.geometryTools import WkbConversor, GeometryChecks
from .models import Roads
from .serializers import RoadsSerializer
from djangoapi.settings import EPSG_FOR_GEOMETRIES, ST_SNAP_PRECISION, MAX_NUMBER_OF_RETRIEVED_ROWS
from core.myLib.baseDjangoView import BaseDjangoView

from decimal import Decimal, ROUND_HALF_UP

def custom_logout_view(request):
    logout(request)                      # tu odjavimo uporabnika iz seje
    return redirect("/accounts/login/")  # tu nas preusmeri nazaj na login stran, 

class HelloWord(View):
    def get(self, request):
        return JsonResponse({"ok":True,"message": "Hello world from app. Roads", "data":[]})        

class RoadsView(BaseDjangoView):
    # BaseDjangoView je OSNOVNI razred, ki definira skupno logiko, ki jo uporablja več podedovanih view-ov. 
    # Ponuja privzete metode GET, POST, UPDATE, SELECTONE, SELECTALL... in omogoča ponovno uporabo te logike v podedovanih view-ih.

    # The get and post methods are defined in the BaseDjangoView. They forward the request
    # to the methods selectone, selectall, insert, update, and delete, depending of the 
    # action parameter in the URL.

    # This class redefine the the methods selectone, selectall, insert, update, and delete
    # of the BaseDjangoView class to add a new action, insert2.
  
    # To use this view:
    # To get a record, the URL must be like:
    #     GET /roads_view/selectone/<id>/
    # To get all the records, the URL must be like:
    #     GET /roads_view/selectall/
    # To insert a record, the URL must be like:
    #     POST /roads_view/insert/ --> The data must be sent in the body of the request.
    # To update a record, the URL must be like:
    #     POST /roads_view/update/<id>/ --> The data must be sent in the body of the request.
    # To delete a record, the URL must be like:
    #     POST /roads_view/delete/<id>/
 
    
    def post(self, request, *args, **kwargs):
        # request vsebuje podatke o zahtevi, ki jo je uporabnik poslal
        # *args je list argumentov, ki jih posredujemo metodi
        # **kwargs je dictionary argumentov, ki jih posredujemo metodi

        # Te spodnje vrstice redifinirajo post metodo razreda BaseDjangoView, tako da podtaknemo novo metodo oz. akcijo insert2.
        # če je akcija insert2, pokliče metodo insert2, sicer
        # pokliče metodo post razreda BaseDjangoView.
        
        action = kwargs.get('action')
        print(f"action child: {action}")

        if action == 'insert2':             # če imamo svojo metodo insert2, jo pokličemo
            return self.insert2(request)
        else:                               # sicer pokličemo metodo post razreda BaseDjangoView
            return super().post(request, *args, **kwargs)

    #GET OPERATIONS
    # Ta metoda (selectone) ni javna URL, ne moreš je poklicati iz brskalnika, ker nima URL-ja
    # ampak je javna metoda, ki jo lahko pokličeš v programu iz razreda BaseDjangoView
    # Tu redifiniramo metodo selectone, ki je definirana v razredu BaseDjangoView. Tam je definirana kot splošna metoda,
    # tu pa to splošno metodo prilagodimo tako, da deluje samo za model Roads.
    # link: http://localhost:8000/roads/roads_view/selectone/1/
    def selectone(self, id):                        # metoda selectone je definirana v razredu BaseDjangoView 
        l=list(Roads.objects.filter(id=id))     # l je seznam objektov Roads, ki jih dobimo iz baze
        if len(l)==0:                               # če seznam l nima elementov, to pomeni, da objekt Roads z id-jem id ne obstaja
            return JsonResponse({'ok':False, "message": f"The road id {id} does not exist", "data":[]}, status=400)
        b=l[0]                                      # b je prvi element seznama l, ki je objekt Roads
        d=model_to_dict(b)                          # naredi dictionary d iz objekta Roads
        d['geom']=b.geom.wkt                        # b.geom.wkt pretvori Poligon stavbe v WKT (Well Known Text) format, ki je primeren za izpis
        return JsonResponse({'ok':True, 'message': 'Road Retriewed', 'data': [d]}, status=200)

    # podobna metoda kot zgoraj, samo da vrne vse objekte Roads
    # Link: http://localhost:8000/roads/roads_view/selectall/
    def selectall(self):
        l=Roads.objects.all()[:MAX_NUMBER_OF_RETRIEVED_ROWS]
        data=[]
        for r in l:
            d=model_to_dict(r)
            d['geom']=r.geom.wkt
            data.append(d)
        return JsonResponse({'ok':True, 'message': 'Road data retrieved', 'data': data}, status=200)

    #POST OPERATIONS
    # Tudi metoda insert ni samostojna URL metoda, ampak je metoda, ki jo lahko pokličeš iz razreda BaseDjangoView.
    # link: POST http://localhost:8000/roads/roads_view/insert/        INSERT torej POST torej POSTMAN
    # zahtevo pošljemo v POSTMANU kot telo zahteve (x-www-form-urlencoded) navedemo:
    #      KEY:           VALUE:  
    #     "str_name": "Celjska cesta",
    #     "administrator": "DARS",
    #     "maintainer": "JKP SG",
    #     "length": 700,
    #     "geom": "LINESTRING(0 0, 0 10)"
    def insert(self, request):
        # Inserts the polygon. Latter snap it to the grid. This must be done
        # in the database. So we need to insert it before.
        # After the road has been inserted:
        #     - snap it to grid
        #     - Check if the geometry is valid
        #     - Check if the interior intersects with other geometry
        #     - If any check fails, remove the row.
        #     - The only inconvenient is the id counter sums one more
        
        originalWkt=request.POST.get('geom', None)   # preverimo ali imamo geometrijo v POST zahtevi
        if originalWkt is None:                      # če nimamo geometrije, se spremenljivka originalWkt nastavi na None, in vrnemo napako
            return JsonResponse({'ok':False, 'message': 'The geometry is mandartory', 'data':[], 'post_data': dict(request.POST) },  status=400)
        
        #Creates the geometry
        g=GEOSGeometry(request.POST.get('geom',''), srid=EPSG_FOR_GEOMETRIES)   # EPSG 25830 zamenjan z WGS84 4326
        #print the representation of the object
        print(f"Original geometry: {g}")

        str_name = request.POST.get('str_name','') 
        administrator = request.POST.get('str_name','') 
        maintainer = request.POST.get('str_name','') 
        str_name = request.POST.get('str_name','') 

        r=Roads(st_name=str_name, administrator=administrator, maintainer=maintainer, length=g.length, geom=g)
        r.save()
        print(f"Road geometry inserted id: {r.id}")

        #Update the geometry to an snaped one to the grid
        Roads.objects.filter(id=r.id).update(geom=SnapToGrid('geom', ST_SNAP_PRECISION))

        #Now we get a new object with the new geometry to perform the checks
        r=Roads.objects.get(id=r.id)           # ponovno preberemo objekt Roads iz baze, da dobimo novo geometrijo
        print('Snapped geometry',r.geom.wkt)       # pretvori geometrijo v WKT format in jo izpiše
        #bGeos=GEOSGeometry(b.geom.wkt, srid=25830)
        #valid=bGeos.valid
        #b.geom is a GEOSGeometry object, so we can use it directly
        valid=r.geom.valid
        print(f'Valid: {valid}')
        if not valid:
            print(f"Deleting invalid geometry {r.id}")   # če geometrija ni veljavna, jo izbrišemo
            r.delete()
            return JsonResponse({'ok':False, 'message': 'The Road geometry is not valid after the st_SnapToGrid', 'data':[]}, status=400)   

        #create a filter to get all the geometries which interiors intersects,
        #but excluding the one just created
        filt=Roads.objects.filter(geom__relate=(g.wkt,'T********')).exclude(id=b.id)   # te filtre že poznamo iz prejšnjih vaj
        print(f"Query:{filt.query}")
        exist=filt.exists()
        print(f"Exists {exist}") 
        n=filt.count() 
        print(f"Count: {n}")
        print(f"Values: {list(filt)}")
        
        if exist:         # če obstajajo geometrije, ki se sekajo z novo geometrijo, jo izbrišemo in izpišemo poročilo o napaki
            print(f"Deleting roads id {r.id}, as it intersects with others")
            r.delete()
            return JsonResponse({'ok':False, 'message': f'The road intersects with {n} road/s'}, status=400)
        
        #create a roads object, from the model Roads
        d=model_to_dict(r)       # pretvori objekt Roads v dictionary, da ga lahko izpišemo v JSON formatu
        d['geom']=r.geom.wkt
        return JsonResponse({'ok':True, 'message': 'Road data inserted', 'data': [d]}, status=201)





    def update(self, request, id):
        # On update you shoud also check the new geometry: snap it, check if it is valid,
        #     check if it intersects with others except itself.
        
        # The problem here is, if after having updated the geometry, if it is not valid, 
        #     or interesects with others, you must restore the original geometry.
        #     This is perfectry possible but we are not going to do it, istead
        #     we are going to use a psycop connection and a raw sql query to
        #     get the snapped geometry as wkb. This demonstrates
        #     some times it is better to know raw sql.
        l=list(Roads.objects.filter(id=id))    # naredili bomo update road z danim id-jem, torej pridobimo to stavbo iz baze
        if len(l)==0:                              # če stavba ne obstaja, vrnemo napako
            return JsonResponse({'ok':False, "message": f"The road id {id} does not exist", "data":[]}, status=400)
        r=l[0]                                     # r je prvi (z indexom=0) objekt Roads, ki ga dobimo iz baze.

        originalWkt=request.POST.get('geom', None)    # iz POST zahteve izluščimo geometrijo
        
        if originalWkt is not None:                        # če imamo geometrijo, jo pretvorimo v WKB format
            conversor=WkbConversor()                       # Ustvarimo objekt wkb za pretvorbo geometrijskih podatkov
            wkb=conversor.set_wkt_from_text(originalWkt)   # Pretvorimo WKT v WKB (Well-Known Binary)
            newWkt=conversor.get_as_wkt()                  # Dobimo pretvorjen WKT iz WKB
            geojson=conversor.get_as_geojson()             # Dobimo GeoJSON predstavitev geometrije
            gc=GeometryChecks(wkb)                         # Ustvarimo objekt gc za preverjanje geometrije
            isValid=gc.is_geometry_valid()                 # Preverimo, ali je geometrija veljavna
            interesectionIds=gc.check_st_relate('roads_roads','T********', id_to_avoid=id) # Preverimo, ali se geometrija sekajo z drugimi geometrijami
            thereAre = gc.are_there_related_ids()          # vrne True ali False, glede na to ali obstajajo geometrije, ki se sekajo z novo geometrijo
            
            print(f"Snaped wkt: {newWkt}")
            print(f"Snaped geojson: {geojson}")
            print(f"Snaped is valid: {isValid}")
            print(f"Snaped intersection ids: {interesectionIds}")
            print(f"There are intersection ids: {thereAre}")
            print(gc.get_relate_message())

            if not(isValid):                     # če geometrija ni veljavna, vrnemo napako
                return JsonResponse({'ok':False, 'message': 'The geometry is not valid after the st_SnapToGrid', 'data':[]}, status=400)   
            if gc.are_there_related_ids():       # če obstajajo geometrije, ki se sekajo z novo geometrijo, vrnemo napako
                return JsonResponse({'ok':False, 'message': gc.get_relate_message(), 'data':gc.related_ids}, status=400)   
            r.geom=wkb
            r.str_name=request.POST.get('str_name', '')
            r.administrator=request.POST.get('administrator', '')
            r.maintainer=request.POST.get('maintainer', '')
            polyGeos=GEOSGeometry(wkb)
            r.length=polyGeos.length                  # izračunamo površino nove geometrije
            r.save()
            d=model_to_dict(r)
            d['geom']=conversor.get_as_wkt()#snaped version
        else:                                     # če v zahtevi nimamo geometrije, vrnemo napako
            return JsonResponse({'ok':False, 'message': 'The geometry mandartory', 'data':[]}, status=400)
             # če je geometrija veljavna, izpišemo sporočilo o uspehu in vrnemo podatke o stavbi
        return JsonResponse({'ok':True, 'message': "Road updated", 'data':[d]}, status=200) 




    def delete(self, id):
        l=list(Roads.objects.filter(id=id))
        if len(l)==0:
            return JsonResponse({'ok':False, "message": f"The road id {id} does not exist", "data":[]}, status=400)
        b=l[0]
        b.delete()  
        return JsonResponse({'ok':True, "message": f"The road id {id} has been deleted", "data":[]}, status=200)



    # Ta medoda je enaka kot insert, samo da uporablja modul geometryTools.py, ki ga je napisal učitelj.
    # Ta modul je bil napisan, ker sem ugotovil, da je uporaba Geoss knjižnice nekoliko zapletena, predvsem pri posodabljanju,
    # zaradi preverjanja geometrijskih podatkov, ki jih insertiramo
    # Ta knjižnica je v direktoriju core/myLib/geometryTools.py
    #
    # Malo drugače deluje kot zgornji insert!
    # Pri insert smo stavbo vpisali v bazo, potem pa smo jo posodobili, da smo dobili geometrijo, ki je bila snapana na mrežo.
    # Tu pa najprej pretvorimo geometrijo v WKB format, iz zahteve dobimo geometrijo v WKT formatu,...
    # potem pa jo snapamo na mrežo in preverimo geometrijske podatke.
    # in šele nato jo vpišemo v bazo.
    # Ta postopek je bolj naraven, saj ne pišemo in brišemo iz baze če to ni treba.
    #
    # Je pa treba vsaj približno razumeti, učiteljeve metode v /core/myLib/geometryTools.py
    # link: POST http://localhost:8000/roads/roads_view/insert2/
    def insert2(self, request):
        originalWkt=request.POST.get('geom', None) # iz post zahteve izluščimo geometrijo, ki je že v WKT formatu
        
        if originalWkt is not None:
            conversor=WkbConversor()
            wkb=conversor.set_wkt_from_text(originalWkt) # WKT spretvorimo v WKB format
            gc=GeometryChecks(wkb)                       # Ustvarimo objekt gc za preverjanje geometrijskih podatkov
            isValid=gc.is_geometry_valid()               # Preverimo, ali je geometrija veljavna
            gc.check_st_relate('roads_roads','T********')    # Preverimo, ali se geometrija sekajo z drugimi geometrijami
            print(gc.get_relate_message())                           # izpišemo sporočilo o napaki, če obstaja 

            if not(isValid):    # če geometrija ni veljavna, vrnemo napako
                return JsonResponse({'ok':False, 'message': 'The geometry is not valid after the st_SnapToGrid', 'data':[]}, status=400)   
            if gc.are_there_related_ids():    # če obstajajo geometrijske geometrija, ki se sekajo z novo geometrijo, vrnemo napako
                return JsonResponse({'ok':False, 'message': gc.get_relate_message(), 'data':gc.related_ids}, status=400)   
            
            r=Roads()            # Ustvarimo nov objekt Roads
            r.geom=wkb               # nastavimo geometrijo na WKB format, wkt pretvorimo v wkb format
            r.str_name=request.POST.get('str_name', '')   # iz POST zahteve izluščimo street name
            r.administrator=request.POST.get('administrator', '')   # iz POST zahteve izluščimo upravljalca ceste
            r.maintainer=request.POST.get('maintainer', '')   # iz POST zahteve izluščimo vzdrževalca ceste
            r.length=round(r.geom.length, 2)                                  # izračunamo površino nove geometrije
            r.save()                                            # shranimo objekt Roads v bazo
            d=model_to_dict(r)
            d['geom']=r.geom.wkt
        else:                       # če v zahtevi nimamo geometrijo, vrnemo napako            
            return JsonResponse({'ok':False, 'message': 'The geometry mandartory', 'data':[]}, status=400)
        # če je geometrija veljavna, izpišemo sporočilo o uspehu in vrnemo podatke o stavbi
        return JsonResponse({'ok':True, 'message': "Roads Inserted", 'data':[d]}, status=200)  




# Create your views here.
class RoadsModelViewSet(viewsets.ModelViewSet):
    #     GET operation over /roads/roads/. It will return all reccords
    #     GET operation over /roads/roads/<id>/. 
    #     POST operation over /roads/roads/. It will insert a new record
    #     PUT operation over /roads/roads/<id>/. 
    #     PATCH operation over /roads/roads/<id>/. 
    #     DELETE operation over /roads/roads/<id>/. 
    queryset = Roads.objects.all().order_by('id')  # izpis na front-endu bo urejen po id-ju
    serializer_class = RoadsSerializer           
    permission_classes = [permissions.AllowAny]
                                