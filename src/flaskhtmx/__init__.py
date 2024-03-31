from flask import Flask, render_template, jsonify, request, abort, redirect, url_for
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
                    feed_["entries"][entry.link] = {
                        **entry,
                        "read": False,
                    }  # Args to declare read, and set value to False

        if feed_url is None:
            # Default url
            feed = list(feeds.values())[0]

        else:
            feed = feeds[feed_url]

        return render_template("feed.html", feed=feed, feeds=feeds)

    @app.route("/entries/<path:feed_url>")
    def render_feed_entries(feed_url: str):
        try:
            feed = feeds[feed_url]
        except KeyError:
            abort(400)

        page = int(request.args.get("page", 0))  # /entries/<path:feed_url>?page=3

        return render_template(
            "partials/entry_page.html",
            entries=list(feed["entries"].values())[page * 5 : page * 5 + 5],
            href=feed["href"],
            page=page,
            max_page=len(feed["entries"]) // 5,
        )

    @app.route("/feed/<path:feed_url>/entry/<path:entry_url>")
    def read_entry(feed_url: str, entry_url: str):
        feed = feeds[feed_url]
        entry = feed["entries"][entry_url]
        entry["read"] = True
        return redirect(entry_url)

    @app.route("/add_feed", methods=["POST"])
    def add_feed():
        feed = request.form.get("url")
        title = request.form.get("title")
        show_images = request.form.get("showImages") == "on"
        feeds[feed] = {
            "title": title,
            "href": feed,
            "show_images": show_images,
            "entries": {},
        }
        return redirect(url_for("render_feed", feed_url=feed))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  # Enable debug mode
