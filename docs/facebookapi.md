# Use of Facebook API

### Example purpose
Fetch the number of reactions, shares and comments for a given list of urls.
For this case, one use the [URL section](https://developers.facebook.com/docs/graph-api/reference/v3.2/url "Graph API - URL") of Facebook's Graph API.

### :page_facing_up: How to

You need to have an **ACCESSTOKEN** in order to use the API. If you have a Facebook developer account, you can use your App ID & Secret Key as a permanent access token : `access_token = "APPID|APPSECRET"`

Once you have the **URL** to analyze and the **FIELDS** you want ("*engagement*" in our example purpose, to get the number of reactions, shares & comments), just call the API with the following url:

<pre>https://graph.facebook.com/v3.1/?id=<b>URL</b>&fields=<b>FIELDS</b>&access_token=<b>ACCESSTOKEN</b></pre>

Example request: 
```https://graph.facebook.com/v3.1/?id=http%3A%2F%2Flemonde.fr&fields=engagement&access_token=APPID|APPSECRET```

Result: 
```json
{
   "engagement": {
      "reaction_count": 74380,
      "comment_count": 53597,
      "share_count": 197091,
      "comment_plugin_count": 8
   },
   "id": "http://lemonde.fr"
}
```

### :no_entry_sign: Restrictions

Our tests showed that the request rate is limited to **one call every 15 seconds**.
May take long if you have 10k urls to process (3,5 days actually :sleeping:).

:warning: Keep in mind that every field counts as one call. If your request features 3 fields, with for example `&fields=engagement,app_links,og_object`, it counts as 3 calls.


### :information_source: Not to forget

* **Call the API with both the HTTP AND the HTTPS versions of the URL** you want to analyze, in order to have the whole number of reactions concerning this URL. *Beware, some urls return the exact same number of reactions for the HTTP and for the HTTPS versions. Be sure to check this before making a total of reactions, in order to avoid a fake (doubled) total.*

* **Encode the URL** to analyze before putting it in the graph url.
Can be done with `encodeURI()` in JS for example.

* **Be sure to have a strictly valid URL**. You can clean your URLs and remove the irrelevant parts, but do not mess with the final `/` if there is one for example. Your browser can add or remove it automatically to find the right page, but the API won't. 
