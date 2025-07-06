Scrapes EventBrite website for the Event IDs of the events that show up, then uses the IDs to query the EventBrite API for jsons about the information of these events.

This is needed because the EventBrite API deprecated their "search by location" functionality a few years back.

The amount of Event IDs is slightly more than the number of lines in the ndjson, this is because the API refuses to return a response when you query it with an event ID, returns something about lacking permissions to view the information for that event. 


Run EventBriteIDScraper first, then run WebScraper, then APICaller.

