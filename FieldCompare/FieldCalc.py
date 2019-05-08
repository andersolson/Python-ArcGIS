def ifBlock(cat):
    if cat == 'Potable Water':
        return 'Potable'
    elif cat == 'Raw Water':
        return 'NonPotable - Raw'
    elif cat == 'Reclaimed Water':
        return 'NonPotable - Reclaim'
    else:
        return cat
    
def ifBlock(cat):
    if cat == 'Overflow':
        return 'Overflow Drain'
    elif cat == 'Perforated':
        return 'Drain'
    elif cat == 'Reclaim':
        return 'NonPotable - Reclaim'
    elif cat == 'Sump Pump Drain':
        return 'Sump Drain'   
    else:
        return cat
    
def ifBlock(cat):
    if cat == 'Altitude':
        return 'Altitude'
    elif cat == 'Check Valve':
        return 'Check'
    elif cat == 'PRV - Pressure Reducer Valve':
        return 'PRV'
    elif cat == 'Surge Valve':
        return 'Surge' 
    elif cat == 'Other':
        return ''    
    elif cat == 'PSV - Pressure Sustainer Valve' :
        return ''      
    else:
        return cat

NULL?
'Zone Change Valve'?