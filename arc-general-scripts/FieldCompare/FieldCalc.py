def codeBlock(fld):
    if fld == 'BELOW':
        return 'BELOW GROUND'
    elif fld == 'ABOVE':
        return 'ABOVE GROUND'
    elif fld == 'INDOOR':
        return 'INDOOR'
    else:
        return 'UNKNOWN'

def codeBlock(fld):
    if fld == '1':
        return 'CONTROLLER 1'
    elif fld == '2':
        return 'CONTROLLER 2'
    elif fld == '3':
        return 'CONTROLLER 3'
    elif fld == '4':
        return 'CONTROLLER 4'
    elif fld == '5':
        return 'CONTROLLER 5'
    elif fld == '6':
        return 'CONTROLLER 6'
    elif fld == 'Unknown':
        return 'UNKNOWN'
    else:
        return 'UNKNOWN'

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
    elif cat == 'PSV - Pressure Sustainer Valve' :
        return 'PSV'      
    else:
        return cat

