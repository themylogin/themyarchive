var path = require("path");
var config = {
    entry: ["babel-polyfill", path.resolve(__dirname, "themyarchive/static/js/themyarchive.jsx")],
    output: {
        path: path.resolve(__dirname),
        filename: "themyarchive/static/themyarchive.js"
    },
    module: {
        loaders: [{
            test: /\.jsx?$/,
            loader: "babel",
            query: {
                presets: ["es2015", "react"]
            }
        }]
    }
};

module.exports = config;
