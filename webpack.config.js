const NODE_ENV = process.env.NODE_ENV || "development";

const path = require("path");
const webpack = require("webpack");

var config = {
    entry: [
        "babel-polyfill",
        path.resolve(__dirname, "themyarchive/static/js/themyarchive.jsx")
    ],
    output: {
        path: path.resolve(__dirname),
        filename: "themyarchive/static/themyarchive.js"
    },
    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                loader: "babel-loader",
                query: {
                    presets: ["es2015", "react"]
                }
            }
        ]
    },
    plugins: [
        new webpack.optimize.DedupePlugin(),
    ],
};
if (NODE_ENV == "production")
{
    config.plugins.push(
        new webpack.optimize.UglifyJsPlugin({
            compress: {
                warnings:     false,
                drop_console: true,
                unsafe:       true
            }
        })
    );
}

module.exports = config;
