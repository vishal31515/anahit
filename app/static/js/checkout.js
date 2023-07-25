function displayError(event) {

  let displayError = document.getElementById('card-errors');
  if (event.error) {
    displayError.textContent = event.error.message;
    document.getElementById("submit").disabled = false;
    document.querySelector("#spinner").classList.add("hidden");
    document.querySelector("#button-text").classList.remove("hidden");
  } else {
    displayError.textContent = '';
  }
}

stripeElements();

const LOG_FETCH_COUNT = 1;


function stripeElements() {
  stripe = Stripe(document.getElementById('publishable_key').value);

  if (document.getElementById('card-element')) {
    let elements = stripe.elements();


    var paymentRequest = stripe.paymentRequest({
      country: "US",
      currency: "usd",
      total: {
        amount: 2000,
        label: "Total"
      },
      requestPayerName: true,
      requestPayerEmail: true,
    });

    var paymentRequestElement = elements.create("paymentRequestButton", {
      paymentRequest: paymentRequest,
      style: {
        paymentRequestButton: {
          type: "donate"
        }
      }
    });

    paymentRequest.canMakePayment().then(result => {
      console.log(result, "can make payment");
      if (result) {
        // Mount paymentRequestButtonElement to the DOM
      }
    });



    // paymentRequest.on("token", function(result) {
    //   processSubscription(result.token.id)
    //   result.complete("success");
    // });

    paymentRequest.on('paymentmethod', function (ev) {
      processSubscription(ev.paymentMethod.id)
      // Confirm the PaymentIntent without handling potential next actions (yet).
      // stripe.confirmCardPayment(
      //   clientSecret,
      //   {payment_method: ev.paymentMethod.id},
      //   {handleActions: false}
      // ).then(function(confirmResult) {
      //   if (confirmResult.error) {
      //     // Report to the browser that the payment failed, prompting it to
      //     // re-show the payment interface, or show an error message and close
      //     // the payment interface.
      //     ev.complete('fail');
      //   } else {
      //     // Report to the browser that the confirmation was successful, prompting
      //     // it to close the browser payment method collection interface.
      //     ev.complete('success');
      //     // Check if the PaymentIntent requires any actions and if so let Stripe.js
      //     // handle the flow. If using an API version older than "2019-02-11"
      //     // instead check for: `paymentIntent.status === "requires_source_action"`.
      //     if (confirmResult.paymentIntent.status === "requires_action") {
      //       // Let Stripe.js handle the rest of the payment flow.
      //       stripe.confirmCardPayment(clientSecret).then(function(result) {
      //         if (result.error) {
      //           // The payment failed -- ask your customer for a new payment method.
      //         } else {
      //           // The payment has succeeded.
      //         }
      //       });
      //     } else {
      //       // The payment has succeeded.
      //     }
      //   }
      // });
    });

    // Card Element styles
    let style = {
      base: {
        color: "#32325d",
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: "antialiased",
        fontSize: "16px",
        "::placeholder": {
          color: "#aab7c4"
        }
      },
      invalid: {
        color: "#fa755a",
        iconColor: "#fa755a"
      }
    };


    card = elements.create('card', { style: style });

    card.mount('#card-element');

    card.on('focus', function () {
      let el = document.getElementById('card-errors');
      el.classList.add('focused');
    });

    card.on('blur', function () {
      let el = document.getElementById('card-errors');
      el.classList.remove('focused');
    });

    card.on('change', function (event) {
      var displayError = document.getElementById('card-errors');
      if (event.error) {
        displayError.textContent = event.error.message;
      } else {
        displayError.textContent = '';
      }
    });
  }
  //we'll add payment form handling here
}

function createPaymentMethod({ card }) {

  // Set up payment method for recurring usage
  let billingName = '{{user.username}}';
  // stripe
  //   .createPaymentMethod({
  //     type: 'card',
  //     card: card,
  //     billing_details: {
  //       name: billingName,
  //     },
  //   })
  //   .then((result) => {
  //     if (result.error) {
  //       displayError(result);
  //     } else {
  //      processSubscription(result.paymentMethod.id)

  //     }
  //   });
  stripe
    .confirmCardSetup(document.getElementById('setup_intent_secret').value, {

      payment_method: {
        card: card,
        billing_details: {
          name: 'Test',
        },
      },
    })
    .then((result) => {
      if (result.error) {
        displayError(result);
      } else {
        processSubscription(result.setupIntent.payment_method)

      }
    });
}


var changeLoadingState = function (isLoading) {
  if (isLoading) {
    document.getElementById("submit").disabled = true;
    document.querySelector("#spinner").classList.remove("hidden");
    document.querySelector("#button-text").classList.add("hidden");
  } else {
    document.getElementById("submit").disabled = false;
    document.querySelector("#spinner").classList.add("hidden");
    document.querySelector("#button-text").classList.remove("hidden");
  }
};

function processSubscription(paymentID) {

  var paymentParams = {
    price_id: document.getElementById('price_id').value,
    payment_method: paymentID,
  };

  fetch("/sub/create-subscription/", {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(paymentParams),
  }).then((response) => {
    return response.json();
  }).then((result) => {
    if (result.error) {
      // The card had an error when trying to attach it to a customer
      throw result;
    }
    return result;
  }).then((result) => {
    if (result && result.status === 'incomplete') {

      ConfirmIncompleteSubscription(result.latest_invoice.payment_intent.client_secret,
        result.latest_invoice.payment_intent.payment_method, result.id)
    };
    if (result && result.status === 'active') {

      window.location.href = '/thankyou';
    };
  }).catch(function (error) {
    displayError(error);

  });

}

let paymentForm = document.getElementById('subscription-form');
if (paymentForm) {

  paymentForm.addEventListener('submit', function (evt) {
    evt.preventDefault();
    changeLoadingState(true);


    // create new payment method & create subscription
    createPaymentMethod({ card });
  });
}

function confirmPendingSubscription(secretIntent) {
  var payment_secret_str = document.getElementById('pending_intent_secret').value;
  payment_secret_str = payment_secret_str.split(':')

  ConfirmIncompleteSubscription(payment_secret_str[0], payment_secret_str[1], secretIntent);

}

function ConfirmIncompleteSubscription(secretIntent, paymentMethod, sub_id) {

  stripe.confirmCardPayment(secretIntent, {
    payment_method: paymentMethod,
  })
    .then((result) => {
      if (result.error) {
        // The card was declined (that is, insufficient funds, card has expired, etc).
        alert("SOME thing wrong with Your Card")
      } else {
        if (result.paymentIntent.status === 'succeeded') {
          // Show a success message to your customer.
          console.log("Payment Confirmed Successfully, Waiting for your service activation")
          //alert("Payment Confirmed Successfully, Waiting for your service activation")
          pollSubscriptionStatus(sub_id)
        }
      }
    })
}

function pollSubscriptionStatus(subscriptionID) {

  fetch(`/sub/subscription_poll/${subscriptionID}/`, {
    method: 'GET',
  }).then((response) => {
    return response.json();
  }).then((result) => {
    if (result.status == "active") {
      alert("YOU HAVE MADE IT")
    }
    else {
      LOG_FETCH_COUNT = LOG_FETCH_COUNT + 1;
      if (LOG_FETCH_COUNT < 10)
        pollSubscriptionStatus(subscriptionID)
      else alert("SOME THING WENT WRONG")

    }
  }).catch(function (error) {
    alert("Failed to fetch status")

  });

}

console.log('card')