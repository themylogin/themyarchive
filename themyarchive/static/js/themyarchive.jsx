import classNames from "classnames"
import it from "iter-tools";
import React from "react";
import ReactDOM from "react-dom";

var Index = React.createClass({
    componentDidMount: function() {
        this.updateUrls();
    },
    getInitialState: function() {
        return {
        };
    },
    render: function() {
        return (
            <div>
                <div style={{ textAlign: "center", marginBottom: "20px" }}>
                    <form className="form-inline" onSubmit={ this.handleSubmit }>
                        <div className="form-group">
                            <label htmlFor="url">URL</label>
                            { " " }
                            <input type="text" className="form-control" id="url" ref="url" />
                        </div>
                        { " " }
                        <div className="form-group">
                            <button type="submit" className="btn btn-primary">Archive</button>
                        </div>
                    </form>
                </div>

                <div className="row">
                    <div className="col-xs-8 col-md-offset-2">
                        <div ref="messages"></div>

                        <UrlList ref="urlList" />
                    </div>
                </div>
            </div>
        );
    },
    updateUrls: function() {
        $.get("/urls/recent", function(urls) {
            this.refs.urlList.setState({
                urls: urls,
            });
        }.bind(this));
    },
    handleSubmit: function(event) {
        var url = this.refs.url.value.trim();

        $.ajax({
            url: "/url",
            method: "POST",
            data: {"url": url},
            success: function() {
                var $success = $("<div/>").addClass("alert alert-success").text("URL " + url + " was added to the worker queue").hide();
                $(this.refs.messages).prepend($success);
                $success.slideDown();
                $success.delay(5000).slideUp();

                this.refs.url.value = "";

                this.updateUrls();
            }.bind(this),
            error: function(jqXHR, textStatus, errorThrown) {
                if (jqXHR.responseJSON && jqXHR.responseJSON.message)
                {
                    var $error = $("<div/>").addClass("alert alert-danger").text(jqXHR.responseJSON.message).hide();
                    $(this.refs.messages).prepend($error);
                    $error.slideDown();
                    $error.delay(5000).slideUp();
                }
            }.bind(this),
        });
        event.preventDefault();
    },
});

var UrlList = React.createClass({
    getInitialState: function() {
        return {
            urls: [],
        };
    },

    render: function() {
        var urls = this.state.urls;
        return (
            <div>
                <h1>Recent URLs</h1>
                {
                    urls.map(function(url) {
                        var key = url.url + " " + url.archived_at;
                        return <UrlListItem key={ key } url={ url } />
                    })
                }
            </div>
        );
    },
});
 
var UrlListItem = React.createClass({
    render: function() {
        var url = this.props.url;
        var anythingReady = it.some(url.variants, (variant) => variant.is_ready);

        return (
            <div className={ anythingReady ? "" : "unavailable" }>
                <span className={ classNames("glyphicon", anythingReady ? "glyphicon-ok" : "glyphicon-time") }></span>
                { " " }
                <a href={ url.view } target="_blank">{ url.url }</a>
            </div>
        );
    }
});

ReactDOM.render(
    <Index />,
    document.getElementById("index")
);

