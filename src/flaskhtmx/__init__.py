from flask import Flask, render_template, jsonify
import jinja_partials
import feedparser

feeds = {
    "https://blog.teclado.com/rss/": {
        "title": "The Teclado Blog",
        "href": "https://blog.teclado.com/rss/",
        "show_images": True,
        "entries": {},
    },
    "https://www.joshwcomeau.com/rss.xml": {
        "title": "Josh W. Comeau",
        "href": "https://www.joshwcomeau.com/rss.xml",
        "show_images": False,
        "entries": {},
    },
}


# Flask app
def create_app():
    app = Flask(__name__)
    jinja_partials.register_extensions(app)

    @app.route("/")
    def hello():
        return "Hello from flaskhtmx!"

    # This decorator registers a route for the "/feed/" endpoint in the Flask application.
    # It means that when a request is made to the "/feed/" URL, this function will be executed.
    # Additionally, it registers a route for "/feed/<path:feed_url>", which allows for dynamic URLs.
    # Here, "<path:feed_url>" is a variable part of the URL, allowing for more flexibility.
    # This route can handle URLs like "/feed/example.com/rss" where "example.com/rss" is passed as feed_url.
    @app.route("/feed/")
    @app.route("/feed/<path:feed_url>")
    def render_feed(feed_url: str = None):
        # The feed_url parameter is specified with a type hint of str and set to None as a default value.
        # This means that the function can be called with or without a feed_url parameter.
        # If no parameter is provided, feed_url will be None.
        for url, feed_ in feeds.items():
            parsed_feed = feedparser.parse(url)

            for entry in parsed_feed.entries:
                if entry.link not in feed_["entries"]:
                    feed_["entries"][entry.link] = entry

            if feed_url is None:
                # Default url
                feed = list(feeds.values())[0]
                print(feed)

            else:
                feed = feeds[feed_url]

            return render_template(
                "feed.html", feed=feed, entries=feed["entries"].values(), feeds=feeds
            )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  # Enable debug mode
