from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from apps.pages.forms import RegistrationForm, LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from django.contrib import messages
from allauth.account.utils import send_email_confirmation
from django.contrib.auth.decorators import login_required
from apps.companies.decorators import company_active_required, active_user_required

# Create your views here.

# Dashboard
@login_required
@active_user_required
@company_active_required
def analytics(request):
  context = {
    'parent': 'dashboard',
    'segment': 'analytics'
  }
  return render(request, 'pages/dashboards/analytics.html', context)

@login_required
@active_user_required
@company_active_required
def discover(request):
  context = {
    'parent': 'dashboard',
    'segment': 'discover'
  }
  return render(request, 'pages/dashboards/discover.html', context)

@login_required
@active_user_required
@company_active_required
def sales(request):
  context = {
    'parent': 'dashboard',
    'segment': 'sales'
  }
  return render(request, 'pages/dashboards/sales.html', context)

@login_required
@active_user_required
@company_active_required
def automotive(request):
  context = {
    'parent': 'dashboard',
    'segment': 'automotive'
  }
  return render(request, 'pages/dashboards/automotive.html', context)

@login_required
@active_user_required
@company_active_required
def smart_home(request):
  context = {
    'parent': 'dashboard',
    'segment': 'smart_home'
  }
  return render(request, 'pages/dashboards/smart-home.html', context)


# Pages -> Team

def profile_overview(request):
  context = {
    'parent': 'team',
    'segment': 'profile_overview'
  }
  return render(request, 'pages/team/profile-overview.html', context)

def all_projects(request):
  context = {
    'parent': 'team',
    'segment': 'projects'
  }
  return render(request, 'pages/team/all-projects.html', context)

def projects(request):
  context = {
    'parent': 'profile',
    'segment': 'projects'
  }
  return render(request, 'pages/profile/projects.html', context)


def team_messages(request):
  context = {
    'parent': 'team',
    'segment': 'messages'
  }
  return render(request, 'pages/team/messages.html', context)

def reports(request):
  context = {
    'parent': 'team',
    'segment': 'reports'
  }
  return render(request, 'pages/team/reports.html', context)

def new_user(request):
  context = {
    'parent': 'team',
    'segment': 'new_user'
  }
  return render(request, 'pages/team/new-user.html', context)


# Pages -> Accounts
@login_required
def settings(request):
  context = {
    'parent': 'accounts',
    'segment': 'settings'
  }
  return render(request, 'pages/account/settings.html', context)

def billing(request):
  context = {
    'parent': 'accounts',
    'segment': 'billing'
  }
  return render(request, 'pages/account/billing.html', context)

def invoice(request):
  context = {
    'parent': 'accounts',
    'segment': 'invoice'
  }
  return render(request, 'pages/account/invoice.html', context)

def security(request):
  context = {
    'parent': 'accounts',
    'segment': 'security'
  }
  return render(request, 'pages/account/security.html', context)


# Pages -> Projects
def general(request):
  context = {
    'parent': 'projects',
    'segment': 'general'
  }
  return render(request, 'pages/projects/general.html', context)

def timeline(request):
  context = {
    'parent': 'projects',
    'segment': 'timeline'
  }
  return render(request, 'pages/projects/timeline.html', context)

def new_project(request):
  context = {
    'parent': 'projects',
    'segment': 'new_project'
  }
  return render(request, 'pages/projects/new-project.html', context)

# Pages -> VR
def vr_default(request):
  context = {
    'parent': 'pages',
    'sub_parent': 'vr',
    'segment': 'vr_default'
  }
  return render(request, 'pages/pages/vr/vr-default.html', context)

def vr_info(request):
  context = {
    'parent': 'pages',
    'sub_parent': 'vr',
    'segment': 'vr_info'
  }
  return render(request, 'pages/pages/vr/vr-info.html', context)

# Pages
def rtl(request):
  context = {
    'parent': 'pages',
    'segment': 'rtl'
  }
  return render(request, 'pages/pages/rtl-page.html', context)

def pricing(request):
  context = {
    'parent': 'pages',
    'segment': 'pricing'
  }
  return render(request, 'pages/pages/pricing-page.html', context)

def landing(request):
  """Public landing page."""
  context = {
    'parent': 'pages',
    'segment': 'landing'
  }
  return render(request, 'pages/pages/landing-page.html', context)

def faq(request):
  """Public frequently asked questions page."""
  context = {
    'parent': 'pages',
    'segment': 'faq'
  }
  return render(request, 'pages/pages/faq.html', context)

def widgets(request):
  context = {
    'parent': 'pages',
    'segment': 'widgets'
  }
  return render(request, 'pages/pages/widgets.html', context)

def charts(request):
  context = {
    'parent': 'pages',
    'segment': 'charts'
  }
  return render(request, 'pages/pages/charts.html', context)

def sweet_alerts(request):
  context = {
    'parent': 'pages',
    'segment': 'sweet_alerts'
  }
  return render(request, 'pages/pages/sweet-alerts.html', context)

def notifications(request):
  context = {
    'parent': 'pages',
    'segment': 'notifications'
  }
  return render(request, 'pages/pages/notifications.html', context)


# Applications
def crm(request):
  context = {
    'parent': 'applications',
    'segment': 'crm'
  }
  return render(request, 'pages/applications/crm.html', context)
  
def kanban(request):
  context = {
    'parent': 'applications',
    'segment': 'kanban'
  }
  return render(request, 'pages/applications/kanban.html', context)

def wizard(request):
  context = {
    'parent': 'applications',
    'segment': 'wizard'
  }
  return render(request, 'pages/applications/wizard.html', context)

def datatables(request):
  context = {
    'parent': 'applications',
    'segment': 'datatables'
  }
  return render(request, 'pages/applications/datatables.html', context)

def calendar(request):
  context = {
    'parent': 'applications',
    'segment': 'calendar'
  }
  return render(request, 'pages/applications/calendar.html', context)

def stats(request):
  context = {
    'parent': 'applications',
    'segment': 'stats'
  }
  return render(request, 'pages/applications/stats.html', context)

def validation(request):
  context = {
    'parent': 'applications',
    'segment': 'validation'
  }
  return render(request, 'pages/applications/validation.html', context)

# Ecommerce -> Products
def new_product(request):
  context = {
    'parent': 'ecommerce',
    'sub_parent': 'products',
    'segment': 'new_product'
  }
  return render(request, 'pages/ecommerce/products/new-product.html', context)

def edit_product(request):
  context = {
    'parent': 'ecommerce',
    'sub_parent': 'products',
    'segment': 'edit_product'
  }
  return render(request, 'pages/ecommerce/products/edit-product.html', context)

def product_page(request):
  context = {
    'parent': 'ecommerce',
    'sub_parent': 'products',
    'segment': 'product_page'
  }
  return render(request, 'pages/ecommerce/products/product-page.html', context)

def products_list(request):
  context = {
    'parent': 'ecommerce',
    'sub_parent': 'products',
    'segment': 'products_list'
  }
  return render(request, 'pages/ecommerce/products/products-list.html', context)

# Ecommerce -> Orders
def order_list(request):
  context = {
    'parent': 'ecommerce',
    'sub_parent': 'orders',
    'segment': 'order_list'
  }
  return render(request, 'pages/ecommerce/orders/list.html', context)

def order_details(request):
  context = {
    'parent': 'ecommerce',
    'sub_parent': 'orders',
    'segment': 'order_details'
  }
  return render(request, 'pages/ecommerce/orders/details.html', context)

# Ecommerce -> Referral
def referral(request):
  context = {
    'parent': 'ecommerce',
    'segment': 'referral'
  }
  return render(request, 'pages/ecommerce/referral.html', context)


# Authentication -> Login
@method_decorator(ratelimit(key='ip', rate='5/m', group=lambda r: getattr(r, 'company', None).id if getattr(r,'company', None) else 'anon', block=True), name='dispatch')
class BasicLoginView(LoginView):
  template_name = 'accounts/signin/basic.html'
  form_class = LoginForm

class CoverLoginView(BasicLoginView):
  template_name = 'accounts/signin/cover.html'

class IllustrationLoginView(BasicLoginView):
  template_name = 'accounts/signin/illustration.html'

# Authentication -> Register
def basic_register(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      user = form.save()
      send_email_confirmation(request, user)
      messages.success(request, "Please check your inbox to confirm your account.")
      return redirect('/accounts/basic-login/')
    else:
      messages.error(request, "Register failed!")
  else:
    form = RegistrationForm()

  context = { 'form': form }
  return render(request, 'accounts/signup/basic.html', context)

def cover_register(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      user = form.save()
      send_email_confirmation(request, user)
      messages.success(request, "Please check your inbox to confirm your account.")
      return redirect('/accounts/cover-login/')
    else:
      messages.error(request, "Register failed!")
  else:
    form = RegistrationForm()

  context = { 'form': form }
  return render(request, 'accounts/signup/cover.html', context)

def illustration_register(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      user = form.save()
      send_email_confirmation(request, user)
      messages.success(request, "Please check your inbox to confirm your account.")
      return redirect('/accounts/illustration-login/')
    else:
      messages.error(request, "Register failed!")
  else:
    form = RegistrationForm()

  context = { 'form': form }
  return render(request, 'accounts/signup/illustration.html', context)

# Authentication -> Lock
def basic_lock(request):
  return render(request, 'accounts/lock/basic.html')

def cover_lock(request):
  return render(request, 'accounts/lock/cover.html')

def illustration_lock(request):
  return render(request, 'accounts/lock/illustration.html')

# Authentication -> Reset
class BasicPasswordResetView(PasswordResetView):
  template_name = 'accounts/reset/basic.html'
  form_class = UserPasswordResetForm

class CoverPasswordResetView(PasswordResetView):
  template_name = 'accounts/reset/cover.html'
  form_class = UserPasswordResetForm

class IllustrationPasswordResetView(PasswordResetView):
  template_name = 'accounts/reset/illustration.html'
  form_class = UserPasswordResetForm

class UserPasswordResetConfirmView(PasswordResetConfirmView):
  template_name = 'accounts/reset-confirm/basic.html'
  form_class = UserSetPasswordForm

class UserPasswordChangeView(PasswordChangeView):
  template_name = 'accounts/change/basic.html'
  form_class = UserPasswordChangeForm

# Authentication -> Verification
def basic_verification(request):
  return render(request, 'accounts/verification/basic.html')

def cover_verification(request):
  return render(request, 'accounts/verification/cover.html')

def illustration_verification(request):
  return render(request, 'accounts/verification/illustration.html')

# Error
def error_404(request, exception=None):
  return render(request, 'accounts/error/404.html')

def error_500(request, exception=None):
  return render(request, 'accounts/error/500.html')




# i18n
def i18n_view(request):
  context = {
    'parent': 'apps',
    'segment': 'i18n'
  }
  return render(request, 'pages/apps/i18n.html', context)