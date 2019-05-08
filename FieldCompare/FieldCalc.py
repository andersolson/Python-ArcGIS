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