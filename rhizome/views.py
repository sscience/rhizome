from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, resolve
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.template import RequestContext
from django.conf import settings

from rhizome.models.dashboard_models import CustomDashboard

from rhizome.forms import UserCreateForm, UserEditForm
from rhizome.mixins import PermissionRequiredMixin

from rhizome.pdf_utils import print_pdf

def ok(request):
    import json
    from django.http import HttpResponse
    resp_data = {'ok':'ok'}

    return HttpResponse(json.dumps(resp_data), content_type="application/json")


def about(request):
    html = settings.ABOUT_HTML
    return render_to_response('about.html', {'html': html},
                              context_instance=RequestContext(request))


def export_file(request):
    file_type = request.GET['type']
    url = request.GET['path']
    file_name = 'dashboards.' + file_type
    css_file = 'file://' + settings.STATICFILES_DIRS[0] + '/css/pdf.css'

    cookie = {}
    cookie['name'] = 'sessionid'
    cookie['value'] = request.COOKIES[cookie['name']]

    javascript_delay = '10000'

    if 'pdf' in file_type:
        options = {'orientation': 'Landscape',
                   'javascript-delay': javascript_delay, 'quiet': ' '}
        content_type = 'application/pdf'
    else:
        options = {'javascript-delay': javascript_delay,
                   'width': '1425', 'quality': '100', 'quiet': ' '}
        content_type = 'image/JPEG'

    pdf_content = print_pdf(type=file_type, url=url, output_path=None,
                            options=options, cookie=cookie, css_file=css_file)

    if isinstance(pdf_content, IOError):
        response = HttpResponse(status=500)
    else:
        response = HttpResponse(content=pdf_content, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename=' + file_name

    response.set_cookie('fileDownloadToken', 'true')
    return response

#############################################################################
#                                  OPEN VIEWS                               #
#             ( needs authentication, but no specific permissions )         #
#############################################################################


# RESOURCES
#---------------------------------------------------------------------------
def dashboards(request):
    return render_to_response('dashboards/index.html',
                              context_instance=RequestContext(request))


def dashboard_create(request):
    return render_to_response('dashboards/create.html',
                              context_instance=RequestContext(request))


def dashboard(request, dashboard_id=None):

    try:
        CustomDashboard.objects.get(id=dashboard_id)
    except CustomDashboard.DoesNotExist:
        return HttpResponseRedirect('/dashboards/create')

    return render_to_response('dashboards/show.html', {'dashboard_id': dashboard_id},
                              context_instance=RequestContext(request))


def charts(request):
    return render_to_response('charts/index.html',
                              context_instance=RequestContext(request))


def chart_create(request):
    return render_to_response('charts/create.html',
                              context_instance=RequestContext(request))


def chart(request, chart_id=None):
    return render_to_response('charts/show.html', {'chart_id': chart_id},
                              context_instance=RequestContext(request))

#############################################################################
#                                                                           #
#                              RESTRICTED VIEWS                             #
#                                                                           #
#############################################################################

@user_passes_test(lambda u: u.groups.filter(name='chart_edit') or u.is_superuser,
                  login_url='/permissions_needed', redirect_field_name=None)
def chart_edit(request, chart_id=None):
    return render_to_response('charts/show.html', {'chart_id': chart_id},
                              context_instance=RequestContext(request))


#----------------------------------------------------------------------------
@user_passes_test(lambda u: u.groups.filter(name='react_app') or u.is_superuser,
                  login_url='/permissions_needed', redirect_field_name=None)
def react_app(request):
    return render_to_response('react_app.html',\
        context_instance=RequestContext(request))

@user_passes_test(lambda u: u.groups.filter(name='data_entry') or u.is_superuser,
                  login_url='/permissions_needed', redirect_field_name=None)
def data_entry(request):
    return render_to_response('data-entry/index.html',
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.groups.filter(name='source-data') or u.is_superuser,
                  login_url='/permissions_needed', redirect_field_name=None)
def source_data(request):
    return render_to_response('source-data/index.html',
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.groups.filter(name='manage-system') or u.is_superuser,
                  login_url='/permissions_needed', redirect_field_name=None)
def manage_system(request):
    return render_to_response('manage_system.html',
                              context_instance=RequestContext(request))

@user_passes_test(lambda u: u.groups.filter(name='manage-system') or u.is_superuser,
                  login_url='/permissions_needed', redirect_field_name=None)
def update_campaign(request):
    return render_to_response('manage_system.html',
        context_instance=RequestContext(request))

class UserCreateView(PermissionRequiredMixin, generic.CreateView):
    model = User
    template_name = 'users/create.html'
    form_class = UserCreateForm

    def get_success_url(self):
        new_user_id = self.object.id

        return reverse_lazy('user_update',
                            kwargs={'pk': new_user_id})


class UserEditView(PermissionRequiredMixin, generic.UpdateView):
    model = User
    template_name = 'users/edit.html'
    form_class = UserEditForm

    def dispatch(self, *args, **kwargs):
        return super(UserEditView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        requested_user_id = self.get_object().id
        return reverse_lazy('user_update',
                            kwargs={'pk': requested_user_id})

    def get_context_data(self, **kwargs):
        view_context = super(UserEditView, self).get_context_data(**kwargs)
        user_obj = self.get_object()
        view_context['user_id'] = user_obj.id

        return view_context

    def form_valid(self, form):
        new_user = form.save()
        return HttpResponseRedirect(self.get_success_url())


def html_decorator(func):
    """
    This decorator wraps the output of the django debug tooldbar in html.
    (From http://stackoverflow.com/a/14647943)
    """

    def _decorated(*args, **kwargs):
        response = func(*args, **kwargs)

        wrapped = ("<html><body>",
                   response.content,
                   "</body></html>")

        return HttpResponse(wrapped)

    return _decorated


@html_decorator
def debug(request):
    """
    Debug endpoint that uses the html_decorator,
    """
    path = request.META.get("PATH_INFO")
    api_url = path.replace("debug/", "")

    view = resolve(api_url)

    accept = request.META.get("HTTP_ACCEPT")
    accept += ",application/json"
    request.META["HTTP_ACCEPT"] = accept

    response = view.func(request, **view.kwargs)
    return HttpResponse(response_container)
