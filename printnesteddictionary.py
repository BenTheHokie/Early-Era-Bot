# Code clipped from http://code.activestate.com/recipes/578094-recursively-print-nested-dictionaries/

def print_dict(dictionary, ident = '', braces=1):
    """ Recursively prints nested dictionaries."""

    for key, value in dictionary.iteritems():
        if isinstance(value, dict):
            print '%s%s%s%s' %(ident,braces*'[',key,braces*']') 
            print_dict(value, ident+'    ', braces+1)
        else:
            print ident+'%s = %s' %(key, value)