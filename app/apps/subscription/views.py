from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse ,HttpResponse, HttpResponseRedirect
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt 
import stripe
import datetime
from . models import Plan, Subscription
from datetime import datetime 
from django.views import View
from .utils import retrieve_subscription_info as get_info


stripe.api_key = settings.STRIPE_SECRET_KEY

# stripe.ApplePayDomain.create(
#   domain_name='example.com',
# )


def create_checkout_session(request):
    if request.method == 'GET':
        
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - lets capture the payment later
            # [customer_email] - lets you prefill the email input in the form
            # For full details see https:#stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id if request.user.is_authenticated else None,
                success_url=request.build_absolute_uri(reverse('stripe_success') )+ '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri(reverse('strip_cancelled')),
                payment_method_types=['card'],
                mode = 'subscription',
                line_items=[
                    {
                        'price': 'price_1KdZXhCy95Kg2yHQW0roAm0y',
                        'quantity': 1,
                    }
                ]
            )
            return HttpResponseRedirect(checkout_session.url)
            # return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})    


class SuccessView(TemplateView):
    template_name = 'subscription/success.html'


class CancelledView(TemplateView):
    template_name = 'subscription/cancelled.html'

def plans(request):
    plans = Plan.objects.exclude(is_active=False)
    existing_subscription = None
    try:
        existing_subscription = Subscription.objects.get(user=request.user , status="active")
    except :
        pass    

    return render(request, 'subscription/plans.html', {'plans': plans, 'existing_subscription':existing_subscription })    


def stripe_checkout(request ,product_id):
    try:
        try:
            subscription = Subscription.objects.get(user = request.user)
            response = get_info(subscription.stripe_sub)
            user_status = response['data']['status'] # active
            if user_status == 'active':
                return redirect('/price')
        except:
            selected_plan = Plan.objects.get(id=product_id,is_active=True)
            # STRIPE_PUBLISHABLE_KEY
            publishable_key = settings.STRIPE_PUBLISHABLE_KEY
            # existing_pending_subs = None
            # existing_pending_subs = Subscription.objects.get(user=request.user, status = "incomplete")
            
            setup_intent = stripe.SetupIntent.create(
                payment_method_types=["card"],
                usage= "off_session",
            )
            context = {
                        'selected_plan': selected_plan,
                        'setup_intent_secret':setup_intent.client_secret, 
                        'publishable_key':publishable_key
                    }
            return render(request, 'subscription/checkout.html', context)
    except (Plan.DoesNotExist, Subscription.DoesNotExist) as e:
        return HttpResponse(str(e))
    except Exception as error:
        return HttpResponse(str(error))


class PaymentView(View):
    def post(self, request, *args, **kwargs):
        card_num = request.POST['card_num']
        exp_month = request.POST['exp_month']
        exp_year = request.POST['exp_year']
        cvc = request.POST['cvc']

        token = stripe.Token.create(
          card={
            "number": card_num,
            "exp_month": int(exp_month),
            "exp_year": int(exp_year),
            "cvc": cvc
          },
        )

        charge = stripe.Charge.create(
          amount=2000,
          currency="inr",
          source=token, 
          description="Charge for jenny.rosen@example.com"
        )

        if charge['captured'] == True:
            Sale.objects.create(product=product, amount=amount)
            return redirect('app:success_page')

        return redirect('app:fail_page')

@login_required
@csrf_exempt
def createSubscription(request):
    if request.method == 'POST':
        # Reads application/json and returns a response
        data = json.loads(request.body)
        payment_method = data['payment_method']

        try:
          # This creates a new Customer and attaches the PaymentMethod in one API call.
          customer = stripe.Customer.create(
              payment_method=payment_method,
              email=request.user.email,
              invoice_settings={
                  'default_payment_method': payment_method
              }
          )
          stripe.Customer.modify(
                customer.id,
                invoice_settings={
                    'default_payment_method': payment_method
              }
          )

          '''store_card = stripe.Customer.create_source(
            customer.id,
            source="tok_visa",
          )'''

          user = request.user
          user.stripe_id = customer.id
          # user.stripe_card_id = store_card.id
          user.save()

          subscription = stripe.Subscription.create(
              customer=customer.id,
              items=[
                  {
                      "price": data["price_id"],
                  },
              ],
              expand=["latest_invoice.payment_intent"]
          )

          local_sub = Subscription()
          local_sub.user = request.user
          try:
            local_sub.plan = Plan.objects.get(stripe_price_id=data["price_id"])
          except Plan.DoesNotExist:
              pass
          local_sub.stripe_sub = subscription.id
          local_sub.status = subscription.status
          local_sub.created_at = subscription
          local_sub.period_start = datetime.fromtimestamp(subscription.current_period_start)
          local_sub.period_end = datetime.fromtimestamp(subscription.current_period_end)
          
          local_sub.created_at = datetime.fromtimestamp(subscription.start_date)
          if subscription.status == "incomplete" :
                local_sub.logs = {"payment_secret": subscription.latest_invoice.payment_intent.client_secret,
                                  "payment_method": payment_method}
          local_sub.save()

          return JsonResponse(subscription)
        except Exception as e:
          return JsonResponse({'error': (e.args[0]), "data":data }, status=403)
    else:
      return HttpResponse('Get request not allowed')

@csrf_exempt
def subscription_poll(request, sub_id):
    try:
        sub_ob = Subscription.objects.get(stripe_sub =sub_id )
        return JsonResponse({"status": sub_ob.status})
    except Exception as e:
        JsonResponse({'error': str(e)}, status=403)

@csrf_exempt
def update_subscription(request, sub_id ,price_id):
    try:
        subscription_obj = Subscription.objects.get(stripe_sub=sub_id)
        subscription = stripe.Subscription.retrieve(sub_id)
        
        updatedSubscription = stripe.Subscription.modify(
            sub_id,
            # cancel_at_period_end=False,
            payment_behavior="pending_if_incomplete",
            proration_behavior='always_invoice',
            
            items=[{
                'id': subscription['items']['data'][0].id,
                'price': price_id,
               
            }]
        )
        if updatedSubscription.status == 'active':
            subscription_obj.plan = Plan.objects.get(stripe_price_id=price_id)
            subscription_obj.save()
        # return JsonResponse({"updatedSubscription": updatedSubscription})
        if request.GET.get('page') == "price":
            return redirect('price')
        return redirect('my_account')

    except Exception as e:
        return JsonResponse({'error': (e.args[0])}, status=403)

@csrf_exempt
def cancel_subscription(request, sub_id ,price_id):
    try:
        subscription_obj = Subscription.objects.get(stripe_sub=sub_id)
        subscription = stripe.Subscription.retrieve(sub_id)
        
        updatedSubscription = stripe.Subscription.modify(
            sub_id,
            cancel_at_period_end=True,
        )
        if updatedSubscription.status == 'active':
            subscription_obj.plan = Plan.objects.get(stripe_price_id=price_id)
            subscription_obj.save()
        # return JsonResponse({"updatedSubscription": updatedSubscription})
        if request.GET.get('page') == "price":
            
            return redirect('price')
        return redirect('my_account')

    except Exception as e:
        return JsonResponse({'error': (e.args[0])}, status=403)


def update_subscription_status(request):
    try:
        sub_id = request.GET.get('sub_id')
        subscription_status = request.GET.get('subscription_status')
        try:
            user = Subscription.objects.get(user=request.user)

            if subscription_status == 'active':
                updatedSubscription = stripe.Subscription.modify(
                sub_id,
                cancel_at_period_end=False,
                )
              

            elif subscription_status == 'inactive':
                updatedSubscription = stripe.Subscription.modify(
                sub_id,
                cancel_at_period_end=True,
                )
              
            user.status = subscription_status
            user.save()
        except stripe.error.StripeError as e:
            pass
        except Exception as e:
            pass    


        # subscription_obj = Subscription.objects.get(stripe_sub=sub_id)
        # subscription = stripe.Subscription.retrieve(sub_id)
        
        # updatedSubscription = stripe.Subscription.modify(
        #     sub_id,
        #     cancel_at_period_end=True,
        # )
        # if updatedSubscription.status == 'active':
        #     subscription_obj.plan = Plan.objects.get(stripe_price_id=price_id)
        #     subscription_obj.save()
        # if updatedSubscription.status == 'inactive':
        #     subscription_obj.plan = Plan.objects.get(stripe_price_id=price_id)
        #     subscription_obj.save()
        # return JsonResponse({"updatedSubscription": updatedSubscription})
        if request.GET.get('page') == "price":
            
            return redirect('price')
        return redirect('my_account')

    except Exception as e:
        return JsonResponse({'error': (e.args[0])}, status=403)

# @csrf_exempt
# def stripe_webhook(request):
#     print("webhook called")
#     endpoint_secret = settings.STRIPE_WEBHOOK_ID
#     payload = json.loads(request.body)
#     sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
#     event = None
#     print((payload),"=====================\n\n\n\n")

#     try:
#         # event = stripe.Webhook.construct_event(
#         #     payload, sig_header, endpoint_secret
#         # )
#         print(event,'=***************=eve\n\n\n\n')
#     except ValueError as e:
#         # Invalid payload
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError as e:
#         # Invalid signature
#         return HttpResponse(status=400)
#     # Handle the checkout.session.completed event
#     # if event['type'] == 'customer.subscription.updated':
#     #     # case of sub complete via auth
#     #     try:
#     #         if event.data.previous_attributes.status == "incomplete" and event.data.object.status == "active":
#     #             sub = Subscription.objects.get(stripe_sub=event.data.object.id)
#     #             sub.status = event.data.object.status
#     #             sub.period_start = datetime.fromtimestamp(event.data.object.current_period_start)
#     #             sub.period_end = datetime.fromtimestamp(event.data.object.current_period_end)
#     #             sub.save()
#     #             return HttpResponse(status=201)
#     #     except Exception as e:
#     #         return HttpResponse(status=200)       

#     #     return HttpResponse(status=200)


#     ## Save recurring payment response

#     if payload['type'] == 'invoice.payment_succeeded':
#         print("-----inside-----------invoice-----------------")
#         # case of sub complete via auth
#         sub = Subscription.objects.get(stripe_sub=event.data.object.id)
#         sub.status = event.data.object.status
#         sub.period_start = datetime.fromtimestamp(event.data.object.current_period_start)
#         sub.period_end = datetime.fromtimestamp(event.data.object.current_period_end)
#         # sub.save()
#         print(sub.period_start,'=======ssssssss')
#         print(sub.period_end,'=======eeeeenn')
        

#     return HttpResponse(status=200)





@csrf_exempt
def stripe_webhook(request):
  print("webhook called")
  payload = request.body
  event = None
  try:
    event = stripe.Event.construct_from(
      json.loads(payload), stripe.api_key
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400) 
  subscription_id = event.get('data').get('object').get('id')
  start_date = event.get('data').get('object').get('current_period_start')
  end_date = event.get('data').get('object').get('current_period_end')

  if event.type == 'customer.subscription.updated':
        # case of sub complete via auth
        try:
            sub = Subscription.objects.get(stripe_sub=subscription_id)
            sub.period_start = datetime.fromtimestamp(start_date)
            sub.period_end = datetime.fromtimestamp(end_date)
            sub.save()
        except Exception as e:
            print(f'''Exception================= str({e})\n
subscription_id - {subscription_id}\n
start_date - {start_date}\n
end_date - {end_date}
            ''' )

  elif event.type == 'invoice.payment_succeeded':
    payment_method = event.data.object

  else:
    print('Unhandled event type {}'.format(event.type))

  return HttpResponse(status=200)