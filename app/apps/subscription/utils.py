import stripe
from datetime import datetime
from django.conf import settings
from subscription.models import Plan



stripe.api_key = settings.STRIPE_SECRET_KEY

get_date_from_timestamp = lambda dt: datetime.fromtimestamp(dt).strftime("%Y-%m-%d:%H:%M:%S")
string_to_date = lambda dt: datetime.strptime(dt, "%Y-%m-%d:%H:%M:%S")

def retrieve_subscription_info(subscription_id):
	response = {
		'status_code': 200,
		'message': 'Successfull Response',
		'data': {}
	}
	try:
		subscription_data = stripe.Subscription.retrieve(
			subscription_id,
		)
		response['data']["id"] = subscription_data.id
		response['data']["created_at"] = subscription_data.created
		response['data']["start_date"] = subscription_data.current_period_start
		response['data']["end_date"] = string_to_date(get_date_from_timestamp(subscription_data.current_period_end))
		response['data']["customer"] = subscription_data.customer
		response['data']["status"] = subscription_data.status

	except stripe.error.StripeError as e:
		response['status_code'] = 400
		response['message'] = "Invalid Subscription ID"
	except Exception as error:
		response['status_code'] = 400
		response['message'] = "Exception: " + str(error)

	return response


def check_plan(user_current_plan):
	all_plans = Plan.objects.order_by('price')
	all_plans = list(all_plans)
	current_plan = []
	for plan in all_plans:
		if plan == user_current_plan:
			get_index = int(all_plans.index(plan)) + 1
			current_plan.extend(all_plans[:get_index])
	return current_plan