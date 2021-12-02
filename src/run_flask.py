import os

from flask import abort, Flask, make_response, redirect, request, url_for

from models import UriType
from redirect_service import RedirectService

app = Flask(__name__)


@app.route("/<identifier>", methods=["GET"])
def redirect_url_api(identifier):
    rs = RedirectService(request)
    redirect_url = rs.parse(identifier)

    if redirect_url is not None:
        if redirect_url.uri_type == UriType.IDENTIFIER:
            # remove starting slash from api url
            url = url_for("redirect_url_api", identifier=redirect_url.redirect_uri)
            url_root = request.url_root

            if url_root.endswith("/"):
                url_root = url_root.rstrip("/")

            short_url = f"{url_root}{url}"
            response = make_response(
                redirect(short_url, code=redirect_url.redirect_type.value)
            )
        else:
            response = make_response(
                redirect(
                    redirect_url.redirect_uri, code=redirect_url.redirect_type.value
                )
            )

        print(f"Redirected: {identifier} -> {redirect_url.redirect_uri}")

        if rs.count_redirect(identifier) is None:
            return abort(404)

        return response
    else:
        return abort(404)


@app.route("/create", methods=["POST"])
def redirect_url_create_api():
    redirect_url = request.args.get("redirect_url", "")

    if not redirect_url:
        return abort(400, "'redirect_url' is missing.")

    rs = RedirectService(request)
    identifier = rs.create_and_add(redirect_url)

    # remove starting slash from api url
    url = url_for("redirect_url_api", identifier=identifier)
    url_root = request.url_root

    if url_root.endswith("/"):
        url_root = url_root.rstrip("/")

    short_url = f"{url_root}{url}"

    print(f"Created Redirection: {identifier} -> {redirect_url}")

    return {
        "short_url": short_url,
    }, 200


if __name__ == "__main__":
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
