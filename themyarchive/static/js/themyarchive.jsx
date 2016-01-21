import classNames from "classnames";
import Cookies from "js-cookie";
import it from "iter-tools";
import React from "react";
import ReactDOM from "react-dom";
import { browserHistory, Router, Route, IndexRoute, Link } from "react-router";

const App = React.createClass({
    render() {
        return (
            <div>
                <nav className="navbar navbar-default">
                    <div className="container">
                        <div className="navbar-header">
                            <button type="button" className="navbar-toggle" data-toggle="collapse" data-target=".navbar-ex1-collapse">
                                <span className="sr-only">Toggle navigation</span>
                                <span className="icon-bar"></span>
                                <span className="icon-bar"></span>
                                <span className="icon-bar"></span>
                            </button>
                            <Link className="navbar-brand" to="/">themyarchive</Link>
                        </div>

                        <div className="collapse navbar-collapse navbar-ex1-collapse">
                            <ul className="nav navbar-nav">
                                <li><Link to="/search">Search</Link></li>
                            </ul>
                            <ul className="nav navbar-nav navbar-right">
                                <li><a href="https://github.com/themylogin/themyarchive">GitHub</a></li>
                            </ul>
                        </div>
                    </div>
                </nav>

                <div className="container" style={{ marginBottom: "20px" }}>
                    {this.props.children}
                </div>
            </div>
        );
    }
});

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
                <div className="jumbotron">
                    <h1>themyarchive</h1>
                    <p>Your personal rich internet archive</p>            
                </div>

                <div style={{ textAlign: "center" }}>
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

                        <h1>Recent URLs</h1>
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

        var url2count = {};
        urls.forEach(url => {
            if (url2count[url.url] == undefined)
            {
                url2count[url.url] = 0;
            }
            
            url2count[url.url]++;
        });

        return (
            <div>
                {
                    urls.map(function(url) {
                        var key = url.url + " " + url.archived_at;
                        var displayDate = url2count[url.url] > 1;
                        return <UrlListItem key={ key } url={ url } displayDate={ displayDate } />
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

        var date = "";
        if (this.props.displayDate)
        {
            var date = (
                <div className={ ".url-list-item__date" }>{ url.archived_at }</div>
            );
        }

        return (
            <div className={ classNames("url-list-item", anythingReady ? "" : "url-list-item_unavailable") }>
                <span className={ classNames("glyphicon", anythingReady ? "glyphicon-ok" : "glyphicon-time") }></span>
                { " " }
                <a href={ url.view } target="_blank">{ url.url }</a>
                { date }
            </div>
        );
    }
});

var Search = React.createClass({
    render: function() {
        return (
            <div>
                <div style={{ textAlign: "center", marginBottom: "20px" }}>
                    <form className="form-inline">
                        <div className="form-group">
                            <input type="text" className="form-control" ref="q" onKeyUp={ this.handleSearch } />
                        </div>
                    </form>
                </div>

                <div className="row">
                    <div className="col-xs-8 col-md-offset-2">
                        <UrlList ref="urlList" />
                    </div>
                </div>
            </div>
        );
    },
    handleSearch: function() {
        var q = this.refs.q.value.trim();
        if (q.length > 3)
        {
            $.get("/urls/search", { q: q }, function(urls) {
                this.refs.urlList.setState({
                    urls: urls,
                });
            }.bind(this));
        }
        else
        {
            this.refs.urlList.setState({
                urls: [],
            });
        }
    },
});

ReactDOM.render((
    <Router history={browserHistory}>
        <Route path="/" component={App}>            
            <IndexRoute component={Index} />
            <Route path="search" component={Search} />
        </Route>
    </Router>
), document.getElementById("container"));

Cookies.set("resolution", $(window).width().toString() + "x" + $(window).height().toString(), { expires: 365 });
