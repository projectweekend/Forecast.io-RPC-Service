var os = require( "os" );
var throng = require( "throng" );
var connections = require( "./shared/connections" );


var logger = connections.logger( [ "Forecast.io-RPC-Service" ] );


var run = function () {
    logger.log( "Starting Forecast.io-RPC-Service" );

    var broker = connections.jackrabbit();
    var weatherman = connections.weatherman();

    var handleMessage = function ( message, ack ) {
        if ( typeof message.options !== "undefined" ) {
            weatherman.options = message.options;
        }
        weatherman.goOnLocation( message.latitude, message.longitude );
        weatherman.doForecast( function ( err, data ) {
            if ( err ) {
                logger.log( "Error with: 'weatherman.doForecast'" );
                process.exit();
            }
            ack( data );
        } );
    };

    var serve = function () {
        logger.log( "Broker ready" );
        broker.handle( "forecast.get", handleMessage );
    };

    var create = function () {
        logger.log( "Broker connected" );
        broker.create( "forecast.get", { prefetch: 5 }, serve );
    };

    process.once( "uncaughtException", function ( err ) {
        logger.log( "Stopping Forecast.io-RPC-Service" );
        logger.log( err );
        process.exit();
    } );

    broker.once( "connected", create );
};


throng( run, {
    workers: os.cpus().length,
    lifetime: Infinity
} );
