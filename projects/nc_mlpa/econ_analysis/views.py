from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context
import os
from lingcod.common.utils import load_session
from nc_mlpa.mlpa.models import *
from econ_analysis.models import *
from Layers import *
from Analysis import *
from django.contrib.auth.models import Group
from django.conf import settings

'''
Generates and returns a list of id values for all publicy shared arrays and all publicly shared mpas
Called by feature_is_public()
'''
def get_public_id_lists():
    #get list of public groups
    public_groups = Group.objects.filter(name__in=settings.SHARING_TO_PUBLIC_GROUPS)
    #use the public groups list to obtain a list of public arrays
    public_arrays = MpaArray.objects.filter(sharing_groups__in=public_groups)
    #generate a list of public array id values
    public_array_ids = [array.id for array in public_arrays]
    
    #use the public groups list to obtain a list of public mpas
    public_mpas = MlpaMpa.objects.filter(sharing_groups__in=public_groups)
    #generate a list of public mpa id values
    public_mpa_ids = [mpa.id for mpa in public_mpas]
    #add to the list of public mpa id values, all those mpa ids belonging to the mpas in the public arrays
    #we want to ensure that a user can view impact analysis on an mpa that belongs to a publicly shared array 
    #(the mpa itself might not be marked as public, but the array it belongs to is)
    mpa_ids_in_public_arrays = [[mpa.id for mpa in array.mpa_set] for array in public_arrays]
    for mpas in mpa_ids_in_public_arrays:
        for id in mpas:
            public_mpa_ids.append(id)
    
    return public_array_ids, public_mpa_ids

'''
Returns boolean value based on whether the feature (mpa/array) in question is publicly shared or not
'''   
def feature_is_public(feature, feature_id):
    try:
        (public_array_ids, public_mpa_ids) = get_public_id_lists()
    except:
        return False
    #if the feature does not belong to the list of public features, return false
    if feature == 'mpa':
        mpa_id = int(feature_id)
        if mpa_id not in public_mpa_ids:
            return False
    else: #must be array request
        array_id = int(feature_id)
        if array_id not in public_array_ids:
            return False
    #otherwise return true
    return True
    
'''
Returns boolean value based on whether the feature (mpa/array) in question belongs to the user
'''   
def feature_belongs_to_user(user, feature_type, feature_id):
    #if a feature does not exist with the given id and the given user, return false
    if feature_type == 'mpa':
        try:
            mpa = MlpaMpa.objects.get(user=user, id=feature_id)
        except:
            return False
    else: #feature_type must be array
        try:
            array = MpaArray.objects.get(user=user, id=feature_id)
        except:
            return False
    #otherwise, return true
    return True
        
'''
Returns boolean value based on whether the feature (mpa/array) in question is shared with the user
'''  
def feature_is_shared_with_user(user, feature_type, feature_id):
    #obtain the groups this feature is associated with
    if feature_type == 'mpa':
        try:
            #obtain the groups this mpa is associated with
            mpa = MlpaMpa.objects.get(id=feature_id)
            sharing_groups = mpa.sharing_groups
            #obtain the groups this mpa's array is associated with
            array = mpa.array
            if array:
                sharing_groups_for_array = array.sharing_groups.all()
                for group in sharing_groups_for_array:
                    sharing_groups.append(group)
        except:
            return False
    else:
        try:
            array = MpaArray.objects.get(id=feature_id)
            sharing_groups = array.sharing_groups.all()
        except:
            return False
    #check all groups the user is associated with against those the feature is associated with
    #if we find a match, return true
    for user_group in user.groups.all():
        if user_group in sharing_groups:
            return True
    #otherwise, return false
    return False

def user_can_view_feature(user, feature_id, feature_type):
    if user.is_anonymous() or not user.is_authenticated():
        if not feature_is_public(feature_type, feature_id):
            return False
    else:
        if not feature_belongs_to_user(user, feature_type, feature_id):
            if not feature_is_public(feature_type, feature_id):
                if not feature_is_shared_with_user(feature_type, feature_id):
                    return False
    return True
    
'''
Accessed via named url when user selects a group (Commercial, Recreational Dive, etc) to run analysis on 
'''
def impact_analysis(request, feature_id, group, feature='mpa'): 
    user = request.user
    if not user_can_view_feature(user, feature_id, feature):
        return HttpResponse('You do not have permission to view this feature', status=401)
        
    group_name = Layers.GROUPS[group]
    if feature == 'mpa':
        #the following port and species parameters are for testing on my local machine
        #return display_mpa_analysis(request, feature_id, group_name, port='Eureka', species='Salmon')
        return display_mpa_analysis(request, feature_id, group_name)
    else:
        array = get_object_or_404(MpaArray, pk=feature_id)
        mpas = array.mpa_set
        array_results = compile_array_results(mpas, group_name)
        return display_array_analysis(request, group_name, array, array_results)

def compile_array_results(mpas, group, port=None, species=None):
    array_results = []
    #Sum results for each species, for each mpa in the array
    for mpa in mpas:
        if mpa.designation_id is not None: #ignore Stewardship Zones and other mpas that have no LOP
            #What to do if mpa_analysis_results returns a Response object instead of a result?
            mpa_results = mpa_analysis_results(mpa, group, port, species)
            array_results.append(mpa_results)
    return array_results
        
def display_array_analysis(request, group, array, array_results, port=None, species=None, template=None):
    if group == 'Commercial':
        #aggregate array results for commercial group
        aggregated_results = aggregate_com_array_results(array_results, group)
        #restructure into AnalysisResults data structure
        (analysis_results, port_impacts, studyregion_impacts) = restructure_aggregated_commercial_results(array, group, aggregated_results)
        if template is None:
            template = 'array_impact_analysis_com.html'
        return render_to_response(template, RequestContext(request, {'user_group': group, 'array':array, 'analysis_results': analysis_results, 'port_impacts': port_impacts, 'studyregion_impacts': studyregion_impacts}))  
    elif group == 'Commercial Passenger Fishing Vessel':
        #aggregate array results for commercial passenger fishing vessel group
        aggregated_results = aggregate_cpfv_array_results(array_results, group)
        #restructure into AnalysisResults data structure
        analysis_results = restructure_aggregated_cpfv_results(array, group, species, aggregated_results)
        if template is None:
            template = 'array_impact_analysis_cpfv.html'
        return render_to_response(template, RequestContext(request, {'user_group': group, 'array':array, 'array_results': analysis_results}))  
    elif group == 'Edible Seaweed':
        #aggregate array results for edible seaweed group
        aggregated_results = aggregate_swd_array_results(array_results, group)
        #restructure into AnalysisResults data structure
        analysis_results = restructure_aggregated_swd_results(array, group, aggregated_results)
        if template is None:
            template = 'array_impact_analysis_swd.html'
        return render_to_response(template, RequestContext(request, {'user_group': group, 'array':array, 'array_results': analysis_results}))  
    else: #(must be Recreational)
        #aggregate array results for edible seaweed group
        aggregated_results = aggregate_rec_array_results(array_results, group)
        #restructure into AnalysisResults data structure
        analysis_results = restructure_aggregated_rec_results(array, group, aggregated_results)
        if template is None:
            template = 'array_impact_analysis_rec.html'
        if group == 'Recreational Dive':
            group_abbr = 'div'
        elif group == 'Recreational Kayak':
            group_abbr = 'kyk'
        elif group == 'Recreational Private Vessel':
            group_abbr = 'pvt'
        return render_to_response(template, RequestContext(request, {'group_abbr': group_abbr, 'user_group': group, 'array':array, 'array_results': analysis_results}))  

def restructure_aggregated_commercial_results(array, group, aggregated_results):
    analysis_results = []
    port_impacts = []
    for port, species_results in aggregated_results.iteritems():
        port_results = []
        port_gross_impact = 0
        port_net_impact = 0
        species_list = []
        for species, results in species_results.iteritems():
            if 'Urchin' in species:
                result1 = AnalysisResult(id=array.id, type='array', group=group, port=port, species='Urchin (Dive Captain)', percOverallArea=results['Area'], percOverallValue=results['Value'])
                result2 = AnalysisResult(id=array.id, type='array', group=group, port=port, species='Urchin (Walk-on Dive)', percOverallArea=results['Area'], percOverallValue=results['Value'])
                port_results.append(result1)
                port_results.append(result2)
                if result1.GEI != '---':
                    port_gross_impact += result1.GEI + result2.GEI
                    port_net_impact += result1.NEI + result2.NEI
                    species_list.append('Urchin (Dive Captain)')
                    species_list.append('Urchin (Walk-on Dive)')
            else:
                result = AnalysisResult(id=array.id, type='array', group=group, port=port, species=species, percOverallArea=results['Area'], percOverallValue=results['Value'])
                port_results.append(result)
                if result.GEI != '---':
                    port_gross_impact += float(result.GEI)
                    port_net_impact += float(result.NEI)
                    species_list.append(species)
        port_totals = CommercialResultsByPort(port, port_gross_impact, port_net_impact, species_list)
        port_impacts.append( port_totals )
        #sort results by species name (alphabetically)
        port_results = sort_results_by_species(port_results)
        analysis_results.append(port_results)
    studyregion_impacts = CommercialStudyRegionResults(port_impacts)
    analysis_results = sort_results_by_port(analysis_results, group)
    port_impacts = sort_results_by_port(port_impacts)
    return analysis_results, port_impacts, studyregion_impacts
        
def restructure_aggregated_cpfv_results(array, group, species, aggregated_results):
    analysis_results = []
    for port, results in aggregated_results.iteritems():
        analysis_results.append(AnalysisResult(id=array.id, type='array', group=group, port=port, species=species, percOverallArea=results['Area'], percOverallValue=results['Value']))
    #sort results by port name (north to south)
    analysis_results = sort_results_by_port(analysis_results, group) 
    return analysis_results       
    
def restructure_aggregated_swd_results(array, group, aggregated_results):
    analysis_results = []
    for port, species_results in aggregated_results.iteritems():
        port_results = []
        for species, results in species_results.iteritems():
            port_results.append(AnalysisResult(id=array.id, type='array', group=group, port=port, species=species, percOverallArea=results['Area'], percOverallValue=results['Value']))
        #sort results by species name (alphabetically)
        port_results = sort_results_by_species(port_results)
        #port_results = roundPercentageValues(port_results, 1)  
        analysis_results.append(port_results)
    #sort results by port name (north to south)
    analysis_results = sort_results_by_port(analysis_results, group) 
    return analysis_results       
               
def restructure_aggregated_rec_results(array, group, aggregated_results):
    analysis_results = []
    for port, species_results in aggregated_results.iteritems():
        port_results = []
        for species, results in species_results.iteritems():
            port_results.append(AnalysisResult(id=array.id, type='array', group=group, port=port, species=species, percOverallArea=results['Area'], percOverallValue=results['Value']))
        #sort results by species name (alphabetically)
        port_results = sort_results_by_species(port_results)
        #port_results = roundPercentageValues(port_results, 1)  
        analysis_results.append(port_results)
    #sort results by port name (north to south)
    analysis_results = sort_results_by_port(analysis_results, group) 
    return analysis_results       

def aggregate_com_array_results(array_results, group):
    aggregated_array_results = get_empty_array_results_dictionary(group)
    for mpa_results in array_results:
        for port in mpa_results:
            for result in port:
                if result.percOverallValue == '---':
                    pass
                elif aggregated_array_results[result.port][result.species]['Value'] == '---':
                    aggregated_array_results[result.port][result.species]['Value'] = float(result.percOverallValue)
                    aggregated_array_results[result.port][result.species]['Area'] = float(result.percOverallArea)
                else:
                    aggregated_array_results[result.port][result.species]['Value'] += result.percOverallValue
                    aggregated_array_results[result.port][result.species]['Area'] += result.percOverallArea
    return aggregated_array_results       
        

def aggregate_cpfv_array_results(array_results, group):
    aggregated_array_results = get_empty_array_results_dictionary(group)
    group_ports = GetPortsByGroup(group)
    #sum up the value percentages at each port, keeping track of the number of summations made
    for mpa_results in array_results:
        #port_counts is used for determining average gei% among all relevant species for each port 
        #(we only need to calculate port_counts for one mpa as it will be the same for each mpa)
        port_counts = dict( (port, 0) for port in group_ports)
        for port_results in mpa_results:
            for result in port_results:
                if result.percOverallValue == '---':
                    pass
                elif aggregated_array_results[result.port]['Value'] == '---':
                    aggregated_array_results[result.port]['Value'] = float(result.percOverallValue)
                    aggregated_array_results[result.port]['Area'] = float(result.percOverallArea)
                    port_counts[result.port] = 1
                else:
                    aggregated_array_results[result.port]['Value'] += result.percOverallValue
                    aggregated_array_results[result.port]['Area'] += result.percOverallArea
                    port_counts[result.port] += 1
    for port in group_ports:
        if aggregated_array_results[port]['Value'] != '---':
            aggregated_array_results[port]['Value'] /= port_counts[port]
    return aggregated_array_results       
    
def aggregate_rec_array_results(array_results, group):
    aggregated_array_results = get_empty_array_results_dictionary(group)
    for mpa_results in array_results:
        for port_results in mpa_results:
            for result in port_results:
                if result.percOverallValue == '---':
                    pass
                elif aggregated_array_results[result.port][result.species]['Value'] == '---':
                    aggregated_array_results[result.port][result.species]['Value'] = float(result.percOverallValue)
                    aggregated_array_results[result.port][result.species]['Area'] = float(result.percOverallArea)
                else:
                    aggregated_array_results[result.port][result.species]['Value'] += result.percOverallValue
                    aggregated_array_results[result.port][result.species]['Area'] += result.percOverallArea
    return aggregated_array_results       
   
def aggregate_swd_array_results(array_results, group):
    aggregated_array_results = get_empty_array_results_dictionary(group)
    for mpa_results in array_results:
        for port_results in mpa_results:
            for result in port_results:
                if result.percOverallValue == '---':
                    pass
                elif aggregated_array_results[result.port][result.species]['Value'] == '---':
                    aggregated_array_results[result.port][result.species]['Value'] = float(result.percOverallValue)
                    aggregated_array_results[result.port][result.species]['Area'] = float(result.percOverallArea)
                else:
                    aggregated_array_results[result.port][result.species]['Value'] += result.percOverallValue
                    aggregated_array_results[result.port][result.species]['Area'] += result.percOverallArea
    return aggregated_array_results      
    
def sort_results_by_species(results):   
    #sort results alphabetically by species name
    results.sort(key=lambda obj: obj.species)  
    return results
    
def sort_results_by_port(results, group=None):
    #sort results by port name (north to south)
    if group is None:
        ports = GetPortsByGroup('Commercial')
    else:
        ports = GetPortsByGroup(group)
    count = 0
    #build a dictionary that maps each port (key), with an ordinal (value)
    ordering = {}
    for port in ports:
        count += 1
        ordering[port] = count
    #use that dictionary to order the results by port
    if group in ['Commercial Passenger Fishing Vessel', None]:
        results.sort(lambda x, y : cmp (ordering[x.port], ordering[y.port]))  
    else: 
        results.sort(lambda x, y : cmp (ordering[x[0].port], ordering[y[0].port]))
    return results
    
    
def get_empty_array_results_dictionary(group):
    #CAN WE CHANGE THE FOLLOWING TWO PROCEDURE CALLS TO DB QUERIES?
    group_species = GetSpeciesByGroup(group)
    group_ports = GetPortsByGroup(group)
    initialValue = '---'
    initialArea = '---'
    if group == 'Commercial':
        empty_results = dict( (port, dict( (Layers.COMMERCIAL_SPECIES_DISPLAY[species], {'Value':initialValue, 'Area':initialArea}) for species in group_species)) for port in group_ports)
    elif group == 'Commercial Passenger Fishing Vessel':
        empty_results = dict( (port, {'Value':initialValue, 'Area':initialArea}) for port in group_ports)
    elif group == 'Edible Seaweed':
        empty_results = dict( (port, {'Seaweed (Hand Harvest)': {'Value':initialValue, 'Area':initialArea}}) for port in group_ports) 
    else:
        empty_results = dict( (port, dict( (species, {'Value':initialValue, 'Area':initialArea}) for species in group_species)) for port in group_ports) 
    return empty_results
  
'''
Called from impact_analysis and MpaEconAnalysis
Renders template with embedded analysis results
'''
def display_mpa_analysis(request, feature_id, group, port=None, species=None, template='impact_analysis.html'):

    mpa = get_object_or_404(MlpaMpa, pk=feature_id)
    
    mpa_results = mpa_analysis_results(mpa, group, port, species)
    
    try:
        #if mpa_analysis_results threw an error it will return a response object of some sort
        if mpa_results.status_code:
            response_object = mpa_results
            return response_object
    except:
        #otherwise it worked 
        return render_to_response(template, RequestContext(request, {'mpa':mpa, 'all_results': mpa_results}))  

#would be nice to produce some helper methods from within here...
def mpa_analysis_results(mpa, group, port, species):
    mpa_results = []
    
    #Get analysis results for given port or all ports 
    if not port:
        ports = GetPortsByGroup(group)
    else:
        ports = [port]
        
    #Get results for each port
    for single_port in ports:
        port_results = []
        #See if we can retreive results from cache
        #There is a problem here in that when a cache row is deleted for a particular mpa_id, group, port, AND species
        #The cache retreival will assume there are no results for that species when the reality may be different
        #This issue should be resolved by future caching strategy 
        #(a strategy that maybe packages a single cache by mpa, group? or mpa, group, port?)
        if species is None:
            cache = FishingImpactResults.objects.filter(mpa=mpa.id, group=group, port=single_port)
        else:
            cache = FishingImpactResults.objects.filter(mpa=mpa.id, group=group, port=single_port, species=species)
        cache_available = False
        if len(cache) > 0:
            cache_available = True
        for single_cache in cache:
            if single_cache.date_modified < mpa.date_modified:
                cache_available = False
                break
        
        #get results from cache
        #if they don't exist or are out of date, then run the analysis
        if cache_available:
            results = list(cache)
            for result in results:
                port_results.append(AnalysisResult(id=result.mpa_id, type='mpa', group=group, port=single_port, species=result.species, percOverallArea=result.perc_area, percOverallValue=result.perc_value))
        else: 
            #since at least one cache was not current, remove all related entries as they will all be recreated and recached below
            for single_cache in cache:
                single_cache.delete()
            #Get all maps from the group and port (and possibly species) that we want to analyze
            maps = FishingImpactAnalysisMap.objects.getSubset(group, single_port, species)
            #WILL THIS SOMETIMES BE EMPTY?
            #AND IF SO, SHOULD THIS BE ALLOWED (I'M SEEING EMPTY RIGHT NOW WITH EUREKA SALMON ON DIV) -- RETURNS [] (NOT '')
            #IF IT'S ALLOWED, WE CAN SIMPLY COUCH THE REST OF THIS ELSE IN AN IF LEN(MAPS) > 0
            if maps is '':
                return HttpResponseBadRequest('A Fishing Map with User group, %s, Port, %s, and Species, %s, does not exist.' % (group, single_port, species))
            if len(maps) > 0:
                #run the analysis
                analysis = Analysis()
                port_results = analysis.run(mpa, maps)
                if port_results < 0:
                    return HttpResponseBadRequest('Error running analysis')
                #Cache analysis results 
                cache_analysis_results(port_results, group, mpa)
            
        #Expand results to include those species that exist within the group but not perhaps within this port (denoted with '---')
        port_results = flesh_out_results(group, single_port, port_results)

        #sort results alphabetically by species name
        port_results.sort(key=lambda obj: obj.species)
                
        mpa_results.append(port_results)
    return mpa_results
    
#no longer used...
def roundPercentageValues(results, sig_digs):
    import utilities as mmutil  
    for result in results:
        if result.type == 'mpa': 
            if result.percOverallValue != '---':
                result.percOverallArea = mmutil.trueRound(float(result.percOverallArea), sig_digs)
                result.percOverallValue = mmutil.trueRound(float(result.percOverallValue), sig_digs)
        else:
            if result.percGEI != '---':
                result.percGEI = mmutil.trueRound(float(result.percGEI), sig_digs)
            if result.percNEI != '---':
                result.percNEI = mmutil.trueRound(float(result.percNEI), sig_digs)
            if result.GEI != '---':
                result.GEI = mmutil.trueRound(float(result.GEI), 0)
            if result.NEI != '---':
                result.NEI = mmutil.trueRound(float(result.NEI), 0)
    return results
    
'''
Accessed via named url when a user selects the View Printable Report link at the bottom of analysis results display
'''
def print_report(request, feature_id, user_group, feature='mpa'):
    user = request.user
    if not user_can_view_feature(user, feature_id, feature):
        return HttpResponse('You do not have permission to view this feature', status=401)
        
    if feature == 'array':
        return print_array_report(request, feature_id, user_group)
    #CAN'T WE ABSTRACT THE FOLLOWING A BIT BETTER?
    #MAYBE WITH A display_array_analysis FOR mpas? (see print_array_report below)
    mpa = get_object_or_404(MlpaMpa, pk=feature_id)
    ports = GetPortsByGroup(user_group)
    all_results = []
    for single_port in ports:
        #should we ensure this only returns a single row?
        cache = FishingImpactResults.objects.filter(mpa=mpa.id, group=user_group, port=single_port)
        results = list(cache)
        analysis_results = []
        for result in results:
            analysis_results.append(AnalysisResult(id=result.mpa_id, type='mpa', group=user_group, port=single_port, species=result.species, percOverallArea=result.perc_area, percOverallValue=result.perc_value))
        analysis_results = flesh_out_results(user_group, single_port, analysis_results)
        
        #sort results alphabetically by species name
        analysis_results.sort(key=lambda obj: obj.species)
        
        #adjust recreational Fort Bragg display
        if user_group in ['Recreational Dive', 'Recreational Kayak', 'Recreational Private Vessel']:
            for result in analysis_results:
                if result.port == 'Fort Bragg':
                    result.port = 'Fort Bragg / Albion'
        
        all_results.append(analysis_results)
    return render_to_response('printable_mpa_report.html', RequestContext(request, {'mpa':mpa, 'user_group':user_group, 'all_results':all_results})) 

def print_array_report(request, array_id, group):
    array = get_object_or_404(MpaArray, pk=array_id)
    mpas = array.mpa_set
    if group == 'com':
        group_name = 'Commercial'
        group_abbr = group
    elif group == 'cpfv':
        group_name = 'Commercial Passenger Fishing Vessel'
        group_abbr = group
    elif group == 'swd':
        group_name = 'Edible Seaweed'
        group_abbr = group
    elif group == 'div':
        group_name = 'Recreational Dive'
        group_abbr = 'rec'
    elif group == 'kyk':
        group_name = 'Recreational Kayak'
        group_abbr = 'rec'
    elif group == 'pvt':
        group_name = 'Recreational Private Vessel'
        group_abbr = 'rec'
    array_results = compile_array_results(mpas, group_name)
    template = 'printable_%s_array_report.html' % group_abbr
    return display_array_analysis(request, group_name, array, array_results, template=template)
    
def cache_analysis_results(results, group, mpa):
    for result in results:
        cache = FishingImpactResults(mpa_id=mpa.id, group=group, port=result.port, species=result.species, perc_value=result.percOverallValue, perc_area=result.percOverallArea)
        #WHY IS THIS NOT SAVING DURING ARRAY ANALYSIS???
        cache.save()
        
'''
Called by display_mpa_analysis and print_report
Fills out analysis results with species that are relevant for the given group, but not yet present in the results
'''
def flesh_out_results(group, port, results):
    group_species = GetSpeciesByGroup(group)
    result_species = [result.species for result in results]
    missing_species = [specs for specs in group_species if specs not in result_species]
    for spec in missing_species:
        results.append(EmptyAnalysisResult(group, port, spec, 'mpa'))
    if group == 'Commercial':
        results = adjust_commercial_species(results)
    if group == 'Edible Seaweed':
        for result in results:
            result.species = 'Seaweed (Hand Harvest)'
    return results
     
'''
Called by flesh_out_results
Modifies commercial species for appropriate display:
    Species Name(s) (Catch Method)
'''
def adjust_commercial_species(results):
    species_dict = Layers.COMMERCIAL_SPECIES_DISPLAY
    for result in results:
        result.species = species_dict[result.species]
    return results
 


