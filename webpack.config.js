const webpack = require('webpack');

/*
 * Webpack Plugins
 */
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const ManifestRevisionPlugin = require('manifest-revision-webpack-plugin');

// take debug mode from the environment
const debug = (process.env.NODE_ENV !== 'production');

// Development asset host (webpack dev server)
const publicHost = debug ? 'http://localhost:2992' : '';

const rootAssetPath = './assets/';

module.exports = {
  // configuration
  context: __dirname,
  entry: {
    main_js: './assets/js/index',
    app_js: './assets/js/app',
    app_css: [
      './node_modules/font-awesome/css/font-awesome.css',
      './node_modules/bootstrap/dist/css/bootstrap.css',
      './assets/css/style.css',
    ],
  },
  output: {
    path: `${__dirname}/annotator/static`,
    publicPath: `${publicHost}/static/`,
    filename: '[name].[hash].js',
    chunkFilename: '[id].[hash].js',
  },
  resolve: {
    extensions: ['.js', '.jsx', '.css'],
  },
  devtool: debug ? 'inline-sourcemap' : 'source-map',
  devServer: {
    headers: { 'Access-Control-Allow-Origin': '*' },
  },
  mode: debug ? 'development' : 'production',
  module: {
    rules: [
      { test: /\.html$/, use: 'raw-loader' },
      { test: /\.less$/, use: ExtractTextPlugin.extract({ fallback: 'style-loader', use: 'css-loader!less-loader' }) },
      { test: /\.css$/, use: ExtractTextPlugin.extract({ fallback: 'style-loader', use: 'css-loader' }) },
      { test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/, use: 'url-loader?limit=10000&mimetype=application/font-woff' },
      { test: /\.(ttf|eot|svg|png|jpe?g|gif|ico)(\?.*)?$/i,
        use: `file-loader?context=${rootAssetPath}&name=[path][name].[hash].[ext]` },
      { test: /\.js$/,
        exclude: /node_modules/,
        use: [{ loader: 'babel-loader', options: { presets: ['env'], cacheDirectory: true } }] },
    ]
  },
  plugins: [
    new ExtractTextPlugin('[name].[hash].css'),
    new webpack.ProvidePlugin({ $: 'jquery',
                                jQuery: 'jquery' }),
    new ManifestRevisionPlugin(`${__dirname}/annotator/webpack/manifest.json`, {
      rootAssetPath,
      ignorePaths: ['/js', '/css'],
    }),
  ].concat(debug ? [] : [
    // production webpack plugins go here
    new webpack.DefinePlugin({
      'process.env': {
        'NODE_ENV': JSON.stringify('production'),
      },
    }),
  ]),
};
