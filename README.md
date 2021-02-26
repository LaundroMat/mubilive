## MubiLive

Source code that powers the @MubiLive Twitter bot.

Ready to be deployed to Heroku.

### Prerequisites

You'll need a Twitter account to post to and a [Fauna](https://fauna.com/ "Fauna") account.

You'll need a .env file (or set environment variables) containing:

* TWITTER_API_KEY
* TWITTER_API_SECRET
* TWITTER_ACCESS_TOKEN
* TWITTER_ACCESS_TOKEN_SECRET
* FAUNA_DB_KEY

In the Fauna DB, a collection containing documents with this schema is stored:

```
nowShowing
{
    "name": "Ireland", // Country
    "feed": // API Gateway URL for an AWS Lambda function,
	"proxy": // proxy IP address and port (<ip>:<port>)
    "flag": // emoji of the country's flaf, i.e. "🇮🇪" (<- see what I did there)
    "currentMovieId": // id of the movie (as returned from the call to Mubi)
}
```

Each document in the collection corresponds to a country. Mubi Live shows a different movie based on the visitor's country.

The script first sees if there's a feed URL (at first, I used AWS Lambda functions to access Mubi from different countries). If there isn't, it looks for a proxy. If there isn't a proxy, or the proxy times out, it goes through all the proxies for this country on https://free-proxy-list.net/. So make sure the country in your document is written the same as the country in the list on https://free-proxy-list.net/.

### Installation

`./poetry install`

