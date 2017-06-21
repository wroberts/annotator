const webpack = require('webpack');

/*
 * Webpack Plugins
 */
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const ManifestRevisionPlugin = require('manifest-revision-webpack-plugin');

// take debug mode from the environment
const debug = (process.env.NODE_ENV !== 'prod');

// Development asset host (webpack dev server)
const publicHost = debug ? 'http://localhost:2992' : '';

module.exports = {
  // configuration
  context: __dirname,
  entry: {
    favicon_ico: './assets/img/favicon.ico',
    main_js: './assets/js/index',
    app_js: './assets/js/app',
    app_css: [
      './node_modules/font-awesome/css/font-awesome.css',
      './node_modules/bootstrap/dist/css/bootstrap.css',
      './assets/css/style.css'
    ]
  },
  output: {
    path: __dirname + '/annotator/static',
    publicPath: publicHost + '/static/',
    filename: '[name].[hash].js',
    chunkFilename: '[id].[hash].js'
  },
  resolve: {
    extensions: ['.js', '.jsx', '.css']
  },
  devServer: {
    headers: {'Access-Control-Allow-Origin': '*'}
  },
  module: {
    loaders: [
      { test: /\.html$/, loader: 'raw-loader' },
      { test: /\.less$/, loader: ExtractTextPlugin.extract({fallback: 'style-loader', use: 'css-loader!less-loader'}) },
      { test: /\.css$/, loader: ExtractTextPlugin.extract({fallback: 'style-loader', use: 'css-loader'}) },
      { test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/, loader: 'url-loader?limit=10000&mimetype=application/font-woff' },
      { test: /\.(ttf|eot|svg|ico)(\?v=[0-9]\.[0-9]\.[0-9])?$/, loader: 'file-loader' },
      { test: /\.(png|jpe?g|gif)(\?\S*)?$/, loader: 'url-loader?limit=100000' },
      { test: /\.js$/, exclude: /node_modules/, loader: 'babel-loader', query: { presets: ['es2015'], cacheDirectory: true, compact: true } },
    ]
  },
  plugins: [
    new ExtractTextPlugin('[name].[hash].css'),
    new webpack.ProvidePlugin({ $: 'jquery',
                                jQuery: 'jquery' }),
    new ManifestRevisionPlugin(__dirname + '/annotator/webpack/manifest.json', {
      rootAssetPath: './assets/'
    }),
  ].concat(debug ? [] : [
    //new webpack.optimize.OccurrenceOrderPlugin(),
    //new webpack.HotModuleReplacementPlugin(),
  ])
};
