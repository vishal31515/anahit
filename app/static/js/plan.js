function updateSubscription(subscriptionID, PriceID){

    fetch(`/sub/update-subscription/${subscriptionID}/${PriceID}`, {
      method: 'GET',
    }).then((response) => {
      return response.json(); 
    }).then((result) => {
      if (result.status=="active") {
        alert("YOU HAVE MADE IT")
      }
      else{
        LOG_FETCH_COUNT = LOG_FETCH_COUNT + 1;
        if (LOG_FETCH_COUNT<10)
        pollSubscriptionStatus(subscriptionID)
        else alert("SOME THING WENT WRONG")
        
      }
    }).catch(function (error) {
        alert("Failed to fetch status")

    });

}