from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = 'index.html'

class ApiView(TemplateView):
    template_name = 'api.html'

class Fail2BanView(TemplateView):
    template_name = 'fail2ban.html'

class DocsView(TemplateView):
    template_name = 'docs.html'

class ModulesView(TemplateView):
    template_name = 'modules.html'

class PlanView(TemplateView):
    template_name = 'plan.html'

class CrossRefView(TemplateView):
    template_name = 'crossref.html'

class LoginView(TemplateView):
    template_name = 'login.html'
