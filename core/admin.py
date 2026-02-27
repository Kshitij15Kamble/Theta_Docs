from django.contrib import admin
from django.shortcuts import redirect

def admin_index_redirect(request):
    return redirect('/admin/documents/companydocument/')

admin.site.index = admin_index_redirect
