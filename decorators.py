from django.shortcuts import redirect

def unauthenticated(veiw_func):
    def wrapper_func( request, *args, **kwargs):
        if request.user.is_authenticated:
             if request.user.groups.filter(name='Admin').exists():
                return redirect('adminhome')
             else:
                return redirect('customerhome')
        else:    
            return veiw_func(request,*args, **kwargs)

    return wrapper_func



def allowedusers(allowed_roles=[]):
    def dec(view_func):
        def wrapper_fun(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
                if group in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect('notallowed')  # Redirect to the "notallowed" view
            else:
                return redirect('notallowed')  # Redirect to the "notallowed" view if no group is assigned

        return wrapper_fun

    return dec

