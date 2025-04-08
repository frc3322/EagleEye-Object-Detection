const path = require('path');

module.exports = {
    // Switch to 'production' for optimized builds
    mode: 'development',

    // Entry point for your application; adjust as needed
    entry: '/webui/script.js',

    // Output configuration for the bundled file
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, './webui/static'),
        publicPath: '/',
    },

    // Module rules to handle different file types
    module: {
        rules: [
            {
                // Process ES6+ JavaScript files with Babel
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        // Transpile using the preset-env configuration
                        presets: ['@babel/preset-env']
                    }
                }
            }
        ]
    },

    // Resolve configuration for module imports and aliases
    resolve: {
        alias: {
            // Set aliases for easier import paths for Three.js and its extensions.
            // Now you can import these without needing relative paths from your source files.
            three: path.resolve(__dirname, './node_modules/three/build/three.module.js'),
            OrbitControls: path.resolve(__dirname, './node_modules/three/examples/jsm/controls/OrbitControls.js'),
            GLTFLoader: path.resolve(__dirname, './node_modules/three/examples/jsm/loaders/GLTFLoader.js')
        },
        extensions: ['.js'] // Allow omitting .js in import statements
    },

    // Enable source maps for easier debugging
    devtool: 'source-map',

    // Development server configuration
    devServer: {
        static: path.resolve(__dirname, 'dist'),
        port: 8080,
        open: true // Automatically open the browser upon server start
    },
};
